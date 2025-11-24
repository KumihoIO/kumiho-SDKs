"""Helpers for locating bearer tokens used by the Python client."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Tuple

_TOKEN_ENV = "KUMIHO_AUTH_TOKEN"
_FIREBASE_TOKEN_ENV = "KUMIHO_FIREBASE_ID_TOKEN"
_CREDENTIALS_FILENAME = "kumiho_authentication.json"
_USE_CP_TOKEN_ENV = "KUMIHO_USE_CONTROL_PLANE_TOKEN"


def _normalize(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _env_flag(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes"}


def _config_dir() -> Path:
    base = os.getenv("KUMIHO_CONFIG_DIR")
    if base:
        return Path(base).expanduser()
    return Path.home() / ".kumiho"


def _credentials_path() -> Path:
    return _config_dir() / _CREDENTIALS_FILENAME


def _read_credentials() -> Optional[dict]:
    path = _credentials_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _credentials_tokens() -> Tuple[Optional[str], Optional[str]]:
    data = _read_credentials()
    if not data:
        return None, None
    return _normalize(data.get("control_plane_token")), _normalize(data.get("id_token"))


def load_bearer_token() -> Optional[str]:
    """Return the preferred bearer token for gRPC calls."""

    env_token = _normalize(os.getenv(_TOKEN_ENV))
    if env_token:
        return env_token

    prefer_control_plane = _env_flag(_USE_CP_TOKEN_ENV)
    control_plane_token, firebase_token = _credentials_tokens()
    if prefer_control_plane and control_plane_token:
        return control_plane_token
    if firebase_token:
        return firebase_token
    if control_plane_token:
        return control_plane_token

    return None


def load_firebase_token() -> Optional[str]:
    """Return a Firebase ID token for control-plane interactions."""

    env_token = _normalize(os.getenv(_FIREBASE_TOKEN_ENV))
    if env_token:
        return env_token

    _, firebase_token = _credentials_tokens()
    return firebase_token
