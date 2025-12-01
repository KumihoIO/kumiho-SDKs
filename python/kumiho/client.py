"""Low-level gRPC client for the Kumiho Cloud service.

This module provides the internal ``_Client`` class that handles all gRPC
communication with Kumiho Cloud servers. It manages:

- Connection establishment (TLS/insecure, target resolution)
- Authentication (Bearer token injection)
- Discovery-based tenant routing
- All gRPC method calls

The ``_Client`` class is not intended to be used directly by end users.
Instead, use the high-level functions and classes exposed by the ``kumiho``
package, such as :func:`kumiho.connect`, :class:`kumiho.Project`, etc.

Example:
    Internal usage (not recommended for end users)::

        from kumiho.client import _Client

        client = _Client(target="us-central.kumiho.cloud:443")
        group = client.create_group(project_kref, "my-group")

    Preferred high-level usage::

        import kumiho

        kumiho.connect()
        project = kumiho.create_project(name="my-project")

Attributes:
    _LOGGER: Module-level logger for client operations.
    _DISCOVERY_DISABLE_ENV: Environment variable to disable auto-discovery.
    _FORCE_REFRESH_ENV: Environment variable to force discovery cache refresh.

Note:
    This module is considered internal API. The public interface may change
    between minor versions. Use the ``kumiho`` package-level API instead.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlparse

import grpc

from google.protobuf.json_format import MessageToDict

from ._token_loader import load_bearer_token
from .discovery import DiscoveryError, DiscoveryManager
from .proto import kumiho_pb2
from .proto import kumiho_pb2_grpc
from .event import Event
from .group import Group
from .kref import Kref
from .proto.kumiho_pb2 import (
    CreateGroupRequest,
    CreateLinkRequest,
    CreateProductRequest,
    CreateResourceRequest,
    CreateVersionRequest,
    CreateProjectRequest,
    DeleteGroupRequest,
    DeleteLinkRequest,
    DeleteProductRequest,
    DeleteResourceRequest,
    DeleteVersionRequest,
    DeleteProjectRequest,
    EventStreamRequest,
    GetChildGroupsRequest,
    GetGroupRequest,
    GetLinksRequest,
    GetProductRequest,
    GetProductsRequest,
    GetProjectsRequest,
    GetResourceRequest,
    GetResourcesRequest,
    GetResourcesByLocationRequest,
    GetTenantUsageRequest,
    GetVersionsRequest,
    HasTagRequest,
    KrefRequest,
    Link as PbLink,
    PeekNextVersionRequest,
    ProductSearchRequest,
    ResolveKrefRequest,
    ResolveLocationRequest,
    SetDefaultResourceRequest,
    TagVersionRequest,
    UnTagVersionRequest,
    UpdateMetadataRequest,
    WasTaggedRequest,
    SetDeprecatedRequest,
)
from .link import Link
from .proto.kumiho_pb2 import ProjectResponse, StatusResponse
from .project import Project

class ProjectLimitError(Exception):
    """Raised when guardrails block project creation (e.g., max projects reached)."""
from .product import Product
from .resource import Resource
from .version import Version


_LOGGER = logging.getLogger("kumiho.client")
_DISCOVERY_DISABLE_ENV = "KUMIHO_DISABLE_AUTO_DISCOVERY"
_FORCE_REFRESH_ENV = "KUMIHO_FORCE_DISCOVERY_REFRESH"


class _Client:
    """Low-level gRPC client for interacting with the Kumiho Cloud service.

    This client provides direct access to all Kumiho gRPC endpoints for
    managing projects, groups, products, versions, resources, and links.
    It handles connection management, authentication, and discovery-based
    tenant routing automatically.

    The client is typically not instantiated directly. Instead, use
    :func:`kumiho.connect` which manages a context-variable-scoped client
    instance.

    Attributes:
        channel (grpc.Channel): The gRPC channel to the Kumiho server.
        stub (KumihoGraphStub): The gRPC stub for making service calls.

    Example:
        Using the client directly (not recommended)::

            from kumiho.client import _Client

            client = _Client(
                target="us-central.kumiho.cloud:443",
                auth_token="eyJhbG..."
            )
            projects = client.get_projects()

        Using via kumiho.connect (recommended)::

            import kumiho

            kumiho.connect()
            projects = kumiho.list_projects()

    Note:
        This class is considered internal API. Use the public ``kumiho``
        module functions instead for stable interfaces.
    """

    def __init__(
        self,
        target: Optional[str] = None,
        *,
        auth_token: Optional[str] = None,
        default_metadata: Optional[Sequence[Tuple[str, str]]] = None,
        use_discovery: Optional[bool] = None,
        tenant_hint: Optional[str] = None,
        force_discovery_refresh: Optional[bool] = None,
        enable_auto_login: bool = True,
    ) -> None:
        """Initialize the gRPC client with connection and authentication settings.

        The client resolves the target server using the following priority:

        1. Explicit ``target`` parameter
        2. Discovery endpoint (if enabled and token available)
        3. ``KUMIHO_SERVER_ENDPOINT`` environment variable
        4. ``KUMIHO_SERVER_ADDRESS`` environment variable (legacy)
        5. ``localhost:8080`` (default for local development)

        Args:
            target: Server endpoint. Accepts formats:

                - ``host:port`` — plain gRPC
                - ``https://host`` — secure gRPC on port 443
                - ``grpcs://host:port`` — secure gRPC on custom port

                If None, the client attempts discovery or falls back to
                environment variables.
            auth_token: Bearer token for authentication. Sent as
                ``Authorization: Bearer <token>`` on every RPC. If not
                provided, falls back to:

                - ``KUMIHO_AUTH_TOKEN`` environment variable
                - Token file from ``kumiho-auth`` CLI cache
            default_metadata: Additional gRPC metadata to attach to all
                outbound RPCs. Each entry is a ``(key, value)`` tuple.
            use_discovery: Whether to use the discovery endpoint for
                tenant routing. Defaults to True unless disabled via
                ``KUMIHO_DISABLE_AUTO_DISCOVERY=true``.
            tenant_hint: Optional tenant ID hint for discovery or direct
                tenant header injection when discovery is disabled.
            force_discovery_refresh: Force refresh of discovery cache.
                Overrides ``KUMIHO_FORCE_DISCOVERY_REFRESH`` env var.
            enable_auto_login: Whether to enable auto-login when no
                credentials are available. Defaults to True.

        Raises:
            grpc.RpcError: If the connection cannot be established.
            DiscoveryError: If discovery fails and no fallback is available.

        Example:
            Basic initialization::

                client = _Client()  # Uses defaults

            With explicit settings::

                client = _Client(
                    target="us-central.kumiho.cloud:443",
                    auth_token="eyJhbG...",
                    default_metadata=[("x-custom-header", "value")]
                )
        """
        metadata: List[Tuple[str, str]] = list(default_metadata or [])
        resolved_token = auth_token or load_bearer_token()

        discovery = self._maybe_resolve_via_discovery(
            explicit_target=target,
            use_discovery=use_discovery,
            id_token=resolved_token,
            tenant_hint=tenant_hint,
            force_discovery_refresh=force_discovery_refresh,
        )
        tenant_header_set = False

        if discovery:
            target = discovery[0]
            if len(discovery) > 1 and discovery[1]:
                metadata.append(("x-tenant-id", discovery[1]))
                tenant_header_set = True
        elif tenant_hint:
            # Fallback: if discovery didn't run (e.g. no token), use the hint directly
            metadata.append(("x-tenant-id", tenant_hint))
            tenant_header_set = True

        if target is None:
            target = (
                os.getenv("KUMIHO_SERVER_ENDPOINT")
                or os.getenv("KUMIHO_SERVER_ADDRESS")
                or "localhost:8080"
            )

        authority_override = os.getenv("KUMIHO_SERVER_AUTHORITY")
        ssl_override = os.getenv("KUMIHO_SSL_TARGET_OVERRIDE")
        ca_bundle = os.getenv("KUMIHO_SERVER_CA_FILE")
        use_tls_env = os.getenv("KUMIHO_SERVER_USE_TLS")

        address, authority, use_tls = self._normalise_target(target)
        if use_tls_env:
            use_tls = use_tls_env.lower() in {"1", "true", "yes"}

        if authority_override:
            authority = authority_override

        if use_tls:
            credentials = self._build_ssl_credentials(ca_bundle)
            options = [("grpc.default_authority", authority)]
            if ssl_override:
                options.append(("grpc.ssl_target_name_override", ssl_override))
            channel = grpc.secure_channel(address, credentials, options=options)
        else:
            channel = grpc.insecure_channel(address)

        if resolved_token:
            metadata.append(("authorization", f"Bearer {resolved_token}"))

        # Apply interceptors in order: auto-login first, then metadata injection
        if enable_auto_login:
            channel = grpc.intercept_channel(channel, _AutoLoginInterceptor())
        if metadata:
            channel = grpc.intercept_channel(channel, _MetadataInjector(metadata))

        self.channel = channel
        self.stub = kumiho_pb2_grpc.KumihoServiceStub(self.channel)


    @staticmethod
    def _env_flag(name: str, *, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() not in {"0", "false", "no"}

    def _maybe_resolve_via_discovery(
        self,
        *,
        explicit_target: Optional[str],
        use_discovery: Optional[bool],
        id_token: Optional[str],
        tenant_hint: Optional[str],
        force_discovery_refresh: Optional[bool],
    ) -> Optional[Tuple[str, Optional[str]]]:
        if explicit_target:
            return None

        should_use = use_discovery
        if should_use is None:
            should_use = not self._env_flag(_DISCOVERY_DISABLE_ENV)

        if not should_use:
            return None

        if not id_token:
            _LOGGER.debug("Discovery skipped: no Firebase token available")
            return None

        hint = tenant_hint or None
        force_refresh = (
            force_discovery_refresh
            if force_discovery_refresh is not None
            else self._env_flag(_FORCE_REFRESH_ENV, default=False)
        )

        manager = DiscoveryManager()
        try:
            record = manager.resolve(
                id_token=id_token,
                tenant_hint=hint,
                force_refresh=force_refresh,
            )
        except DiscoveryError as exc:
            _LOGGER.info("Discovery failed (%s); falling back to legacy target", exc)
            return None
        except Exception:  # pragma: no cover - defensive logging
            _LOGGER.exception("Unexpected discovery failure; falling back to legacy target")
            return None

        target = record.region.grpc_authority or record.region.server_url
        tenant_id = record.tenant_id
        _LOGGER.debug(
            "Resolved Kumiho endpoint via discovery: target=%s tenant=%s", target, tenant_id
        )
        return target, tenant_id

    @staticmethod
    def _normalise_target(raw_target: str) -> Tuple[str, str, bool]:
        """Convert the provided target into an address, authority, and TLS flag."""

        target = raw_target.strip()
        if not target:
            raise ValueError("Kumiho client target cannot be empty")

        scheme = ""
        host = ""
        port: Optional[int] = None

        if "://" in target:
            parsed = urlparse(target)
            scheme = parsed.scheme.lower()
            host = parsed.hostname or ""
            port = parsed.port
            if not host:
                raise ValueError(f"Invalid Kumiho endpoint: {target}")
            if port is None:
                if scheme in {"https", "grpcs"}:
                    port = 443
                elif scheme in {"http", "grpc"}:
                    port = 80
        else:
            scheme = ""
            # Strip any trailing path components
            if "/" in target:
                target = target.split("/", 1)[0]
            if ":" in target:
                host, port_str = target.split(":", 1)
                port = int(port_str) if port_str else None
            else:
                host = target
            if not host:
                raise ValueError(f"Invalid Kumiho endpoint: {raw_target}")

        if port is None:
            port = 443 if scheme in {"https", "grpcs"} else 8080

        authority = host
        address = f"{host}:{port}"
        use_tls = scheme in {"https", "grpcs"} or port == 443
        return address, authority, use_tls

    @staticmethod
    def _build_ssl_credentials(ca_file: Optional[str]) -> grpc.ChannelCredentials:
        """Create SSL credentials, optionally using a custom CA bundle."""

        if ca_file:
            with open(ca_file, "rb") as handle:
                root_certs = handle.read()
            return grpc.ssl_channel_credentials(root_certificates=root_certs)
        return grpc.ssl_channel_credentials()

    # Project methods
    def create_project(self, name: str, description: str = "") -> Project:
        req = CreateProjectRequest(name=name, description=description)
        try:
            resp = self.stub.CreateProject(req)
        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                raise ProjectLimitError(exc.details()) from None
            raise
        return Project(resp, self)

    def get_projects(self) -> List[Project]:
        req = GetProjectsRequest()
        resp = self.stub.GetProjects(req)
        return [Project(pb, self) for pb in resp.projects]

    def get_project(self, name: str) -> Optional[Project]:
        """Return the first project matching the given name, or None if not found."""
        for project in self.get_projects():
            if project.name == name:
                return project
        return None

    def delete_project(self, project_id: str, force: bool = False) -> StatusResponse:
        req = DeleteProjectRequest(project_id=project_id, force=force)
        resp = self.stub.DeleteProject(req)
        return resp

    def update_project(
        self,
        project_id: str,
        allow_public: Optional[bool] = None,
        description: Optional[str] = None
    ) -> Project:
        req = kumiho_pb2.UpdateProjectRequest(
            project_id=project_id,
            allow_public=allow_public,
            description=description
        )
        resp = self.stub.UpdateProject(req)
        return Project(resp, self)

    # Group methods
    def create_group(self, parent_path: str, group_name: str) -> Group:
        """Create a new group.

        Args:
            parent_path: The path of the parent group.
            group_name: The name of the new group.

        Returns:
            The created Group object.
        """
        req = CreateGroupRequest(parent_path=parent_path, group_name=group_name)
        resp = self.stub.CreateGroup(req)
        return Group(resp, self)

    def get_group(self, path: str) -> Group:
        """Get a group by its path.

        Args:
            path: The path of the group to retrieve.

        Returns:
            The Group object.
        """
        req = GetGroupRequest(path_or_kref=path)
        resp = self.stub.GetGroup(req)
        return Group(resp, self)

    def get_child_groups(self, parent_path: str = "", recursive: bool = False) -> List[Group]:
        """Get child groups of a parent group.

        Args:
            parent_path: The path of the parent group. If empty or "/",
                         returns root-level groups.
            recursive: Whether to fetch all descendant groups recursively.

        Returns:
            A list of Group objects that are direct children of the parent.
        """
        req = GetChildGroupsRequest(parent_path=parent_path, recursive=recursive)
        resp = self.stub.GetChildGroups(req)
        return [Group(group_resp, self) for group_resp in resp.groups]

    def update_group_metadata(self, kref: Kref, metadata: Dict[str, str]) -> Group:
        """Update metadata for a group.

        Args:
            kref: The kref of the group.
            metadata: The metadata to update.

        Returns:
            The updated Group object.
        """
        req = UpdateMetadataRequest(kref=kref.to_pb(), metadata=metadata)
        resp = self.stub.UpdateGroupMetadata(req)
        return Group(resp, self)

    # Product methods
    def create_product(self, parent_path: str, product_name: str, product_type: str) -> Product:
        """Create a new product.

        Args:
            parent_path: The path of the parent group.
            product_name: The name of the product.
            product_type: The type of the product (e.g., "model", "texture").

        Returns:
            The created Product object.
        """
        req = CreateProductRequest(parent_path=parent_path, product_name=product_name, product_type=product_type)
        resp = self.stub.CreateProduct(req)
        return Product(resp, self)

    def get_product(self, parent_path: str, product_name: str, product_type: str) -> Product:
        """Get a product by its parent path, name, and type.

        Args:
            parent_path: The path of the parent group.
            product_name: The name of the product.
            product_type: The type of the product.

        Returns:
            The Product object.
        """
        req = GetProductRequest(parent_path=parent_path, product_name=product_name, product_type=product_type)
        resp = self.stub.GetProduct(req)
        return Product(resp, self)

    def get_product_by_kref(self, kref_uri: str) -> Product:
        """Get a product by its kref URI.

        Args:
            kref_uri: The kref URI of the product.

        Returns:
            The Product object.
        """
        kref = Kref(kref_uri)
        product_path = kref.get_path()  # e.g., "projectA/modelA.asset"
        if "/" not in product_path:
            raise ValueError(f"Invalid product kref format: {kref}")
        
        group_path, product_name_type = product_path.split("/", 1)
        parent_path = f"/{group_path}"  # Add leading slash
        if "." not in product_name_type:
            raise ValueError(f"Invalid product name.type format: {product_name_type}")
        
        product_name, product_type = product_name_type.split(".", 1)
        
        return self.get_product(parent_path, product_name, product_type)

    def get_products(self, parent_path: str, product_name_filter: str = "", product_type_filter: str = "") -> List[Product]:
        """Get products within a group with optional filtering.

        Args:
            parent_path: The path of the parent group.
            product_name_filter: Optional filter for product names.
            product_type_filter: Optional filter for product types.

        Returns:
            A list of Product objects matching the filters.
        """
        req = GetProductsRequest(parent_path=parent_path, product_name_filter=product_name_filter, product_type_filter=product_type_filter)
        resp = self.stub.GetProducts(req)
        return [Product(p, self) for p in resp.products]

    def product_search(self, context_filter: str = "", product_name_filter: str = "", product_type_filter: str = "") -> List[Product]:
        """Search for products across the system.

        Args:
            context_filter: Filter by context/path.
            product_name_filter: Filter by product name.
            product_type_filter: Filter by product type.

        Returns:
            A list of Product objects matching the search criteria.
        """
        req = ProductSearchRequest(context_filter=context_filter, product_name_filter=product_name_filter, product_type_filter=product_type_filter)
        resp = self.stub.ProductSearch(req)
        return [Product(p, self) for p in resp.products]

    def update_product_metadata(self, kref: Kref, metadata: Dict[str, str]) -> Product:
        """Update metadata for a product.

        Args:
            kref: The kref of the product.
            metadata: The metadata to update.

        Returns:
            The updated Product object.
        """
        req = UpdateMetadataRequest(kref=kref.to_pb(), metadata=metadata)
        resp = self.stub.UpdateProductMetadata(req)
        return Product(resp, self)

    def create_version(self, product_kref: Kref, metadata: Optional[Dict[str, str]] = None, number: int = 0) -> Version:
        """Create a new version for a product.

        Args:
            product_kref: The kref of the product.
            metadata: Optional metadata for the version.
            number: Specific version number to use (0 for auto-increment).

        Returns:
            The created Version object.
        """
        req = CreateVersionRequest(product_kref=product_kref.to_pb(), metadata=metadata or {}, number=number)
        resp = self.stub.CreateVersion(req)
        return Version(resp, self)
    def get_version(self, kref_uri: str) -> Version:
        """Get a version by its kref URI, with optional tag/time resolution.

        Args:
            kref_uri: The kref URI of the version. Can include ?t=tag or ?time=timestamp
                     for tag/time resolution.

        Returns:
            The Version object.
        """
        # Parse kref_uri for tag/time parameters
        base_kref = kref_uri
        tag = None
        time = None
        
        if '?' in kref_uri:
            base_kref, params = kref_uri.split('?', 1)
            for param in params.split('&'):
                if param.startswith('t=') or param.startswith('tag='):
                    tag = param.split('=')[1]
                elif param.startswith('time='):
                    time = param.split('=')[1]
                    # Validate time format (YYYYMMDDHHMM)
                    import re
                    if not re.match(r"^\d{12}$", time):
                        raise ValueError("time must be in YYYYMMDDHHMM format")
        
        if tag is not None or time is not None:
            # Use ResolveKref to find the specific version
            # We pass the base_kref (Product Kref) and the constraints
            req = ResolveKrefRequest(kref=base_kref, tag=tag, time=time)
            try:
                resp = self.stub.ResolveKref(req)
                return Version(resp, self)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    # Re-raise as NOT_FOUND
                    context = grpc.RpcError()
                    context.code = lambda: grpc.StatusCode.NOT_FOUND
                    context.details = lambda: "Version not found"
                    raise context
                raise
        else:
            req = KrefRequest(kref=kumiho_pb2.Kref(uri=kref_uri))
        
        resp = self.stub.GetVersion(req)
        return Version(resp, self)

    def get_product_from_version(self, version_kref: str) -> Product:
        """Get the product that contains a specific version.

        Args:
            version_kref: The kref URI of the version.

        Returns:
            The Product object that contains the version.
        """
        # First get the version to find its product relationship
        version = self.get_version(version_kref)
        # Parse the product_kref to extract parent_path, product_name, and product_type
        product_path = version.product_kref.get_path()  # e.g., "group/product.type"
        if "/" not in product_path:
            raise ValueError(f"Invalid product kref format: {version.product_kref}")
        
        parent_path, product_name_type = product_path.split("/", 1)
        parent_path = f"/{parent_path}"  # Add leading slash
        if "." not in product_name_type:
            raise ValueError(f"Invalid product name.type format: {product_name_type}")
        
        product_name, product_type = product_name_type.split(".", 1)
        
        return self.get_product(parent_path, product_name, product_type)

    def get_versions(self, product_kref: Kref) -> List[Version]:
        """Get all versions of a product.

        Args:
            product_kref: The kref of the product.

        Returns:
            A list of Version objects for the product.
        """
        req = GetVersionsRequest(product_kref=product_kref.to_pb())
        resp = self.stub.GetVersions(req)
        return [Version(v, self) for v in resp.versions]

    def get_latest_version(self, product_kref: Kref) -> Optional[Version]:
        """Get the latest version of a product.

        Args:
            product_kref: The kref of the product.

        Returns:
            The latest Version object, or None if no versions exist.
        """
        req = ResolveKrefRequest(kref=product_kref.uri)
        try:
            resp = self.stub.ResolveKref(req)
            return Version(resp, self)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def delete_version(self, kref: Kref, force: bool) -> None:
        """Delete a version.

        Args:
            kref: The kref of the version to delete.
            force: Whether to force deletion.
        """
        req = DeleteVersionRequest(kref=kref.to_pb(), force=force)
        self.stub.DeleteVersion(req)

    def delete_group(self, path: str, force: bool) -> None:
        """Delete a group.

        Args:
            path: The path of the group to delete.
            force: Whether to force deletion.
        """
        req = DeleteGroupRequest(path=path, force=force)
        self.stub.DeleteGroup(req)

    def delete_product(self, kref: Kref, force: bool) -> None:
        """Delete a product.

        Args:
            kref: The kref of the product to delete.
            force: Whether to force deletion.
        """
        req = DeleteProductRequest(kref=kref.to_pb(), force=force)
        self.stub.DeleteProduct(req)

    def update_version_metadata(self, kref: Kref, metadata: Dict[str, str]) -> Version:
        """Update metadata for a version.

        Args:
            kref: The kref of the version.
            metadata: The metadata to update.

        Returns:
            The updated Version object.
        """
        req = UpdateMetadataRequest(kref=kref.to_pb(), metadata=metadata)
        resp = self.stub.UpdateVersionMetadata(req)
        return Version(resp, self)

    def peek_next_version(self, product_kref: Kref) -> int:
        """Get the next version number that would be assigned to a product.

        Args:
            product_kref: The kref of the product.

        Returns:
            The next version number.
        """
        req = PeekNextVersionRequest(product_kref=product_kref.to_pb())
        resp = self.stub.PeekNextVersion(req)
        return resp.number

    # Tagging methods
    def tag_version(self, kref: Kref, tag: str) -> None:
        """Apply a tag to a version.

        Args:
            kref: The kref of the version.
            tag: The tag to apply.
        """
        req = TagVersionRequest(kref=kref.to_pb(), tag=tag)
        self.stub.TagVersion(req)

    def untag_version(self, kref: Kref, tag: str) -> None:
        """Remove a tag from a version.

        Args:
            kref: The kref of the version.
            tag: The tag to remove.
        """
        req = UnTagVersionRequest(kref=kref.to_pb(), tag=tag)
        self.stub.UnTagVersion(req)

    def has_tag(self, kref: Kref, tag: str) -> bool:
        """Check if a version has a specific tag.

        Args:
            kref: The kref of the version.
            tag: The tag to check for.

        Returns:
            True if the version has the tag, False otherwise.
        """
        req = HasTagRequest(kref=kref.to_pb(), tag=tag)
        resp = self.stub.HasTag(req)
        return resp.has_tag

    def was_tagged(self, kref: Kref, tag: str) -> bool:
        """Check if a version was ever tagged with a specific tag.

        Args:
            kref: The kref of the version.
            tag: The tag to check for.

        Returns:
            True if the version was ever tagged with the given tag.
        """
        req = WasTaggedRequest(kref=kref.to_pb(), tag=tag)
        resp = self.stub.WasTagged(req)
        return resp.was_tagged

    def set_default_resource(self, version_kref: Kref, resource_name: str) -> None:
        """Set the default resource for a version.

        Args:
            version_kref: The kref of the version.
            resource_name: The name of the resource to set as default.
        """
        req = SetDefaultResourceRequest(version_kref=version_kref.to_pb(), resource_name=resource_name)
        self.stub.SetDefaultResource(req)

    # Resource methods
    def create_resource(self, version_kref: Kref, name: str, location: str) -> Resource:
        """Create a new resource for a version.

        Args:
            version_kref: The kref of the parent version.
            name: The name of the resource.
            location: The storage location of the resource.

        Returns:
            The created Resource object.
        """
        req = CreateResourceRequest(version_kref=version_kref.to_pb(), name=name, location=location)
        resp = self.stub.CreateResource(req)
        return Resource(resp, self)

    def get_resource(self, version_kref: Kref, name: str) -> Resource:
        """Get a resource by version kref and name.

        Args:
            version_kref: The kref of the parent version.
            name: The name of the resource.

        Returns:
            The Resource object.
        """
        req = GetResourceRequest(version_kref=version_kref.to_pb(), name=name)
        resp = self.stub.GetResource(req)
        return Resource(resp, self)

    def get_resource_by_kref(self, kref_uri: str) -> Resource:
        """Get a resource by its kref URI.

        Args:
            kref_uri: The kref URI of the resource (e.g., "kref://group/product.type?v=1&r=resource_name").

        Returns:
            The Resource object.

        Raises:
            ValueError: If the kref URI does not contain a resource name.
        """
        kref = Kref(kref_uri)
        resource_name = kref.get_resource_name()
        if not resource_name:
            raise ValueError(f"Invalid resource kref format: {kref_uri} (missing &r=resource_name)")
        
        # Build the version kref by removing the resource part
        version_kref_uri = kref_uri.split("&r=")[0]
        version_kref = Kref(version_kref_uri)
        
        return self.get_resource(version_kref, resource_name)

    def get_resources(self, version_kref: Kref) -> List[Resource]:
        """Get all resources for a version.

        Args:
            version_kref: The kref of the version.

        Returns:
            A list of Resource objects.
        """
        req = GetResourcesRequest(version_kref=version_kref.to_pb())
        resp = self.stub.GetResources(req)
        return [Resource(r, self) for r in resp.resources]

    def get_resources_by_location(self, location: str) -> List[Resource]:
        """Get all resources at a specific location.

        Args:
            location: The location to search for resources.

        Returns:
            A list of Resource objects at the location.
        """
        req = GetResourcesByLocationRequest(location=location)
        resp = self.stub.GetResourcesByLocation(req)
        return [Resource(r, self) for r in resp.resources]

    def delete_resource(self, kref: Kref, force: bool) -> None:
        """Delete a resource.

        Args:
            kref: The kref of the resource to delete.
            force: Whether to force deletion.
        """
        req = DeleteResourceRequest(kref=kref.to_pb(), force=force)
        self.stub.DeleteResource(req)

    def set_deprecated(self, kref: Kref, deprecated: bool) -> None:
        """Set the deprecated status of a node (Product, Version, Resource).

        Args:
            kref: The kref of the node.
            deprecated: True to deprecate, False to un-deprecate.
        """
        req = SetDeprecatedRequest(kref=kref.to_pb(), deprecated=deprecated)
        self.stub.SetDeprecated(req)

    def update_resource_metadata(self, kref: Kref, metadata: Dict[str, str]) -> Resource:
        """Update metadata for a resource.

        Args:
            kref: The kref of the resource.
            metadata: The metadata to update.

        Returns:
            The updated Resource object.
        """
        req = UpdateMetadataRequest(kref=kref.to_pb(), metadata=metadata)
        resp = self.stub.UpdateResourceMetadata(req)
        return Resource(resp, self)

    def get_tenant_usage(self) -> Dict[str, Any]:
        """Get the current tenant's usage and limits.

        Returns:
            A dictionary containing node_count, node_limit, and tenant_id.
        """
        req = GetTenantUsageRequest()
        resp = self.stub.GetTenantUsage(req)
        return MessageToDict(resp, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)

    def resolve(self, kref: str) -> Optional[str]:
        """
        Resolves a Kref to a file location using the server-side ResolveLocation RPC.
        
        Args:
            kref: The Kref URI to resolve. Can include query parameters like ?v=, ?t=, ?time=.
            
        Returns:
            The resolved file location string, or None if resolution fails.
        """
        try:
            # Parse tag/time from kref if present to pass explicitly
            tag = None
            time = None
            
            if '?' in kref:
                _, params = kref.split('?', 1)
                for param in params.split('&'):
                    if param.startswith('t=') or param.startswith('tag='):
                        tag = param.split('=')[1]
                    elif param.startswith('time='):
                        time = param.split('=')[1]

            req = ResolveLocationRequest(kref=kref, tag=tag, time=time)
            resp = self.stub.ResolveLocation(req)
            return resp.location
        except grpc.RpcError:
            return None
        except Exception:
            return None

    # Link methods
    def create_link(
        self,
        source_version: Version,
        target_version: Version,
        link_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Link:
        """Create a link between two versions.

        Args:
            source_version: The source version of the link.
            target_version: The target version of the link.
            link_type: The type of relationship (e.g., kumiho.LinkType.DEPENDS_ON).
                       See kumiho.LinkType for standard types.
            metadata: Optional metadata for the link.

        Returns:
            The created Link object.
        """
        req = CreateLinkRequest(
            source_version_kref=source_version.kref.to_pb(),
            target_version_kref=target_version.kref.to_pb(),
            link_type=link_type,
            metadata=metadata or {}
        )
        self.stub.CreateLink(req)
        # Construct Link object client-side since RPC returns only status
        pb_link = PbLink(
            source_kref=source_version.kref.to_pb(),
            target_kref=target_version.kref.to_pb(),
            link_type=link_type,
            metadata=metadata or {},
        )
        return Link(pb_link, self)

    def get_links(self, kref: Kref, link_type_filter: str = "", direction: int = 0) -> List[Link]:
        """Get links associated with a kref.

        Args:
            kref: The kref to get links for.
            link_type_filter: Optional filter for link types.
            direction: The direction of links to retrieve (0=OUTGOING, 1=INCOMING, 2=BOTH).
                       See kumiho.LinkDirection.

        Returns:
            A list of Link objects.
        """
        req = GetLinksRequest(kref=kref.to_pb(), link_type_filter=link_type_filter, direction=direction)
        resp = self.stub.GetLinks(req)
        return [Link(pb, self) for pb in resp.links]

    def delete_link(self, source_kref: Kref, target_kref: Kref, link_type: str) -> None:
        """Delete a link between versions.

        Args:
            source_kref: The source version kref.
            target_kref: The target version kref.
            link_type: The type of link to delete.
        """
        req = DeleteLinkRequest(
            source_kref=source_kref.to_pb(),
            target_kref=target_kref.to_pb(),
            link_type=link_type
        )
        self.stub.DeleteLink(req)

    # Event Streaming
    def event_stream(self, routing_key_filter: str = "", kref_filter: str = "") -> Iterator[Event]:
        """Subscribe to the event stream from the Kumiho server.

        Args:
            routing_key_filter: A filter for the events to receive.
                                Supports wildcards, e.g., "product.model.*"
            kref_filter: A filter for the kref URIs to receive events for.
                        Supports wildcards, e.g., "kref://projectA/**/*.model"

        Yields:
            Event objects representing changes in the database.
        """
        req = EventStreamRequest(routing_key_filter=routing_key_filter, kref_filter=kref_filter)
        for pb_event in self.stub.EventStream(req):
            yield Event(pb_event)


class _ClientCallDetails(grpc.ClientCallDetails):
    """Mutable wrapper that lets us override metadata on outbound RPCs."""

    def __init__(
        self,
        method: str,
        timeout: Optional[float],
        metadata: Optional[Sequence[Tuple[str, str]]],
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        compression: Optional[grpc.Compression],
    ) -> None:
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


def _augment_call_details(
    client_call_details: grpc.ClientCallDetails,
    metadata: Sequence[Tuple[str, str]],
) -> _ClientCallDetails:
    existing = list(client_call_details.metadata or [])
    existing.extend(metadata)
    return _ClientCallDetails(
        method=client_call_details.method,
        timeout=client_call_details.timeout,
        metadata=existing,
        credentials=client_call_details.credentials,
        wait_for_ready=getattr(client_call_details, "wait_for_ready", None),
        compression=getattr(client_call_details, "compression", None),
    )


class _MetadataInjector(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Client interceptor that injects static metadata such as auth tokens."""

    def __init__(self, metadata: Sequence[Tuple[str, str]]) -> None:
        self._metadata = tuple(metadata)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        _LOGGER.info(f"Injecting metadata: {self._metadata}")
        updated = _augment_call_details(client_call_details, self._metadata)
        return continuation(updated, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        updated = _augment_call_details(client_call_details, self._metadata)
        return continuation(updated, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        updated = _augment_call_details(client_call_details, self._metadata)
        return continuation(updated, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        updated = _augment_call_details(client_call_details, self._metadata)
        return continuation(updated, request_iterator)


class _AutoLoginInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
):
    """Client interceptor that automatically prompts for login on auth failures."""

    def intercept_unary_unary(self, continuation, client_call_details, request):
        response = continuation(client_call_details, request)
        
        # Check if this is an auth error
        try:
            # Force the response to be evaluated
            if hasattr(response, 'code'):
                code = response.code()
                if code in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
                    _LOGGER.info("Authentication error detected, prompting for login...")
                    try:
                        from . import auth_cli
                        new_token, _ = auth_cli.ensure_token(interactive=True)
                        
                        # Update the authorization header with the new token
                        existing_metadata = list(client_call_details.metadata or [])
                        # Remove old authorization header
                        existing_metadata = [(k, v) for k, v in existing_metadata if k.lower() != "authorization"]
                        # Add new token
                        existing_metadata.append(("authorization", f"Bearer {new_token}"))
                        
                        updated_details = _ClientCallDetails(
                            method=client_call_details.method,
                            timeout=client_call_details.timeout,
                            metadata=existing_metadata,
                            credentials=client_call_details.credentials,
                            wait_for_ready=getattr(client_call_details, "wait_for_ready", None),
                            compression=getattr(client_call_details, "compression", None),
                        )
                        
                        # Retry the RPC with the new token
                        _LOGGER.info("Retrying RPC with new credentials...")
                        return continuation(updated_details, request)
                    except Exception as e:
                        _LOGGER.error(f"Auto-login failed: {e}")
                        return response
        except Exception:
            # If we can't check the error, just return the original response
            pass
        
        return response

    def intercept_unary_stream(self, continuation, client_call_details, request):
        # For streaming responses, we can't easily retry, so just pass through
        # The first error will be caught and user will be prompted to re-run
        return continuation(client_call_details, request)

