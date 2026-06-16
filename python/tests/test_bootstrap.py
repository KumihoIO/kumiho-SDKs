from __future__ import annotations

import importlib


def test_bootstrap_uses_env_token_without_ensure(monkeypatch) -> None:
    bootstrap = importlib.import_module("kumiho._bootstrap")

    captured = {}

    class FakeClient:
        def __init__(self, *, force_discovery_refresh=None, auth_token=None, target=None, **_kwargs):
            captured["force_discovery_refresh"] = force_discovery_refresh
            captured["auth_token"] = auth_token
            captured["target"] = target

    def fail_ensure_token(*, interactive=True):
        raise AssertionError("ensure_token should not be called when env token is set")

    monkeypatch.setenv("KUMIHO_AUTH_TOKEN", "env.header.signature")
    monkeypatch.setattr(bootstrap, "_Client", FakeClient)
    monkeypatch.setattr(bootstrap, "ensure_token", fail_ensure_token)

    bootstrap.bootstrap_default_client()

    assert captured["auth_token"] == "env.header.signature"
    assert captured["force_discovery_refresh"] is None


def test_bootstrap_uses_cached_refresh_when_no_env(monkeypatch) -> None:
    bootstrap = importlib.import_module("kumiho._bootstrap")

    captured = {}

    class FakeClient:
        def __init__(self, *, force_discovery_refresh=None, auth_token=None, target=None, **_kwargs):
            captured["force_discovery_refresh"] = force_discovery_refresh
            captured["auth_token"] = auth_token
            captured["target"] = target

    def fake_ensure_token(*, interactive=True):
        return "cached.header.signature", "cached"

    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(bootstrap, "_Client", FakeClient)
    monkeypatch.setattr(bootstrap, "load_bearer_token", lambda: None)
    monkeypatch.setattr(bootstrap, "ensure_token", fake_ensure_token)

    bootstrap.bootstrap_default_client(force_refresh=True)

    assert captured["auth_token"] == "cached.header.signature"
    assert captured["force_discovery_refresh"] is True


def test_client_uses_local_ce_when_cached_token_is_malformed(monkeypatch) -> None:
    client_mod = importlib.import_module("kumiho.client")

    captured = {"interceptors": []}

    class FakeChannel:
        pass

    def fake_insecure_channel(address, options=None):
        captured["address"] = address
        captured["options"] = options
        return FakeChannel()

    def fake_intercept_channel(channel, interceptor):
        captured["interceptors"].append(type(interceptor).__name__)
        return channel

    monkeypatch.setattr(
        client_mod,
        "load_bearer_token",
        lambda: (_ for _ in ()).throw(ValueError("bad token")),
    )
    monkeypatch.setattr(client_mod, "resolve_local_ce_endpoint", lambda: "127.0.0.1:9190")
    monkeypatch.setattr(client_mod.grpc, "insecure_channel", fake_insecure_channel)
    monkeypatch.setattr(client_mod.grpc, "intercept_channel", fake_intercept_channel)
    monkeypatch.setattr(
        client_mod.kumiho_pb2_grpc,
        "KumihoServiceStub",
        lambda channel: {"channel": channel},
    )

    client = client_mod._Client()

    assert client._auth_token is None
    assert captured["address"] == "127.0.0.1:9190"
    assert "_AutoLoginInterceptor" not in captured["interceptors"]


def test_auto_configure_uses_local_ce_without_cached_credentials(monkeypatch) -> None:
    kumiho = importlib.import_module("kumiho")

    recorded = {}

    def fail_ensure_token(*, interactive=True):
        raise AssertionError("cloud login should not run when local CE is available")

    def fake_configure_default_client(client):
        recorded["configured"] = client
        return client

    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.setattr("kumiho._token_loader.load_bearer_token", lambda: None)
    monkeypatch.setattr("kumiho.auth_cli.ensure_token", fail_ensure_token)
    monkeypatch.setattr(kumiho, "client_from_local_ce", lambda: {"client": "local-ce"})
    monkeypatch.setattr(kumiho, "configure_default_client", fake_configure_default_client)

    result = kumiho.auto_configure_from_discovery()

    assert result == {"client": "local-ce"}
    assert recorded["configured"] == result
