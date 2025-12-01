"""Product module for Kumiho asset management.

This module provides the :class:`Product` class, which represents a versioned
asset in the Kumiho system. Products are the core entities that get versioned,
and each version can have multiple resources (file references).

Example:
    Working with products and versions::

        import kumiho

        # Get a product
        product = kumiho.get_product("kref://my-project/models/hero.model")

        # Create a new version
        v1 = product.create_version(metadata={"artist": "john"})

        # Add resources to the version
        v1.create_resource("mesh", "/assets/hero_v1.fbx")
        v1.create_resource("rig", "/assets/hero_v1_rig.fbx")

        # Tag the version
        v1.tag("approved")

        # Get all versions
        for version in product.get_versions():
            print(f"v{version.number}: {version.tags}")
"""

import grpc
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import ProductResponse, ResolveKrefRequest
from .version import Version

if TYPE_CHECKING:
    from .client import _Client
    from .group import Group
    from .project import Project


class Product(KumihoObject):
    """A versioned asset in the Kumiho system.

    Products represent assets that can have multiple versions, such as 3D models,
    textures, workflows, or any other type of creative content. Each product
    belongs to a group and is identified by a combination of name and type.

    The product's kref (Kumiho Reference) is a URI that uniquely identifies it:
    ``kref://project/group/product.type``

    Attributes:
        kref (Kref): The unique reference URI for this product.
        name (str): The full name including type (e.g., "hero.model").
        product_name (str): The base name of the product (e.g., "hero").
        product_type (str): The type of product (e.g., "model", "texture").
        created_at (Optional[str]): ISO timestamp when the product was created.
        author (str): The user ID who created the product.
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        deprecated (bool): Whether the product is deprecated.
        username (str): Display name of the creator.

    Example:
        Basic product operations::

            import kumiho

            # Get product by kref
            product = kumiho.get_product("kref://film/chars/hero.model")

            # Create versions
            v1 = product.create_version()
            v2 = product.create_version(metadata={"notes": "Updated mesh"})

            # Get specific version
            v1 = product.get_version(1)
            latest = product.get_latest_version()

            # Get version by tag
            approved = product.get_version_by_tag("approved")

            # Get version at a specific time
            historical = product.get_version_by_time("202312011200")

            # Set metadata
            product.set_metadata({"status": "final", "priority": "high"})

            # Deprecate the product
            product.set_deprecated(True)
    """

    def __init__(self, pb_product: ProductResponse, client: '_Client') -> None:
        """Initialize a Product from a protobuf response.

        Args:
            pb_product: The protobuf ProductResponse message.
            client: The client instance for making API calls.
        """
        super().__init__(client)
        self.kref = Kref(pb_product.kref.uri)
        self.name = pb_product.name
        self.product_name = pb_product.product_name
        self.product_type = pb_product.product_type
        self.created_at = pb_product.created_at or None
        self.author = pb_product.author
        self.metadata = dict(pb_product.metadata)
        self.deprecated = pb_product.deprecated
        self.username = pb_product.username

    def __repr__(self) -> str:
        """Return a string representation of the Product."""
        return f"<Product kref='{self.kref.uri}'>"

    def create_version(
        self,
        metadata: Optional[Dict[str, str]] = None,
        number: int = 0
    ) -> Version:
        """Create a new version of this product.

        Versions are automatically numbered sequentially. Each version starts
        with the "latest" tag, which moves to the newest version.

        Args:
            metadata: Optional metadata for the version (e.g., artist notes,
                render settings, software versions).
            number: Specific version number to use. If 0 (default), auto-assigns
                the next available number.

        Returns:
            Version: The newly created Version object.

        Example:
            >>> # Auto-numbered version
            >>> v1 = product.create_version()
            >>> v2 = product.create_version(metadata={"artist": "jane"})

            >>> # Specific version number (use with caution)
            >>> v5 = product.create_version(number=5)
        """
        return self._client.create_version(self.kref, metadata, number)

    def get_versions(self) -> List[Version]:
        """Get all versions of this product.

        Returns:
            List[Version]: A list of Version objects, ordered by version number.

        Example:
            >>> versions = product.get_versions()
            >>> for v in versions:
            ...     print(f"v{v.number}: created {v.created_at}")
        """
        return self._client.get_versions(self.kref)

    def get_version(self, version_number: int) -> Optional[Version]:
        """Get a specific version by its number.

        Args:
            version_number: The version number to retrieve (1-based).

        Returns:
            Optional[Version]: The Version object if found, None otherwise.

        Example:
            >>> v3 = product.get_version(3)
            >>> if v3:
            ...     resources = v3.get_resources()
        """
        kref_uri = f"{self.kref.uri}?v={version_number}"
        return self._client.get_version(kref_uri)

    def get_latest_version(self) -> Optional[Version]:
        """Get the latest version of this product.

        The latest version is the one with the "latest" tag, or if none
        exists, the version with the highest number.

        Returns:
            Optional[Version]: The latest Version object, or None if no
                versions exist.

        Example:
            >>> latest = product.get_latest_version()
            >>> if latest:
            ...     print(f"Latest: v{latest.number}")
        """
        versions = self.get_versions()
        if not versions:
            return None
        # Find the version with latest=True, or fallback to highest number
        latest_versions = [v for v in versions if hasattr(v, 'latest') and v.latest]
        if latest_versions:
            return latest_versions[0]
        return max(versions, key=lambda v: v.number)

    def get_group(self) -> 'Group':
        """Get the group that contains this product.

        Returns:
            Group: The parent Group object.

        Example:
            >>> product = kumiho.get_product("kref://project/chars/hero.model")
            >>> group = product.get_group()
            >>> print(group.path)  # "/project/chars"
        """
        group_path = f"/{self.kref.get_group()}"
        return self._client.get_group(group_path)

    def get_project(self) -> 'Project':
        """Get the project that contains this product.

        Returns:
            Project: The parent Project object.

        Example:
            >>> project = product.get_project()
            >>> print(project.name)
        """
        return self.get_group().get_project()

    def get_version_by_tag(self, tag: str) -> Optional[Version]:
        """Get a version by its tag.

        Common tags include "latest", "published", "approved", etc.
        Custom tags can be applied to versions using :meth:`Version.tag`.

        Args:
            tag: The tag to search for.

        Returns:
            Optional[Version]: The Version object if found, None otherwise.

        Example:
            >>> approved = product.get_version_by_tag("approved")
            >>> published = product.get_version_by_tag("published")
        """
        request = ResolveKrefRequest(kref=self.kref.uri, tag=tag)
        try:
            response = self._client.stub.ResolveKref(request)
            return Version(response, self._client)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def get_version_by_time(self, time: Union[str, datetime]) -> Optional[Version]:
        """Get the version that was active at a specific time.

        This finds the version that was tagged as "latest" at the given
        time, useful for historical queries and reproducing past states.

        Args:
            time: The time as a datetime object, or a string in either
                YYYYMMDDHHMM format (e.g., "202312251430") or RFC3339
                format (e.g., "2023-12-25T14:30:00Z").

        Returns:
            Optional[Version]: The Version that was current at that time,
                or None if not found.

        Example:
            >>> from datetime import datetime

            >>> # Using datetime object
            >>> v = product.get_version_by_time(datetime(2023, 12, 25, 14, 30))

            >>> # Using string format
            >>> v = product.get_version_by_time("202312251430")

            >>> # Using RFC3339 format
            >>> v = product.get_version_by_time("2023-12-25T14:30:00Z")
        """
        if isinstance(time, datetime):
            time_str = time.strftime("%Y%m%d%H%M")
        elif isinstance(time, str):
            # Check if it's RFC3339 format (contains T and ends with Z or timezone)
            if 'T' in time and (time.endswith('Z') or '+' in time or '-' in time[-6:]):
                # Parse RFC3339 and convert to YYYYMMDDHHMM
                dt = datetime.fromisoformat(time.replace('Z', '+00:00'))
                time_str = dt.strftime("%Y%m%d%H%M")
            else:
                # Assume it's already in YYYYMMDDHHMM format
                time_str = time
        else:
            raise ValueError("time must be a datetime object or string")
        request = ResolveKrefRequest(kref=self.kref.uri, time=time_str)
        try:
            response = self._client.stub.ResolveKref(request)
            return Version(response, self._client)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def peek_next_version(self) -> int:
        """Get the next version number that would be assigned.

        This is useful for previewing version numbers before creating
        versions, such as for naming files or planning workflows.

        Returns:
            int: The next version number.

        Example:
            >>> next_num = product.peek_next_version()
            >>> print(f"Next version will be v{next_num}")
        """
        return self._client.peek_next_version(self.kref)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Product':
        """Set or update metadata for this product.

        Metadata is merged with existing metadata—existing keys are
        overwritten and new keys are added.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            Product: The updated Product object.

        Example:
            >>> product.set_metadata({
            ...     "status": "final",
            ...     "department": "modeling",
            ...     "complexity": "high"
            ... })
        """
        return self._client.update_product_metadata(self.kref, metadata)

    def delete(self, force: bool = False) -> None:
        """Delete this product.

        Args:
            force: If True, permanently delete the product and all its
                versions. If False (default), deletion may fail if the
                product has versions.

        Raises:
            grpc.RpcError: If deletion fails.

        Example:
            >>> # Delete product (fails if has versions)
            >>> product.delete()

            >>> # Force delete with all versions
            >>> product.delete(force=True)
        """
        self._client.delete_product(self.kref, force)

    def set_deprecated(self, status: bool) -> None:
        """Set the deprecated status of this product.

        Deprecated products are hidden from default searches but remain
        accessible for historical reference.

        Args:
            status: True to deprecate, False to restore.

        Example:
            >>> product.set_deprecated(True)  # Hide from searches
            >>> product.set_deprecated(False)  # Restore visibility
        """
        self._client.set_deprecated(self.kref, status)
        self.deprecated = status
