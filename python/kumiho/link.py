"""Link-related classes and functionality."""

from datetime import datetime
from typing import Dict, Optional

from typing import TYPE_CHECKING

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import Link as PbLink


class LinkType:
    """Standard link types for Kumiho links."""
    BELONGS_TO = "belongs_to"
    CREATED_FROM = "created_from"
    REFERENCED = "referenced"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"
    CONTAINS = "contains"


class LinkDirection:
    """Direction for link traversal."""
    OUTGOING = 0
    INCOMING = 1
    BOTH = 2

if TYPE_CHECKING:
    from .client import _Client


class Link(KumihoObject):
    """A high-level object representing a Kumiho link.

    A Link represents a relationship between two versions, such as dependencies
    or references between different assets.

    Attributes:
        source_kref (Kref): Reference to the source version.
        target_kref (Kref): Reference to the target version.
        link_type (str): The type of relationship (e.g., "depends_on", "references").
        metadata (Dict[str, str]): Custom metadata associated with the link.
        created_at (Optional[datetime]): When the link was created.
        author (str): The user who created the link.
        username (str): The username of the creator.
    """

    def __init__(self, pb_link: PbLink, client: '_Client') -> None:
        """Initialize a Link from a protobuf message.

        Args:
            pb_link: The protobuf Link message.
            client: The client instance for API calls.
        """
        super().__init__(client)
        self.source_kref = Kref(pb_link.source_kref.uri)
        self.target_kref = Kref(pb_link.target_kref.uri)
        self.link_type = pb_link.link_type
        self.metadata = dict(pb_link.metadata)
        self.created_at = pb_link.created_at or None
        self.author = pb_link.author
        self.username = pb_link.username

    def __repr__(self) -> str:
        """Return a string representation of the Link."""
        return f"<Link {self.source_kref.uri} -> {self.target_kref.uri} type={self.link_type}>"

    def delete(self, force: bool = False) -> None:
        """Delete the link."""
        self._client.delete_link(self.source_kref, self.target_kref, self.link_type)
