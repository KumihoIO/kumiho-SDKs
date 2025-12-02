"""Collection module for Kumiho asset management.

This module provides the :class:`Collection` class, which represents a special
type of product that aggregates other products. Collections are used to group
related products together and maintain an audit trail of membership changes.

Collections are unique in that:
    - The ``collection`` product type is reserved and cannot be created manually.
    - Use :meth:`Project.create_collection` or :meth:`Group.create_collection`.
    - Each membership change (add/remove) creates a new version for audit trail.
    - Version metadata is immutable, providing complete change history.

Example::

    import kumiho

    # Create a collection from a project or group
    project = kumiho.get_project("my-project")
    collection = project.create_collection("asset-bundle")

    # Add products to the collection
    hero_model = kumiho.get_product("kref://my-project/models/hero.model")
    collection.add_member(hero_model)

    # Get all members
    members = collection.get_members()
    for member in members:
        print(f"Product: {member.product_kref}")

    # View history of changes (immutable audit trail)
    for entry in collection.get_history():
        print(f"v{entry.version_number}: {entry.action} {entry.member_product_kref}")

See Also:
    - :class:`CollectionMember`: Data class for collection members.
    - :class:`CollectionVersionHistory`: Data class for audit trail entries.
    - :exc:`ReservedProductTypeError`: Error for reserved type violations.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .kref import Kref
from .product import Product

if TYPE_CHECKING:
    from .client import _Client
    from .version import Version
    from .proto.kumiho_pb2 import ProductResponse


# Reserved product types that cannot be created manually
RESERVED_PRODUCT_TYPES = frozenset(["collection"])
"""frozenset: Product types that are reserved and cannot be created via create_product.

Currently includes:
    - ``collection``: Use :meth:`Project.create_collection` or 
      :meth:`Group.create_collection` instead.
"""


class ReservedProductTypeError(Exception):
    """Raised when attempting to create a product with a reserved type.

    This error is raised when calling :meth:`Group.create_product` or the
    low-level client ``create_product`` with a reserved product type such
    as ``collection``.

    Example::

        import kumiho

        group = project.get_group("assets")

        # This will raise ReservedProductTypeError
        try:
            group.create_product("my-bundle", "collection")
        except kumiho.ReservedProductTypeError as e:
            print(f"Error: {e}")
            # Use create_collection instead
            collection = group.create_collection("my-bundle")
    """
    pass


@dataclass
class CollectionMember:
    """A product that is a member of a collection.

    Represents the membership relationship between a product and a collection,
    including metadata about when and by whom the product was added.

    Attributes:
        product_kref (Kref): The kref of the member product.
        added_at (str): ISO timestamp when the product was added.
        added_by (str): UUID of the user who added the product.
        added_by_username (str): Display name of the user who added the product.
        added_in_version (int): The collection version when this product was added.

    Example::

        members = collection.get_members()
        for member in members:
            print(f"Product: {member.product_kref}")
            print(f"Added by: {member.added_by_username}")
            print(f"Added at: {member.added_at}")
            print(f"In version: {member.added_in_version}")
    """
    product_kref: Kref
    """Kref: The kref of the member product."""
    
    added_at: str
    """str: ISO timestamp when the product was added to the collection."""
    
    added_by: str
    """str: UUID of the user who added the product."""
    
    added_by_username: str
    """str: Display name of the user who added the product."""
    
    added_in_version: int
    """int: The collection version number when this product was added."""


@dataclass
class CollectionVersionHistory:
    """A historical change to a collection's membership.

    Each entry captures a single add or remove operation, providing
    an immutable audit trail of all membership changes. The metadata
    is immutable once created, ensuring complete traceability.

    Attributes:
        version_number (int): The collection version number for this change.
        action (str): The action performed: ``"CREATED"``, ``"ADDED"``, or ``"REMOVED"``.
        member_product_kref (Optional[Kref]): The product that was added/removed.
            None for the initial ``"CREATED"`` action.
        author (str): UUID of the user who made the change.
        username (str): Display name of the user who made the change.
        created_at (str): ISO timestamp of the change.
        metadata (Dict[str, str]): Immutable metadata captured at the time of change.

    Example::

        history = collection.get_history()
        for entry in history:
            print(f"Version {entry.version_number}: {entry.action}")
            if entry.member_product_kref:
                print(f"  Product: {entry.member_product_kref}")
            print(f"  By: {entry.username} at {entry.created_at}")
    """
    version_number: int
    """int: The collection version number for this change."""
    
    action: str
    """str: The action performed: ``"CREATED"``, ``"ADDED"``, or ``"REMOVED"``."""
    
    member_product_kref: Optional[Kref]
    """Optional[Kref]: The product that was added/removed (None for CREATED)."""
    
    author: str
    """str: UUID of the user who made the change."""
    
    username: str
    """str: Display name of the user who made the change."""
    
    created_at: str
    """str: ISO timestamp of when the change was made."""
    
    metadata: Dict[str, str]
    """Dict[str, str]: Immutable metadata captured at the time of the change."""


class Collection(Product):
    """A special product type that aggregates other products.

    Collections provide a way to group related products together. Unlike regular
    products, collections cannot be created using the standard ``create_product``
    method—the ``collection`` product type is reserved.

    Use :meth:`Project.create_collection` or :meth:`Group.create_collection`
    to create collections.

    Key features:
        - Aggregates products (not versions) via ``COLLECTS`` relationships.
        - Each membership change creates a new version for audit trail.
        - Version metadata is immutable, providing complete history.
        - Cannot contain itself (self-reference protection).

    Attributes:
        kref (Kref): The unique identifier for this collection.
        name (str): The combined name (e.g., "my-bundle.collection").
        product_name (str): The collection name (e.g., "my-bundle").
        product_type (str): Always "collection".
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        created_at (str): ISO timestamp when the collection was created.
        author (str): The user ID who created the collection.
        username (str): Display name of the creator.
        deprecated (bool): Whether the collection is deprecated.

    Example::

        import kumiho

        # Create a collection from a project
        project = kumiho.get_project("film-2024")
        bundle = project.create_collection("release-v1")

        # Add products
        model = kumiho.get_product("kref://film-2024/models/hero.model")
        texture = kumiho.get_product("kref://film-2024/textures/hero.texture")
        bundle.add_member(model)
        bundle.add_member(texture)

        # List current members
        for member in bundle.get_members():
            print(f"{member.product_kref} added by {member.added_by_username}")

        # Remove a member
        bundle.remove_member(model)

        # View complete audit history
        for entry in bundle.get_history():
            print(f"v{entry.version_number}: {entry.action}")

    See Also:
        :meth:`Project.create_collection`: Create a collection in a project.
        :meth:`Group.create_collection`: Create a collection in a group.
        :class:`CollectionMember`: Data class for member information.
        :class:`CollectionVersionHistory`: Data class for audit entries.
    """

    def __init__(self, pb: 'ProductResponse', client: '_Client') -> None:
        """Initialize a Collection from a protobuf response.

        Args:
            pb: The ProductResponse protobuf message.
            client: The client instance for making subsequent calls.

        Raises:
            ValueError: If the product_type is not 'collection'.
        """
        super().__init__(pb, client)
        if self.product_type != "collection":
            raise ValueError(
                f"Cannot create Collection from product_type '{self.product_type}'. "
                "Expected 'collection'."
            )

    def add_member(
        self,
        member: 'Product',
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional['Version']]:
        """Add a product to this collection.

        Creates a new version of the collection to track the change.
        The version metadata will include the action (``"ADDED"``) and
        the member product kref for audit purposes.

        Args:
            member: The product to add to the collection.
            metadata: Optional additional metadata to store in the version.
                This metadata becomes part of the immutable audit trail.

        Returns:
            Tuple[bool, str, Optional[Version]]: A tuple containing:
                - success: Whether the operation succeeded.
                - message: A status message.
                - new_version: The new collection version created for this change.

        Raises:
            ValueError: If trying to add the collection to itself.
            grpc.RpcError: If the member is already in the collection
                (status code ``ALREADY_EXISTS``).

        Example::

            hero_model = kumiho.get_product("kref://project/models/hero.model")
            
            # Add with optional metadata
            success, msg, version = collection.add_member(
                hero_model,
                metadata={"reason": "character bundle", "approved_by": "director"}
            )
            
            if success:
                print(f"Added in version {version.number}")
        """
        return self._client.add_collection_member(
            self.kref,
            member.kref,
            metadata=metadata
        )

    def remove_member(
        self,
        member: 'Product',
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional['Version']]:
        """Remove a product from this collection.

        Creates a new version of the collection to track the change.
        The version metadata will include the action (``"REMOVED"``) and
        the member product kref for audit purposes.

        Args:
            member: The product to remove from the collection.
            metadata: Optional additional metadata to store in the version.
                This metadata becomes part of the immutable audit trail.

        Returns:
            Tuple[bool, str, Optional[Version]]: A tuple containing:
                - success: Whether the operation succeeded.
                - message: A status message.
                - new_version: The new collection version created for this change.

        Raises:
            grpc.RpcError: If the member is not in the collection
                (status code ``NOT_FOUND``).

        Example::

            # Remove a product from the collection
            success, msg, version = collection.remove_member(hero_model)
            
            if success:
                print(f"Removed in version {version.number}")
        """
        return self._client.remove_collection_member(
            self.kref,
            member.kref,
            metadata=metadata
        )

    def get_members(
        self,
        version_number: Optional[int] = None
    ) -> List[CollectionMember]:
        """Get all products that are members of this collection.

        Returns information about each member product, including when
        it was added and by whom.

        Args:
            version_number: Optional specific version to query.
                If not provided, returns current membership.

        Returns:
            List[CollectionMember]: List of member information objects.

        Example::

            # Get current members
            members = collection.get_members()
            for member in members:
                print(f"{member.product_kref}")
                print(f"  Added by: {member.added_by_username}")
                print(f"  In version: {member.added_in_version}")

            # Get empty list if no members
            if not members:
                print("Collection is empty")
        """
        members, _, _ = self._client.get_collection_members(
            self.kref,
            version_number=version_number
        )
        return members

    def get_history(self) -> List[CollectionVersionHistory]:
        """Get the full history of membership changes.

        Returns all versions with their associated actions, providing
        a complete and immutable audit trail of all adds and removes.

        The history is ordered by version number, starting with the
        initial ``"CREATED"`` action.

        Returns:
            List[CollectionVersionHistory]: List of history entries, ordered
                by version number (oldest first).

        Example::

            history = collection.get_history()
            
            for entry in history:
                print(f"Version {entry.version_number}:")
                print(f"  Action: {entry.action}")
                print(f"  By: {entry.username}")
                print(f"  At: {entry.created_at}")
                if entry.member_product_kref:
                    print(f"  Product: {entry.member_product_kref}")
        """
        return self._client.get_collection_history(self.kref)

    def __repr__(self) -> str:
        """Return a string representation of the Collection."""
        return f"Collection(kref={self.kref!r}, name={self.name!r})"
