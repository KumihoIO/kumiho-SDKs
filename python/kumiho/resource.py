"""Resource module for Kumiho asset management.

This module provides the :class:`Resource` class, which represents a file
reference within a version. Resources are the leaf nodes of the Kumiho
hierarchy and point to actual files on local or network storage.

Kumiho follows a "BYO Storage" (Bring Your Own Storage) philosophy—it tracks
file paths and metadata but does not upload or copy files.

Example:
    Working with resources::

        import kumiho

        # Get a resource
        resource = kumiho.get_resource(
            "kref://project/models/hero.model?v=1&r=mesh"
        )

        # Check the file location
        print(f"File: {resource.location}")

        # Set metadata
        resource.set_metadata({
            "file_size": "125MB",
            "format": "FBX",
            "triangles": "2.5M"
        })

        # Navigate to parent objects
        version = resource.get_version()
        product = resource.get_product()
"""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import ResourceResponse

if TYPE_CHECKING:
    from .client import _Client
    from .version import Version
    from .product import Product
    from .group import Group
    from .project import Project


class Resource(KumihoObject):
    """A file reference within a version in the Kumiho system.

    Resources are the leaf nodes of the Kumiho hierarchy. They point to
    actual files on local disk, network storage, or cloud URIs. Kumiho
    tracks the path and metadata but does not upload or modify the files.

    The resource's kref includes both version and resource name:
    ``kref://project/group/product.type?v=1&r=resource_name``

    Attributes:
        kref (Kref): The unique reference URI for this resource.
        location (str): The file path or URI where the resource is stored.
        version_kref (Kref): Reference to the parent version.
        product_kref (Optional[Kref]): Reference to the parent product.
        created_at (Optional[str]): ISO timestamp when the resource was created.
        author (str): The user ID who created the resource.
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        deprecated (bool): Whether the resource is deprecated.
        username (str): Display name of the creator.

    Example:
        Working with resources::

            import kumiho

            version = kumiho.get_version("kref://project/models/hero.model?v=1")

            # Create resources
            mesh = version.create_resource("mesh", "/assets/hero.fbx")
            rig = version.create_resource("rig", "/assets/hero_rig.fbx")
            textures = version.create_resource("textures", "smb://server/tex/hero/")

            # Set metadata
            mesh.set_metadata({
                "triangles": "2.5M",
                "format": "FBX 2020",
                "units": "centimeters"
            })

            # Set as default resource
            mesh.set_default()

            # Get resource by name
            retrieved = version.get_resource("mesh")
            print(f"Location: {retrieved.location}")

            # Navigate hierarchy
            product = mesh.get_product()
            project = mesh.get_project()
    """

    def __init__(self, pb_resource: ResourceResponse, client: '_Client') -> None:
        """Initialize a Resource from a protobuf response.

        Args:
            pb_resource: The protobuf ResourceResponse message.
            client: The client instance for making API calls.
        """
        super().__init__(client)
        self.kref = Kref(pb_resource.kref.uri)
        self.location = pb_resource.location
        self.version_kref = Kref(pb_resource.version_kref.uri)
        self.product_kref = (
            Kref(pb_resource.product_kref.uri)
            if pb_resource.HasField('product_kref') else None
        )
        self.created_at = pb_resource.created_at or None
        self.author = pb_resource.author
        self.metadata = dict(pb_resource.metadata)
        self.deprecated = pb_resource.deprecated
        self.username = pb_resource.username

    def __repr__(self) -> str:
        """Return a string representation of the Resource."""
        return f"<Resource kref='{self.kref.uri}'>"

    @property
    def name(self) -> str:
        """Get the resource name from its kref.

        Returns:
            str: The resource name extracted from the kref URI.

        Example:
            >>> resource = version.get_resource("mesh")
            >>> print(resource.name)  # "mesh"
        """
        return self.kref.uri.split('&r=')[-1]

    def set_metadata(self, metadata: Dict[str, str]) -> 'Resource':
        """Set or update metadata for this resource.

        Metadata is merged with existing metadata—existing keys are
        overwritten and new keys are added.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            Resource: The updated Resource object.

        Example:
            >>> resource.set_metadata({
            ...     "file_size": "125MB",
            ...     "format": "FBX 2020",
            ...     "triangles": "2.5M",
            ...     "software": "Maya 2024"
            ... })
        """
        return self._client.update_resource_metadata(self.kref, metadata)

    def set_attribute(self, key: str, value: str) -> bool:
        """Set a single metadata attribute.

        This allows granular updates to metadata without replacing the entire
        metadata map.

        Args:
            key: The attribute key to set.
            value: The attribute value.

        Returns:
            bool: True if the attribute was set successfully.

        Example:
            >>> resource.set_attribute("file_size", "125MB")
            True
        """
        result = self._client.set_attribute(self.kref, key, value)
        if result:
            self.metadata[key] = value
        return result

    def get_attribute(self, key: str) -> Optional[str]:
        """Get a single metadata attribute.

        Args:
            key: The attribute key to retrieve.

        Returns:
            The attribute value if it exists, None otherwise.

        Example:
            >>> resource.get_attribute("file_size")
            "125MB"
        """
        return self._client.get_attribute(self.kref, key)

    def delete_attribute(self, key: str) -> bool:
        """Delete a single metadata attribute.

        Args:
            key: The attribute key to delete.

        Returns:
            bool: True if the attribute was deleted successfully.

        Example:
            >>> resource.delete_attribute("old_field")
            True
        """
        result = self._client.delete_attribute(self.kref, key)
        if result and key in self.metadata:
            del self.metadata[key]
        return result

    def delete(self, force: bool = False) -> None:
        """Delete this resource.

        Args:
            force: If True, force deletion. If False (default), normal
                deletion rules apply.

        Raises:
            grpc.RpcError: If deletion fails.

        Example:
            >>> resource.delete()
        """
        self._client.delete_resource(self.kref, force)

    def set_deprecated(self, status: bool) -> None:
        """Set the deprecated status of this resource.

        Deprecated resources are hidden from default queries but remain
        accessible for historical reference.

        Args:
            status: True to deprecate, False to restore.

        Example:
            >>> resource.set_deprecated(True)  # Hide from queries
            >>> resource.set_deprecated(False)  # Restore visibility
        """
        self._client.set_deprecated(self.kref, status)
        self.deprecated = status

    def set_default(self) -> None:
        """Set this resource as the default for its version.

        The default resource is used when resolving the version's kref
        without specifying a resource name.

        Example:
            >>> mesh = version.create_resource("mesh", "/assets/model.fbx")
            >>> mesh.set_default()
            >>> # Now resolving the version kref returns this resource's location
        """
        self.get_version().set_default_resource(self.name)

    def get_version(self) -> 'Version':
        """Get the parent version of this resource.

        Returns:
            Version: The Version object that contains this resource.

        Example:
            >>> version = resource.get_version()
            >>> print(f"Version {version.number}")
        """
        return self._client.get_version(self.version_kref.uri)

    def get_product(self) -> 'Product':
        """Get the product that contains this resource.

        Returns:
            Product: The Product object.

        Example:
            >>> product = resource.get_product()
            >>> print(product.product_name)
        """
        if self.product_kref:
            return self._client.get_product_by_kref(self.product_kref.uri)
        # Fallback via version
        return self.get_version().get_product()

    def get_group(self) -> 'Group':
        """Get the group containing this resource's product.

        Returns:
            Group: The Group object.

        Example:
            >>> group = resource.get_group()
            >>> print(group.path)
        """
        return self.get_product().get_group()

    def get_project(self) -> 'Project':
        """Get the project containing this resource.

        Returns:
            Project: The Project object.

        Example:
            >>> project = resource.get_project()
            >>> print(project.name)
        """
        return self.get_group().get_project()