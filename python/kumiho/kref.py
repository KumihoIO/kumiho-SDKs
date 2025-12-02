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


class KrefValidationError(ValueError):
    """Raised when a Kref URI is invalid or contains malicious patterns."""
    pass


# Regex for validating Kref URIs.
# Valid format: kref://project/group/product.type?v=VERSION&r=RESOURCE
# Each path segment must be alphanumeric with dots, underscores, or hyphens.
_KREF_PATTERN = re.compile(
    r'^kref://[a-zA-Z0-9][a-zA-Z0-9._-]*'
    r'(/[a-zA-Z0-9][a-zA-Z0-9._-]*)*'
    r'(\?v=\d+(&r=[a-zA-Z0-9._-]+)?)?$'
)


def validate_kref(uri: str) -> None:
    """Validate a Kref URI for security and correctness.
    
    Checks for:
    - Proper kref:// scheme
    - No path traversal patterns (..)
    - No control characters
    - Valid path segment format
    
    Args:
        uri: The kref URI to validate.
        
    Raises:
        KrefValidationError: If the URI is invalid or contains malicious patterns.
        
    Example::
    
        from kumiho.kref import validate_kref, KrefValidationError
        
        try:
            validate_kref("kref://project/group/product.type?v=1")
        except KrefValidationError as e:
            print(f"Invalid kref: {e}")
    """
    if not isinstance(uri, str):
        raise KrefValidationError(f"Kref must be a string, got {type(uri).__name__}")
    
    # Check for path traversal attempts
    if '..' in uri:
        raise KrefValidationError(
            f"Invalid kref URI '{uri}': path traversal (..) not allowed"
        )
    
    # Check for control characters
    if any(ord(c) < 32 or c == '\x7f' for c in uri):
        raise KrefValidationError(
            f"Invalid kref URI '{uri}': control characters not allowed"
        )
    
    # Check format with regex
    if not _KREF_PATTERN.match(uri):
        raise KrefValidationError(
            f"Invalid kref URI '{uri}': must be format kref://project/group/product.type"
        )


def is_valid_kref(uri: str) -> bool:
    """Check if a Kref URI is valid without raising exceptions.
    
    Args:
        uri: The kref URI to validate.
        
    Returns:
        True if the URI is valid, False otherwise.
        
    Example::
    
        from kumiho.kref import is_valid_kref
        
        if is_valid_kref("kref://project/group/product.type"):
            print("Valid!")
    """
    try:
        validate_kref(uri)
        return True
    except KrefValidationError:
        return False


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

    def __new__(cls, uri: str, *, validate: bool = True) -> 'Kref':
        """Create a new Kref instance.

        Args:
            uri: The kref URI string.
            validate: Whether to validate the URI (default: True).
                      Set to False for trusted internal sources.

        Returns:
            Kref: A Kref instance that is also a string.
            
        Raises:
            KrefValidationError: If validate=True and the URI is invalid.

        Example:
            >>> kref = Kref("kref://project/group/product.type?v=1")
            >>> isinstance(kref, str)
            True
        """
        if validate:
            validate_kref(uri)
        return str.__new__(cls, uri)
    
    @classmethod
    def from_pb(cls, pb_kref: kumiho_pb2.Kref) -> 'Kref':
        """Create a Kref from a protobuf message.
        
        This is used for krefs received from the server, which are trusted.
        
        Args:
            pb_kref: The protobuf Kref message.
            
        Returns:
            Kref: A Kref instance.
        """
        # Don't validate server-returned krefs - they're trusted
        return cls(pb_kref.uri, validate=False)

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