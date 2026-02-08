"""Internal helpers for bootstrapping the default Kumiho client."""
from __future__ import annotations

import logging
import os

from .client import _Client
from .auth_cli import ensure_token, TokenAcquisitionError
from ._token_loader import load_bearer_token

_LOGGER = logging.getLogger("kumiho.bootstrap")


def bootstrap_default_client(*, force_refresh: bool = False) -> _Client:
    """Return a Client that delegates discovery to the public constructor."""

    refresh_flag = True if force_refresh else None

    token = load_bearer_token()
    env_token_present = bool((os.getenv("KUMIHO_AUTH_TOKEN") or "").strip())

    # In non-interactive plugin sessions, an explicit env token should be enough.
    # Only require cached login refresh when no explicit token is provided.
    if not env_token_present:
        try:
            token, _ = ensure_token(interactive=False)
        except TokenAcquisitionError:
            if token is None:
                _LOGGER.warning("Failed to acquire token from cache and no explicit token was provided.")

    try:
        return _Client(force_discovery_refresh=refresh_flag, auth_token=token)
    except Exception:  # pragma: no cover - defensive logging
        _LOGGER.exception("Falling back to direct Client initialisation")
        return _Client(target=None, force_discovery_refresh=None)


__all__ = ["bootstrap_default_client"]
