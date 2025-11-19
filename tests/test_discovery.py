from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from kumiho.discovery import (
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
