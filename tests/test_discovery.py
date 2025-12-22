from __future__ import annotations

import base64
import importlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from kumiho.discovery import (  # type: ignore[import]
    CacheControl,
    DiscoveryCache,
    DiscoveryRecord,
    RegionRouting,
    client_from_discovery,
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


def _raise_network():
    raise AssertionError("Network should not be invoked when cache is valid")

def _fake_jwt(payload: Dict[str, Any]) -> str:
    def _encode(section: Dict[str, Any]) -> str:
        data = json.dumps(section, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    header = _encode({"alg": "ES256", "typ": "JWT"})
    body = _encode(payload)
    return f"{header}.{body}.sig"


def test_discovery_swaps_control_plane_token(monkeypatch, tmp_path: Path) -> None:
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

    captured: Dict[str, Any] = {}

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

        def json(self):
            return payload

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["authorization"] = headers.get("Authorization") if headers else None
        return FakeResponse()

    monkeypatch.setattr("kumiho.discovery.requests.post", fake_post)

    client_from_discovery(cache_path=str(cache_path), force_refresh=True)

    assert captured["authorization"] == f"Bearer {firebase_token}"
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
