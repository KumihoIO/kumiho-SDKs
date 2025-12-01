"""Link module for Kumiho asset management.

This module provides the :class:`Link` class and related constants for
tracking relationships between versions. Links enable dependency tracking,
lineage visualization, and impact analysis.

Link Types:
    - ``DEPENDS_ON``: Source depends on target (e.g., model uses texture).
    - ``DERIVED_FROM``: Source was created from target (e.g., LOD from highpoly).
    - ``REFERENCED``: Source references target (soft dependency).
    - ``CONTAINS``: Source contains target (composition).
    - ``CREATED_FROM``: Source was generated from target.
    - ``BELONGS_TO``: Source belongs to target (grouping).

Example::

    import kumiho

    # Get versions
    model = kumiho.get_version("kref://project/models/hero.model?v=1")
    texture = kumiho.get_version("kref://project/tex/skin.texture?v=2")

    # Create a dependency link
    link = model.create_link(texture, kumiho.DEPENDS_ON)

    # Query links
    deps = model.get_links(kumiho.DEPENDS_ON, kumiho.OUTGOING)
    for dep in deps:
        print(f"{dep.source_kref} depends on {dep.target_kref}")
"""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import Link as PbLink

if TYPE_CHECKING:
    from .client import _Client


class LinkType:
    """Standard link types for Kumiho relationships.

    These constants define the semantic meaning of relationships between
    versions. Use them when creating or querying links.

    Attributes:
        BELONGS_TO (str): Indicates ownership or grouping relationship.
        CREATED_FROM (str): Indicates the source was generated from target.
        REFERENCED (str): Indicates a soft reference relationship.
        DEPENDS_ON (str): Indicates the source requires the target.
        DERIVED_FROM (str): Indicates the source was derived/modified from target.
        CONTAINS (str): Indicates the source contains or includes the target.

    Example::

        import kumiho

        # Model depends on texture
        model_v1.create_link(texture_v2, kumiho.DEPENDS_ON)

        # LOD derived from high-poly
        lod_v1.create_link(highpoly_v1, kumiho.DERIVED_FROM)
    """

    BELONGS_TO = "belongs_to"
    """Ownership or grouping relationship."""

    CREATED_FROM = "created_from"
    """Source was generated/created from target."""

    REFERENCED = "referenced"
    """Soft reference relationship."""

    DEPENDS_ON = "depends_on"
    """Source requires target to function."""

    DERIVED_FROM = "derived_from"
    """Source was derived or modified from target."""

    CONTAINS = "contains"
    """Source contains or includes target."""


class LinkDirection:
    """Direction constants for link traversal queries.

    When querying links, you can specify which direction to traverse:
    outgoing links (from source), incoming links (to target), or both.

    Attributes:
        OUTGOING (int): Links where the queried version is the source.
        INCOMING (int): Links where the queried version is the target.
        BOTH (int): Links in either direction.

    Example::

        import kumiho

        # Get dependencies (what this version depends on)
        deps = version.get_links(kumiho.DEPENDS_ON, kumiho.OUTGOING)

        # Get dependents (what depends on this version)
        dependents = version.get_links(kumiho.DEPENDS_ON, kumiho.INCOMING)

        # Get all relationships
        all_links = version.get_links(direction=kumiho.BOTH)
    """

    OUTGOING = 0
    """Links where the queried version is the source."""

    INCOMING = 1
    """Links where the queried version is the target."""

    BOTH = 2
    """Links in either direction."""


class Link(KumihoObject):
    """A relationship between two versions in the Kumiho system.

    Links represent semantic relationships between versions, enabling
    dependency tracking, lineage visualization, and impact analysis.
    They are directional (source -> target) and typed.

    Common use cases:
        - Track which textures a model uses (DEPENDS_ON)
        - Record that a LOD was created from a high-poly model (DERIVED_FROM)
        - Link a render to the scene file that created it (CREATED_FROM)

    Attributes:
        source_kref (Kref): Reference to the source version.
        target_kref (Kref): Reference to the target version.
        link_type (str): The type of relationship (see :class:`LinkType`).
        metadata (Dict[str, str]): Custom metadata key-value pairs.
        created_at (Optional[str]): ISO timestamp when the link was created.
        author (str): The user ID who created the link.
        username (str): Display name of the creator.

    Example::

        import kumiho

        # Get versions
        model = kumiho.get_version("kref://project/models/hero.model?v=1")
        texture = kumiho.get_version("kref://project/tex/skin.texture?v=2")

        # Create link with metadata
        link = model.create_link(texture, kumiho.DEPENDS_ON, {
            "channel": "diffuse",
            "uv_set": "0"
        })

        # Inspect link
        print(f"Type: {link.link_type}")
        print(f"From: {link.source_kref}")
        print(f"To: {link.target_kref}")

        # Delete link
        link.delete()
    """

    def __init__(self, pb_link: PbLink, client: '_Client') -> None:
        """Initialize a Link from a protobuf message.

        Args:
            pb_link: The protobuf Link message.
            client: The client instance for making API calls.
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
        """Delete this link.

        Args:
            force: Reserved for future use.

        Example:
            >>> link = model.create_link(texture, kumiho.DEPENDS_ON)
            >>> link.delete()  # Remove the relationship
        """
        self._client.delete_link(self.source_kref, self.target_kref, self.link_type)
