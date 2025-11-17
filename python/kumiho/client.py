"""Low-level client for interacting with the Kumiho gRPC service."""

import os
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
from urllib.parse import urlparse

import grpc

from google.protobuf.json_format import MessageToDict

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
    DeleteGroupRequest,
    DeleteLinkRequest,
    DeleteProductRequest,
    DeleteResourceRequest,
    DeleteVersionRequest,
    EventStreamRequest,
    GetChildGroupsRequest,
    GetChildGroupsResponse,
    GetGroupRequest,
    GetLinksRequest,
    GetProductRequest,
    GetProductsRequest,
    GetResourceRequest,
    GetResourcesByLocationRequest,
    GetResourcesRequest,
    GetVersionsRequest,
    HasTagRequest,
    KrefRequest,
    Link as PbLink,
    PeekNextVersionRequest,
    ProductSearchRequest,
    TagVersionRequest,
    UnTagVersionRequest,
    UpdateMetadataRequest,
    WasTaggedRequest,
)
from .link import Link
from .product import Product
from .resource import Resource
from .version import Version


class Client:
    """Low-level client for interacting with the Kumiho gRPC service.

    This client provides direct access to all Kumiho gRPC endpoints.
    For higher-level operations, use the classes in the kumiho module.

    Attributes:
        channel: The gRPC channel to the server.
        stub: The gRPC stub for making service calls.
    """

    def __init__(self, target: Optional[str] = None) -> None:
        """Initialize the client with a target server address.

        Args:
            target: Server endpoint. Accepts `host:port`, `https://host`, or
                `grpcs://host:port`. If None, consults the following in order:
                1. ``KUMIHO_SERVER_ENDPOINT``
                2. ``KUMIHO_SERVER_ADDRESS`` (legacy name)
                3. ``localhost:8080``
        """
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
            self.channel = grpc.secure_channel(address, credentials, options=options)
        else:
            self.channel = grpc.insecure_channel(address)
        self.stub = kumiho_pb2_grpc.KumihoServiceStub(self.channel)

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

    def get_child_groups(self, parent_path: str = "") -> List[Group]:
        """Get child groups of a parent group.

        Args:
            parent_path: The path of the parent group. If empty or "/",
                         returns root-level groups.

        Returns:
            A list of Group objects that are direct children of the parent.
        """
        req = GetChildGroupsRequest(parent_path=parent_path)
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

    # Version methods
    def create_version(
        self,
        product_kref: Kref,
        metadata: Optional[Dict[str, str]] = None,
        number: int = 0
    ) -> Version:
        """Create a new version for a product.

        Args:
            product_kref: The kref of the product.
            metadata: Optional metadata for the version.
            number: Specific version number (0 for auto-increment).

        Returns:
            The created Version object.
        """
        req = CreateVersionRequest(
            product_kref=product_kref.to_pb(),
            metadata=metadata or {},
            number=number
        )
        resp = self.stub.CreateVersion(req)
        return Version(resp, self)

    def resolve_kref(
        self,
        kref: str,
        tag: Optional[str] = None,
        time: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Resolve a kref to a specific version with optional tag/time constraints.

        Args:
            kref: The kref URI to resolve.
            tag: Optional tag to resolve to a specific tagged version.
            time: Optional time in 'YYYYMMDDHHMM' format to resolve at.

        Returns:
            A dictionary representation of the resolved version, or None if not found.

        Raises:
            ValueError: If the time format is invalid.
        """
        if time:
            try:
                datetime.strptime(time, "%Y%m%d%H%M")
            except ValueError as e:
                raise ValueError("time must be in YYYYMMDDHHMM format") from e

        request = kumiho_pb2.ResolveKrefRequest(kref=kref, tag=tag, time=time)
        try:
            response = self.stub.ResolveKref(request)
            return MessageToDict(response, preserving_proto_field_name=True)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            print(f"An RPC error occurred: {e.details()}")
            raise

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
                if param.startswith('t='):
                    tag = param[2:]
                elif param.startswith('time='):
                    time = param[5:]
        
        # If tag or time is specified, use resolve_kref
        if tag is not None or time is not None:
            resolved = self.resolve_kref(base_kref, tag=tag, time=time)
            if resolved is None:
                raise grpc.RpcError("Version not found")
            # Create a Version object from the resolved data
            # For now, construct a kref from the resolved data
            resolved_kref = resolved.get('kref', {}).get('uri', kref_uri)
            req = KrefRequest(kref=kumiho_pb2.Kref(uri=resolved_kref))
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
        versions = self.get_versions(product_kref)
        if not versions:
            return None
        # Find the version with latest=True, or fallback to highest number
        latest_versions = [v for v in versions if hasattr(v, 'latest') and v.latest]
        if latest_versions:
            return latest_versions[0]
        # Fallback: return the version with the highest number
        return max(versions, key=lambda v: v.number)

    def delete_version(self, kref: Kref, force: bool, user_permission: str) -> None:
        """Delete a version.

        Args:
            kref: The kref of the version to delete.
            force: Whether to force deletion.
            user_permission: The username for permission checking.
        """
        req = DeleteVersionRequest(kref=kref.to_pb(), force=force, user_permission=user_permission)
        self.stub.DeleteVersion(req)

    def delete_group(self, path: str, force: bool, user_permission: str) -> None:
        """Delete a group.

        Args:
            path: The path of the group to delete.
            force: Whether to force deletion.
            user_permission: The username for permission checking.
        """
        req = DeleteGroupRequest(path=path, force=force, user_permission=user_permission)
        self.stub.DeleteGroup(req)

    def delete_product(self, kref: Kref, force: bool, user_permission: str) -> None:
        """Delete a product.

        Args:
            kref: The kref of the product to delete.
            force: Whether to force deletion.
            user_permission: The username for permission checking.
        """
        req = DeleteProductRequest(kref=kref.to_pb(), force=force, user_permission=user_permission)
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

    def delete_resource(self, kref: Kref, force: bool, user_permission: str) -> None:
        """Delete a resource.

        Args:
            kref: The kref of the resource to delete.
            force: Whether to force deletion.
            user_permission: The username for permission checking.
        """
        req = DeleteResourceRequest(kref=kref.to_pb(), force=force, user_permission=user_permission)
        self.stub.DeleteResource(req)

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

    def resolve(self, kref: str) -> Optional[str]:
        """Resolve a KREF to a file location.

        This method implements the KREF resolution logic:
        - Product KREF: resolves to latest version → default resource → location
        - Version KREF: resolves to default resource → location
        - Resource KREF: returns the resource location directly

        Args:
            kref: The KREF URI to resolve.

        Returns:
            The file location string, or None if resolution fails.
        """
        kref_obj = Kref(kref)
        path = kref_obj.get_path()
        parts = path.split('/')

        # Check for resource parameter in query string
        resource_name = kref_obj.get_resource_name()

        if len(parts) == 2 and '.' in parts[1]:
            # Product KREF: group/product.type
            try:
                product = self.get_product_by_kref(kref)
                latest_version = self.get_latest_version(product.kref)
                if latest_version:
                    # Use specified resource or default
                    target_resource = resource_name or latest_version.default_resource
                    if target_resource:
                        resource = self.get_resource(latest_version.kref, target_resource)
                        return resource.location
                    else:
                        # Fallback: use first available resource
                        resources = self.get_resources(latest_version.kref)
                        if resources:
                            return resources[0].location
            except Exception:
                return None
        elif len(parts) == 2 and '?' in kref and 'v=' in kref:
            # Version KREF: group/product.type?v=123
            try:
                version = self.get_version(kref)
                # Use specified resource or default
                target_resource = resource_name or version.default_resource
                if target_resource:
                    resource = self.get_resource(version.kref, target_resource)
                    return resource.location
                else:
                    # Fallback: use first available resource
                    resources = self.get_resources(version.kref)
                    if resources:
                        return resources[0].location
            except Exception:
                return None
        elif len(parts) == 3:
            # Resource KREF: group/product.type/resource_name?v=123
            try:
                # Extract resource name from path, override with query param if present
                path_resource_name = parts[2].split('?')[0]  # Remove query params
                final_resource_name = resource_name or path_resource_name
                version_kref_str = f"kumiho://{parts[0]}/{parts[1]}"
                if '?' in kref:
                    version_kref_str += f"?{kref.split('?', 1)[1]}"
                version_kref = Kref(version_kref_str)
                resource = self.get_resource(version_kref, final_resource_name)
                return resource.location
            except Exception:
                return None

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
            link_type: The type of relationship (e.g., "depends_on").
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

    def get_links(self, kref: Kref, link_type_filter: str = "") -> List[Link]:
        """Get links associated with a kref.

        Args:
            kref: The kref to get links for.
            link_type_filter: Optional filter for link types.

        Returns:
            A list of Link objects.
        """
        req = GetLinksRequest(kref=kref.to_pb(), link_type_filter=link_type_filter)
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
