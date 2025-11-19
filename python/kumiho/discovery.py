"""Helpers for bootstrapping a Client via the control-plane discovery endpoint."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

import requests

from ._token_loader import load_bearer_token
from .client import Client

DEFAULT_CONTROL_PLANE_URL = os.getenv("KUMIHO_CONTROL_PLANE_URL") or "https://kumiho.io"
DEFAULT_CACHE_PATH = Path(
    os.getenv("KUMIHO_DISCOVERY_CACHE_FILE")
    or (Path.home() / ".kumiho" / "discovery-cache.json")
)
_DEFAULT_TIMEOUT = float(os.getenv("KUMIHO_DISCOVERY_TIMEOUT_SECONDS", "10"))
_DEFAULT_CACHE_KEY = "__default__"


class DiscoveryError(RuntimeError):
    """Raised when the discovery endpoint cannot be reached or returns an error."""


@dataclass(frozen=True)
class RegionRouting:
    region_code: str
    server_url: str
    grpc_authority: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RegionRouting":
        return cls(
            region_code=payload["region_code"],
            server_url=payload["server_url"],
            grpc_authority=payload.get("grpc_authority"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "region_code": self.region_code,
            "server_url": self.server_url,
        }
        if self.grpc_authority:
            data["grpc_authority"] = self.grpc_authority
        return data


@dataclass(frozen=True)
class CacheControl:
    issued_at: datetime
    refresh_at: datetime
    expires_at: datetime
    expires_in_seconds: int
    refresh_after_seconds: int

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CacheControl":
        issued_at = _parse_iso8601(payload.get("issued_at"))
        refresh_at = _parse_iso8601(payload.get("refresh_at"))
        expires_at = _parse_iso8601(payload.get("expires_at"))
        return cls(
            issued_at=issued_at,
            refresh_at=refresh_at,
            expires_at=expires_at,
            expires_in_seconds=int(payload.get("expires_in_seconds", 0)),
            refresh_after_seconds=int(payload.get("refresh_after_seconds", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issued_at": self.issued_at.isoformat(),
            "refresh_at": self.refresh_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "expires_in_seconds": self.expires_in_seconds,
            "refresh_after_seconds": self.refresh_after_seconds,
        }

    def is_expired(self, *, now: Optional[datetime] = None) -> bool:
        moment = now or datetime.now(timezone.utc)
        return moment >= self.expires_at

    def should_refresh(self, *, now: Optional[datetime] = None) -> bool:
        moment = now or datetime.now(timezone.utc)
        return moment >= self.refresh_at


@dataclass(frozen=True)
class DiscoveryRecord:
    tenant_id: str
    tenant_name: Optional[str]
    roles: Sequence[str]
    guardrails: Optional[Dict[str, Any]]
    region: RegionRouting
    cache_control: CacheControl

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DiscoveryRecord":
        cache_section = payload.get("cache_control")
        if not cache_section:
            raise DiscoveryError("Discovery payload is missing cache_control metadata")
        region_section = payload.get("region")
        if not region_section:
            raise DiscoveryError("Discovery payload is missing region metadata")
        return cls(
            tenant_id=payload["tenant_id"],
            tenant_name=payload.get("tenant_name"),
            roles=list(payload.get("roles", [])),
            guardrails=payload.get("guardrails"),
            region=RegionRouting.from_dict(region_section),
            cache_control=CacheControl.from_dict(cache_section),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "roles": list(self.roles),
            "guardrails": self.guardrails,
            "region": self.region.to_dict(),
            "cache_control": self.cache_control.to_dict(),
        }


class DiscoveryCache:
    """Simple JSON file cache keyed by tenant hint."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or DEFAULT_CACHE_PATH

    def load(self, cache_key: str) -> Optional[DiscoveryRecord]:
        payload = self._read_all().get(cache_key)
        if not payload:
            return None
        try:
            return DiscoveryRecord.from_dict(payload)
        except DiscoveryError:
            return None

    def store(self, cache_key: str, record: DiscoveryRecord) -> None:
        data = self._read_all()
        data[cache_key] = record.to_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        tmp_path.replace(self.path)

    def _read_all(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}


class DiscoveryManager:
    """Coordinates cache usage and remote discovery calls."""

    def __init__(
        self,
        *,
        control_plane_url: Optional[str] = None,
        cache_path: Optional[Path] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.base_url = control_plane_url or DEFAULT_CONTROL_PLANE_URL
        self.cache = DiscoveryCache(cache_path)
        self.timeout = timeout or _DEFAULT_TIMEOUT

    def resolve(
        self,
        *,
        id_token: str,
        tenant_hint: Optional[str] = None,
        force_refresh: bool = False,
    ) -> DiscoveryRecord:
        cache_key = tenant_hint or _DEFAULT_CACHE_KEY
        if not force_refresh:
            cached = self.cache.load(cache_key)
            if cached and not cached.cache_control.is_expired():
                if cached.cache_control.should_refresh():
                    try:
                        fresh = self._fetch_remote(id_token=id_token, tenant_hint=tenant_hint)
                        self.cache.store(cache_key, fresh)
                        return fresh
                    except DiscoveryError:
                        # Fall back to cached copy if it is still valid.
                        if not cached.cache_control.is_expired():
                            return cached
                        raise
                return cached

        fresh = self._fetch_remote(id_token=id_token, tenant_hint=tenant_hint)
        self.cache.store(cache_key, fresh)
        return fresh

    def _fetch_remote(self, *, id_token: str, tenant_hint: Optional[str]) -> DiscoveryRecord:
        url = _build_discovery_url(self.base_url)
        headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
        payload: Dict[str, Any] = {}
        if tenant_hint:
            payload["tenant_hint"] = tenant_hint

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if response.status_code >= 400:
            raise DiscoveryError(
                f"Discovery endpoint returned {response.status_code}: {response.text[:200]}"
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise DiscoveryError("Discovery endpoint returned invalid JSON") from exc
        return DiscoveryRecord.from_dict(body)


def client_from_discovery(
    *,
    id_token: Optional[str] = None,
    tenant_hint: Optional[str] = None,
    control_plane_url: Optional[str] = None,
    cache_path: Optional[str] = None,
    force_refresh: bool = False,
    default_metadata: Optional[Sequence[Tuple[str, str]]] = None,
) -> Client:
    """Create a Client configured via the public discovery endpoint.

    The helper caches discovery payloads based on the tenant hint, respects the
    cache-control metadata emitted by the control plane, and refreshes the
    routing info once the `refresh_after_seconds` deadline passes.
    """

    token = id_token or load_bearer_token()
    if not token:
        raise DiscoveryError(
            "A Firebase ID token is required. Set KUMIHO_AUTH_TOKEN or run kumiho-auth login."
        )

    manager = DiscoveryManager(control_plane_url=control_plane_url, cache_path=Path(cache_path) if cache_path else None)
    record = manager.resolve(id_token=token, tenant_hint=tenant_hint, force_refresh=force_refresh)

    target = record.region.grpc_authority or record.region.server_url
    metadata: Iterable[Tuple[str, str]] = list(default_metadata or [])
    metadata = list(metadata)
    metadata.append(("x-tenant-id", record.tenant_id))

    return Client(target=target, auth_token=token, default_metadata=metadata)


def _parse_iso8601(raw: Optional[str]) -> datetime:
    if not raw:
        raise DiscoveryError("Discovery payload missing required timestamp")
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _build_discovery_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/api/discovery/tenant"):
        return base
    if base.endswith("/api/discovery"):
        return f"{base}/tenant"
    if base.endswith("/api"):
        return f"{base}/discovery/tenant"
    return f"{base}/api/discovery/tenant"
