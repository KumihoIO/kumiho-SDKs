"""Kref class for handling Kumiho resource references."""

from typing import Optional
import re
from .proto import kumiho_pb2

class Kref(str):
    """A Kumiho resource reference, represented as a URI string.
    
    Kref is a subclass of str, so it behaves like a string (the URI) but provides
    utility methods for parsing and manipulation.
    
    Attributes:
        uri (str): The URI string (for backward compatibility).
    """
    
    def __new__(cls, uri: str) -> 'Kref':
        """Create a new Kref instance.
        
        Args:
            uri: The URI string for the Kref.
            
        Returns:
            A Kref instance that is also a string.
        """
        return str.__new__(cls, uri)
    
    @property
    def uri(self) -> str:
        """The URI string (for backward compatibility)."""
        return str(self)
    
    def to_pb(self) -> kumiho_pb2.Kref:
        """Convert to a protobuf Kref object.
        
        Returns:
            A kumiho_pb2.Kref instance with the URI set.
        """
        return kumiho_pb2.Kref(uri=str(self))
    
    def get_path(self) -> str:
        """Extract the path part of the URI (e.g., 'group/product.type')."""
        if "://" not in self:
            return self
        return self.split("://", 1)[1].split("?", 1)[0]
    
    def get_group(self) -> str:
        """Extract the group name from the URI."""
        path = self.get_path()
        if "/" not in path:
            return path
        return path.split("/", 1)[0]
    
    def get_product_name(self) -> str:
        """Extract the product name (including type) from the URI."""
        path = self.get_path()
        if "/" not in path:
            return ""
        return path.split("/", 1)[1]
    
    def get_type(self) -> str:
        """Extract the product type from the URI."""
        name = self.get_product_name()
        if "." not in name:
            return ""
        return name.split(".", 1)[1]
    
    def get_version(self) -> int:
        """Extract the version number from the URI query string."""
        match = re.search(r'\?v=(\d+)', self)
        return int(match.group(1)) if match else 1
    
    def get_resource_name(self) -> Optional[str]:
        """Extract the resource name from the URI query string (&r=resource_name)."""
        match = re.search(r'&r=([^&]+)', self)
        return match.group(1) if match else None
    
    def __repr__(self) -> str:
        return f"Kref('{self}')"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)
    
    def __hash__(self) -> int:
        return str.__hash__(self)