"""Resource-related classes and functionality."""

from datetime import datetime
from typing import Dict, Optional

from typing import TYPE_CHECKING

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
    """A high-level object representing a Kumiho resource.

    A Resource represents a file or asset associated with a specific version
    of a product, stored at a particular location.

    Attributes:
        kref (Kref): The unique reference for this resource.
        location (str): The storage location/path of the resource.
        version_kref (Kref): Reference to the parent version.
        product_kref (Optional[Kref]): Reference to the parent product, if available.
        created_at (Optional[datetime]): When the resource was created.
        author (str): The user who created the resource.
        metadata (Dict[str, str]): Custom metadata associated with the resource.
        deprecated (bool): Whether the resource is deprecated.
        username (str): The username of the creator.
    """

    def __init__(self, pb_resource: ResourceResponse, client: '_Client') -> None:
        """Initialize a Resource from a protobuf response.

        Args:
            pb_resource: The protobuf ResourceResponse message.
            client: The client instance for API calls.
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
        """Extract the resource name from its kref.

        Returns:
            The resource name extracted from the kref URI.
        """
        return self.kref.uri.split('&r=')[-1]

    def set_metadata(self, metadata: Dict[str, str]) -> 'Resource':
        """Set or update the metadata for this resource.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The updated Resource object.
        """
        return self._client.update_resource_metadata(self.kref, metadata)

    def delete(self, force: bool = False) -> None:
        """Delete the resource.

        Args:
            force: If True, force deletion. Requires appropriate permissions.
        """
        self._client.delete_resource(self.kref, force)

    def set_deprecated(self, status: bool) -> None:
        """Set the deprecated status of the resource.

        Args:
            status: True to deprecate, False to un-deprecate.
        """
        self._client.set_deprecated(self.kref, status)
        self.deprecated = status

    def set_default(self) -> None:
        """Set this resource as the default for its version."""
        self.get_version().set_default_resource(self.name)

    def get_version(self) -> 'Version':
        """Get the parent version of this resource.

        Returns:
            The Version object.
        """
        return self._client.get_version(self.version_kref.uri)

    def get_product(self) -> 'Product':
        """Get the parent product of this resource.

        Returns:
            The Product object.
        """
        if self.product_kref:
            return self._client.get_product_by_kref(self.product_kref.uri)
        # Fallback via version
        return self.get_version().get_product()

    def get_group(self) -> 'Group':
        """Get the group containing this resource's product.

        Returns:
            The Group object.
        """
        return self.get_product().get_group()

    def get_project(self) -> 'Project':
        """Get the project containing this resource.

        Returns:
            The Project object.
        """
        return self.get_group().get_project()