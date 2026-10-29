"""Kref module for Kumiho artifact references.

This module provides the :class:`Kref` class, which represents a Kumiho
Artifact Reference—a URI-based unique identifier for any object in the
Kumiho system.

Kref Format:
    The kref URI follows this pattern::

        kref://project/space/item.kind?r=REVISION&a=ARTIFACT

    Components:
        - ``project``: The project name
        - ``space``: The space path (can be nested: ``space/subspace``)
        - ``item.kind``: Item name and kind separated by dot
        - ``?r=REVISION``: Optional revision number (default: 1)
        - ``&a=ARTIFACT``: Optional artifact name

Examples:
    Item kref::

        kref://film-2024/characters/hero.model

    Revision kref::

        kref://film-2024/characters/hero.model?r=3

    Artifact kref::

        kref://film-2024/characters/hero.model?r=3&a=mesh

Parsing:
    :func:`parse_kref` is the one parser. It reads a kref once, with the grammar
    in ``spec/kref/README.md`` that kumiho-db and every Kumiho SDK share, and
    returns a :class:`KrefParts` value. Everything that needs a piece of a kref
    reads it from there: the ``GetItem`` request comes from
    :meth:`KrefParts.get_item_request`, and the :class:`Kref` accessors
    ``get_item_name()`` and ``get_kind()`` read the same textual split. A kref's
    last ``/`` ends the parent path and its last ``.`` ends the item name, so
    ``kref://p/a/b/my.file.v2.k`` is item ``my.file.v2`` of kind ``k`` in
    ``/p/a/b``.

    The parser is total and cheap: it never raises, the textual split is cut
    when it is created, and the kernel's reading (``valid``, ``error_class``,
    ``revision`` and the rest) is computed the first time one of those
    attributes is read. A revision with more digits than ``u64::MAX`` has is
    refused without being converted to an ``int``.

    Whether a string is *accepted* is a separate question, answered by
    :func:`validate_kref` and unchanged by the parser: a kref the kernel
    refuses but this SDK accepts (``?r=0``, a 33rd segment, the legacy
    ``kref:///space`` spelling) is still sent, and the backend decides.

    Every request is either the one the SDK sent before the structured parser
    (a7f155e) or resolves to the same node on kumiho-server. The server joins
    ``normalize_space_path(parent_path)``, ``/``, the item name, ``.`` and the
    kind, and ``normalize_space_path`` trims whitespace and ``/``. Where that
    would move a nested parent to a different space (a space segment that ends
    in whitespace, an empty trailing segment), the request keeps the shape
    a7f155e used: the project as the parent and everything after it as the
    name. The legacy ``kref:///s/x.k`` is sent as ``("//s", "x", "k")``, which
    the server normalizes to the node a7f155e's ``("/", "s/x", "k")`` named.

Usage::

    import kumiho
    from kumiho import Kref

    # Parse a kref
    kref = Kref("kref://project/models/hero.model?r=2&a=mesh")

    # Extract components
    print(kref.get_space())        # "project/models"
    print(kref.get_item_name())    # "hero.model"
    print(kref.get_kind())         # "model"
    print(kref.get_revision())     # 2
    print(kref.get_artifact_name()) # "mesh"

    # Use as string
    print(f"Reference: {kref}")  # Works like a string
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Dict, NamedTuple, Optional, Tuple
import re
import unicodedata
from .proto import kumiho_pb2


class KrefValidationError(ValueError):
    """Raised when a Kref URI is invalid or contains malicious patterns."""
    pass


# Regex for validating Kref URIs.
# Valid formats:
#   - Item: kref://project/space/item.kind?r=REVISION&a=ARTIFACT
#   - Space: kref://project/space or kref:///space (root-level)
# Path segments may contain Unicode letters/digits (\w is Unicode-aware in
# Python 3), plus dots and hyphens. Path traversal (..) and control characters
# are blocked by explicit checks in validate_kref, not by this regex.
# Artifact IDs remain ASCII-only since they are server-generated opaque
# identifiers — never user-provided content names.
_KREF_PATTERN = re.compile(
    r'^kref://'                      # scheme
    r'(/\w[\w.-]*(/\w[\w.-]*)*'      # space path starting with / (root-level)
    r'|'                             # OR
    r'\w[\w.-]*(/\w[\w.-]*)*)'       # project/item path segments
    r'(\?r=\d+(&a=[a-zA-Z0-9._-]+)?)?$',  # optional revision and artifact
    re.UNICODE,
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
            validate_kref("kref://project/space/item.kind?r=1")
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
            f"Invalid kref URI '{uri}': must be format kref://project/space/item.kind"
        )


def is_valid_kref(uri: str) -> bool:
    """Check if a Kref URI is valid without raising exceptions.
    
    Args:
        uri: The kref URI to validate.
        
    Returns:
        True if the URI is valid, False otherwise.
        
    Example::
    
        from kumiho.kref import is_valid_kref
        
        if is_valid_kref("kref://project/space/item.kind"):
            print("Valid!")
    """
    try:
        validate_kref(uri)
        return True
    except KrefValidationError:
        return False


# ---------------------------------------------------------------------------
# The structured parser (spec/kref/README.md).
# ---------------------------------------------------------------------------

_SCHEME = "kref://"
MAX_KREF_BYTES = 1024
MAX_KREF_SEGMENTS = 32
MAX_TAG_BYTES = 1024
MAX_ARTIFACT_NAME_BYTES = 256
_MAX_REVISION = 2**64 - 1
_MAX_REVISION_DIGITS = len(str(_MAX_REVISION))
# Other_Alphabetic code points whose category is So: circled and squared letters.
_OTHER_ALPHABETIC_SYMBOLS = (
    (0x24B6, 0x24E9),
    (0x1F130, 0x1F149),
    (0x1F150, 0x1F169),
    (0x1F170, 0x1F189),
)


class _Lexical(NamedTuple):
    """The purely textual split of a kref: no grammar is applied."""

    path: str
    parent: Optional[str]
    leaf: Optional[str]
    leaf_name: Optional[str]
    leaf_kind: Optional[str]


def _lexical(uri: str) -> _Lexical:
    """Split ``uri`` at the first ``://``, the first ``?``, the last ``/`` and the last ``.``.

    This is the one place a kref is cut into parent path, item name and kind.
    It never fails: ``leaf_name`` and ``leaf_kind`` are ``None`` when the leaf
    has no ``.``, and ``parent`` and ``leaf`` are ``None`` when the path has no
    ``/``.
    """
    if "://" in uri:
        path = uri.split("://", 1)[1].split("?", 1)[0]
    else:
        # No scheme: the whole string is the path, as get_path() always returned it.
        path = uri
    parent: Optional[str] = None
    leaf: Optional[str] = None
    if "/" in path:
        parent, leaf = path.rsplit("/", 1)
    leaf_name: Optional[str] = None
    leaf_kind: Optional[str] = None
    if leaf is not None and "." in leaf:
        # Item names may contain dots; kinds never do.
        leaf_name, leaf_kind = leaf.rsplit(".", 1)
    return _Lexical(path, parent, leaf, leaf_name, leaf_kind)


def _is_word(ch: str) -> bool:
    """The kernel's word class: Alphabetic, Mark, Nd, Pc and Join_Control.

    Built from the Unicode general categories (L*, M*, Nd, Nl, Pc, U+200C,
    U+200D) plus the Other_Alphabetic symbols that are neither letters nor marks
    (the circled and squared Latin letters). The corpus pins it; what this SDK
    accepts is decided by :func:`validate_kref`, not by this class.
    """
    category = unicodedata.category(ch)
    return (
        category[0] in "LM"
        or category in ("Nd", "Nl", "Pc")
        or ch in "‌‍"
        or any(first <= ord(ch) <= last for first, last in _OTHER_ALPHABETIC_SYMBOLS)
    )


def _has_control(text: str) -> bool:
    return any(unicodedata.category(ch) == "Cc" for ch in text)


def _byte_len(text: str) -> int:
    return len(text.encode("utf-8", "surrogatepass"))


def _segment_ok(segment: str) -> bool:
    return (
        bool(segment)
        and _is_word(segment[0])
        and all(_is_word(ch) or ch in ".-" for ch in segment[1:])
    )


def _path_shapes(base: str) -> Tuple[str, ...]:
    """Every namespace whose path rule ``base`` satisfies, in resolver order.

    The order is ``root_item``, ``item``, ``space``, ``project``: the order the
    kernel parser and the resolver try them in.
    """
    if (
        not base
        or _byte_len(base) > MAX_KREF_BYTES
        or ".." in base
        or _has_control(base)
    ):
        return ()
    segments = base.split("/")
    if len(segments) > MAX_KREF_SEGMENTS or not all(_segment_ok(s) for s in segments):
        return ()
    name, dot, kind = segments[-1].rpartition(".")
    names_an_item = bool(dot) and bool(name) and bool(kind)
    count = len(segments)
    shapes = []
    if count == 2 and names_an_item:
        shapes.append("root_item")
    if count >= 3 and names_an_item:
        shapes.append("item")
    if count >= 2:
        shapes.append("space")
    if count == 1:
        shapes.append("project")
    return tuple(shapes)


def _valid_tag(text: str) -> bool:
    return (
        bool(text)
        and _byte_len(text) <= MAX_TAG_BYTES
        and '"' not in text
        and "\\" not in text
        and not _has_control(text)
    )


def _valid_artifact_name(text: str) -> bool:
    return (
        bool(text)
        and _byte_len(text) <= MAX_ARTIFACT_NAME_BYTES
        and all(ch.isascii() and (ch.isalnum() or ch in "._-") for ch in text)
    )


def _read_revision(text: str) -> Optional[int]:
    """A revision number: ASCII digits, no leading zero, 1..=u64::MAX.

    ``u64::MAX`` has 20 digits, so a longer digit string is out of range and is
    never converted: ``int()`` refuses strings of thousands of digits, and the
    answer would be ``None`` anyway.
    """
    if (
        text
        and len(text) <= _MAX_REVISION_DIGITS
        and text[0] != "0"
        and all(ch in "0123456789" for ch in text)
    ):
        number = int(text)
        if number <= _MAX_REVISION:
            return number
    return None


def _read_query(query: Optional[str]):
    """Return ``(error_class, revision, tag, artifact)`` for the text after ``?``."""
    if query is None:
        return None, None, None, None
    slots: Dict[str, Optional[str]] = {"r": None, "t": None, "a": None}
    for pair in query.split("&"):
        key, equals, value = pair.partition("=")
        if not equals:
            # A tag holding '&' leaves a pair without '=' behind.
            error = "tag_reserved_char" if slots["t"] is not None else "query_pair"
            return error, None, None, None
        if key not in slots:
            return "unknown_key", None, None, None
        if slots[key] is not None:
            return "duplicate_key", None, None, None
        slots[key] = value
    r, t, a = slots["r"], slots["t"], slots["a"]
    revision: Optional[int] = None
    tag: Optional[str] = None
    if r is not None and t is not None:
        return "r_and_t", None, None, None
    if r == "latest":
        tag = "latest"
    elif r is not None:
        revision = _read_revision(r)
        if revision is None:
            return "revision_number", None, None, None
    elif t is not None:
        if not _valid_tag(t):
            return "tag", None, None, None
        tag = t
    artifact: Optional[str] = None
    if a is not None:
        if (revision is None and tag is None) or not _valid_artifact_name(a):
            return "artifact", None, None, None
        artifact = a
    return None, revision, tag, artifact


# What kumiho-server trims from a GetItem parent path: Rust ``char::is_whitespace``.
_SERVER_WHITESPACE = (
    "\t\n\x0b\x0c\r \x85\xa0        "
    "        　"
)


def _server_normalize_space_path(path: str) -> str:
    """kumiho-server ``normalize_space_path`` (``src/item.rs:14-31``)."""
    trimmed = path.strip(_SERVER_WHITESPACE)
    if not trimmed:
        return "/"
    without_trailing = trimmed.rstrip("/")
    if not without_trailing:
        return "/"
    without_leading = without_trailing.lstrip("/")
    if not without_leading:
        return "/"
    return "/" + without_leading


def _server_item_key(parent_path: str, item_name: str, kind: str) -> str:
    """The kref string kumiho-server matches for a ``GetItem`` request.

    ``src/item.rs:443-449``: the normalized parent path without its leading
    ``/``, then ``/``, the name, ``.`` and the kind. Two requests reach the
    same node exactly when they build the same string.
    """
    base = _server_normalize_space_path(parent_path).lstrip("/")
    if not base:
        return f"kref://{item_name}.{kind}"
    return f"kref://{base}/{item_name}.{kind}"


@dataclass(frozen=True)
class KrefParts:
    """A kref read once: the textual split now, the kernel's reading on demand.

    The textual split (``path``, ``parent``, ``leaf``, ``leaf_name``,
    ``leaf_kind``) is cut when the value is created and is independent of the
    kernel's verdict. It is what :meth:`get_item_request` uses, so a kref this
    SDK passes through to the backend (for example ``kref://p/s/x.k?r=0``)
    still yields its request.

    The kernel's reading (``valid``, ``error_class``, ``base``, ``shapes`` and
    the fields below) follows ``spec/kref/README.md``. It is computed the first
    time one of those attributes is read, and never raises. A kref the kernel
    refuses has ``error_class`` set and no reading: ``base`` and every field are
    ``None`` and ``shapes`` is empty.

    ``item_name``, ``kind`` and ``is_project_root_item`` describe the *first*
    shape the base satisfies, in the order ``root_item``, ``item``, ``space``,
    ``project``; ``item_name`` and ``kind`` are ``None`` when that shape is a
    space or a project.
    """

    uri: str
    path: str
    parent: Optional[str]
    leaf: Optional[str]
    leaf_name: Optional[str]
    leaf_kind: Optional[str]

    @cached_property
    def _kernel(self):
        """``(error_class, base, shapes, fields)`` from :func:`_read`, once."""
        return _read(self.uri)

    @property
    def error_class(self) -> Optional[str]:
        """The kernel's refusal class, or ``None`` when it accepts the kref."""
        return self._kernel[0]

    @property
    def base(self) -> Optional[str]:
        """The text between the scheme and the first ``?``, when the kernel accepts it."""
        return self._kernel[1]

    @property
    def shapes(self) -> Tuple[str, ...]:
        """Every namespace the base satisfies, in resolver order."""
        return self._kernel[2]

    @property
    def project(self) -> Optional[str]:
        return self._kernel[3]["project"]

    @property
    def space_path(self) -> Optional[Tuple[str, ...]]:
        return self._kernel[3]["space_path"]

    @property
    def item_name(self) -> Optional[str]:
        return self._kernel[3]["item_name"]

    @property
    def kind(self) -> Optional[str]:
        return self._kernel[3]["kind"]

    @property
    def is_project_root_item(self) -> Optional[bool]:
        return self._kernel[3]["is_project_root_item"]

    @property
    def revision(self) -> Optional[int]:
        return self._kernel[3]["revision"]

    @property
    def tag(self) -> Optional[str]:
        return self._kernel[3]["tag"]

    @property
    def artifact(self) -> Optional[str]:
        return self._kernel[3]["artifact"]

    @property
    def valid(self) -> bool:
        """Whether the kumiho-db kernel accepts this kref."""
        return self.error_class is None

    def get_item_tuple(self) -> Tuple[str, str, str]:
        """The grammar's ``GetItem`` split ``(parent_path, item_name, kind)``.

        The parent path is ``/`` plus everything before the LAST ``/`` of the
        path, so it holds the project and every nested space. The leaf after
        it is split at its LAST ``.``: item names may contain dots, kinds never
        do. The query is dropped. This is the corpus field ``get_item_tuple``;
        the request the client sends is :meth:`get_item_request`.

        It depends on the text only, never on the kernel's verdict, so a kref
        the backend should judge (``?r=0``, the legacy ``kref:///space/x.k``
        spelling) is still split.

        Raises:
            ValueError: If the path has no ``/`` or its leaf has no ``.``. A
                leaf without a dot (``kref://p/s.v1/x``) names a space, not an
                item.
        """
        if self.parent is None or self.leaf is None:
            raise ValueError(f"Invalid item kref format: {self.uri}")
        if self.leaf_name is None or self.leaf_kind is None:
            raise ValueError(f"Invalid item name.kind format: {self.leaf}")
        return f"/{self.parent}", self.leaf_name, self.leaf_kind

    def get_item_request(self) -> Tuple[str, str, str]:
        """The ``GetItem`` request ``(parent_path, item_name, kind)`` to send.

        This is :meth:`get_item_tuple`, except where kumiho-server would turn
        it into a different node than the request a7f155e sent for the same
        kref. The server rebuilds ``parent/name.kind`` after
        ``normalize_space_path``, which trims whitespace and ``/`` from the
        parent: a space segment that ends in whitespace (``kref://p/s /x.k``)
        or an empty trailing segment (``kref://p//x.k``) would be moved to the
        space ``/p/s`` or ``/p``. For those krefs, which only a server-returned
        item kref can be (the client validators refuse them), the request keeps
        a7f155e's shape: the project as the parent, the text between the
        project and the last ``.`` as the name, and the text after it as the
        kind. That shape names the node the kref spells.

        Raises:
            ValueError: As :meth:`get_item_tuple`.
        """
        split = self.get_item_tuple()
        project, _, rest = self.path.partition("/")
        kind = split[2]
        a7f155e_shape = (f"/{project}", rest[: -(len(kind) + 1)], kind)
        if _server_item_key(*split) == _server_item_key(*a7f155e_shape):
            return split
        return a7f155e_shape


_NO_READING = dict(
    project=None,
    space_path=None,
    item_name=None,
    kind=None,
    is_project_root_item=None,
    revision=None,
    tag=None,
    artifact=None,
)


def _read(uri: str):
    """The kernel's verdict and reading: ``(error_class, base, shapes, fields)``."""
    if not uri.startswith(_SCHEME):
        return "scheme", None, (), _NO_READING
    rest = uri[len(_SCHEME):]
    base, question, query_text = rest.partition("?")
    query = query_text if question else None
    if "#" in rest or "%" in rest:
        in_tag = query is not None and any(
            pair.startswith("t=") and ("#" in pair[2:] or "%" in pair[2:])
            for pair in query.split("&")
        )
        error = "tag_reserved_char" if in_tag else "fragment_or_percent"
        return error, None, (), _NO_READING
    shapes = _path_shapes(base)
    if not shapes:
        return "path", None, (), _NO_READING
    error, revision, tag, artifact = _read_query(query)
    if error:
        return error, None, (), _NO_READING

    segments = base.split("/")
    reading = dict(
        project=segments[0],
        space_path=(),
        item_name=None,
        kind=None,
        is_project_root_item=False,
        revision=revision,
        tag=tag,
        artifact=artifact,
    )
    first = shapes[0]
    if first in ("item", "root_item"):
        name, _, kind = segments[-1].rpartition(".")
        reading.update(
            space_path=tuple(segments[1:-1]),
            item_name=name,
            kind=kind,
            is_project_root_item=first == "root_item",
        )
    elif first == "space":
        reading.update(space_path=tuple(segments[1:]))
    return None, base, shapes, reading


def parse_kref(uri: str) -> KrefParts:
    """Parse ``uri`` once into a :class:`KrefParts`.

    Never raises: a string the kernel refuses comes back with ``error_class``
    set (one of ``scheme``, ``fragment_or_percent``, ``tag_reserved_char``,
    ``path``, ``query_pair``, ``unknown_key``, ``duplicate_key``, ``r_and_t``,
    ``revision_number``, ``tag``, ``artifact``). The kernel's reading is
    computed lazily, the first time one of its attributes is read.

    Example::

        >>> parts = parse_kref("kref://p/a/b/my.file.k?r=2")
        >>> parts.get_item_request()
        ('/p/a/b', 'my.file', 'k')
        >>> parts.revision
        2
    """
    lexical = _lexical(uri)
    return KrefParts(
        uri=uri,
        path=lexical.path,
        parent=lexical.parent,
        leaf=lexical.leaf,
        leaf_name=lexical.leaf_name,
        leaf_kind=lexical.leaf_kind,
    )


class Kref(str):
    """A Kumiho Artifact Reference (URI-based unique identifier).

    Kref is a subclass of ``str``, so it behaves like a string but provides
    utility methods for parsing and extracting components from the URI.

    The kref format is::

        kref://project/space/item.kind?r=REVISION&a=ARTIFACT

    Attributes:
        uri (str): The URI string (for backward compatibility).

    Example::

        from kumiho import Kref

        # Create from string
        kref = Kref("kref://my-project/assets/hero.model?r=2")

        # Use as string (since Kref extends str)
        print(kref)  # kref://my-project/assets/hero.model?r=2

        # Parse components
        print(kref.get_space())    # "my-project/assets"
        print(kref.get_revision()) # 2

        # Compare with strings
        if kref == "kref://my-project/assets/hero.model?r=2":
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
            >>> kref = Kref("kref://project/space/item.kind?r=1")
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
    def parts(self) -> KrefParts:
        """The kref read once by :func:`parse_kref`.

        Returns:
            KrefParts: The kernel's reading of this kref plus its textual split.
            ``parts.get_item_request()`` is the ``GetItem`` request for it.

        Example:
            >>> Kref("kref://project/models/hero.v2.model").parts.get_item_request()
            ('/project/models', 'hero.v2', 'model')
        """
        return parse_kref(str(self))

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
            str: The path (e.g., "project/space/item.kind").

        Example:
            >>> Kref("kref://project/models/hero.model?r=1").get_path()
            'project/models/hero.model'
        """
        return _lexical(self).path

    def get_project(self) -> str:
        """Extract the project name from the URI.

        Returns the first path component (project name).

        Returns:
            str: The project name (e.g., "my-project").

        Example:
            >>> Kref("kref://my-project/models/hero.model").get_project()
            'my-project'
        """
        path = self.get_path()
        if "/" not in path:
            return path
        return path.split("/", 1)[0]

    def get_space(self) -> str:
        """Extract the space path from the URI (without project).

        Returns the path between project and item name.

        Returns:
            str: The space path (e.g., "models" or "models/characters").

        Example:
            >>> Kref("kref://project/models/hero.model").get_space()
            'models'
            >>> Kref("kref://project/models/characters/hero.model").get_space()
            'models/characters'
        """
        path = self.get_path()
        if "/" not in path:
            return ""
        # Remove project (first segment) and item (last segment)
        parts = path.split("/")
        if len(parts) <= 2:
            # Only project/item.kind - no space
            return ""
        # Return everything between project and item
        return "/".join(parts[1:-1])

    def get_item_name(self) -> str:
        """Extract the item name with kind from the URI.

        Returns:
            str: The item name including kind (e.g., "hero.model").

        Example:
            >>> Kref("kref://project/models/hero.model").get_item_name()
            'hero.model'
        """
        leaf = _lexical(self).leaf
        return "" if leaf is None else leaf

    def get_kind(self) -> str:
        """Extract the item kind from the URI.

        Returns:
            str: The item kind (e.g., "model", "texture").

        Example:
            >>> Kref("kref://project/models/hero.model").get_kind()
            'model'
        """
        # Item names may contain dots; the kind is the text after the last one.
        kind = _lexical(self).leaf_kind
        return "" if kind is None else kind

    def get_revision(self) -> int:
        """Extract the revision number from the URI query string.

        Returns:
            int: The revision number, or 1 if not specified.

        Example:
            >>> Kref("kref://project/models/hero.model?r=3").get_revision()
            3
            >>> Kref("kref://project/models/hero.model").get_revision()
            1
        """
        match = re.search(r'\?r=(\d+)', self)
        return int(match.group(1)) if match else 1

    def get_artifact_name(self) -> Optional[str]:
        """Extract the artifact name from the URI query string.

        Returns:
            Optional[str]: The artifact name if present, None otherwise.

        Example:
            >>> Kref("kref://project/models/hero.model?r=1&a=mesh").get_artifact_name()
            'mesh'
            >>> Kref("kref://project/models/hero.model?r=1").get_artifact_name()
            None
        """
        match = re.search(r'&a=([^&]+)', self)
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