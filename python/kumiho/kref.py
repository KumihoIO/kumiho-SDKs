"""Kref module for Kumiho resource references.

This module provides the :class:`Kref` class, which represents a Kumiho
Resource Reference—a URI-based unique identifier for any object in the
Kumiho system.

Kref Format:
    The kref URI follows this pattern::

        kref://project/group/product.type?v=VERSION&r=RESOURCE

    Components:
        - ``project``: The project name
        - ``group``: The group path (can be nested: ``group/subgroup``)
        - ``product.type``: Product name and type separated by dot
        - ``?v=VERSION``: Optional version number (default: 1)
        - ``&r=RESOURCE``: Optional resource name

Examples:
    Product kref::

        kref://film-2024/characters/hero.model

    Version kref::

        kref://film-2024/characters/hero.model?v=3

    Resource kref::

        kref://film-2024/characters/hero.model?v=3&r=mesh

Usage::

    import kumiho
    from kumiho import Kref

    # Parse a kref
    kref = Kref("kref://project/models/hero.model?v=2&r=mesh")

    # Extract components
    print(kref.get_group())        # "project/models"
    print(kref.get_product_name()) # "hero.model"
    print(kref.get_type())         # "model"
    print(kref.get_version())      # 2
    print(kref.get_resource_name()) # "mesh"

    # Use as string
    print(f"Reference: {kref}")  # Works like a string
"""

from typing import Optional
import re
from .proto import kumiho_pb2


class Kref(str):
    """A Kumiho Resource Reference (URI-based unique identifier).

    Kref is a subclass of ``str``, so it behaves like a string but provides
    utility methods for parsing and extracting components from the URI.

    The kref format is::

        kref://project/group/product.type?v=VERSION&r=RESOURCE

    Attributes:
        uri (str): The URI string (for backward compatibility).

    Example::

        from kumiho import Kref

        # Create from string
        kref = Kref("kref://my-project/assets/hero.model?v=2")

        # Use as string (since Kref extends str)
        print(kref)  # kref://my-project/assets/hero.model?v=2

        # Parse components
        print(kref.get_group())   # "my-project/assets"
        print(kref.get_version()) # 2

        # Compare with strings
        if kref == "kref://my-project/assets/hero.model?v=2":
            print("Match!")

    Note:
        Since Kref is a string subclass, you can use it anywhere a string
        is expected. All string methods work normally.
    """

    def __new__(cls, uri: str) -> 'Kref':
        """Create a new Kref instance.

        Args:
            uri: The kref URI string.

        Returns:
            Kref: A Kref instance that is also a string.

        Example:
            >>> kref = Kref("kref://project/group/product.type?v=1")
            >>> isinstance(kref, str)
            True
        """
        return str.__new__(cls, uri)

    @property
    def uri(self) -> str:
        """Get the URI string.

        This property exists for backward compatibility with older code
        that accessed ``.uri`` directly.

        Returns:
            str: The kref URI string.
        """
        return str(self)

    def to_pb(self) -> kumiho_pb2.Kref:
        """Convert to a protobuf Kref object.

        Used internally for gRPC communication.

        Returns:
            kumiho_pb2.Kref: A protobuf Kref message.
        """
        return kumiho_pb2.Kref(uri=str(self))

    def get_path(self) -> str:
        """Extract the path component from the URI.

        Returns the part after ``kref://`` and before any query parameters.

        Returns:
            str: The path (e.g., "project/group/product.type").

        Example:
            >>> Kref("kref://project/models/hero.model?v=1").get_path()
            'project/models/hero.model'
        """
        if "://" not in self:
            return self
        return self.split("://", 1)[1].split("?", 1)[0]

    def get_group(self) -> str:
        """Extract the group path from the URI.

        Returns the path up to but not including the product name.

        Returns:
            str: The group path (e.g., "project/models").

        Example:
            >>> Kref("kref://project/models/hero.model").get_group()
            'project/models'
        """
        path = self.get_path()
        if "/" not in path:
            return path
        return path.rsplit("/", 1)[0]

    def get_product_name(self) -> str:
        """Extract the product name with type from the URI.

        Returns:
            str: The product name including type (e.g., "hero.model").

        Example:
            >>> Kref("kref://project/models/hero.model").get_product_name()
            'hero.model'
        """
        path = self.get_path()
        if "/" not in path:
            return ""
        return path.rsplit("/", 1)[1]

    def get_type(self) -> str:
        """Extract the product type from the URI.

        Returns:
            str: The product type (e.g., "model", "texture").

        Example:
            >>> Kref("kref://project/models/hero.model").get_type()
            'model'
        """
        name = self.get_product_name()
        if "." not in name:
            return ""
        return name.split(".", 1)[1]

    def get_version(self) -> int:
        """Extract the version number from the URI query string.

        Returns:
            int: The version number, or 1 if not specified.

        Example:
            >>> Kref("kref://project/models/hero.model?v=3").get_version()
            3
            >>> Kref("kref://project/models/hero.model").get_version()
            1
        """
        match = re.search(r'\?v=(\d+)', self)
        return int(match.group(1)) if match else 1

    def get_resource_name(self) -> Optional[str]:
        """Extract the resource name from the URI query string.

        Returns:
            Optional[str]: The resource name if present, None otherwise.

        Example:
            >>> Kref("kref://project/models/hero.model?v=1&r=mesh").get_resource_name()
            'mesh'
            >>> Kref("kref://project/models/hero.model?v=1").get_resource_name()
            None
        """
        match = re.search(r'&r=([^&]+)', self)
        return match.group(1) if match else None

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"Kref('{self}')"

    def __eq__(self, other: object) -> bool:
        """Compare with another Kref or string."""
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        return str.__hash__(self)