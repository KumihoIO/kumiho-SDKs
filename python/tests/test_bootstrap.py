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
