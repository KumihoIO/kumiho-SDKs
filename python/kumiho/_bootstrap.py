"""Internal helpers for bootstrapping the default Kumiho client."""
from __future__ import annotations

import logging

from .client import Client

_LOGGER = logging.getLogger("kumiho.bootstrap")


def bootstrap_default_client(*, force_refresh: bool = False) -> Client:
    """Return a Client that delegates discovery to the public constructor."""

    refresh_flag = True if force_refresh else None
    try:
        return Client(force_discovery_refresh=refresh_flag)
    except Exception:  # pragma: no cover - defensive logging
        _LOGGER.exception("Falling back to direct Client initialisation")
        return Client(target=None, force_discovery_refresh=None)


__all__ = ["bootstrap_default_client"]
