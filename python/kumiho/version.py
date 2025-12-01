"""Version module for Kumiho asset management.

This module provides the :class:`Version` class, which represents a specific
iteration of a product. Versions contain resources (file references), tags,
and metadata, and can be linked to other versions to track dependencies.

Example:
    Working with versions::

        import kumiho

        # Get a version
        version = kumiho.get_version("kref://project/models/hero.model?v=1")

        # Add resources
        version.create_resource("mesh", "/assets/hero.fbx")
        version.create_resource("textures", "/assets/hero_tex.zip")

        # Tag the version
        version.tag("approved")
        version.tag("ready-for-lighting")

        # Create links to dependencies
        texture_version = kumiho.get_version("kref://project/textures/skin.texture?v=3")
        version.create_link(texture_version, kumiho.DEPENDS_ON)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import VersionResponse
from .resource import Resource
from .link import Link

if TYPE_CHECKING:
    from .client import _Client
    from .product import Product
    from .group import Group
    from .project import Project


class Version(KumihoObject):
    """A specific iteration of a product in the Kumiho system.

    Versions are immutable snapshots of a product at a point in time. Each
    version can have multiple resources (file references), tags for
    categorization, and links to other versions for dependency tracking.

    The version's kref includes the version number:
    ``kref://project/group/product.type?v=1``

    Versions support dynamic tag checking—the ``tags`` property automatically
    refreshes from the server if the local data might be stale (older than 5
    seconds). This ensures tags like "latest" are always current.

    Attributes:
        kref (Kref): The unique reference URI for this version.
        product_kref (Kref): Reference to the parent product.
        number (int): The version number (1-based).
        latest (bool): Whether this is currently the latest version.
        tags (List[str]): Tags applied to this version (auto-refreshes).
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        created_at (Optional[str]): ISO timestamp when the version was created.
        author (str): The user ID who created the version.
        deprecated (bool): Whether the version is deprecated.
        published (bool): Whether the version is published.
        username (str): Display name of the creator.
        default_resource (Optional[str]): Name of the default resource.

    Example:
        Creating and managing versions::

            import kumiho

            product = kumiho.get_product("kref://project/models/hero.model")

            # Create a version with metadata
            v1 = product.create_version(metadata={
                "artist": "jane.doe",
                "software": "maya-2024",
                "notes": "Initial model"
            })

            # Add resources
            mesh = v1.create_resource("mesh", "/assets/hero.fbx")
            rig = v1.create_resource("rig", "/assets/hero_rig.fbx")

            # Set default resource (for resolve)
            v1.set_default_resource("mesh")

            # Tag the version
            v1.tag("approved")

            # Check tags
            if v1.has_tag("approved"):
                print("Version is approved!")

            # Get all resources
            for r in v1.get_resources():
                print(f"  {r.name}: {r.location}")

            # Link to dependencies
            texture = kumiho.get_version("kref://project/tex/skin.texture?v=2")
            v1.create_link(texture, kumiho.DEPENDS_ON)
    """

    def __init__(self, pb_version: VersionResponse, client: '_Client') -> None:
        """Initialize a Version from a protobuf response.

        Args:
            pb_version: The protobuf VersionResponse message.
            client: The client instance for making API calls.
        """
        super().__init__(client)
        self.kref = Kref(pb_version.kref.uri)
        self.product_kref = Kref(pb_version.product_kref.uri)
        self.number = pb_version.number
        self.latest = pb_version.latest
        self._cached_tags = list(pb_version.tags)
        self.metadata = dict(pb_version.metadata)
        self.created_at = pb_version.created_at or None
        self.author = pb_version.author
        self.deprecated = pb_version.deprecated
        self.published = pb_version.published
        self.username = pb_version.username
        self.default_resource = pb_version.default_resource or None
        self._fetched_at = datetime.now()

    def _is_stale(self) -> bool:
        """Check if this version's data might be stale.
        
        Returns:
            bool: True if the data is older than 5 seconds, indicating
                that tags like 'latest' might have changed.
        """
        return (datetime.now() - self._fetched_at).total_seconds() > 5

    @property
    def tags(self) -> List[str]:
        """Get the current tags for this version.

        This property automatically refreshes from the server if the data
        might be stale (older than 5 seconds), ensuring dynamic tags like
        "latest" are always current.

        Returns:
            List[str]: The list of tags on this version.

        Example:
            >>> version = product.get_version(1)
            >>> print(version.tags)  # ['latest', 'approved']
        """
        if self._is_stale():
            self.refresh()
        return self._cached_tags

    @tags.setter
    def tags(self, value: List[str]) -> None:
        """Set the cached tags (used internally)."""
        self._cached_tags = value

    def __repr__(self) -> str:
        """Return a string representation of the Version."""
        return f"<Version number='{self.number}' kref='{self.kref.uri}'>"

    def create_resource(self, name: str, location: str) -> Resource:
        """Create a new resource for this version.

        Resources are file references that point to actual assets on disk
        or network storage. Kumiho tracks the path and metadata but does
        not upload or copy the files.

        Args:
            name: The name of the resource (e.g., "mesh", "textures", "rig").
            location: The file path or URI where the resource is stored.

        Returns:
            Resource: The newly created Resource object.

        Example:
            >>> mesh = version.create_resource("mesh", "/assets/hero.fbx")
            >>> textures = version.create_resource("textures", "smb://server/tex/hero.zip")
        """
        return self._client.create_resource(self.kref, name, location)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Version':
        """Set or update metadata for this version.

        Metadata is merged with existing metadata—existing keys are
        overwritten and new keys are added.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            Version: The updated Version object.

        Example:
            >>> version.set_metadata({
            ...     "render_engine": "arnold",
            ...     "frame_range": "1-100",
            ...     "resolution": "4K"
            ... })
        """
        return self._client.update_version_metadata(self.kref, metadata)

    def has_tag(self, tag: str) -> bool:
        """Check if this version currently has a specific tag.

        This makes a server call to ensure the tag status is current.

        Args:
            tag: The tag to check for.

        Returns:
            bool: True if the version has the tag, False otherwise.

        Example:
            >>> if version.has_tag("approved"):
            ...     print("Ready for production!")
        """
        return self._client.has_tag(self.kref, tag)

    def tag(self, tag: str) -> None:
        """Apply a tag to this version.

        Tags are used to categorize versions and mark their status.
        Common tags include "latest", "published", "approved", etc.

        Note:
            The "latest" tag is automatically managed—it always points
            to the newest version.

        Args:
            tag: The tag to apply.

        Example:
            >>> version.tag("approved")
            >>> version.tag("ready-for-lighting")
        """
        self._client.tag_version(self.kref, tag)
        if tag not in self._cached_tags:
            self._cached_tags.append(tag)
        self._fetched_at = datetime.now()

    def untag(self, tag: str) -> None:
        """Remove a tag from this version.

        Args:
            tag: The tag to remove.

        Example:
            >>> version.untag("work-in-progress")
        """
        self._client.untag_version(self.kref, tag)
        if tag in self._cached_tags:
            self._cached_tags.remove(tag)
        self._fetched_at = datetime.now()

    def was_tagged(self, tag: str) -> bool:
        """Check if this version was ever tagged with a specific tag.

        This checks the historical record, not just current tags.

        Args:
            tag: The tag to check for.

        Returns:
            bool: True if the version was ever tagged with this tag.

        Example:
            >>> if version.was_tagged("approved"):
            ...     print("Was approved at some point")
        """
        return self._client.was_tagged(self.kref, tag)

    def get_resource(self, name: str) -> Resource:
        """Get a specific resource by name from this version.

        Args:
            name: The name of the resource.

        Returns:
            Resource: The Resource object.

        Raises:
            grpc.RpcError: If the resource is not found.

        Example:
            >>> mesh = version.get_resource("mesh")
            >>> print(mesh.location)
        """
        return self._client.get_resource(self.kref, name)

    def get_resources(self) -> List[Resource]:
        """Get all resources associated with this version.

        Returns:
            List[Resource]: A list of Resource objects.

        Example:
            >>> for resource in version.get_resources():
            ...     print(f"{resource.name}: {resource.location}")
        """
        return self._client.get_resources(self.kref)

    def get_locations(self) -> List[str]:
        """Get the file locations of all resources in this version.

        This is a convenience method to quickly get all file paths.

        Returns:
            List[str]: A list of file location strings.

        Example:
            >>> locations = version.get_locations()
            >>> for loc in locations:
            ...     print(loc)
        """
        return [r.location for r in self.get_resources()]

    def get_product(self) -> 'Product':
        """Get the parent product of this version.

        Returns:
            Product: The Product object that contains this version.

        Example:
            >>> product = version.get_product()
            >>> print(product.product_name)
        """
        return self._client.get_product_by_kref(self.product_kref.uri)

    def get_group(self) -> 'Group':
        """Get the group that contains this version's product.

        Returns:
            Group: The Group object.

        Example:
            >>> group = version.get_group()
            >>> print(group.path)
        """
        group_path = f"/{self.product_kref.get_group()}"
        return self._client.get_group(group_path)

    def get_project(self) -> 'Project':
        """Get the project that contains this version.

        Returns:
            Project: The Project object.

        Example:
            >>> project = version.get_project()
            >>> print(project.name)
        """
        return self.get_group().get_project()

    def refresh(self) -> None:
        """Refresh this version's data from the server.
        
        This updates all properties to reflect the current state in the
        database, including tags that may have changed (like "latest").

        Example:
            >>> version.refresh()
            >>> print(version.tags)  # Now shows current tags
        """
        fresh_version = self._client.get_version(self.kref)
        self.number = fresh_version.number
        self.latest = fresh_version.latest
        self._cached_tags = fresh_version.tags
        self.metadata = fresh_version.metadata
        self.created_at = fresh_version.created_at
        self.author = fresh_version.author
        self.deprecated = fresh_version.deprecated
        self.published = fresh_version.published
        self.username = fresh_version.username
        self.default_resource = fresh_version.default_resource
        self._fetched_at = datetime.now()

    def set_default_resource(self, resource_name: str) -> None:
        """Set the default resource for this version.

        The default resource is used when resolving the version's kref
        without specifying a resource name.

        Args:
            resource_name: The name of the resource to set as default.

        Example:
            >>> version.set_default_resource("mesh")
            >>> # Now kref://project/model.type?v=1 resolves to the mesh
        """
        from .proto.kumiho_pb2 import SetDefaultResourceRequest
        req = SetDefaultResourceRequest(
            version_kref=self.kref.to_pb(),
            resource_name=resource_name
        )
        self._client.stub.SetDefaultResource(req)
        self.default_resource = resource_name

    def delete(self, force: bool = False) -> None:
        """Delete this version.

        Args:
            force: If True, force deletion even if the version has
                resources. If False (default), deletion may fail.

        Raises:
            grpc.RpcError: If deletion fails.

        Example:
            >>> version.delete()  # Fails if has resources
            >>> version.delete(force=True)  # Force delete
        """
        self._client.delete_version(self.kref, force)

    def set_deprecated(self, status: bool) -> None:
        """Set the deprecated status of this version.

        Deprecated versions are hidden from default queries but remain
        accessible for historical reference.

        Args:
            status: True to deprecate, False to restore.

        Example:
            >>> version.set_deprecated(True)  # Hide from queries
        """
        self._client.set_deprecated(self.kref, status)
        self.deprecated = status

    def create_link(
        self,
        target_version: 'Version',
        link_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> 'Link':
        """Create a link from this version to another version.

        Links represent relationships between versions, such as dependencies,
        references, or derivations. This is useful for tracking asset lineage.

        Args:
            target_version: The target version to link to.
            link_type: The type of link. Use constants from :class:`kumiho.LinkType`:
                - ``kumiho.DEPENDS_ON``: This version depends on target.
                - ``kumiho.DERIVED_FROM``: This version was derived from target.
                - ``kumiho.REFERENCED``: This version references target.
                - ``kumiho.CONTAINS``: This version contains target.
            metadata: Optional metadata for the link.

        Returns:
            Link: The created Link object.

        Example:
            >>> import kumiho

            >>> # Link to a texture dependency
            >>> texture = kumiho.get_version("kref://project/tex/skin.texture?v=2")
            >>> version.create_link(texture, kumiho.DEPENDS_ON)

            >>> # Link with metadata
            >>> base = kumiho.get_version("kref://project/models/base.model?v=1")
            >>> version.create_link(base, kumiho.DERIVED_FROM, {
            ...     "modification": "Added details"
            ... })
        """
        return self._client.create_link(self, target_version, link_type, metadata)

    def get_links(
        self,
        link_type_filter: Optional[str] = None,
        direction: int = 0
    ) -> List['Link']:
        """Get links involving this version.

        Args:
            link_type_filter: Optional filter for link type.
            direction: The direction of links to retrieve:
                - ``kumiho.OUTGOING`` (0): Links from this version.
                - ``kumiho.INCOMING`` (1): Links to this version.
                - ``kumiho.BOTH`` (2): Links in both directions.

        Returns:
            List[Link]: A list of Link objects.

        Example:
            >>> import kumiho

            >>> # Get all dependencies
            >>> deps = version.get_links(kumiho.DEPENDS_ON, kumiho.OUTGOING)

            >>> # Get all versions that depend on this one
            >>> dependents = version.get_links(kumiho.DEPENDS_ON, kumiho.INCOMING)
        """
        return self._client.get_links(self.kref, link_type_filter or "", direction)

    def delete_link(self, target_version: 'Version', link_type: str) -> None:
        """Delete a link from this version.

        Args:
            target_version: The target version of the link.
            link_type: The type of link to delete.

        Example:
            >>> version.delete_link(texture_version, kumiho.DEPENDS_ON)
        """
        self._client.delete_link(self.kref, target_version.kref, link_type)
