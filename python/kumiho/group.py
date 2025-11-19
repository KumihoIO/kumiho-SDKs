"""Group-related classes and functionality."""

from typing import Dict, List, Optional

from typing import TYPE_CHECKING

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import GroupResponse
from .product import Product

if TYPE_CHECKING:
    from .client import Client


class Group(KumihoObject):
    """A high-level object representing a Kumiho group.

    A Group is a hierarchical container that can hold other groups and products.
    Groups form the organizational structure of the Kumiho system.

    Attributes:
        path (str): The full path of the group (e.g., "/project/asset").
        name (str): The name of the group.
        type (str): The type of the group ("root" or "sub").
        created_at (Optional[datetime]): When the group was created.
        author (str): The user who created the group.
        metadata (Dict[str, str]): Custom metadata associated with the group.
        username (str): The username of the creator.
    """

    def __init__(self, pb_group: GroupResponse, client: 'Client') -> None:
        """Initialize a Group from a protobuf response.

        Args:
            pb_group: The protobuf GroupResponse message.
            client: The client instance for API calls.
        """
        super().__init__(client)
        self.path = pb_group.path
        self.name = pb_group.name
        self.type = pb_group.type
        self.created_at = pb_group.created_at or None
        self.author = pb_group.author
        self.metadata = dict(pb_group.metadata)
        self.username = pb_group.username

    def __repr__(self) -> str:
        """Return a string representation of the Group."""
        return f"<kumiho.Group path='{self.path}'>"

    def create_group(self, name: str) -> 'Group':
        """Create a new subgroup within this group.

        Args:
            name: The name of the new subgroup.

        Returns:
            The newly created Group object.
        """
        return self._client.create_group(parent_path=self.path, group_name=name)

    def create_product(self, product_name: str, product_type: str) -> Product:
        """Create a new product within this group.

        Args:
            product_name: The name of the product.
            product_type: The type of the product (e.g., "model", "texture").

        Returns:
            The newly created Product object.
        """
        return self._client.create_product(self.path, product_name, product_type)

    def get_products(self, product_name_filter: str = "", product_type_filter: str = "") -> List[Product]:
        """Search for products within this group.

        Args:
            product_name_filter: Optional name filter for products.
            product_type_filter: Optional type filter for products.

        Returns:
            A list of Product objects matching the filters.
        """
        return self._client.get_products(self.path, product_name_filter, product_type_filter)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Group':
        """Set or update the metadata for this group.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The updated Group object.
        """
        return self._client.update_group_metadata(Kref(self.path), metadata)

    def delete(self, force: bool = False) -> None:
        """Delete the group.

        Args:
            force: If True, force deletion even if the group contains products.
                  Requires appropriate permissions.
        """
        self._client.delete_group(self.path, force)

    def get_product(self, product_name: str, product_type: str) -> Product:
        """Get a specific product within this group by name and type.

        Args:
            product_name: The name of the product.
            product_type: The type of the product.

        Returns:
            The Product object.
        """
        return self._client.get_product(self.path, product_name, product_type)

    def get_parent_group(self) -> Optional['Group']:
        """Get the parent group of this group.

        Returns:
            The parent Group object, or None if this is a root group.
        """
        if self.path == "/":
            return None
        # Split path and remove the last component
        parts = [p for p in self.path.split('/') if p]  # Remove empty strings
        if len(parts) <= 1:
            return None  # This is a root-level group
        parent_parts = parts[:-1]
        if not parent_parts:
            parent_path = "/"
        else:
            parent_path = "/" + "/".join(parent_parts)
        return self._client.get_group(parent_path)

    def get_child_groups(self) -> List['Group']:
        """Get the child groups of this group.

        Returns:
            A list of Group objects that are direct children of this group.
        """
        return self._client.get_child_groups(self.path)