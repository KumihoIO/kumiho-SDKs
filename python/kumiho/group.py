"""Group module for Kumiho asset management.

This module provides the :class:`Group` class, which represents hierarchical
containers for organizing products within a project. Groups form the folder
structure of the Kumiho asset hierarchy.

Example:
    Working with groups::

        import kumiho

        project = kumiho.get_project("film-2024")

        # Create group hierarchy
        chars = project.create_group("characters")
        heroes = chars.create_group("heroes")
        villains = chars.create_group("villains")

        # Create products in groups
        hero_model = heroes.create_product("main-hero", "model")

        # Navigate group hierarchy
        parent = heroes.get_parent_group()  # Returns chars
        children = chars.get_child_groups()  # Returns [heroes, villains]
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import GroupResponse
from .product import Product

if TYPE_CHECKING:
    from .client import _Client
    from .collection import Collection
    from .project import Project


class Group(KumihoObject):
    """A hierarchical container for organizing products in Kumiho.

    Groups form the folder structure within a project. They can contain
    other groups (subgroups) and products, allowing you to organize assets
    in a meaningful hierarchy.

    Groups are identified by their full path (e.g., "/project/characters/heroes")
    and can store custom metadata.

    Attributes:
        path (str): The full path of the group (e.g., "/project/assets").
        name (str): The name of this group (last component of path).
        type (str): The type of group ("root" for project-level, "sub" for nested).
        created_at (Optional[str]): ISO timestamp when the group was created.
        author (str): The user ID who created the group.
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        username (str): Display name of the creator.

    Example:
        Creating and navigating groups::

            import kumiho

            project = kumiho.get_project("my-project")

            # Create a group
            assets = project.create_group("assets")

            # Create subgroups
            models = assets.create_group("models")
            textures = assets.create_group("textures")

            # Create products
            chair = models.create_product("chair", "model")

            # List products with filters
            all_models = models.get_products()
            wood_textures = textures.get_products(name_filter="wood*")

            # Navigate hierarchy
            parent = models.get_parent_group()  # Returns assets
            project = models.get_project()  # Returns my-project
    """

    def __init__(self, pb_group: GroupResponse, client: '_Client') -> None:
        """Initialize a Group from a protobuf response.

        Args:
            pb_group: The protobuf GroupResponse message.
            client: The client instance for making API calls.
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
            Group: The newly created Group object.

        Example:
            >>> assets = project.create_group("assets")
            >>> models = assets.create_group("models")
            >>> textures = assets.create_group("textures")
        """
        return self._client.create_group(parent_path=self.path, group_name=name)

    def get_group(self, name: str) -> 'Group':
        """Get an existing subgroup by name.

        Args:
            name: The name of the subgroup (not full path).

        Returns:
            Group: The Group object.

        Raises:
            grpc.RpcError: If the group is not found.

        Example:
            >>> assets = project.get_group("assets")
            >>> models = assets.get_group("models")
        """
        path = f"{self.path.rstrip('/')}/{name}"
        return self._client.get_group(path)

    def get_groups(self, recursive: bool = False) -> List['Group']:
        """List child groups under this group.

        Args:
            recursive: If True, include all nested groups. If False (default),
                only direct children.

        Returns:
            List[Group]: A list of Group objects.

        Example:
            >>> # Direct children only
            >>> children = group.get_groups()

            >>> # All nested groups
            >>> all_groups = group.get_groups(recursive=True)
        """
        return self._client.get_child_groups(self.path, recursive=recursive)

    def create_product(self, product_name: str, product_type: str) -> Product:
        """Create a new product within this group.

        Products are versioned assets that can contain multiple resources.
        The combination of name and type must be unique within the group.

        Args:
            product_name: The name of the product (e.g., "hero-character").
            product_type: The type of product (e.g., "model", "texture", "workflow").

        Returns:
            Product: The newly created Product object.

        Example:
            >>> models = project.get_group("models")
            >>> chair = models.create_product("office-chair", "model")
            >>> wood = textures.create_product("oak-wood", "texture")
        """
        return self._client.create_product(self.path, product_name, product_type)

    def create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> 'Collection':
        """Create a new collection within this group.

        Collections are special products that aggregate other products.
        They provide a way to group related products together and maintain
        an audit trail of membership changes through version history.

        Args:
            collection_name: The name of the collection. Must be unique within
                the group.
            metadata: Optional key-value metadata for the collection.

        Returns:
            Collection: The newly created Collection object with type "collection".

        Raises:
            grpc.RpcError: If the collection name is already taken or if there
                is a connection error.

        See Also:
            :class:`~kumiho.collection.Collection`: The Collection class.
            :meth:`~kumiho.project.Project.create_collection`: Create collection in a project.

        Example::

            >>> # Create a collection for a character bundle
            >>> assets = project.get_group("assets")
            >>> bundle = assets.create_collection("character-bundle")
            >>>
            >>> # Add products to the collection
            >>> hero = assets.get_product("hero", "model")
            >>> bundle.add_member(hero)
        """
        from .collection import Collection
        product = self._client.create_collection(
            parent_path=self.path,
            collection_name=collection_name,
            metadata=metadata
        )
        return Collection(product._pb, self._client)

    def get_products(
        self,
        product_name_filter: str = "",
        product_type_filter: str = ""
    ) -> List[Product]:
        """List products within this group with optional filtering.

        Args:
            product_name_filter: Filter by product name. Supports wildcards.
            product_type_filter: Filter by product type.

        Returns:
            List[Product]: A list of Product objects matching the filters.

        Example:
            >>> # All products in group
            >>> products = group.get_products()

            >>> # Only models
            >>> models = group.get_products(product_type_filter="model")

            >>> # Products starting with "hero"
            >>> heroes = group.get_products(product_name_filter="hero*")
        """
        return self._client.get_products(self.path, product_name_filter, product_type_filter)

    def get_product(self, product_name: str, product_type: str) -> Product:
        """Get a specific product by name and type.

        Args:
            product_name: The name of the product.
            product_type: The type of the product.

        Returns:
            Product: The Product object.

        Raises:
            grpc.RpcError: If the product is not found.

        Example:
            >>> chair = models.get_product("office-chair", "model")
            >>> versions = chair.get_versions()
        """
        return self._client.get_product(self.path, product_name, product_type)

    def set_metadata(self, metadata: Dict[str, str]) -> 'Group':
        """Set or update metadata for this group.

        Metadata is a dictionary of string key-value pairs that can store
        any custom information about the group.

        Args:
            metadata: Dictionary of metadata to set. Existing keys are
                overwritten, new keys are added.

        Returns:
            Group: The updated Group object.

        Example:
            >>> group.set_metadata({
            ...     "department": "modeling",
            ...     "supervisor": "jane.doe",
            ...     "status": "active"
            ... })
        """
        return self._client.update_group_metadata(Kref(self.path), metadata)

    def delete(self, force: bool = False) -> None:
        """Delete this group.

        Args:
            force: If True, force deletion even if the group contains
                products. If False (default), deletion fails if group
                is not empty.

        Raises:
            grpc.RpcError: If deletion fails (e.g., group not empty
                and force=False).

        Example:
            >>> # Delete empty group
            >>> empty_group.delete()

            >>> # Force delete group with contents
            >>> old_group.delete(force=True)
        """
        self._client.delete_group(self.path, force)

    def get_parent_group(self) -> Optional['Group']:
        """Get the parent group of this group.

        Returns:
            Optional[Group]: The parent Group object, or None if this is
                a project-level root group.

        Example:
            >>> heroes = project.get_group("characters/heroes")
            >>> chars = heroes.get_parent_group()  # Returns "characters" group
            >>> root = chars.get_parent_group()  # Returns None (project root)
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
        """Get immediate child groups of this group.

        This is a convenience method equivalent to ``get_groups(recursive=False)``.

        Returns:
            List[Group]: A list of direct child Group objects.

        Example:
            >>> assets = project.get_group("assets")
            >>> children = assets.get_child_groups()
            >>> for child in children:
            ...     print(child.name)
        """
        return self._client.get_child_groups(self.path)

    def get_project(self) -> 'Project':
        """Get the project that contains this group.

        Returns:
            Project: The parent Project object.

        Example:
            >>> group = kumiho.get_product("kref://my-project/assets/hero.model").get_group()
            >>> project = group.get_project()
            >>> print(project.name)
            my-project
        """
        # The project name is the first component of the path
        parts = [p for p in self.path.split('/') if p]
        if not parts:
            raise ValueError("Root group has no project")
        project_name = parts[0]
        return self._client.get_project(project_name)
