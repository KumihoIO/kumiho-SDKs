"""Per-request tenant/user context for hosted (multi-tenant) deployments.

The stdio MCP server is single-tenant by construction: one process, one user,
one set of credentials in the environment. A hosted deployment inverts that —
one process serves many tenants concurrently — so every piece of state that
used to be safely process-global (auth token, caches, session pointers) has to
become request-scoped instead.

This module is the seam. A hosting layer (``kumiho-plugins/cloud-mcp``) builds
a :class:`RequestContext` from the verified bearer token and enters
:func:`request_context` for the duration of the request; everything downstream
reads it through :func:`current_request`.

A ``contextvars.ContextVar`` is the right carrier rather than a thread-local:
the MCP server dispatches tool handlers with ``asyncio.to_thread``, which
copies the current context into the worker thread, so the value follows the
request across the async/sync boundary without being passed explicitly through
every call site.

Rules when :func:`current_request` returns a context (see the hosted-connector
plan, §2.1):

- never read ``~/.kumiho/*``, never mutate ``os.environ``, never use the
  machine-id discovery cache file;
- every per-process cache must be keyed by ``tenant_id``;
- ``kumiho.get_client()`` must resolve through :func:`kumiho.use_client`, and
  ``kumiho_memory`` must set ``redis_token_override_var`` from
  ``ctx.auth_token`` when it is unset.

:func:`hosted_mode` is the coarse, process-wide opt-in
(``KUMIHO_MCP_HOSTED=1``). It is deliberately separate from
:func:`current_request`: a hosted process must behave defensively (no env
mutation, no filesystem writes) even on code paths that run outside a request,
such as server construction.
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Iterator, List, Optional
from contextlib import contextmanager


@dataclass(frozen=True)
class RequestContext:
    """Identity and routing for a single hosted request.

    Frozen on purpose: a handler that mutated the context would change it for
    every other frame sharing the same ``contextvars`` copy, including worker
    threads already running. Replace it with :func:`request_context` instead.
    """

    tenant_id: str            # UUID from token claims
    user_id: str              # firebase uid (OAuth) or "service:<token_id>" (API key)
    auth_token: str           # the raw bearer/api-key JWT presented by the caller
    context: str = "claude"   # memory context namespace (active-session pointer key)
    session_id: Optional[str] = None
    client_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    tenant_slug: Optional[str] = None
    region_code: Optional[str] = None
    token_id: Optional[str] = None   # jti


_request_var: contextvars.ContextVar[Optional[RequestContext]] = contextvars.ContextVar(
    "kumiho_request", default=None
)


def current_request() -> Optional[RequestContext]:
    """Return the context for the in-flight request, or ``None`` when local."""
    return _request_var.get()


@contextmanager
def request_context(ctx: RequestContext) -> Iterator[RequestContext]:
    """Bind *ctx* for the duration of the block.

    Resets to the previous value on exit — including on exception — so nested
    and concurrent requests never leak into each other.
    """
    token = _request_var.set(ctx)
    try:
        yield ctx
    finally:
        _request_var.reset(token)


def hosted_mode() -> bool:
    """True when this process is running as a multi-tenant hosted server."""
    import os
    return os.environ.get("KUMIHO_MCP_HOSTED", "").strip().lower() in ("1", "true", "yes")


__all__ = [
    "RequestContext",
    "current_request",
    "request_context",
    "hosted_mode",
]
