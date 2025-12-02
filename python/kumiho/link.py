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
import re

from .base import KumihoObject
from .kref import Kref
from .proto.kumiho_pb2 import Link as PbLink

if TYPE_CHECKING:
    from .client import _Client


class LinkTypeValidationError(ValueError):
    """Raised when a link type is invalid or potentially malicious."""
    pass


# Regex for validating link types - must match Rust server validation
_LINK_TYPE_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]{0,49}$')


def validate_link_type(link_type: str) -> None:
    """Validate a link type for security and correctness.
    
    Link types must:
    - Start with an uppercase letter
    - Contain only uppercase letters, digits, and underscores
    - Be 1-50 characters long
    
    Args:
        link_type: The link type to validate.
        
    Raises:
        LinkTypeValidationError: If the link type is invalid.
        
    Example::
    
        from kumiho.link import validate_link_type, LinkTypeValidationError
        
        try:
            validate_link_type("DEPENDS_ON")  # OK
            validate_link_type("depends_on")  # Raises error
        except LinkTypeValidationError as e:
            print(f"Invalid link type: {e}")
    """
    if not isinstance(link_type, str):
        raise LinkTypeValidationError(
            f"Link type must be a string, got {type(link_type).__name__}"
        )
    
    if not _LINK_TYPE_PATTERN.match(link_type):
        raise LinkTypeValidationError(
            f"Invalid link_type '{link_type}'. Must start with uppercase letter, "
            "contain only uppercase letters, digits, underscores, and be 1-50 chars."
        )


def is_valid_link_type(link_type: str) -> bool:
    """Check if a link type is valid without raising exceptions.
    
    Args:
        link_type: The link type to validate.
        
    Returns:
        True if the link type is valid, False otherwise.
    """
    try:
        validate_link_type(link_type)
        return True
    except LinkTypeValidationError:
        return False


class LinkType:
    """Standard link types for Kumiho relationships.

    These constants define the semantic meaning of relationships between
    versions. Use them when creating or querying links.
    
    All link types use UPPERCASE format as required by the Neo4j graph database.

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

    BELONGS_TO = "BELONGS_TO"
    """Ownership or grouping relationship."""

    CREATED_FROM = "CREATED_FROM"
    """Source was generated/created from target."""

    REFERENCED = "REFERENCED"
    """Soft reference relationship."""

    DEPENDS_ON = "DEPENDS_ON"
    """Source requires target to function."""

    DERIVED_FROM = "DERIVED_FROM"
    """Source was derived or modified from target."""

    CONTAINS = "CONTAINS"
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


# --- Graph Traversal Result Classes ---

from dataclasses import dataclass, field
from typing import List


@dataclass
class PathStep:
    """A single step in a traversal path.

    Represents one hop in a graph traversal, including the version
    reached and the link type used to reach it.

    Attributes:
        version_kref (Kref): The version at this step.
        link_type (str): The relationship type used to reach this version.
        depth (int): Distance from the origin (0 = origin).

    Example::

        for step in path.steps:
            print(f"Step {step.depth}: {step.version_kref} via {step.link_type}")
    """
    version_kref: Kref
    link_type: str
    depth: int


@dataclass
class VersionPath:
    """A complete path between versions.

    Represents a sequence of steps from one version to another,
    used in traversal and shortest-path queries.

    Attributes:
        steps (List[PathStep]): The sequence of steps in the path.
        total_depth (int): Total length of the path.

    Example::

        path = source_version.find_path_to(target_version)
        if path:
            print(f"Path length: {path.total_depth}")
            for step in path.steps:
                print(f"  -> {step.version_kref}")
    """
    steps: List[PathStep] = field(default_factory=list)
    total_depth: int = 0


@dataclass
class ImpactedVersion:
    """A version impacted by changes to another version.

    Represents a version that directly or indirectly depends on
    a target version, used in impact analysis.

    Attributes:
        version_kref (Kref): The impacted version.
        product_kref (Kref): The product containing the impacted version.
        impact_depth (int): How many hops away from the target.
        impact_path_types (List[str]): Link types in the impact chain.

    Example::

        impact = texture_v1.analyze_impact()
        for iv in impact:
            print(f"{iv.version_kref} at depth {iv.impact_depth}")
    """
    version_kref: Kref
    product_kref: Optional[Kref] = None
    impact_depth: int = 0
    impact_path_types: List[str] = field(default_factory=list)


class TraversalResult:
    """Result of a graph traversal query.

    Contains all versions discovered during a multi-hop traversal,
    along with optional path information.

    Attributes:
        version_krefs (List[Kref]): Flat list of discovered version references.
        paths (List[VersionPath]): Path information if requested.
        links (List[Link]): All traversed links.
        total_count (int): Total number of discovered versions.
        truncated (bool): True if results were limited by max_depth or limit.

    Example::

        # Get all transitive dependencies
        result = version.get_all_dependencies(max_depth=5)
        
        print(f"Found {result.total_count} dependencies")
        if result.truncated:
            print("Results were truncated")
        
        for kref in result.version_krefs:
            print(f"  - {kref}")
    """

    def __init__(
        self,
        version_krefs: List[Kref],
        paths: List[VersionPath],
        links: List['Link'],
        total_count: int,
        truncated: bool,
        client: '_Client'
    ) -> None:
        self.version_krefs = version_krefs
        self.paths = paths
        self.links = links
        self.total_count = total_count
        self.truncated = truncated
        self._client = client

    def __repr__(self) -> str:
        return f"<TraversalResult count={self.total_count} truncated={self.truncated}>"

    def get_versions(self) -> List['Version']:
        """Fetch full Version objects for all discovered versions.

        Returns:
            List[Version]: List of Version objects.

        Example::

            result = version.get_all_dependencies()
            for v in result.get_versions():
                print(f"{v.kref} - {v.metadata}")
        """
        from .version import Version
        return [self._client.get_version(kref) for kref in self.version_krefs]


class ShortestPathResult:
    """Result of a shortest path query.

    Contains path(s) between two versions if found.

    Attributes:
        paths (List[VersionPath]): One or more shortest paths found.
        path_exists (bool): True if any path was found.
        path_length (int): Length of the shortest path(s).

    Example::

        result = source_version.find_path_to(target_version)
        if result.path_exists:
            print(f"Found path of length {result.path_length}")
            for path in result.paths:
                for step in path.steps:
                    print(f"  {step.depth}: {step.version_kref}")
    """

    def __init__(
        self,
        paths: List[VersionPath],
        path_exists: bool,
        path_length: int
    ) -> None:
        self.paths = paths
        self.path_exists = path_exists
        self.path_length = path_length

    def __repr__(self) -> str:
        return f"<ShortestPathResult exists={self.path_exists} length={self.path_length}>"

    @property
    def first_path(self) -> Optional[VersionPath]:
        """Get the first (or only) shortest path.

        Returns:
            VersionPath if a path exists, None otherwise.
        """
        return self.paths[0] if self.paths else None
