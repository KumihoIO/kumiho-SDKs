"""Product-related classes and functionality."""

import grpc
from datetime import datetime
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import ProductResponse, ResolveKrefRequest
from .version import Version

if TYPE_CHECKING:
    from .client import Client
    from .group import Group


class Product(KumihoObject):
    """A high-level object representing a Kumiho product.

    A Product represents a specific asset or item within a group that can have
    multiple versions. Products are the core entities that get versioned.

    Attributes:
        kref (Kref): The unique reference for this product.
        name (str): The name of the product.
        product_name (str): The product name.
        product_type (str): The type of the product (e.g., "model", "texture").
        created_at (Optional[datetime]): When the product was created.
        author (str): The user who created the product.
        metadata (Dict[str, str]): Custom metadata associated with the product.
        deprecated (bool): Whether the product is deprecated.
        username (str): The username of the creator.
    """

    def __init__(self, pb_product: ProductResponse, client: 'Client') -> None:
        """Initialize a Product from a protobuf response.

        Args:
            pb_product: The protobuf ProductResponse message.
            client: The client instance for API calls.
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
        """Create a new version for this product.

        Args:
            metadata: Optional metadata for the version.
            number: Specific version number to use (0 for auto-increment).

        Returns:
            The newly created Version object.
        """
        return self._client.create_version(self.kref, metadata, number)

    def get_versions(self) -> List[Version]:
        """Get all versions of this product.

        Returns:
            A list of Version objects for this product.
        """
        return self._client.get_versions(self.kref)

    def get_version(self, version_number: int) -> Optional[Version]:
        """Get a specific version by its number.

        Args:
            version_number: The version number to retrieve.

        Returns:
            The Version object if found, None otherwise.
        """
        kref_uri = f"{self.kref.uri}?v={version_number}"
        return self._client.get_version(kref_uri)

    def get_latest_version(self) -> Optional[Version]:
        """Get the latest version of this product.

        Returns:
            The latest Version object, or None if no versions exist.
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
        """Get the leaf group that contains this product.

        Returns:
            The Group object that contains this product.
        """
        group_path = f"/{self.kref.get_group()}"
        return self._client.get_group(group_path)

    def get_version_by_tag(self, tag: str) -> Optional[Version]:
        """Get a version by its tag.

        Args:
            tag: The tag to search for.

        Returns:
            The Version object if found, None otherwise.
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
        """Get a version by time.

        Args:
            time: The time as a datetime object or string in YYYYMMDDHHMM format or RFC3339 format.

        Returns:
            The Version object if found, None otherwise.
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

        Returns:
            The next version number.
        """
        return self._client.peek_next_version(self.kref)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Product':
        """Set or update the metadata for this product.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The updated Product object.
        """
        return self._client.update_product_metadata(self.kref, metadata)

    def delete(self, force: bool = False) -> None:
        """Delete the product.

        Args:
            force: If True, force deletion even if it has versions.
                  Requires appropriate permissions.
        """
        self._client.delete_product(self.kref, force)
