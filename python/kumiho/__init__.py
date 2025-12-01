"""
Kumiho Python Client Library
"""

__version__ = "0.3.0"

import contextvars
from typing import Dict, List, Optional, Iterator, Tuple

# Import the main classes to make them available at the package level.
from .base import KumihoObject, KumihoError
from .client import _Client
from .event import Event
from .group import Group
from .kref import Kref
from .link import Link, LinkType, LinkDirection
from .product import Product
from .project import Project
from .resource import Resource
from .proto.kumiho_pb2 import StatusResponse
from .version import Version
from .client import ProjectLimitError
from .discovery import client_from_discovery
from ._bootstrap import bootstrap_default_client

# Expose LinkType constants for convenience
BELONGS_TO = LinkType.BELONGS_TO
CREATED_FROM = LinkType.CREATED_FROM

# Constants
LATEST_TAG = "latest"
PUBLISHED_TAG = "published"
REFERENCED = LinkType.REFERENCED
DEPENDS_ON = LinkType.DEPENDS_ON
DERIVED_FROM = LinkType.DERIVED_FROM
CONTAINS = LinkType.CONTAINS

# Expose LinkDirection constants for convenience
OUTGOING = LinkDirection.OUTGOING
INCOMING = LinkDirection.INCOMING
BOTH = LinkDirection.BOTH

# Instantiate a default client instance for convenience.
_default_client: Optional[_Client] = None
_AUTO_CONFIGURE_ENV = "KUMIHO_AUTO_CONFIGURE"

# Context variable for request-scoped client instances
_client_context_var: contextvars.ContextVar[Optional[_Client]] = contextvars.ContextVar("kumiho_client", default=None)


def get_client() -> _Client:
    """Gets the current client instance, preferring context-local over global default."""
    # Check for context-local client first
    local_client = _client_context_var.get()
    if local_client is not None:
        return local_client
        
    # Fallback to global default
    global _default_client
    if _default_client is None:
        _default_client = bootstrap_default_client()
    return _default_client


def configure_default_client(client: _Client) -> _Client:
    """Override the lazily created default client used by top-level helpers."""
    global _default_client
    _default_client = client
    return _default_client


class use_client:
    """Context manager to temporarily set the current client instance."""
    
    def __init__(self, client: _Client):
        self.client = client
        self.token = None
        
    def __enter__(self):
        self.token = _client_context_var.set(self.client)
        return self.client
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            _client_context_var.reset(self.token)


def auto_configure_from_discovery(
    *,
    tenant_hint: Optional[str] = None,
    force_refresh: bool = False,
    interactive: bool = False,
) -> _Client:
    """Resolve and configure the default client using the cached ~/.kumiho credentials.

    This helper keeps all token material inside the auth cache managed by
    ``kumiho-auth``—no need to write ``firebase_token.txt`` in the repo. It will
    reuse the cached credentials (refreshing if necessary), call the
    control-plane discovery endpoint, and install the resulting client as the
    package-wide default.

    Args:
        tenant_hint: Optional tenant slug/ID to pass to the discovery endpoint.
        force_refresh: Whether to bypass the discovery cache on disk.
        interactive: Allow ``ensure_token`` to fall back to interactive login
            if no cached credentials are available. Defaults to ``False`` so
            REPLs and scripts fail fast when the cache is missing.

    Returns:
        The configured :class:`_Client` instance.

    Raises:
        RuntimeError: If no cached credentials exist and interactive mode is
            disabled.
    """

    from .auth_cli import ensure_token, TokenAcquisitionError  # Lazy import to avoid polluting module attrs
    from ._token_loader import load_bearer_token

    try:
        ensure_token(interactive=interactive)
    except TokenAcquisitionError as exc:
        raise RuntimeError(
            "No cached credentials found. Run 'kumiho-auth login' to "
            "populate ~/.kumiho before calling auto_configure_from_discovery()."
        ) from exc

    token = load_bearer_token()
    if not token:
        raise RuntimeError(
            "Cached credentials missing valid token. Re-run 'kumiho-auth login' "
            "or set KUMIHO_AUTH_TOKEN."
        )

    client = client_from_discovery(
        id_token=token,
        tenant_hint=tenant_hint,
        force_refresh=force_refresh,
    )
    return configure_default_client(client)


def _auto_configure_flag_enabled() -> bool:
    import os

    raw = os.getenv(_AUTO_CONFIGURE_ENV)
    if not raw:
        return False
    return raw.strip().lower() in {"1", "true", "yes"}


def _auto_configure_from_env_if_requested() -> None:
    if not _auto_configure_flag_enabled():
        return
    try:
        auto_configure_from_discovery()
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            "KUMIHO_AUTO_CONFIGURE is set, but automatic discovery bootstrap failed."
        ) from exc

# Expose methods from the default client as top-level package functions (project-scoped entry points only).

def create_project(name: str, description: str = "") -> Project:
    return get_client().create_project(name=name, description=description)

def get_projects() -> List[Project]:
    return get_client().get_projects()

def get_project(name: str) -> Optional[Project]:
    return get_client().get_project(name)

def delete_project(project_id: str, force: bool = False) -> StatusResponse:
    return get_client().delete_project(project_id=project_id, force=force)

def product_search(context_filter: str = "", name_filter: str = "", ptype_filter: str = "") -> List['Product']:
    return get_client().product_search(context_filter, name_filter, ptype_filter)

def get_product(kref: str) -> 'Product':
    """Fetch a product by kref URI."""
    return get_client().get_product_by_kref(kref)

def get_version(kref: str) -> 'Version':
    """Fetch a version by kref URI."""
    return get_client().get_version(kref)

def get_resource(kref: str) -> 'Resource':
    """Fetch a resource by kref URI."""
    return get_client().get_resource_by_kref(kref)

def get_resources_by_location(location: str) -> List['Resource']:
    return get_client().get_resources_by_location(location)

def event_stream(routing_key_filter: str = "", kref_filter: str = "") -> Iterator[Event]:
    """
    Subscribes to the event stream from the Kumiho server.

    Args:
        routing_key_filter (str): A filter for the events to receive.
                                  Supports wildcards, e.g., "product.model.*"
        kref_filter (str): A filter for the kref URIs to receive events for.
                          Supports wildcards, e.g., "kref://projectA/**/*.model"

    Yields:
        Event: An event object representing a change in the database.
    """
    return get_client().event_stream(routing_key_filter, kref_filter)


def resolve(kref: str) -> Optional[str]:
    """
    Resolve a KREF URI to a file location.
    """
    return get_client().resolve(kref)

def connect(
    endpoint: Optional[str] = None,
    token: Optional[str] = None,
    *,
    enable_auto_login: bool = True,
    use_discovery: Optional[bool] = None,
    default_metadata: Optional[List[Tuple[str, str]]] = None,
    tenant_hint: Optional[str] = None,
) -> _Client:
    """
    Connect to a specific Kumiho server.
    
    Args:
        endpoint: The server endpoint (e.g. "localhost:50051").
        token: Optional authentication token.
        enable_auto_login: Whether to enable auto-login.
        use_discovery: Whether to use discovery.
        default_metadata: Optional default metadata.
        tenant_hint: Optional tenant hint.
        
    Returns:
        A configured Client instance.
    """
    return _Client(
        target=endpoint,
        auth_token=token,
        enable_auto_login=enable_auto_login,
        use_discovery=use_discovery,
        default_metadata=default_metadata,
        tenant_hint=tenant_hint,
    )

__all__ = [
    "KumihoObject",
    "KumihoError",
    # "Client",  # Never expose Client directly
    "connect",
    "Project",
    "Group",
    "Product",
    "Version",
    "Resource",
    "Link",
    "Kref",
    "Event",
    "ProjectLimitError",
    # Constants
    "LATEST_TAG",
    "PUBLISHED_TAG",
    # Functions
    "create_project",
    "get_projects",
    "get_project",
    "delete_project",
    "product_search",
    "get_product",
    "get_version",
    "get_resource",
    "get_resources_by_location",
    "event_stream",
    "resolve",
    "auto_configure_from_discovery",
    "LinkType",
    "BELONGS_TO",
    "CREATED_FROM",
    "REFERENCED",
    "DEPENDS_ON",
    "DERIVED_FROM",
    "CONTAINS",
    "LinkDirection",
    "OUTGOING",
    "INCOMING",
    "BOTH",
]

# Remove typing imports from public namespace
del Dict, List, Optional, Iterator


_auto_configure_from_env_if_requested()
