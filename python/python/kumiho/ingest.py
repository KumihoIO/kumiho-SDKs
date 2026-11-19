"""Typed inputs and receipts for ``BatchIngest`` and ``GetMutationCapabilities``.

``BatchIngest`` writes memories (revisions with their artifacts), the edges
among them or to existing revisions, and tags on them in **one atomic server
command** — one transaction, one commit — instead of one call per edge and per
tag. Every element is keyed under the request's idempotency prefix, so sending
the same request again after a lost reply replays what already committed and
commits only what is new.

It is a kumiho-db RPC. kumiho-server (Community Edition) does not implement
it; the call then raises :class:`BatchIngestUnsupportedError`, and
:meth:`kumiho.client._Client.get_mutation_capabilities` lets a caller check
first.

Everything here is a plain frozen dataclass. The ``Client.batch_ingest`` /
:func:`kumiho.batch_ingest` entry points turn them into protobuf and the
response back into :class:`BatchIngestResult`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import grpc

from .kref import Kref
from .revision import Revision

__all__ = [
    "ArtifactInput",
    "BatchIngestLimits",
    "BatchIngestResult",
    "BatchIngestUnsupportedError",
    "BatchIngestValidationError",
    "DEFAULT_LIMITS",
    "EdgeReceipt",
    "ElementFailure",
    "IngestEdge",
    "IngestTag",
    "KrefRef",
    "MutationCapabilities",
    "RevisionInput",
    "RowRef",
    "TagReceipt",
]


# --- errors ------------------------------------------------------------------


class BatchIngestValidationError(ValueError):
    """The request was refused client-side, before any network call.

    The server reports a bad row, edge or tag by position and still commits the
    rest of the request, so everything it would reject per element is refused
    here for the whole request instead of writing a partial result.
    """


class BatchIngestUnsupportedError(grpc.RpcError):
    """The server does not implement ``BatchIngest`` (gRPC ``UNIMPLEMENTED``).

    ``BatchIngest`` is a kumiho-db RPC; kumiho-server (CE) and older servers
    answer ``UNIMPLEMENTED``. Fall back to :func:`kumiho.batch_create_revisions`
    plus individual edge and tag calls, or check
    :meth:`~kumiho.client._Client.get_mutation_capabilities` first.

    It is a :class:`grpc.RpcError` so handlers written for the other batch
    calls still catch it, and exposes ``code()`` / ``details()`` like one.
    """

    def __init__(self, message: str, *, cause: Optional[grpc.RpcError] = None) -> None:
        super().__init__(message)
        self.message = message
        self.__cause__ = cause

    def code(self) -> grpc.StatusCode:
        return grpc.StatusCode.UNIMPLEMENTED

    def details(self) -> str:
        return self.message

    def __str__(self) -> str:
        return self.message


# --- limits ------------------------------------------------------------------


@dataclass(frozen=True)
class BatchIngestLimits:
    """Request-size limits of kumiho-db's ``BatchIngest``.

    The defaults are the server's. ``GetMutationCapabilities`` carries feature
    flags, never numbers, so a caller who knows an operator raised or lowered
    them passes its own instance as ``limits=``.

    A request is bounded by what its atomic command may read, not only by
    count: ``reads_per_revision`` per revision plus ``reads_per_edge_or_tag``
    per edge or tag must stay within ``read_budget``.
    """

    max_revisions: int = 200
    max_edges: int = 500
    max_tags: int = 500
    read_budget: int = 32_000
    reads_per_revision: int = 60
    reads_per_edge_or_tag: int = 32

    def read_estimate(self, revisions: int, edges: int, tags: int) -> int:
        return (
            self.reads_per_revision * revisions
            + self.reads_per_edge_or_tag * (edges + tags)
        )


DEFAULT_LIMITS = BatchIngestLimits()


# --- inputs ------------------------------------------------------------------


@dataclass(frozen=True)
class ArtifactInput:
    """An artifact attached to a created revision, in the same transaction.

    ``name`` must be kref-safe (``[A-Za-z0-9._-]+``) and unique within the row;
    at most one artifact per row may set ``is_default``.
    """

    name: str
    location: str
    metadata: Mapping[str, str] = field(default_factory=dict)
    is_default: bool = False


@dataclass(frozen=True)
class RevisionInput:
    """One row: a revision of ``item_kref``, created with its item if missing.

    The parent space must already exist; a row under a missing one is rejected
    by position. Rows targeting the same item apply in request order.
    """

    item_kref: Union[str, Kref]
    metadata: Mapping[str, str] = field(default_factory=dict)
    embedding_text: str = ""
    artifacts: Sequence[ArtifactInput] = ()


@dataclass(frozen=True)
class RowRef:
    """The revision that ``revisions[index]`` of the same request creates."""

    index: int


@dataclass(frozen=True)
class KrefRef:
    """An existing revision named by number, e.g. ``kref://p/s/item.kind?r=3``.

    A tag selector (``?t=``) or an artifact is refused.
    """

    kref: Union[str, Kref]


EdgeEnd = Union[RowRef, KrefRef, int, str, Kref]


@dataclass(frozen=True)
class IngestEdge:
    """A directed, typed edge between two revisions.

    Each end is a :class:`RowRef` (a revision created by this request), a
    :class:`KrefRef` (an existing revision), or shorthand: an ``int`` is a row
    index and a ``str`` / :class:`~kumiho.kref.Kref` an existing revision kref.
    ``edge_type`` must match ``^[A-Z][A-Z0-9_]{0,49}$``.
    """

    source: EdgeEnd
    target: EdgeEnd
    edge_type: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class IngestTag:
    """A tag on the revision that ``revisions[row_index]`` creates.

    ``latest`` is system-managed and refused; ``published`` publishes and
    freezes the revision.
    """

    row_index: int
    tag: str


# --- results -----------------------------------------------------------------


@dataclass(frozen=True)
class EdgeReceipt:
    """What happened to one edge."""

    #: False when the edge was already active (the assert was a no-op).
    created: bool
    #: True when this edge was committed by an earlier request with the same prefix.
    replayed: bool


@dataclass(frozen=True)
class TagReceipt:
    """What happened to one tag."""

    #: The revision number the tag points at now (0 when it points nowhere).
    revision_number: int
    tag_version: int
    #: False when the tag already pointed there.
    changed: bool
    replayed: bool


@dataclass(frozen=True)
class ElementFailure:
    """A row, edge or tag the server rejected by position while committing the rest."""

    kind: str  # "revision" | "edge" | "tag"
    index: int
    reason: str


@dataclass(frozen=True)
class BatchIngestResult:
    """Receipts of one ``BatchIngest``, positional and 1:1 with the request.

    A rejected element is ``None`` in its list and appears in ``failures``.
    """

    revisions: List[Optional[Revision]]
    edges: List[Optional[EdgeReceipt]]
    tags: List[Optional[TagReceipt]]
    failures: List[ElementFailure] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when every revision, edge and tag was accepted."""
        return not self.failures


@dataclass(frozen=True)
class MutationCapabilities:
    """The native atomic mutations a server implements.

    A server that does not implement ``GetMutationCapabilities`` is reported
    with every flag False and an empty ``contract_version``.
    """

    batch_ingest: bool = False
    batch_expected_latest_revision: bool = False
    transactional_idempotency_fingerprint: bool = False
    atomic_derived_from_edges: bool = False
    contract_version: str = ""


# --- validation --------------------------------------------------------------

_EDGE_NAME = re.compile(r"[A-Z][A-Z0-9_]{0,49}")
_REVISION_KREF_QUERY = re.compile(r"r=[1-9][0-9]*")


def _uri(value: Union[str, Kref]) -> str:
    return value.uri if isinstance(value, Kref) else str(value)


def _end(end: EdgeEnd) -> Union[RowRef, KrefRef]:
    if isinstance(end, (RowRef, KrefRef)):
        return end
    if isinstance(end, bool):
        raise BatchIngestValidationError("an edge end cannot be a bool")
    if isinstance(end, int):
        return RowRef(end)
    return KrefRef(end)


def _artifact(spec: Union[ArtifactInput, Mapping[str, Any]]) -> ArtifactInput:
    if isinstance(spec, ArtifactInput):
        return spec
    return ArtifactInput(
        name=spec.get("name", ""),
        location=spec.get("location", ""),
        metadata=spec.get("metadata") or {},
        is_default=bool(spec.get("is_default", spec.get("default", False))),
    )


def _revision(index: int, spec: Union[RevisionInput, Mapping[str, Any]]) -> RevisionInput:
    if isinstance(spec, RevisionInput):
        return spec
    if spec.get("item_kref") is None:
        raise BatchIngestValidationError(f"revisions[{index}] is missing 'item_kref'")
    return RevisionInput(
        item_kref=spec["item_kref"],
        metadata=spec.get("metadata") or {},
        embedding_text=spec.get("embedding_text", ""),
        artifacts=tuple(_artifact(a) for a in spec.get("artifacts") or ()),
    )


def _check_revision(index: int, revision: RevisionInput) -> None:
    uri = _uri(revision.item_kref)
    if not uri.startswith("kref://") or "?" in uri:
        raise BatchIngestValidationError(
            f"revisions[{index}].item_kref must be an item kref without a "
            f"selector (got {uri!r})"
        )
    names = set()
    defaults = 0
    for artifact in revision.artifacts:
        if not artifact.name or not re.fullmatch(r"[A-Za-z0-9._-]+", artifact.name):
            raise BatchIngestValidationError(
                f"revisions[{index}] artifact name {artifact.name!r} must be "
                f"non-empty and kref-safe ([A-Za-z0-9._-]+)"
            )
        if not artifact.location:
            raise BatchIngestValidationError(
                f"revisions[{index}] artifact {artifact.name!r} needs a location"
            )
        if artifact.name in names:
            raise BatchIngestValidationError(
                f"revisions[{index}] has a duplicate artifact name {artifact.name!r}"
            )
        names.add(artifact.name)
        defaults += bool(artifact.is_default)
    if defaults > 1:
        raise BatchIngestValidationError(
            f"revisions[{index}] sets is_default on more than one artifact"
        )


def _check_end(where: str, end: Union[RowRef, KrefRef], row_count: int) -> str:
    if isinstance(end, RowRef):
        if not 0 <= end.index < row_count:
            raise BatchIngestValidationError(
                f"{where} names row {end.index}, which is not in the request"
            )
        return f"row:{end.index}"
    uri = _uri(end.kref)
    if not uri.startswith("kref://"):
        raise BatchIngestValidationError(f"{where} must be a kref (got {uri!r})")
    _, _, query = uri.partition("?")
    if not _REVISION_KREF_QUERY.fullmatch(query):
        raise BatchIngestValidationError(
            f"{where} must name an existing revision by number "
            f"(...?r=<positive integer>), not a tag or artifact (got {uri!r})"
        )
    return f"kref:{uri}"


def normalize_and_check(
    revisions: Sequence[Union[RevisionInput, Mapping[str, Any]]],
    edges: Sequence[IngestEdge],
    tags: Sequence[IngestTag],
    idempotency_prefix: str,
    limits: BatchIngestLimits,
) -> Tuple[List[RevisionInput], List[IngestEdge], List[IngestTag]]:
    """Refuse any request the server would refuse or partly reject.

    Returns the inputs with row dicts and edge-end shorthands normalized.
    Raises :class:`BatchIngestValidationError`.
    """
    if not isinstance(idempotency_prefix, str) or not idempotency_prefix.strip():
        raise BatchIngestValidationError(
            "idempotency_prefix is required and must be non-empty: every row, "
            "edge and tag is keyed '{prefix}:{index}'"
        )
    for name, count, maximum in (
        ("revisions", len(revisions), limits.max_revisions),
        ("edges", len(edges), limits.max_edges),
        ("tags", len(tags), limits.max_tags),
    ):
        if count > maximum:
            raise BatchIngestValidationError(
                f"{name} is {count}, over the limit of {maximum} per request; "
                f"split the request"
            )
    estimate = limits.read_estimate(len(revisions), len(edges), len(tags))
    if estimate > limits.read_budget:
        raise BatchIngestValidationError(
            f"the request would read an estimated {estimate} records, over the "
            f"atomic command's budget of {limits.read_budget} "
            f"({limits.reads_per_revision} per revision, "
            f"{limits.reads_per_edge_or_tag} per edge or tag); split the request"
        )

    rows = [_revision(i, spec) for i, spec in enumerate(revisions)]
    for index, row in enumerate(rows):
        _check_revision(index, row)

    checked_edges: List[IngestEdge] = []
    for index, edge in enumerate(edges):
        if not _EDGE_NAME.fullmatch(edge.edge_type or ""):
            raise BatchIngestValidationError(
                f"edges[{index}].edge_type must match ^[A-Z][A-Z0-9_]{{0,49}}$ "
                f"(got {edge.edge_type!r})"
            )
        source, target = _end(edge.source), _end(edge.target)
        a = _check_end(f"edges[{index}].source", source, len(rows))
        b = _check_end(f"edges[{index}].target", target, len(rows))
        if a == b:
            raise BatchIngestValidationError(
                f"edges[{index}] connects an endpoint to itself"
            )
        checked_edges.append(IngestEdge(source, target, edge.edge_type, edge.metadata))

    for index, tag in enumerate(tags):
        if not tag.tag:
            raise BatchIngestValidationError(f"tags[{index}].tag is empty")
        if tag.tag == "latest":
            raise BatchIngestValidationError(
                f"tags[{index}]: 'latest' is system-managed and cannot be set"
            )
        if not 0 <= tag.row_index < len(rows):
            raise BatchIngestValidationError(
                f"tags[{index}] names row {tag.row_index}, which is not in the request"
            )
    return rows, checked_edges, list(tags)
