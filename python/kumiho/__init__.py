"""Kumiho Python Client Library.

Kumiho is a graph-native creative and AI asset management system that tracks
versions, relationships, and lineage without uploading original files to the
cloud. This SDK provides a Pythonic interface to the Kumiho gRPC backend.

Getting Started:
    The simplest way to use Kumiho is with the top-level functions that
    use a default client configured from your environment::

        import kumiho

        # Authenticate and configure (run once per session)
        kumiho.auto_configure_from_discovery() # This can be avoided if env var KUMIHO_AUTO_CONFIGURE=1 is set

        # Create a project
        project = kumiho.create_project("my-vfx-project", "VFX assets for commercial")

        # Create groups and products
        group = project.create_group("characters")
        product = group.create_product("hero", "model")

        # Create versions and resources
        version = product.create_version()
        resource = version.create_resource("main", "/path/to/hero.fbx")

    For more control, you can create a client manually::

        import kumiho

        client = kumiho.connect(
            endpoint="localhost:50051",
            token="your-auth-token"
        )

        with kumiho.use_client(client):
            projects = kumiho.get_projects()

Key Concepts:
    - **Project**: Top-level container for all assets and groups.
    - **Group**: Hierarchical folder structure within a project.
    - **Product**: A versioned asset (model, texture, workflow, etc.).
    - **Version**: A specific iteration of a product with resources.
    - **Resource**: A file reference (path/URI) within a version.
    - **Link**: A relationship between versions (dependencies, references).
    - **Kref**: A URI-based unique identifier for any Kumiho object.

Authentication:
    Kumiho uses Firebase authentication. Run the CLI to log in::

        kumiho-auth login

    This caches credentials in ``~/.kumiho/``. Then use
    :func:`auto_configure_from_discovery` to bootstrap the client.

Environment Variables:
    - ``KUMIHO_AUTO_CONFIGURE``: Set to "1" to auto-configure on import.
    - ``KUMIHO_AUTH_TOKEN``: Override the authentication token.
    - ``KUMIHO_CONTROL_PLANE_URL``: Override the control plane URL.
    - ``KUMIHO_ENDPOINT``: Override the gRPC endpoint.

Example:
    Complete workflow example::

        import kumiho

        # Configure client from cached credentials
        kumiho.auto_configure_from_discovery()

        # Get or create project
        project = kumiho.get_project("my-project")
        if not project:
            project = kumiho.create_project("my-project", "My VFX project")

        # Navigate to asset group
        assets = project.get_group("assets") or project.create_group("assets")

        # Create a new model product
        model = assets.create_product("character", "model")

        # Create first version
        v1 = model.create_version(metadata={"author": "artist1"})
        v1.create_resource("mesh", "/projects/char/v1/mesh.fbx")
        v1.create_resource("textures", "/projects/char/v1/textures.zip")
        v1.tag("approved")
        v1.tag("published") # published tag is reserved tag within Kumiho as version with immutable semantics

        # Query by kref
        product = kumiho.get_product("kref://my-project/assets/character.model")
        version = kumiho.get_version("kref://my-project/assets/character.model?v=1")

        # Search across project
        models = kumiho.product_search(
            context_filter="my-project",
            ptype_filter="model"
        )

Note:
    Kumiho follows a "BYO Storage" philosophy—files remain on your local
    or network storage. Kumiho only tracks paths, metadata, and relationships
    in its graph database.

See Also:
    - Kumiho documentation: https://docs.kumiho.cloud
    - GitHub: https://github.com/kumihoclouds/kumiho-python

Attributes:
    __version__ (str): The current version of the kumiho package.
    LATEST_TAG (str): Standard tag name for the latest version.
    PUBLISHED_TAG (str): Standard tag name for published versions.
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
"""str: Standard tag name indicating the latest version of a product."""

PUBLISHED_TAG = "published"
"""str: Standard tag name indicating a published/released version."""

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
    """Get the current Kumiho client instance.

    Returns the context-local client if set via :class:`use_client`,
    otherwise returns the global default client (creating one if needed).

    Returns:
        _Client: The active client instance.

    Raises:
        RuntimeError: If no client is configured and auto-bootstrap fails.

    Example:
        >>> client = kumiho.get_client()
        >>> projects = client.get_projects()
    """
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
    """Set the global default client used by top-level helper functions.

    This function allows you to manually configure the default client
    that will be used by functions like :func:`create_project`,
    :func:`get_projects`, etc.

    Args:
        client: The client instance to set as the default.

    Returns:
        _Client: The same client instance (for chaining).

    Example:
        >>> client = kumiho.connect(endpoint="localhost:50051")
        >>> kumiho.configure_default_client(client)
        >>> # Now all top-level functions use this client
        >>> projects = kumiho.get_projects()
    """
    global _default_client
    _default_client = client
    return _default_client


class use_client:
    """Context manager to temporarily set the current client instance.

    This is useful for multi-tenant scenarios or when you need to
    use different clients for different operations within the same
    thread or async context.

    Args:
        client: The client to use within the context.

    Example:
        Using different clients for different tenants::

            import kumiho

            tenant_a_client = kumiho.connect(endpoint="tenant-a.kumiho.cloud:443")
            tenant_b_client = kumiho.connect(endpoint="tenant-b.kumiho.cloud:443")

            with kumiho.use_client(tenant_a_client):
                # All operations here use tenant_a_client
                projects_a = kumiho.get_projects()

            with kumiho.use_client(tenant_b_client):
                # All operations here use tenant_b_client
                projects_b = kumiho.get_projects()

    Note:
        Context-local clients take precedence over the global default.
        This works correctly with async code and concurrent requests.
    """
    
    def __init__(self, client: _Client):
        """Initialize the context manager.

        Args:
            client: The client to use within the context.
        """
        self.client = client
        self.token = None
        
    def __enter__(self):
        """Enter the context and set the client."""
        self.token = _client_context_var.set(self.client)
        return self.client
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and restore the previous client."""
        if self.token:
            _client_context_var.reset(self.token)


def auto_configure_from_discovery(
    *,
    tenant_hint: Optional[str] = None,
    force_refresh: bool = False,
    interactive: bool = False,
) -> _Client:
    """Configure the default client using cached credentials and discovery.

    This is the recommended way to bootstrap the Kumiho client. It uses
    credentials cached by ``kumiho-auth login`` and calls the control-plane
    discovery endpoint to resolve the correct regional server.

    Args:
        tenant_hint: Optional tenant slug or ID to use for discovery.
            If not provided, the user's default tenant is used.
        force_refresh: If True, bypass the discovery cache and fetch
            fresh routing information from the control plane.
        interactive: If True and no cached credentials exist, prompt
            for interactive login. Defaults to False for script safety.

    Returns:
        _Client: The configured client instance, also set as the default.

    Raises:
        RuntimeError: If no cached credentials exist and interactive
            mode is disabled.

    Example:
        Basic usage::

            import kumiho

            # First, run: kumiho-auth login
            # Then in your code:
            kumiho.auto_configure_from_discovery()

            # Now you can use all kumiho functions
            projects = kumiho.get_projects()

        With tenant hint for multi-tenant access::

            kumiho.auto_configure_from_discovery(tenant_hint="my-studio")

    See Also:
        :func:`connect`: For manual client configuration.
        :class:`use_client`: For temporary client switching.
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

# =============================================================================
# Top-level convenience functions
# =============================================================================


def create_project(name: str, description: str = "") -> Project:
    """Create a new project.

    Projects are the top-level containers for all assets. Each project
    has its own namespace for groups and products.

    Args:
        name: The unique name for the project. Must be URL-safe
            (lowercase letters, numbers, hyphens).
        description: Optional human-readable description.

    Returns:
        Project: The newly created Project object.

    Raises:
        ProjectLimitError: If the tenant has reached their project limit.
        KumihoError: If the project name is invalid or already exists.

    Example:
        >>> project = kumiho.create_project(
        ...     "commercial-2024",
        ...     "Assets for 2024 commercial campaign"
        ... )
        >>> print(project.name)
        commercial-2024
    """
    return get_client().create_project(name=name, description=description)


def get_projects() -> List[Project]:
    """List all projects accessible to the current user.

    Returns:
        List[Project]: A list of Project objects.

    Example:
        >>> projects = kumiho.get_projects()
        >>> for p in projects:
        ...     print(f"{p.name}: {p.description}")
        commercial-2024: Assets for 2024 commercial campaign
        film-project: Feature film VFX assets
    """
    return get_client().get_projects()


def get_project(name: str) -> Optional[Project]:
    """Get a project by name.

    Args:
        name: The name of the project to retrieve.

    Returns:
        Optional[Project]: The Project object if found, None otherwise.

    Example:
        >>> project = kumiho.get_project("commercial-2024")
        >>> if project:
        ...     groups = project.get_groups()
    """
    return get_client().get_project(name)


def delete_project(project_id: str, force: bool = False) -> StatusResponse:
    """Delete a project.

    Args:
        project_id: The unique ID of the project to delete.
        force: If True, permanently delete the project and all its
            contents. If False (default), mark as deprecated.

    Returns:
        StatusResponse: A StatusResponse indicating success or failure.

    Warning:
        Force deletion is irreversible and removes all groups, products,
        versions, resources, and links within the project.

    Example:
        >>> # Soft delete (deprecate)
        >>> kumiho.delete_project("proj-uuid-here")

        >>> # Hard delete (permanent)
        >>> kumiho.delete_project("proj-uuid-here", force=True)
    """
    return get_client().delete_project(project_id=project_id, force=force)


def product_search(
    context_filter: str = "",
    name_filter: str = "",
    ptype_filter: str = ""
) -> List[Product]:
    """Search for products across projects and groups.

    Args:
        context_filter: Filter by project or group path. Supports glob
            patterns like ``project-*`` or ``*/characters/*``.
        name_filter: Filter by product name. Supports wildcards.
        ptype_filter: Filter by product type (e.g., "model", "texture").

    Returns:
        List[Product]: A list of Product objects matching the filters.

    Example:
        >>> # Find all models in any project
        >>> models = kumiho.product_search(ptype_filter="model")

        >>> # Find character assets in a specific project
        >>> chars = kumiho.product_search(
        ...     context_filter="film-project/characters",
        ...     ptype_filter="model"
        ... )

        >>> # Wildcard search
        >>> heroes = kumiho.product_search(name_filter="hero*")
    """
    return get_client().product_search(context_filter, name_filter, ptype_filter)


def get_product(kref: str) -> Product:
    """Get a product by its kref URI.

    Args:
        kref: The kref URI of the product
            (e.g., "kref://project/group/product.type").

    Returns:
        Product: The Product object.

    Raises:
        grpc.RpcError: If the product is not found.

    Example:
        >>> product = kumiho.get_product(
        ...     "kref://film-project/characters/hero.model"
        ... )
        >>> versions = product.get_versions()
    """
    return get_client().get_product_by_kref(kref)


def get_version(kref: str) -> Version:
    """Get a version by its kref URI.

    Args:
        kref: The kref URI of the version
            (e.g., "kref://project/group/product.type?v=1").

    Returns:
        Version: The Version object.

    Raises:
        grpc.RpcError: If the version is not found.

    Example:
        >>> version = kumiho.get_version(
        ...     "kref://film-project/characters/hero.model?v=3"
        ... )
        >>> resources = version.get_resources()
        >>> for r in resources:
        ...     print(r.location)
    """
    return get_client().get_version(kref)


def get_resource(kref: str) -> Resource:
    """Get a resource by its kref URI.

    Args:
        kref: The kref URI of the resource
            (e.g., "kref://project/group/product.type?v=1&r=main").

    Returns:
        Resource: The Resource object.

    Raises:
        grpc.RpcError: If the resource is not found.
        ValueError: If the kref is missing the resource name (&r=).

    Example:
        >>> resource = kumiho.get_resource(
        ...     "kref://film-project/characters/hero.model?v=3&r=mesh"
        ... )
        >>> print(resource.location)
        /projects/film/char/hero_v3.fbx
    """
    return get_client().get_resource_by_kref(kref)


def get_resources_by_location(location: str) -> List[Resource]:
    """Find all resources at a specific file location.

    This is useful for reverse lookups—finding which Kumiho resources
    reference a particular file path.

    Args:
        location: The file path or URI to search for.

    Returns:
        List[Resource]: A list of Resource objects at that location.

    Example:
        >>> resources = kumiho.get_resources_by_location(
        ...     "/shared/assets/hero_v3.fbx"
        ... )
        >>> for r in resources:
        ...     print(f"{r.kref} -> {r.location}")
    """
    return get_client().get_resources_by_location(location)


def event_stream(
    routing_key_filter: str = "",
    kref_filter: str = ""
) -> Iterator[Event]:
    """Subscribe to real-time events from the Kumiho server.

    Events are streamed as they occur, allowing you to react to changes
    in the database such as new versions, tag changes, or deletions.

    Args:
        routing_key_filter: Filter events by routing key pattern.
            Supports wildcards (e.g., ``product.model.*``, ``version.#``).
        kref_filter: Filter events by kref pattern.
            Supports glob patterns (e.g., ``kref://projectA/**/*.model``).

    Yields:
        Event: Event objects as they occur.

    Example:
        >>> # Watch for all version events in a project
        >>> for event in kumiho.event_stream(
        ...     routing_key_filter="version.*",
        ...     kref_filter="kref://film-project/**"
        ... ):
        ...     print(f"{event.routing_key}: {event.kref}")
        ...     if event.routing_key == "version.tagged":
        ...         print(f"  Tag: {event.details.get('tag')}")

    Note:
        This is a blocking iterator. Use in a separate thread or
        async context for production applications.
    """
    return get_client().event_stream(routing_key_filter, kref_filter)


def resolve(kref: str) -> Optional[str]:
    """Resolve a kref URI to a file location.

    This is a convenience function to get the file path for a resource
    or the default resource of a version.

    Args:
        kref: The kref URI to resolve.

    Returns:
        Optional[str]: The file location string, or None if not resolvable.

    Example:
        >>> # Resolve a specific resource
        >>> path = kumiho.resolve(
        ...     "kref://film-project/chars/hero.model?v=3&r=mesh"
        ... )
        >>> print(path)
        /projects/film/char/hero_v3.fbx

        >>> # Resolve version's default resource
        >>> path = kumiho.resolve(
        ...     "kref://film-project/chars/hero.model?v=3"
        ... )
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
    """Create a new Kumiho client with explicit configuration.

    Use this when you need more control over the client configuration,
    such as connecting to a specific server or using a custom token.

    Args:
        endpoint: The gRPC server endpoint (e.g., "localhost:50051"
            or "https://us-central.kumiho.cloud").
        token: The authentication token. If not provided and
            enable_auto_login is True, attempts to load from cache.
        enable_auto_login: If True, automatically use cached credentials
            when no token is provided.
        use_discovery: If True, use the discovery service to find the
            regional server. If None, auto-detect.
        default_metadata: Additional gRPC metadata to include with all
            requests (e.g., custom headers).
        tenant_hint: Tenant slug or ID for multi-tenant routing.

    Returns:
        _Client: A configured client instance.

    Example:
        Connect to a local development server::

            client = kumiho.connect(
                endpoint="localhost:50051",
                token=None  # No auth for local dev
            )

        Connect to production with explicit token::

            client = kumiho.connect(
                endpoint="https://us-central.kumiho.cloud",
                token=os.environ["KUMIHO_TOKEN"]
            )

        Use with context manager for temporary switching::

            client = kumiho.connect(endpoint="localhost:50051")
            with kumiho.use_client(client):
                local_projects = kumiho.get_projects()

    See Also:
        :func:`auto_configure_from_discovery`: Recommended for production.
        :func:`configure_default_client`: Set as global default.
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
    # Core classes
    "KumihoObject",
    "KumihoError",
    "Project",
    "Group",
    "Product",
    "Version",
    "Resource",
    "Link",
    "Kref",
    "Event",
    "ProjectLimitError",
    # Connection
    "connect",
    "use_client",
    "get_client",
    "configure_default_client",
    "auto_configure_from_discovery",
    # Constants
    "LATEST_TAG",
    "PUBLISHED_TAG",
    # Link types
    "LinkType",
    "BELONGS_TO",
    "CREATED_FROM",
    "REFERENCED",
    "DEPENDS_ON",
    "DERIVED_FROM",
    "CONTAINS",
    # Link directions
    "LinkDirection",
    "OUTGOING",
    "INCOMING",
    "BOTH",
    # Top-level functions
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
]

# Remove typing imports from public namespace
del Dict, List, Optional, Iterator, Tuple


_auto_configure_from_env_if_requested()
