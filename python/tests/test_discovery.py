from __future__ import annotations

import base64
import importlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

import pytest

from kumiho.discovery import (  # type: ignore[import]
    CacheControl,
    DiscoveryCache,
    DiscoveryRecord,
    DiscoveryError,
    RegionRouting,
    client_from_discovery,
    client_from_local_ce,
    resolve_local_ce_endpoint,
)


def _record(*, refresh_delta: int = 60, expire_delta: int = 300) -> DiscoveryRecord:
    now = datetime.now(timezone.utc)
    cache = CacheControl(
        issued_at=now,
        refresh_at=now + timedelta(seconds=refresh_delta),
        expires_at=now + timedelta(seconds=expire_delta),
        expires_in_seconds=expire_delta,
        refresh_after_seconds=refresh_delta,
    )
    region = RegionRouting(region_code="us-central", server_url="https://us", grpc_authority="us:443")
    return DiscoveryRecord(
        tenant_id="tenant-123",
        tenant_name="Demo",
        roles=["owner"],
        guardrails={"plan": "free"},
        region=region,
        cache_control=cache,
    )


def test_cache_round_trip(tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    cache = DiscoveryCache(cache_path)
    entry = _record()
    cache.store("__default__", entry)

    loaded = cache.load("__default__")
    assert loaded is not None
    assert loaded.tenant_id == "tenant-123"
    assert loaded.region.grpc_authority == "us:443"


def test_client_from_discovery_uses_cache(monkeypatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    cache = DiscoveryCache(cache_path)
    cache.store("__default__", _record())

    monkeypatch.setattr("kumiho.discovery.load_bearer_token", lambda: "token-1")

    created: Dict[str, Any] = {}

    class FakeClient:
        def __init__(self, *, target: str, auth_token: str | None = None, default_metadata=None, **_kwargs):
            created["target"] = target
            created["auth_token"] = auth_token
            created["metadata"] = list(default_metadata or [])

    monkeypatch.setattr("kumiho.discovery.Client", FakeClient)
    monkeypatch.setattr("kumiho.discovery.requests.post", lambda *args, **kwargs: (_raise_network()))

    client_from_discovery(cache_path=str(cache_path))

    assert created["target"] == "us:443"
    assert created["auth_token"] == "token-1"
    assert ("x-tenant-id", "tenant-123") in created["metadata"]


def test_client_from_discovery_refreshes_expired_cache(monkeypatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    expired_entry = _record(refresh_delta=-10, expire_delta=-5)
    cache = DiscoveryCache(cache_path)
    cache.store("__default__", expired_entry)

    monkeypatch.setattr("kumiho.discovery.load_bearer_token", lambda: "token-2")

    created: Dict[str, Any] = {}

    class FakeClient:
        def __init__(self, *, target: str, auth_token: str | None = None, default_metadata=None, **_kwargs):
            created["target"] = target
            created["auth_token"] = auth_token
            created["metadata"] = list(default_metadata or [])

    monkeypatch.setattr("kumiho.discovery.Client", FakeClient)

    new_payload = {
        "tenant_id": "tenant-abc",
        "tenant_name": "Updated",
        "roles": ["editor"],
        "guardrails": None,
        "region": {
            "region_code": "eu",
            "server_url": "https://eu",
            "grpc_authority": "eu:443",
        },
        "cache_control": {
            "issued_at": "2025-01-01T00:00:00+00:00",
            "refresh_at": "2025-01-01T00:05:00+00:00",
            "expires_at": "2025-01-01T00:10:00+00:00",
            "expires_in_seconds": 600,
            "refresh_after_seconds": 300,
        },
    }

    class FakeResponse:
        status_code = 200

        def json(self):
            return new_payload

    monkeypatch.setattr("kumiho.discovery.requests.post", lambda *args, **kwargs: FakeResponse())

    client_from_discovery(cache_path=str(cache_path))

    assert created["target"] == "eu:443"
    assert ("x-tenant-id", "tenant-abc") in created["metadata"]


def test_resolve_local_ce_endpoint_accepts_loopback_live_payload(monkeypatch) -> None:
    monkeypatch.delenv("KUMIHO_LOCAL_SERVER_ENDPOINT", raising=False)
    monkeypatch.delenv("KUMIHO_LOCAL_SERVER_PORT", raising=False)

    captured: Dict[str, Any] = {}

    class FakeResponse:
        status_code = 200

        def json(self) -> Dict[str, str]:
            return {"status": "ok", "deployment_mode": "self_hosted_ce"}

    def fake_get(url: str, timeout: float):
        captured["url"] = url
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("kumiho.discovery.requests.get", fake_get)

    target = resolve_local_ce_endpoint(timeout=0.1)

    assert target == "127.0.0.1:9190"
    assert captured == {"url": "http://127.0.0.1:9190/api/_live", "timeout": 0.1}


def test_resolve_local_ce_endpoint_refuses_non_loopback_override(monkeypatch) -> None:
    monkeypatch.setenv("KUMIHO_LOCAL_SERVER_ENDPOINT", "10.0.0.5:8080")

    with pytest.raises(DiscoveryError, match="localhost"):
        resolve_local_ce_endpoint(timeout=0.1)


def test_client_from_local_ce_is_tokenless(monkeypatch) -> None:
    created: Dict[str, Any] = {}

    class FakeClient:
        def __init__(
            self,
            *,
            target: str,
            auth_token: str | None = None,
            default_metadata=None,
            use_discovery=None,
            enable_auto_login=True,
            skip_auth_token_load=False,
            **_kwargs,
        ):
            created["target"] = target
            created["auth_token"] = auth_token
            created["metadata"] = list(default_metadata or [])
            created["use_discovery"] = use_discovery
            created["enable_auto_login"] = enable_auto_login
            created["skip_auth_token_load"] = skip_auth_token_load

    monkeypatch.setattr("kumiho.discovery.Client", FakeClient)
    monkeypatch.setattr(
        "kumiho.discovery.resolve_local_ce_endpoint",
        lambda timeout=None: "127.0.0.1:9190",
    )

    client_from_local_ce()

    assert created == {
        "target": "127.0.0.1:9190",
        "auth_token": None,
        "metadata": [],
        "use_discovery": False,
        "enable_auto_login": False,
        "skip_auth_token_load": True,
    }


def _raise_network():
    raise AssertionError("Network should not be invoked when cache is valid")

def _fake_jwt(payload: Dict[str, Any]) -> str:
    def _encode(section: Dict[str, Any]) -> str:
        data = json.dumps(section, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    header = _encode({"alg": "ES256", "typ": "JWT"})
    body = _encode(payload)
    return f"{header}.{body}.sig"


def test_discovery_prefers_control_plane_token(monkeypatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    control_plane_token = _fake_jwt(
        {
            "iss": "https://control.kumiho.cloud",
            "aud": "kumiho-server",
            "tenant_id": "tenant-xyz",
        }
    )
    firebase_token = "firebase-id-token"
    monkeypatch.setattr("kumiho.discovery.load_bearer_token", lambda: control_plane_token)
    monkeypatch.setattr("kumiho.discovery.load_firebase_token", lambda: firebase_token)

    created: Dict[str, Any] = {}

    class FakeClient:
        def __init__(self, *, target: str, auth_token: str | None = None, default_metadata=None, **_kwargs):
            created["target"] = target
            created["auth_token"] = auth_token
            created["metadata"] = list(default_metadata or [])

    monkeypatch.setattr("kumiho.discovery.Client", FakeClient)

    captured: Dict[str, Any] = {"authorizations": []}

    payload = {
        "tenant_id": "tenant-xyz",
        "tenant_name": "CP",
        "roles": ["owner"],
        "guardrails": None,
        "region": {
            "region_code": "us",
            "server_url": "https://us",
            "grpc_authority": "us:443",
        },
        "cache_control": {
            "issued_at": "2025-01-01T00:00:00+00:00",
            "refresh_at": "2025-01-01T00:05:00+00:00",
            "expires_at": "2025-01-01T00:10:00+00:00",
            "expires_in_seconds": 600,
            "refresh_after_seconds": 300,
        },
    }

    class FakeResponse:
        status_code = 200
        text = ""

        def json(self):
            return payload

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["authorizations"].append(headers.get("Authorization") if headers else None)
        return FakeResponse()

    monkeypatch.setattr("kumiho.discovery.requests.post", fake_post)

    client_from_discovery(cache_path=str(cache_path), force_refresh=True)

    assert captured["authorizations"] == [f"Bearer {control_plane_token}"]
    assert created["auth_token"] == control_plane_token


def test_discovery_falls_back_to_firebase_token(monkeypatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    control_plane_token = _fake_jwt(
        {
            "iss": "https://control.kumiho.cloud",
            "aud": "kumiho-server",
            "tenant_id": "tenant-xyz",
        }
    )
    firebase_token = "firebase-id-token"
    monkeypatch.setattr("kumiho.discovery.load_bearer_token", lambda: control_plane_token)
    monkeypatch.setattr("kumiho.discovery.load_firebase_token", lambda: firebase_token)

    created: Dict[str, Any] = {}

    class FakeClient:
        def __init__(self, *, target: str, auth_token: str | None = None, default_metadata=None, **_kwargs):
            created["target"] = target
            created["auth_token"] = auth_token
            created["metadata"] = list(default_metadata or [])

    monkeypatch.setattr("kumiho.discovery.Client", FakeClient)

    captured: Dict[str, Any] = {"authorizations": []}

    payload = {
        "tenant_id": "tenant-xyz",
        "tenant_name": "CP",
        "roles": ["owner"],
        "guardrails": None,
        "region": {
            "region_code": "us",
            "server_url": "https://us",
            "grpc_authority": "us:443",
        },
        "cache_control": {
            "issued_at": "2025-01-01T00:00:00+00:00",
            "refresh_at": "2025-01-01T00:05:00+00:00",
            "expires_at": "2025-01-01T00:10:00+00:00",
            "expires_in_seconds": 600,
            "refresh_after_seconds": 300,
        },
    }

    class RejectResponse:
        status_code = 401
        text = '{"error":"invalid_id_token"}'

        def json(self):
            return {"error": "invalid_id_token"}

    class SuccessResponse:
        status_code = 200
        text = ""

        def json(self):
            return payload

    call_count = {"value": 0}

    def fake_post(url, json=None, headers=None, timeout=None):
        call_count["value"] += 1
        captured["authorizations"].append(headers.get("Authorization") if headers else None)
        if call_count["value"] == 1:
            return RejectResponse()
        return SuccessResponse()

    monkeypatch.setattr("kumiho.discovery.requests.post", fake_post)

    client_from_discovery(cache_path=str(cache_path), force_refresh=True)

    assert captured["authorizations"] == [
        f"Bearer {control_plane_token}",
        f"Bearer {firebase_token}",
    ]
    assert created["auth_token"] == control_plane_token


def test_auto_configure_from_discovery(monkeypatch) -> None:
    kumiho = importlib.import_module("kumiho")

    recorded = {}

    def fake_ensure_token(*, token_file=None, interactive=True):
        recorded["ensure_token"] = {"token_file": token_file, "interactive": interactive}
        return "cached-cp", "cached"

    def fake_load_bearer_token():
        return "firebase-from-cache"

    def fake_client_from_discovery(*, id_token, tenant_hint=None, force_refresh=False, cache_path=None):
        recorded["discovery"] = {
            "id_token": id_token,
            "tenant_hint": tenant_hint,
            "force_refresh": force_refresh,
            "cache_path": cache_path,
        }
        return {"client": id_token}

    configured = {}

    def fake_configure_default_client(client):
        configured["client"] = client
        return client

    monkeypatch.setattr("kumiho.auth_cli.ensure_token", fake_ensure_token)
    monkeypatch.setattr(kumiho, "client_from_discovery", fake_client_from_discovery)
    monkeypatch.setattr(kumiho, "configure_default_client", fake_configure_default_client)
    monkeypatch.setattr("kumiho._token_loader.load_bearer_token", fake_load_bearer_token)

    result = kumiho.auto_configure_from_discovery(tenant_hint="tenant-xyz", force_refresh=True)

    assert result == {"client": "firebase-from-cache"}
    assert configured["client"] == result
    assert recorded["ensure_token"] == {"token_file": None, "interactive": False}
    assert recorded["discovery"] == {
        "id_token": "firebase-from-cache",
        "tenant_hint": "tenant-xyz",
        "force_refresh": True,
        "cache_path": None,
    }


def test_auto_configure_from_discovery_uses_env_token(monkeypatch) -> None:
    kumiho = importlib.import_module("kumiho")

    recorded: Dict[str, Any] = {}

    def fail_ensure_token(*, token_file=None, interactive=True):
        raise AssertionError("ensure_token should not be called when KUMIHO_AUTH_TOKEN is set")

    def fake_client_from_discovery(*, id_token, tenant_hint=None, force_refresh=False, cache_path=None):
        recorded["discovery"] = {
            "id_token": id_token,
            "tenant_hint": tenant_hint,
            "force_refresh": force_refresh,
            "cache_path": cache_path,
        }
        return {"client": id_token}

    def fake_configure_default_client(client):
        recorded["configured"] = client
        return client

    monkeypatch.setenv("KUMIHO_AUTH_TOKEN", "env.header.signature")
    monkeypatch.setattr("kumiho.auth_cli.ensure_token", fail_ensure_token)
    monkeypatch.setattr(kumiho, "client_from_discovery", fake_client_from_discovery)
    monkeypatch.setattr(kumiho, "configure_default_client", fake_configure_default_client)

    result = kumiho.auto_configure_from_discovery(tenant_hint="tenant-env", force_refresh=False)

    assert result == {"client": "env.header.signature"}
    assert recorded["configured"] == result
    assert recorded["discovery"] == {
        "id_token": "env.header.signature",
        "tenant_hint": "tenant-env",
        "force_refresh": False,
        "cache_path": None,
    }


def test_auto_configure_helper_runs_when_env_set(monkeypatch) -> None:
    kumiho = importlib.import_module("kumiho")

    called = {}

    def fake_auto():
        called["triggered"] = True

    monkeypatch.setenv("KUMIHO_AUTO_CONFIGURE", "true")
    monkeypatch.setattr(kumiho, "auto_configure_from_discovery", fake_auto)

    kumiho._auto_configure_from_env_if_requested()

    assert called.get("triggered") is True


def test_auto_configure_helper_noop_without_flag(monkeypatch) -> None:
    kumiho = importlib.import_module("kumiho")

    called = {}

    def fake_auto():
        called["triggered"] = True

    monkeypatch.delenv("KUMIHO_AUTO_CONFIGURE", raising=False)
    monkeypatch.setattr(kumiho, "auto_configure_from_discovery", fake_auto)

    kumiho._auto_configure_from_env_if_requested()

    assert "triggered" not in called
