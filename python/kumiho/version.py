"""Version-related classes and functionality."""

from datetime import datetime
from typing import Dict, List, Optional

from typing import TYPE_CHECKING

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import VersionResponse
from .resource import Resource

if TYPE_CHECKING:
    from .client import Client
    from .product import Product
    from .group import Group


class Version(KumihoObject):
    """A high-level object representing a Kumiho version.

    A Version represents a specific iteration of a product with associated
    resources, tags, and metadata.

    The tags property automatically refreshes from the server if the local
    data is stale (older than 5 seconds), ensuring dynamic tags like 'latest'
    are always current. Use refresh() for manual updates of all properties.

    Attributes:
        kref (Kref): The unique reference for this version.
        product_kref (Kref): Reference to the parent product.
        number (int): The version number.
        latest (bool): Whether this is the latest version.
        tags (List[str]): List of tags applied to this version.
        metadata (Dict[str, str]): Custom metadata associated with the version.
        created_at (Optional[datetime]): When the version was created.
        author (str): The user who created the version.
        deprecated (bool): Whether the version is deprecated.
        published (bool): Whether the version is published.
        username (str): The username of the creator.
        default_resource (Optional[str]): The name of the default resource for this version.
    """

    def __init__(self, pb_version: VersionResponse, client: 'Client') -> None:
        """Initialize a Version from a protobuf response.

        Args:
            pb_version: The protobuf VersionResponse message.
            client: The client instance for API calls.
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
        
        Returns True if the data is older than 5 seconds, indicating
        that tags like 'latest' might have changed.
        """
        return (datetime.now() - self._fetched_at).total_seconds() > 5

    @property
    def tags(self) -> List[str]:
        """Get the current tags for this version.
        
        Automatically refreshes from the server if the data might be stale.
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

        Args:
            name: The name of the resource.
            location: The location/path of the resource.

        Returns:
            The newly created Resource object.
        """
        return self._client.create_resource(self.kref, name, location)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Version':
        """Set or update the metadata for this version.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The updated Version object.
        """
        return self._client.update_version_metadata(self.kref, metadata)

    def has_tag(self, tag: str) -> bool:
        """Check if the version has a specific tag.

        Args:
            tag: The tag to check for.

        Returns:
            True if the version has the tag, False otherwise.
        """
        return self._client.has_tag(self.kref, tag)

    def tag(self, tag: str) -> None:
        """Apply a tag to this version.

        Args:
            tag: The tag to apply.
        """
        self._client.tag_version(self.kref, tag)
        if tag not in self._cached_tags:
            self._cached_tags.append(tag)
        self._fetched_at = datetime.now()

    def untag(self, tag: str) -> None:
        """Remove a tag from this version.

        Args:
            tag: The tag to remove.
        """
        self._client.untag_version(self.kref, tag)
        if tag in self._cached_tags:
            self._cached_tags.remove(tag)
        self._fetched_at = datetime.now()

    def was_tagged(self, tag: str) -> bool:
        """Check if the version was ever tagged with a specific tag.

        Args:
            tag: The tag to check for.

        Returns:
            True if the version was ever tagged with the given tag.
        """
        return self._client.was_tagged(self.kref, tag)

    def get_resource(self, name: str) -> Resource:
        """Get a specific resource by name from this version.

        Args:
            name: The name of the resource.

        Returns:
            The Resource object.
        """
        return self._client.get_resource(self.kref, name)

    def get_resources(self) -> List[Resource]:
        """Get all resources associated with this version.

        Returns:
            A list of Resource objects.
        """
        return self._client.get_resources(self.kref)

    def get_locations(self) -> List[str]:
        """Get a list of locations for all resources in this version.

        Returns:
            A list of location strings.
        """
        return [r.location for r in self.get_resources()]

    def get_product(self) -> 'Product':
        """Get the parent product of this version.

        Returns:
            The Product object that contains this version.
        """
        return self._client.get_product_by_kref(self.product_kref.uri)

    def get_group(self) -> 'Group':
        """Get the leaf group that contains this version's product.

        Returns:
            The Group object that contains this version's product.
        """
        group_path = f"/{self.product_kref.get_group()}"
        return self._client.get_group(group_path)

    def refresh(self) -> None:
        """Refresh this version's data from the server.
        
        This updates all properties to reflect the current state in the database,
        including tags that may have changed (like 'latest').
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

        Args:
            resource_name: The name of the resource to set as default.
        """
        from .proto.kumiho_pb2 import SetDefaultResourceRequest
        req = SetDefaultResourceRequest(
            version_kref=self.kref.to_pb(),
            resource_name=resource_name
        )
        self._client.stub.SetDefaultResource(req)
        self.default_resource = resource_name

    def delete(self, force: bool = False) -> None:
        """Delete the version.

        Args:
            force: If True, force deletion even if it has resources.
                  Requires appropriate permissions.
        """
        self._client.delete_version(self.kref, force)
