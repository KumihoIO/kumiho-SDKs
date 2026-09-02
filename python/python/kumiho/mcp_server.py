"""Kumiho MCP Server - Model Context Protocol integration for Kumiho Cloud.

This module provides an MCP (Model Context Protocol) server that exposes
Kumiho Cloud functionality to AI assistants like GitHub Copilot, Claude,
and other MCP-compatible clients.

The server enables AI assistants to:
- Query and navigate asset graphs
- Analyze dependencies and impact
- Search for items across projects
- Track AI lineage and provenance
- Manage revisions and artifacts

Usage:
    Run as a standalone server::

        python -m kumiho.mcp_server

    Or use the CLI entry point::

        kumiho-mcp

Configuration:
    The MCP server uses the same authentication as the Kumiho SDK.
    Run ``kumiho-auth login`` first to cache credentials.

Environment Variables:
    KUMIHO_MCP_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR). Default: INFO
    KUMIHO_MCP_TOOL_PROFILE: Which tool surface to expose — "full" (default,
        every tool) or "connector" (the curated hosted set). Overridden by an
        explicit ``profile`` argument to :func:`create_mcp_server`.
    KUMIHO_MCP_HOSTED: Set to "1" when this process serves many tenants. Stops
        the server touching process-global user state — no ``os.environ``
        writes, no ``~/.kumiho`` reads, no local artifact files — and makes
        every cache tenant-scoped. See :mod:`kumiho.request_context`.

Example MCP client configuration (VS Code settings.json)::

    {
        "mcp": {
            "servers": {
                "kumiho": {
                    "command": "kumiho-mcp"
                }
            }
        }
    }
"""

import asyncio
import hashlib
import json
import logging
import math
import os
import re
import sys
import threading
import time
import traceback
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.lowlevel.helper_types import ReadResourceContents
    from mcp.types import (
        Tool,
        TextContent,
        TextResourceContents,
        Resource,
        ResourceTemplate,
        Prompt,
        PromptMessage,
        PromptArgument,
        GetPromptResult,
        CallToolResult,
        ListToolsResult,
        ListResourcesResult,
        ListPromptsResult,
        ReadResourceResult,
        INVALID_PARAMS,
        INTERNAL_ERROR,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# mcp 2.0 did not delete handler registration, it moved it: the low-level
# ``Server`` lost the six decorators this module used and gained matching
# ``on_*`` constructor keywords (kumiho-SDKs#145). No single call shape works on
# both, so ``create_mcp_server`` branches on this flag.
#
# Detect by capability, not by version. ``importlib.metadata.version("mcp")``
# reports a number rather than a shape: it needs a version-to-shape table that
# goes stale on every upstream move, and it lies outright for editable installs,
# forks and vendored copies (PackageNotFoundError, no dist-info).
_MCP_HAS_DECORATORS = MCP_AVAILABLE and hasattr(Server, "list_tools")


def _server_accepts_instructions() -> bool:
    """Whether the installed ``Server`` takes an ``instructions`` keyword.

    Server instructions reach the client in the ``initialize`` result, which is
    the only channel a *remote* connector has for the memory protocol (there is
    no skill and no hook out there). Probed rather than assumed, for the same
    reason as ``_MCP_HAS_DECORATORS``: a version table goes stale, and lies
    outright for vendored copies.
    """
    if not MCP_AVAILABLE:
        return False
    try:
        import inspect

        return "instructions" in inspect.signature(Server.__init__).parameters
    except (TypeError, ValueError):  # pragma: no cover - unintrospectable build
        return False


_SERVER_SUPPORTS_INSTRUCTIONS = _server_accepts_instructions()

# mcp 1.x's ``@server.call_tool()`` defaulted to validate_input=True and checked
# arguments against each tool's inputSchema before dispatch. mcp 2.0's low-level
# path has no equivalent, so the 2.x branch re-implements it — without this, the
# port serves happily while silently accepting malformed arguments for every
# tool. jsonschema is a hard dependency of both mcp majors; the guard only keeps
# a damaged install from turning a missing validator into a failure to boot.
try:
    import jsonschema as _jsonschema
except ImportError:  # pragma: no cover - jsonschema ships with mcp
    _jsonschema = None

# Kumiho imports
import grpc
import kumiho
from kumiho import (
    Project,
    ProjectDeletionImpact,
    Space,
    Item,
    Revision,
    Artifact,
    Edge,
    Kref,
    EdgeType,
    EdgeDirection,
    DEPENDS_ON,
    DERIVED_FROM,
    REFERENCED,
    CONTAINS,
    CREATED_FROM,
)
from kumiho.request_context import current_request, hosted_mode

# Configure logging
LOG_LEVEL = os.environ.get("KUMIHO_MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("kumiho.mcp")

# Optional privacy utilities (from kumiho-memory package)
try:
    from kumiho_memory.privacy import PIIRedactor, CredentialDetectedError
    _PRIVACY_AVAILABLE = True
except ImportError:
    _PRIVACY_AVAILABLE = False


# ---------------------------------------------------------------------------
# Hosted (multi-tenant) mode
# ---------------------------------------------------------------------------

# One stdio process serves exactly one user, so this module could treat the
# environment and its caches as private. A hosted deployment serves many
# tenants from one process, and every one of those assumptions becomes a
# cross-tenant leak. The two predicates below are the guards.
#
# ``_is_hosted`` is deliberately the OR of the two signals: a request context
# means a request is in flight *now*, while ``KUMIHO_MCP_HOSTED`` marks the
# whole process, so code that runs between requests (server construction,
# cache warming) still behaves defensively.


def _is_hosted() -> bool:
    """True when this process must not touch process-global user state."""
    return current_request() is not None or hosted_mode()


def _tenant_scope() -> str:
    """The cache namespace for the in-flight request; ``"local"`` when stdio."""
    ctx = current_request()
    return ctx.tenant_id if ctx is not None else "local"


# U+001F UNIT SEPARATOR: never appears in a tenant UUID, a project name or a
# space path, so a prefixed key cannot collide with a differently-scoped one.
_TENANT_KEY_SEP = "\x1f"


def _tenant_key(key: str) -> str:
    """Namespace a process-global cache key by the calling tenant.

    Every module-level cache in this file predates hosting and was keyed by
    project name alone. Two tenants routinely have a project called
    ``CognitiveMemory``, so an unprefixed key would serve tenant B the
    ``Project`` handle — and thus the gRPC channel and credentials — that
    tenant A cached.
    """
    return f"{_tenant_scope()}{_TENANT_KEY_SEP}{key}"


def _apply_auth_token_override(auth_token: str, tool_name: str) -> None:
    """Honour a caller-supplied ``auth_token`` argument — locally only.

    Two search tools accept an ``auth_token`` argument and used to publish it
    into ``os.environ["KUMIHO_AUTH_TOKEN"]``. On stdio that is merely blunt:
    one process, one user, and the override outlives the call. Hosted it is a
    credential swap visible to every other tenant's in-flight request, and a
    *persistent* one — the next request that falls back to the environment
    picks up whichever token happened to be written last.

    So hosted mode ignores the argument. The hosting layer already establishes
    the caller's identity from the verified bearer token and enters
    ``kumiho.use_client`` for the request; an argument-supplied token could
    only ever contradict it, and the contradiction would be an escalation
    attempt, not a configuration.
    """
    if not auth_token:
        return
    if _is_hosted():
        logger.warning(
            "Ignoring the auth_token argument to %s: in hosted mode the "
            "request's own credentials are authoritative.",
            tool_name,
        )
        return
    os.environ["KUMIHO_AUTH_TOKEN"] = auth_token


def _request_scoped_client() -> Any:
    """The client bound by ``kumiho.use_client``, or ``None``."""
    var = getattr(kumiho, "_client_context_var", None)
    return var.get() if var is not None else None


def _ensure_configured() -> bool:
    """Ensure Kumiho client is configured.

    Hosted mode takes a different path on purpose. ``auto_configure_from_
    discovery`` reads the *machine's* cached credentials from ``~/.kumiho``
    and installs the resulting client as the process-global default — exactly
    the two things a multi-tenant process must never do. The hosting layer has
    already built a client from the caller's verified token and entered
    ``kumiho.use_client``, so there is nothing to configure.

    When that binding is missing, this raises rather than degrading: the
    fallback would be to serve the *operator's* own graph to a remote caller,
    which is worse than a failed tool call.
    """
    if _is_hosted():
        if _request_scoped_client() is not None:
            return True
        raise RuntimeError(
            "Hosted mode is active but no request-scoped Kumiho client is "
            "bound. The hosting layer must wrap each request in "
            "kumiho.use_client(client); falling back to local credentials "
            "would serve the wrong tenant."
        )
    try:
        kumiho.auto_configure_from_discovery()
        return True
    except Exception as e:
        logger.warning(f"Auto-configure failed: {e}")
        return False


def _serialize_project(project: Project) -> Dict[str, Any]:
    """Serialize a Project to a JSON-friendly dict."""
    return {
        "project_id": project.project_id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "deprecated": project.deprecated,
        "allow_public": getattr(project, "allow_public", False),
    }


def _serialize_space(space: Space) -> Dict[str, Any]:
    """Serialize a Space to a JSON-friendly dict."""
    return {
        "path": space.path,
        "name": space.name,
        "type": space.type,
        "created_at": space.created_at,
        "author": space.author,
        "username": space.username,
        "metadata": dict(space.metadata) if space.metadata else {},
    }


def _serialize_item(item: Item) -> Dict[str, Any]:
    """Serialize an Item to a JSON-friendly dict."""
    return {
        "kref": item.kref.uri,
        "name": item.name,
        "item_name": item.item_name,
        "kind": item.kind,
        "created_at": item.created_at,
        "author": item.author,
        "username": item.username,
        "metadata": dict(item.metadata) if item.metadata else {},
        "deprecated": item.deprecated,
    }


def _serialize_revision(revision: Revision) -> Dict[str, Any]:
    """Serialize a Revision to a JSON-friendly dict."""
    metadata = dict(revision.metadata) if revision.metadata else {}
    # The server reserves the "type" metadata key and strips it from reads;
    # newer writes mirror it as "memory_type". Alias it back so legacy
    # consumers reading metadata["type"] keep working.
    if "memory_type" in metadata and "type" not in metadata:
        metadata["type"] = metadata["memory_type"]
    return {
        "kref": revision.kref.uri,
        "item_kref": revision.item_kref.uri,
        "number": revision.number,
        "latest": revision.latest,
        "tags": list(revision._cached_tags),
        "metadata": metadata,
        "created_at": revision.created_at,
        "author": revision.author,
        "username": revision.username,
        "deprecated": revision.deprecated,
        "published": revision.published,
        "default_artifact": revision.default_artifact,
    }


def _serialize_artifact(artifact: Artifact) -> Dict[str, Any]:
    """Serialize an Artifact to a JSON-friendly dict."""
    return {
        "kref": artifact.kref.uri,
        "name": artifact.name,
        "location": artifact.location,
        "revision_kref": artifact.revision_kref.uri,
        "created_at": artifact.created_at,
        "metadata": dict(artifact.metadata) if artifact.metadata else {},
    }


def _serialize_edge(edge: Edge) -> Dict[str, Any]:
    """Serialize an Edge to a JSON-friendly dict."""
    return {
        "source_kref": edge.source_kref.uri,
        "target_kref": edge.target_kref.uri,
        "edge_type": edge.edge_type,
        "metadata": dict(edge.metadata) if edge.metadata else {},
        "created_at": edge.created_at,
    }




def _parse_json_object(value: Any) -> Dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _stringify_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not metadata:
        return out
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, str):
            out[key] = value
        else:
            out[key] = json.dumps(value, ensure_ascii=True)
    return out


def _slugify(value: str, max_len: int = 48) -> str:
    # Delegates to the canonical Unicode-aware slug so non-Latin space/item
    # hints (Korean, CJK) no longer collapse to an empty slug.
    from kumiho._text import slugify

    return slugify(value, max_len)


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def _artifact_root() -> Path:
    """Resolve the local artifact root directory."""
    return Path(
        os.environ.get(
            "KUMIHO_MEMORY_ARTIFACT_ROOT",
            os.path.join(os.path.expanduser("~"), ".kumiho", "artifacts"),
        )
    )


def _write_memory_artifact(
    *,
    project: str,
    space_path: str,
    item_name: str,
    title: str,
    summary: str,
    user_text: str,
    assistant_text: str,
    memory_type: str,
) -> str:
    """Write a Markdown artifact for a memory entry and return the file path.

    Layout: {artifact_root}/{project}/{space_segments}/{item_name}.md

    Hosted mode writes nothing and returns ``""``. The root is
    ``~/.kumiho/artifacts`` on the *server's* filesystem, so hosted writes
    would drop one tenant's memory text into a directory shared by all of
    them, and then record that server-local path as an artifact location no
    remote caller can ever resolve. Both call sites treat an empty return as
    "no artifact", which is the correct outcome.
    """
    if _is_hosted():
        return ""
    root = _artifact_root()
    target_dir = root / project
    stripped = space_path.strip("/")
    # Remove project prefix from space_path to avoid duplication
    if stripped.startswith(f"{project}/"):
        stripped = stripped[len(project) + 1:]
    elif stripped == project:
        stripped = ""
    if stripped:
        segments = [seg for seg in stripped.split("/") if seg.strip()]
        target_dir = target_dir.joinpath(*segments)
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w\-]", "_", item_name)
    artifact_path = target_dir / f"{safe_name}.md"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f'title: "{title}"',
        f'type: "{memory_type}"',
        f'date: "{now}"',
        f'summary: "{summary}"',
        "---",
        "",
    ]
    if user_text:
        lines.extend([f"**User:** {user_text}", ""])
    if assistant_text:
        lines.extend([f"**Assistant:** {assistant_text}", ""])

    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    return str(artifact_path)


# ---------------------------------------------------------------------------
# In-process caches – avoid redundant gRPC round-trips within a session.
# ---------------------------------------------------------------------------

# Every key here goes through :func:`_tenant_key`. The values are live SDK
# handles bound to a client, i.e. to a tenant's credentials and gRPC channel —
# sharing one across tenants would hand tenant B tenant A's graph.

_project_cache: Dict[str, Project] = {}
_known_spaces: set = set()          # tenant-scoped normalized space paths already ensured
_bundle_cache: Dict[str, Item] = {} # tenant + space_path/bundle_slug -> bundle Item


def _get_project_cached(project_name: str) -> Project:
    """Return a cached Project, fetching (or creating) only on first call."""
    cache_key = _tenant_key(project_name)
    if cache_key in _project_cache:
        return _project_cache[cache_key]
    project_obj = kumiho.get_project(project_name)
    if not project_obj:
        project_obj = kumiho.create_project(project_name, description="AI Cognitive Memory")
    _project_cache[cache_key] = project_obj
    return project_obj


def _normalize_space_path(project_name: str, space_path: str) -> str:
    if not space_path:
        return f"/{project_name}"
    path = space_path.strip()
    if not path:
        return f"/{project_name}"
    if path.startswith("/"):
        trimmed = path.strip("/")
        if trimmed.startswith(f"{project_name}/") or trimmed == project_name:
            return f"/{trimmed}"
        return f"/{project_name}/{trimmed}"
    if path.startswith(f"{project_name}/") or path == project_name:
        return f"/{path}"
    return f"/{project_name}/{path}"


def _ensure_space_path(project: Project, space_path: str) -> str:
    normalized = _normalize_space_path(project.name, space_path)
    known_key = _tenant_key(normalized)
    if known_key in _known_spaces:
        return normalized
    parts = normalized.strip("/").split("/")
    parent = f"/{parts[0]}"
    created_any = False
    for segment in parts[1:]:
        try:
            project.create_space(segment, parent_path=parent)
            created_any = True
        except grpc.RpcError as exc:
            if exc.code() != grpc.StatusCode.ALREADY_EXISTS:
                raise
        parent = f"{parent.rstrip('/')}/{segment}"
    _known_spaces.add(known_key)
    # A new space invalidates the registry listing so the next hint resolves
    # against it (otherwise back-to-back stores wouldn't see each other's
    # freshly-created spaces within the cache TTL).
    if created_any:
        _invalidate_space_registry(project.name)
    return normalized


def _get_or_create_item(project: Project, space_path: str, item_name: str, kind: str) -> Item:
    try:
        return project.create_item(item_name, kind, parent_path=space_path)
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.ALREADY_EXISTS:
            return project.get_item(item_name, kind, parent_path=space_path)
        raise


# ---------------------------------------------------------------------------
# Memory kinds — the recommended write-time taxonomy
# ---------------------------------------------------------------------------

# The kinds tool_memory_store recommends. A policy item can widen this via a
# "memory_kinds" list in its policy JSON; an out-of-vocabulary kind is warned
# (not rejected) so the calling LLM is nudged away from ad-hoc taxonomies
# without breaking existing callers. "decision" is reserved for decision
# promotion (follow-up); "skill" and "space-profile" are written by
# kumiho-memory through its own paths but belong to the same vocabulary.
DEFAULT_MEMORY_KINDS: Tuple[str, ...] = (
    "conversation",
    "skill",
    "space-profile",
    "entity",
    "decision",
)


# ---------------------------------------------------------------------------
# Space registry — resolve a hint against existing spaces before creating
# ---------------------------------------------------------------------------

# Freeform space hints drift: "AI Memory" / "ai memory" arrive across
# sessions and would each mint a distinct Space, fragmenting both scoped
# recall and fulltext term statistics. Before creating a space from a *hint*
# (never an explicit space_path), the leaf segment is matched against
# existing sibling spaces — exact by default (which already unifies
# case/spacing via slugging). Opt-in stem matching (plural/gerund) also
# unifies "benchmarks"/"benchmarking" but risks false-merges
# ("meeting"->"meet"), so it stays behind an env flag until measured. A
# unified variant is recorded on the canonical space's "memory_aliases"
# attribute for auditability.

_SPACE_REGISTRY_TTL_SECONDS = 60.0

# project name -> (fetched_at_monotonic, {normalized space paths}). Guarded
# by _space_registry_lock since stores can run concurrently.
_space_registry_cache: Dict[str, Tuple[float, Set[str]]] = {}
_space_registry_lock = threading.Lock()


def _space_registry_enabled() -> bool:
    return os.environ.get("KUMIHO_MEMORY_SPACE_REGISTRY", "1").strip() != "0"


def _space_stem_match_enabled() -> bool:
    return os.environ.get("KUMIHO_MEMORY_SPACE_STEM_MATCH", "0").strip() == "1"


def _stem_slug(segment: str) -> str:
    """Conservative stem for slug comparison: strips a plural/gerund suffix
    only when a reasonable stem length remains. Lexical and English-only —
    used only when stem matching is explicitly enabled, since it can
    false-merge distinct words ("meeting"->"meet")."""
    for suffix in ("ing", "es", "s"):
        if segment.endswith(suffix) and len(segment) - len(suffix) >= 4:
            return segment[: -len(suffix)]
    return segment


def _existing_space_paths(project: Project) -> Set[str]:
    """All space paths in *project*, cached briefly per process."""
    now = time.monotonic()
    cache_key = _tenant_key(project.name)
    with _space_registry_lock:
        cached = _space_registry_cache.get(cache_key)
        if cached and now - cached[0] < _SPACE_REGISTRY_TTL_SECONDS:
            return cached[1]
    # List outside the lock (network call); last writer wins on the cache.
    paths = {space.path for space in project.get_spaces(recursive=True)}
    with _space_registry_lock:
        _space_registry_cache[cache_key] = (now, paths)
    return paths


def _invalidate_space_registry(project_name: str) -> None:
    with _space_registry_lock:
        _space_registry_cache.pop(_tenant_key(project_name), None)


def _record_space_alias(project: Project, canonical_path: str, alias_slug: str) -> None:
    """Best-effort: append *alias_slug* to the canonical space's
    "memory_aliases" attribute so unifications stay auditable server-side."""
    try:
        space = project.get_space(canonical_path)
        existing = space.get_attribute("memory_aliases") or ""
        aliases = [a for a in (s.strip() for s in existing.split(",")) if a]
        if alias_slug not in aliases:
            aliases.append(alias_slug)
            space.set_attribute("memory_aliases", ",".join(aliases))
    except Exception:  # noqa: BLE001 - alias bookkeeping must never fail a store
        logger.debug("Failed to record space alias %s -> %s", alias_slug, canonical_path)


def _resolve_space_hint_path(project: Project, space_path: str) -> str:
    """Resolve a hint-derived space path against existing spaces.

    Returns a (normalized) path of an existing space when the leaf segment
    matches a sibling exactly or by stem; otherwise returns the normalized
    input unchanged for the caller to create.
    """
    normalized = _normalize_space_path(project.name, space_path)
    try:
        existing = _existing_space_paths(project)
    except Exception:  # noqa: BLE001 - registry is best-effort, never block a store
        logger.debug("Space registry listing failed; storing to %s as-is", normalized)
        return normalized

    if normalized in existing:
        return normalized

    # Stem matching is opt-in — it can false-merge distinct spaces, which is
    # worse than drift because a memory then lands in the wrong space.
    if not _space_stem_match_enabled():
        return normalized

    parent, _, leaf = normalized.rpartition("/")
    if not leaf:
        return normalized
    leaf_stem = _stem_slug(leaf)
    for candidate in sorted(existing):
        cand_parent, _, cand_leaf = candidate.rpartition("/")
        if cand_parent != parent or not cand_leaf:
            continue
        if _stem_slug(cand_leaf) == leaf_stem:
            logger.info(
                "Space registry: unifying hint space %r into existing %r", normalized, candidate
            )
            _record_space_alias(project, candidate, leaf)
            return candidate
    return normalized


# ---------------------------------------------------------------------------
# Revision stacking
# ---------------------------------------------------------------------------

# Fuzzy-search scores are corpus-relative, so these thresholds were
# calibrated by replaying real duplicate pairs against a live CE graph
# (fulltext-only search; hybrid vector search is a STUDIO+ feature).
# What that measurement showed:
#
#   * An item scored against its OWN exact title tops out at 0.72-0.83.
#     The previous 0.92 gate sat ABOVE the scorer's ceiling, so stacking
#     could never fire for any input whatsoever -- not a strict rule, an
#     unreachable one (issue #163: 20 captures, 20 ``stacked: false``).
#   * Same-subject / different-title duplicates -- the case stacking
#     exists to catch -- land at 0.58-0.68.
#   * Unrelated items in the *same* space reach 0.62 when the space is
#     topically homogeneous (every capture in ``decisions`` is about
#     memory design), while in a mixed space they stay at 0.21-0.35.
#
# The duplicate band (0.58-0.68) and the unrelated band (up to 0.62)
# therefore OVERLAP, and no single score can separate them.
#
# WHAT A FALSE STACK ACTUALLY COSTS. It is not "two related memories filed
# as consecutive revisions, both still reachable". Stacking calls
# ``item.create_revision(...)`` and then tags the NEW revision "published"
# (``tag_list = tags or ["published"]``), while every recall path resolves
# ``get_revision_by_tag("published") or get_revision_by_tag("latest")``.
# So the PRIOR revision loses "published" and leaves the default retrieval
# surface entirely -- it survives only for callers passing
# ``unroll_revisions``. That is precisely the paper's Definition 7.4 tag
# move, i.e. a belief revision, performed WITHOUT the SUPERSEDES edge that
# is supposed to accompany it. A false stack is therefore a false belief
# revision: non-conflicting information gets DISPLACED where AGM vacuity
# (K*4) requires it to be merely EXPANDED. Both failure modes destroy
# retrievability, so "err toward stacking" is not available as a tiebreak;
# the gate has to actually discriminate.
#
# WHY THE SECOND SIGNAL IS LEXICAL, NOT THE SCORE AGAIN. Two candidates
# were measured against the labelled pairs (see the table pinned in
# tests/test_mcp_revision_stacking.py):
#
#   * memory_type agreement alone: useless in exactly the space that needs
#     it. ``decisions`` is homogeneous -- nearly every capture is typed
#     "decision" -- so the gate adds no separation there at all.
#   * top1-minus-top2 margin: measured, and it does NOT separate. A
#     no-duplicate capture put an UNRELATED item at top1 with a margin of
#     0.094, wider than the 0.053 margin of a genuine duplicate pair. Any
#     margin floor admitting the real duplicate also admits the impostor.
#     The runner-up score is still reported for inspection, but nothing is
#     gated on it.
#   * normalized-token overlap (Jaccard over lowercased Latin words plus
#     CJK character bigrams): duplicates 0.19-0.25, unrelated 0.03-0.15.
#     Cleanly separable, with the floor below placed in the gap.
#
# Crucially the score and the overlap are near-uncorrelated (score 0.6165
# with overlap 0.088; score 0.2888 with overlap 0.144), because BM25
# weights rare terms and normalizes by length while Jaccard weights a term
# set flatly. That independence is what lets the pair separate a
# homogeneous space when neither coordinate can do it alone.
_STACK_SIMILARITY_THRESHOLD = 0.75

# Middle band: additionally requires ``memory_type`` agreement. Sits just
# under the lowest duplicate score observed (0.578).
_STACK_TYPE_MATCH_THRESHOLD = 0.55

# Lexical floor, enforced in BOTH bands. Measured gap: unrelated peaks at
# 0.148, duplicates bottom out at 0.188.
_STACK_MIN_LEXICAL_OVERLAP = 0.17

# Below this many tokens on either side the overlap ratio is noise rather
# than evidence, and a short capture is exactly where lexical support is
# weakest. Refuse to stack instead of guessing -- a false stack displaces
# a published revision.
_STACK_MIN_OVERLAP_TOKENS = 8

# Hard cap on the generated search query. Long queries are not merely slow:
# a ~230-character Korean query was observed to fail server-side with
# Lucene ``maxClauseCount is set to 1024`` (CJK is bigram-tokenized and then
# fuzzy-expanded, so characters translate into clauses far faster than they
# do for Latin text). The title is always placed first so its terms
# dominate whatever summary text fits in the remaining budget.
_STACK_QUERY_MAX_CHARS = 180

#: Switch for the middle band ([type-match threshold, strong threshold) with a
#: matching ``memory_type``). Default on. Set to ``"0"`` to run the gate in
#: strong-only mode, where a capture stacks only when its score clears the
#: strong threshold AND the lexical floor.
#:
#: Why this exists: the two-band gate was calibrated on one corpus. The strong
#: band sits above every unrelated score observed there (max 0.616) with room
#: to spare; every contested case -- an unrelated same-type neighbour in a
#: topically homogeneous space scoring 0.58-0.62 -- lives in the middle band.
#: A deployment that has not yet measured its own score distribution (a shared
#: multi-tenant server, a corpus in another language or of much shorter
#: captures) can keep stacking for near-duplicates while withholding the band
#: whose false positives displace ``published`` on an unrelated item. The
#: ``stack_*`` fields on every store result are the telemetry that decides when
#: to turn the band back on.
_STACK_MIDDLE_BAND_ENV = "KUMIHO_STACK_MIDDLE_BAND"


def _middle_band_enabled() -> bool:
    """True unless ``KUMIHO_STACK_MIDDLE_BAND`` is explicitly ``"0"``."""
    return os.environ.get(_STACK_MIDDLE_BAND_ENV, "1").strip() != "0"


def _stack_mode() -> str:
    """Human-readable gate mode, reported on store results for telemetry."""
    return "two-band" if _middle_band_enabled() else "strong-only"


def _build_stack_query(title: str, summary: str, fallback: str = "") -> str:
    """Build the similarity query from the title *and* the summary.

    Searching the title alone (the pre-#163 behaviour) throws away the only
    signal that survives a rewritten headline: two captures about one
    subject three hours apart share their body, not their title. The title
    still leads the query -- it is the most concentrated description of the
    capture -- and the summary fills whatever budget is left.
    """
    title = (title or "").strip()
    summary = (summary or "").strip()
    if not title and not summary:
        summary = (fallback or "").strip()
    if not title:
        return summary[:_STACK_QUERY_MAX_CHARS]

    query = title[:_STACK_QUERY_MAX_CHARS]
    remaining = _STACK_QUERY_MAX_CHARS - len(query) - 1
    # Only bother appending summary text if a useful amount of it fits.
    if summary and remaining >= 16:
        query = f"{query} {summary[:remaining]}"
    return query


def _stack_search(
    query_text: str,
    context: str,
    kind: str,
    retry_query: str = "",
) -> Optional[List[Any]]:
    """Run the stacking search, retrying once with a shorter query.

    Returns the result list, or ``None`` when the search itself failed --
    which is *not* the same as "nothing similar" and is logged as such.
    """
    attempts = [query_text]
    if retry_query and retry_query.strip() and retry_query != query_text:
        attempts.append(retry_query)

    last_exc: Optional[Exception] = None
    for position, attempt in enumerate(attempts, start=1):
        try:
            return kumiho.search(
                attempt,
                context=context,
                kind=kind,
                include_revision_metadata=True,
            )
        except Exception as exc:  # noqa: BLE001 - any failure is worth logging
            last_exc = exc
            logger.warning(
                "Revision stacking search failed (attempt %d/%d, context=%r, "
                "query %d chars): %s",
                position, len(attempts), context, len(attempt), exc,
            )

    # A search that fails on every call is a broken install, not a normal
    # state, so this is a warning rather than the debug line it used to be.
    logger.warning(
        "Revision stacking unavailable for this capture (context=%r): every "
        "search attempt failed, so a new item is being minted even though a "
        "similar one may already exist. Last error: %s",
        context or "<project root>", last_exc,
    )
    return None


#: Latin/digit word tokens, kept at length >= 2 so stray letters do not
#: inflate the ratio.
_TOKEN_WORD_RE = re.compile(r"[0-9a-z_]+")
#: Han, Hiragana, Katakana and Hangul. These scripts are written without
#: spaces, so words are approximated by character bigrams -- the same shape
#: the server's own fulltext index uses.
_TOKEN_CJK_RE = re.compile(
    r"[぀-ヿ㐀-䶿一-鿿가-힯]+"
)


def _overlap_tokens(text: str) -> Set[str]:
    """Normalize text to a comparable token set (Latin words + CJK bigrams)."""
    if not text:
        return set()
    text = unicodedata.normalize("NFKC", text).lower()
    tokens: Set[str] = {
        match.group() for match in _TOKEN_WORD_RE.finditer(text)
        if len(match.group()) >= 2
    }
    for run in _TOKEN_CJK_RE.findall(text):
        if len(run) == 1:
            tokens.add(run)
        for i in range(len(run) - 1):
            tokens.add(run[i:i + 2])
    return tokens


def _lexical_overlap(left: str, right: str) -> float:
    """Jaccard overlap of two texts' token sets, or 0.0 if either is too thin.

    Deliberately symmetric and length-aware: a containment ratio would let a
    two-line capture look identical to a long one it happens to sit inside,
    which is the cheapest way to manufacture a false stack.
    """
    a, b = _overlap_tokens(left), _overlap_tokens(right)
    if len(a) < _STACK_MIN_OVERLAP_TOKENS or len(b) < _STACK_MIN_OVERLAP_TOKENS:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _should_stack(
    score: float,
    type_matches: bool,
    overlap: float,
    threshold: float = _STACK_SIMILARITY_THRESHOLD,
    type_match_threshold: float = _STACK_TYPE_MATCH_THRESHOLD,
    min_overlap: float = _STACK_MIN_LEXICAL_OVERLAP,
    middle_band: Optional[bool] = None,
) -> bool:
    """The gate itself, as a pure function of the measured signals.

    Split out so the labelled score/overlap table measured on the live graph
    can drive it directly as a test fixture. *middle_band* defaults to the
    ``KUMIHO_STACK_MIDDLE_BAND`` switch; pass it explicitly in tests.
    """
    if middle_band is None:
        middle_band = _middle_band_enabled()
    if overlap < min_overlap:
        # The lexical floor binds in both bands: it is the only signal that
        # separated duplicates from neighbours in a homogeneous space.
        return False
    if score >= threshold:
        return True
    if not middle_band:
        # Strong-only mode: the contested band is withheld until a deployment
        # has measured its own score distribution.
        return False
    return score >= type_match_threshold and type_matches


def _candidate_profile(item: Any) -> Tuple[str, str]:
    """Best-effort read of a candidate's ``(memory_type, title+summary)``.

    One revision fetch serves both the type gate and the lexical gate. The
    server reserves the "type" metadata key and strips it from reads, so
    "memory_type" is the readable carrier; both are checked, mirroring
    :func:`_matches_memory_types`.
    """
    for getter in (
        lambda: item.get_revision_by_tag("published"),
        lambda: item.get_revision("latest"),
    ):
        try:
            rev = getter()
        except Exception:
            continue
        meta = getattr(rev, "metadata", None) or {}
        if not meta:
            continue
        mem_type = str(meta.get("memory_type") or meta.get("type") or "")
        text = f"{meta.get('title') or ''} {meta.get('summary') or ''}"
        if mem_type.strip() or text.strip():
            return mem_type.strip().lower(), text
    return "", ""


def _find_similar_item(
    project_name: str,
    space_path: str,
    query_text: str,
    kind: str,
    memory_type: str = "",
    threshold: float = _STACK_SIMILARITY_THRESHOLD,
    type_match_threshold: float = _STACK_TYPE_MATCH_THRESHOLD,
    retry_query: str = "",
    compare_text: str = "",
) -> Tuple[Optional[Item], float, float, float]:
    """Search for an existing memory item similar to the incoming content.

    Uses fuzzy search over revision metadata (title/summary) to find items
    in the same space that cover a similar topic, then requires a lexical
    second opinion before displacing anything (see the constants above --
    stacking moves the "published" tag, so a wrong match hides a memory).

    Returns ``(item, score, runner_up, overlap)``:

    * ``item`` -- the candidate to stack onto, or ``None`` to mint a new one.
    * ``score`` -- the best candidate's search score, reported *whether or
      not* it cleared the bar, so a caller can tell "the search returns 0.0
      every time" (a broken install) from "close but not close enough".
    * ``runner_up`` -- the second-best score, 0.0 when there was none. Not
      gated on (the margin was measured and does not separate); exposed so
      the decision stays inspectable and can be recalibrated later.
    * ``overlap`` -- the measured lexical overlap with the best candidate.
    """
    if not query_text or not query_text.strip():
        return None, 0.0, 0.0, 0.0

    # Convert space_path "/CognitiveMemory/work" -> "CognitiveMemory/work"
    context = space_path.lstrip("/")

    results = _stack_search(query_text, context, kind, retry_query)
    if not results:
        return None, 0.0, 0.0, 0.0

    best = results[0]
    score = float(getattr(best, "score", 0.0) or 0.0)
    runner_up = (
        float(getattr(results[1], "score", 0.0) or 0.0) if len(results) > 1 else 0.0
    )

    # Cheap exit: below the lower band nothing can qualify, so skip the
    # revision fetch the two gates would need.
    if score < type_match_threshold:
        logger.debug(
            "Revision stacking: best candidate %s scored %.3f, below %.2f; "
            "minting a new item.",
            best.item.kref.uri, score, type_match_threshold,
        )
        return None, score, runner_up, 0.0

    candidate_type, candidate_text = _candidate_profile(best.item)
    overlap = _lexical_overlap(compare_text or query_text, candidate_text)
    type_matches = bool(
        candidate_type and candidate_type == (memory_type or "").strip().lower()
    )

    if _should_stack(score, type_matches, overlap, threshold, type_match_threshold):
        logger.debug(
            "Revision stacking: matched item %s (score=%.3f, overlap=%.3f, "
            "memory_type agrees=%s) for query '%.60s...'",
            best.item.kref.uri, score, overlap, type_matches, query_text,
        )
        return best.item, score, runner_up, overlap

    logger.debug(
        "Revision stacking: declined %s (score=%.3f, runner_up=%.3f, "
        "overlap=%.3f, memory_type agrees=%s); minting a new item.",
        best.item.kref.uri, score, runner_up, overlap, type_matches,
    )
    return None, score, runner_up, overlap


def _get_or_create_bundle(project: Project, space_path: str, bundle_name: str) -> Item:
    cache_key = _tenant_key(f"{space_path}/{bundle_name}")
    if cache_key in _bundle_cache:
        return _bundle_cache[cache_key]
    try:
        bundle = project.create_bundle(bundle_name, parent_path=space_path)
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.ALREADY_EXISTS:
            bundle = project.get_bundle(bundle_name, parent_path=space_path)
        else:
            raise
    _bundle_cache[cache_key] = bundle
    return bundle


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _most_recent_items(items: List[Any], cap: int) -> List[Any]:
    """Newest-first slice bounding fallback revision resolution.

    The pattern fallback resolves published/latest via 1-2 RPCs per item.
    Unbounded, that is O(items-in-project) serial round-trips (measured in
    production: 457 items -> 914 RPCs -> ~185s over a ~200ms link) only to
    keep ``limit`` of them after sorting by a constant score.  Prefer the
    newest items — fallback hits when relevance search found nothing, so
    recency is the only signal left.
    """
    def _created(item: Any) -> datetime:
        ts = _parse_timestamp(getattr(item, "created_at", None) or None)
        return ts.replace(tzinfo=None) if ts and ts.tzinfo else (ts or datetime.min)

    return sorted(items, key=_created, reverse=True)[:cap]


def _matches_memory_types(rev: Any, allowed: Optional[Set[str]]) -> bool:
    """True when the revision's memory type passes the filter.

    The server reserves the "type" metadata key and strips it from reads,
    so newer writes mirror the type as "memory_type" — check both.
    Revisions without a readable type (anything stored before the
    "memory_type" mirror existed) only match when no filter is set.
    """
    if not allowed:
        return True
    meta = getattr(rev, "metadata", None) or {}
    mem_type = str(meta.get("memory_type") or meta.get("type") or "")
    return mem_type.strip().lower() in allowed


# ============================================================================
# Tool Implementations
# ============================================================================

def tool_list_projects() -> Dict[str, Any]:
    """List all projects accessible to the current user."""
    _ensure_configured()
    projects = kumiho.get_projects()
    return {
        "projects": [_serialize_project(p) for p in projects],
        "count": len(projects),
    }


def tool_get_project(name: str) -> Dict[str, Any]:
    """Get a project by name."""
    _ensure_configured()
    project = kumiho.get_project(name)
    if not project:
        return {"error": f"Project '{name}' not found"}
    return _serialize_project(project)


def tool_get_spaces(project_name: str, recursive: bool = False) -> Dict[str, Any]:
    """Get spaces within a project."""
    _ensure_configured()
    project = kumiho.get_project(project_name)
    if not project:
        return {"error": f"Project '{project_name}' not found"}
    
    spaces = project.get_spaces(recursive=recursive)
    return {
        "project": project_name,
        "spaces": [_serialize_space(s) for s in spaces],
        "count": len(spaces),
    }


def tool_get_space(space_path: str) -> Dict[str, Any]:
    """Get a space by its path."""
    _ensure_configured()
    try:
        path = space_path if space_path.startswith("/") else f"/{space_path}"
        # Parse project name from path: /project/space/... -> project
        parts = path.strip("/").split("/")
        if len(parts) < 1:
            return {"error": "Invalid space path"}
        project_name = parts[0]
        project = kumiho.get_project(project_name)
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        space = project.get_space(path)
        return _serialize_space(space)
    except Exception as e:
        return {"error": str(e)}


def tool_get_item(kref: str) -> Dict[str, Any]:
    """Get an item by its kref URI."""
    _ensure_configured()
    try:
        item = kumiho.get_item(kref)
        return _serialize_item(item)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Item not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_revision(kref: str) -> Dict[str, Any]:
    """Get a revision by its kref URI."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(kref)
        return _serialize_revision(revision)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Revision not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_artifacts(revision_kref: str) -> Dict[str, Any]:
    """Get all artifacts for a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        artifacts = revision.get_artifacts()
        return {
            "revision_kref": revision_kref,
            "artifacts": [_serialize_artifact(a) for a in artifacts],
            "count": len(artifacts),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_artifact(artifact_kref: str) -> Dict[str, Any]:
    """Get a single artifact by its kref URI."""
    _ensure_configured()
    try:
        artifact = kumiho.get_artifact(artifact_kref)
        return _serialize_artifact(artifact)
    except Exception as e:
        return {"error": str(e)}


def tool_get_bundle(bundle_kref: str) -> Dict[str, Any]:
    """Get a bundle by its kref URI."""
    _ensure_configured()
    try:
        bundle = kumiho.get_bundle(bundle_kref)
        return _serialize_item(bundle)  # Bundle is a specialized Item
    except Exception as e:
        return {"error": str(e)}


def tool_search_items(
    context_filter: str = "",
    name_filter: str = "",
    kind_filter: str = "",
    include_metadata: bool = False,
    auth_token: str = "",
) -> Dict[str, Any]:
    """Search for items across projects and spaces."""
    _apply_auth_token_override(auth_token, "kumiho_search_items")
    _ensure_configured()
    items = kumiho.item_search(
        context_filter=context_filter,
        name_filter=name_filter,
        kind_filter=kind_filter,
    )

    serialized = []
    for i in items:
        data = _serialize_item(i)
        if not include_metadata:
            data.pop("metadata", None)
        serialized.append(data)

    return {
        "items": serialized,
        "count": len(items),
        "filters": {
            "context": context_filter,
            "name": name_filter,
            "kind": kind_filter,
        },
    }


def tool_fulltext_search(
    query: str,
    context: str = "",
    kind: str = "",
    include_deprecated: bool = False,
    include_revision_metadata: bool = False,
    include_artifact_metadata: bool = False,
    include_metadata: bool = False,
    limit: int = 20,
    auth_token: str = "",
) -> Dict[str, Any]:
    """Full-text fuzzy search across items (Google-like search).

    For STUDIO+ tiers with vector embeddings enabled, uses hybrid search
    (fulltext + vector similarity) for improved accuracy when searching
    revision metadata.
    """
    _apply_auth_token_override(auth_token, "kumiho_fulltext_search")
    _ensure_configured()
    results = kumiho.search(
        query,
        context=context,
        kind=kind,
        include_deprecated=include_deprecated,
        include_revision_metadata=include_revision_metadata,
        include_artifact_metadata=include_artifact_metadata,
    )

    serialized = []
    for r in results[:limit]:
        item_data = _serialize_item(r.item)
        if not include_metadata:
            item_data.pop("metadata", None)
        serialized.append({
            "item": item_data,
            "score": r.score,
            "matched_in": r.matched_in,
        })

    # Get search_mode from results if available (hybrid vs fulltext)
    # This is populated for STUDIO+ tiers with vector embeddings enabled
    search_mode = getattr(results, "search_mode", None) or "fulltext"

    return {
        "results": serialized,
        "count": len(serialized),
        "total": len(results),
        "query": query,
        "search_mode": search_mode,  # "fulltext" or "hybrid"
        "filters": {
            "context": context,
            "kind": kind,
        },
    }


def tool_memory_store(
    project: str = "CognitiveMemory",
    space_path: str = "",
    space_hint: str = "",
    policy_kref: Optional[str] = None,
    memory_item_kind: str = "conversation",
    bundle_name: str = "",
    memory_type: str = "summary",
    title: str = "",
    summary: str = "",
    user_text: str = "",
    assistant_text: str = "",
    artifact_location: str = "",
    artifact_name: str = "chat_io",
    tags: Optional[List[str]] = None,
    source_revision_krefs: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    edge_type: str = DERIVED_FROM,
    stack_revisions: bool = True,
) -> Dict[str, Any]:
    """Store a memory bundle with minimal inputs.

    When *stack_revisions* is True (the default), searches for an existing
    item in the same space with similar content and stacks a new revision
    on it instead of creating a duplicate item.  Falls back to creating a
    new item when no similar item is found or the search fails.
    """
    _ensure_configured()

    if not user_text and not assistant_text:
        return {"error": "user_text or assistant_text must be provided"}

    # Reject credentials before sending to cloud graph (spec §10.4.5)
    if _PRIVACY_AVAILABLE:
        _redactor = PIIRedactor()
        for _field_value in (user_text, assistant_text, summary, title):
            if _field_value:
                try:
                    _redactor.reject_credentials(_field_value)
                except CredentialDetectedError as exc:
                    return {"error": str(exc)}

    project_name = project or "CognitiveMemory"
    project_obj = _get_project_cached(project_name)

    policy = {}
    schema_version = ""
    if policy_kref:
        try:
            if "?r=" in policy_kref:
                rev = kumiho.get_revision(policy_kref)
            else:
                item = kumiho.get_item(policy_kref)
                rev = item.get_revision_by_tag("published") or item.get_revision_by_tag("latest")
            if rev and rev.metadata:
                schema_version = str(rev.metadata.get("schema", ""))
                policy = _parse_json_object(rev.metadata.get("policy"))
        except Exception as exc:
            return {"error": f"Failed to load policy_kref: {exc}"}

    memory_kind = memory_item_kind or policy.get("memory_item_kind", "conversation")

    # Recommended kind vocabulary: a policy may widen it with an explicit
    # "memory_kinds" list. An out-of-vocabulary kind is *warned, not
    # rejected* — kind is part of the kref identity, so nudging toward a
    # closed set curbs drift, but hard-rejecting on day one would break
    # existing callers/policies that already use other kinds. (Use `is None`
    # so a policy setting memory_kinds: [] is honored, not silently ignored.)
    policy_kinds = policy.get("memory_kinds")
    if policy_kinds is None:
        allowed_kinds = DEFAULT_MEMORY_KINDS
    elif isinstance(policy_kinds, list) and all(isinstance(k, str) for k in policy_kinds):
        allowed_kinds = policy_kinds  # a well-formed override (incl. [] to warn on all)
    else:
        # A non-list override (e.g. the string "conversation,entity") would
        # silently degrade `not in` into a *substring* test — "con", "tity",
        # even "," wrongly accepted and baked into the kref identity — and the
        # reject message would iterate char-by-char. Reject the malformed
        # override and fall back to the closed default vocabulary.
        logger.warning(
            "policy 'memory_kinds' must be a list of strings, got %s; "
            "ignoring the override and using the default vocabulary.",
            type(policy_kinds).__name__,
        )
        allowed_kinds = DEFAULT_MEMORY_KINDS
    if memory_kind not in allowed_kinds:
        logger.warning(
            "memory_item_kind %r is outside the recommended vocabulary (%s); "
            "accepting, but ad-hoc kinds fragment the taxonomy.",
            memory_kind, ", ".join(allowed_kinds),
        )

    space_root = policy.get("space_root", "/")

    space_from_hint = False
    if not space_path:
        hint = space_hint.strip()
        if hint:
            segments = [seg for seg in hint.split("/") if seg]
            slugged = [_slugify(seg) or seg for seg in segments]
            space_path = "/".join(slugged)
            space_from_hint = bool(space_path)
    if space_root and space_root != "/":
        base_root = space_root.strip("/")
        if space_path:
            space_path = f"{base_root}/{space_path}"
        else:
            space_path = base_root

    # Hint-derived paths are resolved against existing spaces (exact/stem)
    # before creation so topic variants converge on one space. An explicit
    # space_path is honored verbatim, as before.
    if space_from_hint and space_path and _space_registry_enabled():
        space_path = _resolve_space_hint_path(project_obj, space_path)

    normalized_space_path = _ensure_space_path(project_obj, space_path)

    base_text = title or summary or user_text or assistant_text or "memory"
    stacked = False
    stack_score = 0.0
    stack_runner_up = 0.0
    stack_overlap = 0.0
    previous_revision_kref = ""
    item = None

    # --- Revision stacking: search for a similar existing item ---
    if stack_revisions:
        # Search title AND summary: a capture revisiting the same subject
        # hours later shares its body, not its headline.
        search_query = _build_stack_query(
            title, summary, fallback=(assistant_text or user_text or "")
        )
        if search_query.strip():
            item, stack_score, stack_runner_up, stack_overlap = _find_similar_item(
                project_name,
                normalized_space_path,
                search_query,
                memory_kind,
                memory_type=memory_type,
                # If the combined query trips the server's clause limit,
                # fall back to the title alone rather than losing stacking.
                retry_query=(title or "")[:_STACK_QUERY_MAX_CHARS],
                # The lexical gate compares full text, not the capped query.
                compare_text=f"{title} {summary}",
            )
            if item is not None:
                stacked = True
                try:
                    prev_rev = item.get_revision_by_tag("published")
                    if prev_rev:
                        previous_revision_kref = prev_rev.kref.uri
                except Exception:
                    pass  # Non-critical; proceed with stacking

    # --- Fallback: create a new item with hash-based naming ---
    if item is None:
        slug = _slugify(base_text) or "memory"
        suffix = _short_hash(user_text + assistant_text + base_text)
        item_name = f"{slug}-{suffix}"
        if len(item_name) > 64:
            item_name = item_name[:64].rstrip("-")
        item = _get_or_create_item(
            project_obj, normalized_space_path, item_name, memory_kind
        )

    final_summary = summary.strip() if summary else (assistant_text or user_text).strip()
    if len(final_summary) > 2000:
        final_summary = f"{final_summary[:1997]}..."

    final_title = title.strip() if title else final_summary[:120]

    base_metadata = {
        "schema": schema_version or "kumiho.agent_memory.v1",
        # "type" is a server-reserved metadata key and is stripped from
        # every read — "memory_type" is the readable carrier. "type" is
        # still written for raw-database consumers.
        "type": memory_type,
        "memory_type": memory_type,
        "title": final_title,
        "summary": final_summary,
        "space": normalized_space_path,
    }
    if metadata:
        base_metadata.update(metadata)

    revision = item.create_revision(metadata=_stringify_metadata(base_metadata))

    artifact_kref = ""
    resolved_artifact_location = artifact_location
    if not resolved_artifact_location:
        try:
            resolved_artifact_location = _write_memory_artifact(
                project=project_name,
                space_path=normalized_space_path,
                item_name=item.item_name,
                title=final_title,
                summary=final_summary,
                user_text=user_text,
                assistant_text=assistant_text,
                memory_type=memory_type,
            )
        except Exception as exc:
            logger.warning(f"Auto-artifact write failed: {exc}")
    if resolved_artifact_location:
        try:
            artifact = revision.create_artifact(artifact_name, resolved_artifact_location)
            artifact_kref = artifact.kref.uri
        except Exception as exc:
            return {"error": f"Failed to create artifact: {exc}"}

    tag_list = tags or ["published"]
    for tag in tag_list:
        if tag == "latest":
            continue
        try:
            revision.tag(tag)
        except Exception:
            continue

    bundle_kref = ""
    if bundle_name:
        bundle_slug = _slugify(bundle_name) or bundle_name
    else:
        bundle_slug = _slugify(space_hint) if space_hint else ""
    if not bundle_slug:
        bundle_slug = "topic"
    try:
        bundle = _get_or_create_bundle(project_obj, normalized_space_path, bundle_slug)
        bundle.add_member(item)
        bundle_kref = bundle.kref.uri
    except Exception:
        bundle_kref = ""

    edges_created = []
    for source_kref in (source_revision_krefs or []):
        try:
            source_rev = kumiho.get_revision(source_kref)
            edge = revision.create_edge(source_rev, edge_type)
            edges_created.append(edge.target_kref.uri)
        except Exception:
            continue

    result = {
        "space_path": normalized_space_path,
        "item_kref": item.kref.uri,
        "revision_kref": revision.kref.uri,
        "bundle_kref": bundle_kref,
        "artifact_kref": artifact_kref,
        "summary": final_summary,
        "edges_created": edges_created,
        "stacked": stacked,
        # Reported even when nothing stacked, so a caller can tell a broken
        # search (0.0 every time) from a genuine near-miss without inferring
        # it from a stream of ``false``, and can see WHICH gate declined.
        "stack_score": round(stack_score, 4),
        "stack_runner_up": round(stack_runner_up, 4),
        "stack_overlap": round(stack_overlap, 4),
        "stack_mode": _stack_mode(),
    }
    if previous_revision_kref:
        result["previous_revision_kref"] = previous_revision_kref
    return result


def tool_memory_store_batch(
    captures: List[Dict[str, Any]],
    project: str = "CognitiveMemory",
    space_path: str = "",
    memory_item_kind: str = "conversation",
    source_revision_krefs: Optional[List[str]] = None,
    edge_type: str = DERIVED_FROM,
    stack_revisions: bool = True,
    idempotency_prefix: str = "",
) -> Dict[str, Any]:
    """Bulk counterpart of :func:`tool_memory_store` — N captures, one batched write.

    Collapses the per-capture ``create_item`` + ``create_revision`` + auto-artifact
    into a single ``batch_create_revisions`` transaction. This is what backfill and
    any other high-volume, multi-capture write should use: it removes the neo4j
    relationship-group deadlock that naive per-capture concurrency triggers, and
    cuts the heaviest writes from ~2N RPCs to one. Per-capture credential
    screening, space resolution, fuzzy-stack decision, tagging, bundling and
    DERIVED_FROM edges are preserved exactly — the server has no batch RPC for
    tag/bundle/edge, so those remain per-item (still far lighter than the
    create/revision writes the batch collapses).

    Each capture dict mirrors the fields reflect passes to ``tool_memory_store``:
        ``type``, ``title``, ``content`` — the memory itself.
        ``tags``      — optional; defaults to ``["published"]``.
        ``metadata``  — optional pre-validated dict (e.g. ``{"event_date": ...}``).
        ``space_hint``— optional per-capture space override.

    Returns ``{"results": [per-capture dict | {"error": ...}], "stored_krefs":
    [...], "stacked": <int>}`` — ``results`` is positional (one entry per input
    capture, ``None`` collapses to an ``error`` entry). Each successful entry
    carries ``stack_score``, the best similarity score the stacking search
    saw, reported whether or not it stacked.
    """
    _ensure_configured()
    source_krefs = source_revision_krefs or []
    project_name = project or "CognitiveMemory"
    project_obj = _get_project_cached(project_name)
    memory_kind = memory_item_kind or "conversation"
    redactor = PIIRedactor() if _PRIVACY_AVAILABLE else None

    results: List[Optional[Dict[str, Any]]] = [None] * len(captures)
    rows: List[Dict[str, Any]] = []
    prep_by_row: Dict[int, Dict[str, Any]] = {}

    # --- Phase 1: per-capture prep (reads / local I/O) -> batch rows ---
    for i, cap in enumerate(captures):
        title = (cap.get("title") or "").strip()
        content = (cap.get("content") or "").strip()
        if not content and not title:
            results[i] = {"error": "empty capture (no title or content)"}
            continue

        # Credential screen before anything reaches the graph (parity §10.4.5).
        if redactor is not None:
            try:
                for _v in (content, title):
                    if _v:
                        redactor.reject_credentials(_v)
            except CredentialDetectedError as exc:
                results[i] = {"error": str(exc)}
                continue

        cap_space = cap.get("space_hint", "") or space_path
        normalized_space = _ensure_space_path(project_obj, cap_space)

        final_summary = content
        if len(final_summary) > 2000:
            final_summary = f"{final_summary[:1997]}..."
        final_title = title or final_summary[:120]
        memory_type = cap.get("type", "summary")

        # Fuzzy-stack: reuse a similar existing item, else mint a hash-named one
        # (batch_create_revisions auto-creates the item from a new kref).
        item = None
        stack_score = 0.0
        stack_runner_up = 0.0
        stack_overlap = 0.0
        if stack_revisions:
            # Title AND summary, same as the single path.
            search_query = _build_stack_query(title, final_summary)
            if search_query.strip():
                item, stack_score, stack_runner_up, stack_overlap = (
                    _find_similar_item(
                        project_name,
                        normalized_space,
                        search_query,
                        memory_kind,
                        memory_type=memory_type,
                        retry_query=(title or "")[:_STACK_QUERY_MAX_CHARS],
                        compare_text=f"{final_title} {final_summary}",
                    )
                )
        if item is not None:
            item_kref = item.kref.uri
        else:
            slug = _slugify(final_title) or "memory"
            item_name = f"{slug}-{_short_hash(content + final_title)}"
            if len(item_name) > 64:
                item_name = item_name[:64].rstrip("-")
            item_kref = f"kref://{normalized_space.strip('/')}/{item_name}.{memory_kind}"

        base_metadata: Dict[str, Any] = {
            "schema": "kumiho.agent_memory.v1",
            "type": memory_type,
            "memory_type": memory_type,
            "title": final_title,
            "summary": final_summary,
            "space": normalized_space,
        }
        extra_metadata = cap.get("metadata")
        if extra_metadata:
            base_metadata.update(extra_metadata)

        # No embedding_text override: leaving it empty makes the server
        # auto-generate the embedding from the concatenated metadata, exactly like
        # the single tool_memory_store path (item.create_revision, embedding_text="").
        # Overriding it here would embed batch-written captures on a different basis
        # than single-written ones, splitting the vector space by capture count.
        row: Dict[str, Any] = {
            "item_kref": item_kref,
            "metadata": _stringify_metadata(base_metadata),
        }
        try:
            location = _write_memory_artifact(
                project=project_name,
                space_path=normalized_space,
                item_name=item_kref.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                title=final_title,
                summary=final_summary,
                user_text="",
                assistant_text=content,
                memory_type=memory_type,
            )
            if location:
                row["artifacts"] = [
                    {"name": "chat_io", "location": location, "default": True}
                ]
        except Exception as exc:  # best-effort, like the single path
            logger.warning(f"batch auto-artifact write failed: {exc}")

        prep_by_row[len(rows)] = {
            "capture_index": i,
            "item_obj": item,
            "item_kref": item_kref,
            "tags": cap.get("tags"),
            "space": normalized_space,
            "stacked": item is not None,
            "stack_score": stack_score,
            "stack_runner_up": stack_runner_up,
            "stack_overlap": stack_overlap,
            "stack_mode": _stack_mode(),
        }
        rows.append(row)

    if not rows:
        return {"results": results, "stored_krefs": [], "stacked": 0}

    # --- Phase 2: batched write, chunked at the server's per-call row cap ---
    # BatchCreateRevisions caps a call at 200 rows (docs/batch-create-revisions.md).
    # A reflect/backfill batch can exceed that, so split into stable, ordered
    # chunks; when an idempotency_prefix is given, suffix it with the chunk offset
    # so re-submitting the same captures replays as a no-op (the doc's recommended
    # "prefix derived from staging-file id and chunk offset").
    _BATCH_ROW_LIMIT = 200
    batch_results: List[Any] = []
    failures: List[Tuple[int, str]] = []
    for start in range(0, len(rows), _BATCH_ROW_LIMIT):
        chunk = rows[start:start + _BATCH_ROW_LIMIT]
        chunk_prefix = f"{idempotency_prefix}:{start}" if idempotency_prefix else ""
        chunk_results, chunk_failures = kumiho.batch_create_revisions(
            chunk, idempotency_prefix=chunk_prefix
        )
        batch_results.extend(chunk_results)
        failures.extend((start + idx, reason) for idx, reason in chunk_failures)
    failure_by_row = {idx: reason for idx, reason in failures}

    # --- Phase 3: per-capture post (tag, bundle, edges) on created revisions ---
    stored_krefs: List[str] = []
    stacked_count = 0
    for row_idx, prep in prep_by_row.items():
        i = prep["capture_index"]
        rev = batch_results[row_idx] if row_idx < len(batch_results) else None
        if rev is None:
            results[i] = {"error": failure_by_row.get(row_idx, "batch row rejected")}
            continue

        for tag in (prep["tags"] or ["published"]):
            if tag == "latest":
                continue
            try:
                rev.tag(tag)
            except Exception:
                continue

        bundle_kref = ""
        try:
            bundle = _get_or_create_bundle(project_obj, prep["space"], "topic")
            item_obj = prep["item_obj"] or kumiho.get_item(prep["item_kref"])
            bundle.add_member(item_obj)
            bundle_kref = bundle.kref.uri
        except Exception:
            bundle_kref = ""

        edges_created: List[str] = []
        for source_kref in source_krefs:
            try:
                edge = rev.create_edge(kumiho.get_revision(source_kref), edge_type)
                edges_created.append(edge.target_kref.uri)
            except Exception:
                continue

        if prep["stacked"]:
            stacked_count += 1
        stored_krefs.append(rev.kref.uri)
        results[i] = {
            "item_kref": prep["item_kref"],
            "revision_kref": rev.kref.uri,
            "bundle_kref": bundle_kref,
            "edges_created": edges_created,
            "stacked": prep["stacked"],
            "stack_score": round(prep["stack_score"], 4),
            "stack_runner_up": round(prep["stack_runner_up"], 4),
            "stack_overlap": round(prep["stack_overlap"], 4),
            "stack_mode": prep.get("stack_mode", _stack_mode()),
        }

    return {"results": results, "stored_krefs": stored_krefs, "stacked": stacked_count}


def tool_memory_retrieve(
    project: str = "CognitiveMemory",
    query: str = "",
    keywords: Optional[List[str]] = None,
    topics: Optional[List[str]] = None,
    space_paths: Optional[List[str]] = None,
    bundle_names: Optional[List[str]] = None,
    memory_item_kind: str = "conversation",
    limit: int = 5,
    mode: str = "search",
    include_revision_metadata: bool = True,
    unroll_revisions: bool = False,
    memory_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Retrieve memory krefs using fuzzy search with bundle and fallback support.

    Uses Google-like fuzzy search (kumiho.search) as the primary method for natural
    language queries. Falls back to pattern matching for specific modes or when
    fuzzy search returns no results.

    Args:
        unroll_revisions: If True, return ALL revisions of stacked items
            (useful for dream-state or history browsing). If False (default),
            return only the published/latest revision per item.
    """
    _ensure_configured()

    project_name = project or "CognitiveMemory"
    project_obj = kumiho.get_project(project_name)
    if not project_obj:
        return {"error": f"Project '{project_name}' not found"}

    def to_list(value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return []

    keyword_list = to_list(keywords)
    topic_list = to_list(topics)
    spaces = to_list(space_paths)
    bundles = to_list(bundle_names)
    # Normalized memory-type filter (see _matches_memory_types). Only
    # revisions stored with the "memory_type" metadata mirror are
    # matchable — older revisions have no readable type.
    allowed_types: Optional[Set[str]] = {
        t.strip().lower() for t in to_list(memory_types) if t.strip()
    } or None

    query_text = (query or "").strip()
    query_lower = query_text.lower()
    mode_text = (mode or "").strip().lower()

    # Auto-detect "first/earliest" mode from query
    if not mode_text and query_lower:
        if any(token in query_lower for token in ["first", "earliest", "oldest", "initial"]):
            mode_text = "first"
    if not mode_text:
        mode_text = "search"

    def normalize_context(value: str) -> str:
        path = value.strip()
        if path.startswith("/"):
            path = path.strip("/")
        if not path:
            return project_name
        if path.startswith(f"{project_name}/") or path == project_name:
            return path
        return f"{project_name}/{path}"

    contexts = [normalize_context(p) for p in spaces] if spaces else [project_name]
    spaces_used: List[str] = []

    # Mode: first/earliest - find oldest item by created_at
    if mode_text in ["first", "earliest", "oldest", "initial"]:
        items = kumiho.item_search(
            context_filter=project_name,
            name_filter="",
            kind_filter=memory_item_kind,
        )
        # Oldest-first, returning the first item whose revision passes the
        # memory_types filter — min() alone would ignore the filter.
        for item in sorted(
            items, key=lambda item: _parse_timestamp(item.created_at) or datetime.max,
        ):
            try:
                rev = item.get_revision_by_tag("published") or item.get_revision_by_tag("latest")
            except Exception:
                continue
            if rev and not _matches_memory_types(rev, allowed_types):
                continue
            return {
                "item_krefs": [item.kref.uri],
                "revision_krefs": [rev.kref.uri] if rev else [],
                "spaces_used": [project_name],
            }
        return {"item_krefs": [], "revision_krefs": [], "spaces_used": []}

    # Build search query from query + keywords + topics
    search_terms = []
    if query_text:
        search_terms.append(query_text)
    search_terms.extend(keyword_list)
    search_terms.extend(topic_list)
    combined_query = " ".join(search_terms).strip()

    results: List[Tuple[str, str, float]] = []  # (item_kref, revision_kref, score)

    # Primary: Use fuzzy search if we have a query
    if combined_query:
        try:
            # Search each space context separately so space_paths filtering
            # is honoured.  When no space_paths are specified, contexts
            # defaults to [project_name] which searches everything.
            search_results = []
            for ctx in contexts:
                search_results.extend(kumiho.search(
                    combined_query,
                    context=ctx,
                    kind=memory_item_kind,
                    include_revision_metadata=include_revision_metadata,
                ))
            # The deep search variant (include_revision_metadata=True) can
            # return zero results on some deployments even when the plain
            # item search matches (observed in production: every deep query
            # returned 0 while the same query without revision metadata
            # returned 100).  Retry shallow before giving up — falling
            # through to the pattern fallback instead costs 1-2 RPCs per
            # item in the project.
            if not search_results and include_revision_metadata:
                for ctx in contexts:
                    search_results.extend(kumiho.search(
                        combined_query,
                        context=ctx,
                        kind=memory_item_kind,
                        include_revision_metadata=False,
                    ))
                if search_results:
                    logger.warning(
                        "tool_memory_retrieve: deep search returned 0 results "
                        "but shallow retry matched %d — deep search may be "
                        "broken on this server", len(search_results),
                    )
            # Sort by score descending after merging contexts
            search_results.sort(key=lambda sr: sr.score, reverse=True)
            for sr in search_results[:limit * 2]:  # Get extra for filtering
                try:
                    if unroll_revisions:
                        # Unroll ALL revisions for stacked items (dream-state,
                        # history browsing). Each revision gets a separate slot.
                        revisions = sr.item.get_revisions()
                        if revisions and len(revisions) > 1:
                            for rev in revisions:
                                if not _matches_memory_types(rev, allowed_types):
                                    continue
                                results.append((
                                    sr.item.kref.uri, rev.kref.uri,
                                    sr.score,
                                ))
                            if sr.item.space:
                                spaces_used.append(sr.item.space.path)
                            continue

                    # Default: return only published/latest per item.
                    # For stacked items this avoids flooding recall slots
                    # with older revisions that share the same search score.
                    rev = (
                        sr.item.get_revision_by_tag("published")
                        or sr.item.get_revision_by_tag("latest")
                    )
                    if rev and _matches_memory_types(rev, allowed_types):
                        results.append((sr.item.kref.uri, rev.kref.uri, sr.score))
                        if sr.item.space:
                            spaces_used.append(sr.item.space.path)
                except Exception:
                    continue
        except Exception as exc:
            logger.warning(
                "tool_memory_retrieve: fulltext search failed: %s: %s",
                type(exc).__name__, exc,
            )
            # Fall through to bundle/pattern search

    # Secondary: Bundle-based search if specified and fuzzy didn't find enough
    if bundles and len(results) < limit:
        for context in contexts:
            for bundle_name in bundles:
                bundle_items = kumiho.item_search(
                    context_filter=context,
                    name_filter=bundle_name,
                    kind_filter="bundle",
                )
                if bundle_items:
                    spaces_used.append(context)
                for bundle_item in bundle_items:
                    try:
                        bundle = kumiho.get_bundle(bundle_item.kref.uri)
                        members = bundle.get_members()
                        for member in members:
                            # Bounded: each member costs 2-3 RPCs and only
                            # `limit` results survive — large auto-collected
                            # bundles must not turn into an RPC storm.
                            if len(results) >= limit * 2:
                                break
                            if member.item_kref.uri not in [r[0] for r in results]:
                                item = kumiho.get_item(member.item_kref.uri)
                                rev = item.get_revision_by_tag("published") or item.get_revision_by_tag("latest")
                                if rev and _matches_memory_types(rev, allowed_types):
                                    results.append((member.item_kref.uri, rev.kref.uri, 0.5))
                    except Exception:
                        continue

    # Fallback: Pattern search if still no results
    if not results:
        name_filter = ""
        if keyword_list:
            name_filter = keyword_list[0]
        elif topic_list:
            name_filter = topic_list[0]

        for context in contexts:
            items = kumiho.item_search(
                context_filter=context,
                name_filter=name_filter,
                kind_filter=memory_item_kind,
            )
            if items:
                spaces_used.append(context)
            # Bounded: resolving published/latest costs 1-2 RPCs per item,
            # and only `limit` results survive — never resolve the whole
            # project (see _most_recent_items).
            for item in _most_recent_items(items, limit * 2):
                try:
                    rev = item.get_revision_by_tag("published") or item.get_revision_by_tag("latest")
                    if rev and _matches_memory_types(rev, allowed_types):
                        results.append((item.kref.uri, rev.kref.uri, 0.0))
                except Exception:
                    continue

        # Last resort: search entire project — but ONLY when the caller
        # did NOT explicitly scope to specific spaces.  When space_paths
        # are provided the caller expects isolation; falling back to the
        # whole project would leak cross-space data (e.g. memories from
        # one benchmark entry appearing in another's recall).
        if not results and contexts != [project_name] and not spaces:
            items = kumiho.item_search(
                context_filter=project_name,
                name_filter="",
                kind_filter=memory_item_kind,
            )
            if items:
                spaces_used.append(project_name)
            for item in _most_recent_items(items, limit * 2):
                try:
                    rev = item.get_revision_by_tag("published") or item.get_revision_by_tag("latest")
                    if rev and _matches_memory_types(rev, allowed_types):
                        results.append((item.kref.uri, rev.kref.uri, 0.0))
                except Exception:
                    continue

    # Dedupe: when unrolling, dedup by revision_kref so stacked revisions
    # survive.  Otherwise dedup by item_kref — one slot per memory item.
    seen: Set[str] = set()
    deduped: List[Tuple[str, str, float]] = []
    for item_kref, rev_kref, score in results:
        dedup_key = rev_kref if unroll_revisions else item_kref
        if dedup_key not in seen:
            seen.add(dedup_key)
            deduped.append((item_kref, rev_kref, score))

    deduped.sort(key=lambda x: x[2], reverse=True)
    final = deduped[:limit]

    return {
        "item_krefs": [item for item, _, _ in final],
        "revision_krefs": [rev for _, rev, _ in final],
        "spaces_used": list(dict.fromkeys(spaces_used)),
        "scores": [score for _, _, score in final],
    }


def tool_get_dependencies(
    revision_kref: str,
    max_depth: int = 5,
    edge_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get all dependencies of a revision (what it depends on)."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        result = revision.get_all_dependencies(
            edge_type_filter=edge_types,
            max_depth=max_depth,
        )
        return {
            "revision_kref": revision_kref,
            "dependencies": list(result.revision_krefs),
            "count": len(result.revision_krefs),
            "max_depth": max_depth,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_dependents(
    revision_kref: str,
    max_depth: int = 5,
    edge_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get all dependents of a revision (what depends on it)."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        result = revision.get_all_dependents(
            edge_type_filter=edge_types,
            max_depth=max_depth,
        )
        return {
            "revision_kref": revision_kref,
            "dependents": list(result.revision_krefs),
            "count": len(result.revision_krefs),
            "max_depth": max_depth,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_provenance_summary(
    revision_kref: str,
    max_depth: int = 10
) -> Dict[str, Any]:
    """Get provenance summary with AI metadata."""
    _ensure_configured()
    try:
        target = kumiho.get_revision(revision_kref)
        deps_result = target.get_all_dependencies(max_depth=max_depth, limit=50)
        
        summary = []
        
        # Helper to extract AI params
        def extract_params(rev):
            meta = rev.metadata or {}
            # Common keys in ComfyUI/Stable Diffusion
            keys = ["model", "seed", "resolution", "width", "height", "cfg", "steps", "sampler", "scheduler", "prompt", "negative_prompt", "denoise"]
            params = {k: meta[k] for k in keys if k in meta}
            return params

        # Process target
        summary.append({
            "kref": target.kref.uri,
            "role": "target",
            "params": extract_params(target)
        })

        # Process dependencies
        for kref in deps_result.revision_krefs:
            try:
                rev = kumiho.get_revision(kref.uri)
                params = extract_params(rev)
                if params: # Only include if it has relevant metadata
                    summary.append({
                        "kref": rev.kref.uri,
                        "role": "dependency",
                        "params": params
                    })
            except Exception as exc:
                logger.debug("Skipping dependency %s: %s", kref.uri, exc)

        return {
            "revision_kref": revision_kref,
            "provenance_summary": summary,
            "dependency_count": len(deps_result.revision_krefs)
        }
    except Exception as e:
        return {"error": str(e)}


def tool_analyze_impact(
    revision_kref: str,
    max_depth: int = 10,
    edge_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze the impact of changes to a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        impacted = revision.analyze_impact(
            edge_type_filter=edge_types,
            max_depth=max_depth,
        )
        return {
            "revision_kref": revision_kref,
            "impacted_revisions": [
                {
                    "revision_kref": iv.revision_kref,
                    "impact_depth": iv.impact_depth,
                }
                for iv in impacted
            ],
            "count": len(impacted),
            "max_depth": max_depth,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_find_path(
    source_kref: str,
    target_kref: str,
    max_depth: int = 10,
    edge_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Find the shortest path between two revisions."""
    _ensure_configured()
    try:
        source = kumiho.get_revision(source_kref)
        target = kumiho.get_revision(target_kref)
        path = source.find_path_to(
            target,
            edge_type_filter=edge_types,
            max_depth=max_depth,
        )
        if not path:
            return {
                "source_kref": source_kref,
                "target_kref": target_kref,
                "path_found": False,
                "message": "No path found between revisions",
            }
        return {
            "source_kref": source_kref,
            "target_kref": target_kref,
            "path_found": True,
            "total_depth": path.total_depth,
            "steps": [
                {
                    "revision_kref": str(step.revision_kref),
                    "edge_type": step.edge_type,
                    "depth": step.depth,
                }
                for step in path.steps
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_edges(
    revision_kref: str,
    direction: str = "both",
    edge_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get edges for a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        
        # Map direction string to constant
        dir_map = {
            "outgoing": EdgeDirection.OUTGOING,
            "incoming": EdgeDirection.INCOMING,
            "both": EdgeDirection.BOTH,
        }
        direction_val = dir_map.get(direction.lower(), EdgeDirection.BOTH)
        
        edges = revision.get_edges(
            edge_type_filter=edge_type,
            direction=direction_val,
        )
        return {
            "revision_kref": revision_kref,
            "direction": direction,
            "edges": [_serialize_edge(e) for e in edges],
            "count": len(edges),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_resolve_kref(kref: str) -> Dict[str, Any]:
    """Resolve a kref URI to a file location."""
    _ensure_configured()
    try:
        location = kumiho.resolve(kref)
        return {
            "kref": kref,
            "location": location,
            "resolved": location is not None,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_artifacts_by_location(location: str) -> Dict[str, Any]:
    """Find all artifacts at a specific file location (reverse lookup)."""
    _ensure_configured()
    try:
        artifacts = kumiho.get_artifacts_by_location(location)
        return {
            "location": location,
            "artifacts": [_serialize_artifact(a) for a in artifacts],
            "count": len(artifacts),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_item_revisions(item_kref: str, include_metadata: bool = False) -> Dict[str, Any]:
    """Get all revisions for an item."""
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        revisions = item.get_revisions()

        serialized = []
        for r in revisions:
            data = _serialize_revision(r)
            if not include_metadata:
                data.pop("metadata", None)
            serialized.append(data)

        return {
            "item_kref": item_kref,
            "revisions": serialized,
            "count": len(revisions),
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Item not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_revision_by_tag(item_kref: str, tag: str) -> Dict[str, Any]:
    """Get a revision by tag (e.g., 'latest', 'published', 'approved')."""
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        revision = item.get_revision_by_tag(tag)
        if not revision:
            return {"error": f"No revision found with tag '{tag}'", "not_found": True}
        return _serialize_revision(revision)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Item not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_revision_as_of(item_kref: str, tag: str, time: str) -> Dict[str, Any]:
    """Get the revision that had a specific tag at a given point in time.

    This enables time-travel queries for reproducible builds and historical analysis.
    For example: "What was the published revision on June 1st, 2025?"

    Args:
        item_kref: The kref URI of the item
        tag: The tag to query (e.g., 'published', 'approved', 'latest')
        time: Timestamp in YYYYMMDDHHMM format (e.g., '202506011430') or ISO 8601 format (e.g., '2025-06-01T14:30:00Z')
    """
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        revision = item.get_revision_by_time(time, tag=tag)
        if not revision:
            return {"error": f"No revision with tag '{tag}' found at time '{time}'", "not_found": True}
        return _serialize_revision(revision)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Item not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_batch_get_revisions(
    revision_krefs: Optional[List[str]] = None,
    item_krefs: Optional[List[str]] = None,
    tag: str = "latest",
    allow_partial: bool = True,
) -> Dict[str, Any]:
    """Batch-fetch multiple revisions in a single call.

    Supports two modes:
    - **Direct revision krefs**: provide ``revision_krefs`` to fetch specific revisions.
    - **Item krefs + tag**: provide ``item_krefs`` and a ``tag`` to resolve
      that tag (e.g. 'latest', 'published') for each item.

    Returns found revisions and a list of krefs that could not be resolved.
    """
    _ensure_configured()
    try:
        revisions, not_found = kumiho.batch_get_revisions(
            revision_krefs=revision_krefs or [],
            item_krefs=item_krefs or [],
            tag=tag,
            allow_partial=allow_partial,
        )
        return {
            "revisions": [_serialize_revision(r) for r in revisions],
            "not_found": not_found,
            "found_count": len(revisions),
            "requested_count": len(revision_krefs or []) + len(item_krefs or []),
        }
    except grpc.RpcError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Write Operations (use with caution)
# ============================================================================

def tool_create_revision(
    item_kref: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a new revision for an item."""
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        revision = item.create_revision(metadata=metadata or {})
        return {
            "created": True,
            "revision": _serialize_revision(revision),
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"error": "Item not found", "not_found": True}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def tool_tag_revision(revision_kref: str, tag: str) -> Dict[str, Any]:
    """Apply a tag to a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        revision.tag(tag)
        return {
            "tagged": True,
            "revision_kref": revision_kref,
            "tag": tag,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_create_edge(
    source_kref: str,
    target_kref: str,
    edge_type: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create an edge between two revisions."""
    _ensure_configured()
    try:
        source = kumiho.get_revision(source_kref)
        target = kumiho.get_revision(target_kref)
        edge = source.create_edge(target, edge_type, metadata=metadata)
        return {
            "created": True,
            "edge": _serialize_edge(edge),
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Create Operations
# ============================================================================

def tool_create_project(
    name: str,
    description: str = "",
    allow_public: bool = False
) -> Dict[str, Any]:
    """Create a new Kumiho project."""
    _ensure_configured()
    try:
        project = kumiho.create_project(name, description)
        if allow_public:
            project.set_public(True)
        return {
            "created": True,
            "project": _serialize_project(project),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_create_space(
    project_name: str,
    space_name: str,
    parent_path: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new space within a project."""
    _ensure_configured()
    try:
        project = kumiho.get_project(project_name)
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        space = project.create_space(space_name, parent_path=parent_path)
        return {
            "created": True,
            "space": _serialize_space(space),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_create_item(
    space_path: str,
    item_name: str,
    kind: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a new item within a space."""
    _ensure_configured()
    try:
        # space_path should be like "/project/space" or "project/space"
        path = space_path if space_path.startswith("/") else f"/{space_path}"
        # Parse project name from path
        parts = path.strip("/").split("/")
        if len(parts) < 1:
            return {"error": "Invalid space path"}
        project_name = parts[0]
        project = kumiho.get_project(project_name)
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        space = project.get_space(path)
        item = space.create_item(item_name, kind)
        if metadata:
            item.set_metadata(metadata)
        return {
            "created": True,
            "item": _serialize_item(item),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_create_artifact(
    revision_kref: str,
    name: str,
    location: str
) -> Dict[str, Any]:
    """Create an artifact for a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        artifact = revision.create_artifact(name, location)
        return {
            "created": True,
            "artifact": _serialize_artifact(artifact),
        }
    except Exception as e:
        return {"error": str(e)}


def tool_create_bundle(
    space_path: str,
    bundle_name: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a new bundle within a space."""
    _ensure_configured()
    try:
        path = space_path if space_path.startswith("/") else f"/{space_path}"
        # Parse project name from path
        parts = path.strip("/").split("/")
        if len(parts) < 1:
            return {"error": "Invalid space path"}
        project_name = parts[0]
        project = kumiho.get_project(project_name)
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        space = project.get_space(path)
        bundle = space.create_bundle(bundle_name, metadata=metadata)
        return {
            "created": True,
            "bundle": _serialize_item(bundle),  # Bundle is a specialized Item
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Delete Operations
# ============================================================================

def tool_delete_project(
    project_name: str,
    force: bool = False,
    impact_snapshot_id: str = "",
    impact_snapshot_hash: str = "",
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Archive a Project, or perform a two-step snapshot-gated hard-delete."""
    _ensure_configured()
    try:
        project = kumiho.get_client().get_project(
            project_name, include_deprecated=force
        )
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        if force and not (impact_snapshot_id and impact_snapshot_hash and confirmed):
            impact = project.analyze_deletion()
            return {
                "deleted": False,
                "requires_confirmation": True,
                "project_name": project_name,
                "impact_snapshot_id": impact.impact_snapshot_id,
                "impact_snapshot_hash": impact.impact_snapshot_hash,
                "blockers": list(impact.blockers),
                "descendants": list(impact.descendants),
            }
        if force:
            impact = ProjectDeletionImpact(
                impact_snapshot_id=impact_snapshot_id,
                impact_snapshot_hash=impact_snapshot_hash,
                project_id=project.project_id,
                project_name=project.name,
                blockers=[],
                descendants=[],
                created_at="",
            )
            project.hard_delete(impact, confirmed=confirmed)
        else:
            project.delete()
        return {
            "deleted": True,
            "project_name": project_name,
            "force": force,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_delete_space(space_path: str, force: bool = False) -> Dict[str, Any]:
    """Delete a space."""
    _ensure_configured()
    try:
        path = space_path if space_path.startswith("/") else f"/{space_path}"
        # Parse project name from path
        parts = path.strip("/").split("/")
        if len(parts) < 1:
            return {"error": "Invalid space path"}
        project_name = parts[0]
        project = kumiho.get_project(project_name)
        if not project:
            return {"error": f"Project '{project_name}' not found"}
        space = project.get_space(path)
        space.delete(force=force)
        return {
            "deleted": True,
            "space_path": space_path,
            "force": force,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_delete_item(item_kref: str, force: bool = False) -> Dict[str, Any]:
    """Delete an item."""
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        item.delete(force=force)
        return {
            "deleted": True,
            "item_kref": item_kref,
            "force": force,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_delete_revision(revision_kref: str, force: bool = False) -> Dict[str, Any]:
    """Delete a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        revision.delete(force=force)
        return {
            "deleted": True,
            "revision_kref": revision_kref,
            "force": force,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_delete_artifact(artifact_kref: str) -> Dict[str, Any]:
    """Delete an artifact."""
    _ensure_configured()
    try:
        artifact = kumiho.get_artifact(artifact_kref)
        artifact.delete()
        return {
            "deleted": True,
            "artifact_kref": artifact_kref,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_delete_edge(
    source_kref: str,
    target_kref: str,
    edge_type: str
) -> Dict[str, Any]:
    """Delete an edge between two revisions."""
    _ensure_configured()
    try:
        source = kumiho.get_revision(source_kref)
        target = kumiho.get_revision(target_kref)
        source.delete_edge(target, edge_type)
        return {
            "deleted": True,
            "source_kref": source_kref,
            "target_kref": target_kref,
            "edge_type": edge_type,
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Update Operations
# ============================================================================

def tool_untag_revision(revision_kref: str, tag: str) -> Dict[str, Any]:
    """Remove a tag from a revision."""
    _ensure_configured()
    try:
        revision = kumiho.get_revision(revision_kref)
        revision.untag(tag)
        return {
            "untagged": True,
            "revision_kref": revision_kref,
            "tag": tag,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_set_metadata(
    kref: str,
    metadata: Dict[str, str]
) -> Dict[str, Any]:
    """Set metadata on an item or revision."""
    _ensure_configured()
    try:
        # Determine if this is an item or revision kref
        if "?r=" in kref:
            obj = kumiho.get_revision(kref)
        else:
            obj = kumiho.get_item(kref)
        obj.set_metadata(metadata)
        return {
            "updated": True,
            "kref": kref,
            "metadata": metadata,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_deprecate_item(item_kref: str, deprecated: bool = True) -> Dict[str, Any]:
    """Set the deprecated status of an item."""
    _ensure_configured()
    try:
        item = kumiho.get_item(item_kref)
        item.set_deprecated(deprecated)
        return {
            "updated": True,
            "item_kref": item_kref,
            "deprecated": deprecated,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_add_bundle_member(
    bundle_kref: str,
    item_kref: str
) -> Dict[str, Any]:
    """Add an item to a bundle."""
    _ensure_configured()
    try:
        bundle = kumiho.get_bundle(bundle_kref)
        item = kumiho.get_item(item_kref)
        bundle.add_member(item)
        return {
            "added": True,
            "bundle_kref": bundle_kref,
            "item_kref": item_kref,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_remove_bundle_member(
    bundle_kref: str,
    item_kref: str
) -> Dict[str, Any]:
    """Remove an item from a bundle."""
    _ensure_configured()
    try:
        bundle = kumiho.get_bundle(bundle_kref)
        item = kumiho.get_item(item_kref)
        bundle.remove_member(item)
        return {
            "removed": True,
            "bundle_kref": bundle_kref,
            "item_kref": item_kref,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_bundle_members(bundle_kref: str) -> Dict[str, Any]:
    """Get all members of a bundle."""
    _ensure_configured()
    try:
        bundle = kumiho.get_bundle(bundle_kref)
        members = bundle.get_members()
        return {
            "bundle_kref": bundle_kref,
            "members": [
                {
                    "item_kref": m.item_kref.uri if hasattr(m.item_kref, 'uri') else str(m.item_kref),
                    "added_at": m.added_at,
                    "added_by": m.added_by,
                    "added_by_username": m.added_by_username,
                    "added_in_revision": m.added_in_revision,
                }
                for m in members
            ],
            "count": len(members),
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# MCP Server Definition
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    # Read operations - Projects
    {
        "name": "kumiho_list_projects",
        "description": "List all Kumiho projects accessible to the current user. Returns project names, descriptions, and metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "kumiho_get_project",
        "description": "Get details about a specific Kumiho project by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the project to retrieve",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "kumiho_get_spaces",
        "description": "Get spaces (organizational folders) within a Kumiho project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "If true, include nested spaces. Default: false",
                    "default": False,
                },
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "kumiho_get_space",
        "description": "Get a space by its path. Example: /project/space or project/space",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_path": {
                    "type": "string",
                    "description": "The path of the space (e.g., '/project/space' or 'project/space')",
                },
            },
            "required": ["space_path"],
        },
    },
    # Read operations - Items
    {
        "name": "kumiho_get_item",
        "description": "Get a Kumiho item (versioned asset) by its kref URI. Example: kref://project/space/item.kind",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kref": {
                    "type": "string",
                    "description": "The kref URI of the item (e.g., kref://project/space/item.kind)",
                },
            },
            "required": ["kref"],
        },
    },
    {
        "name": "kumiho_search_items",
        "description": "Search for items across Kumiho projects and spaces. Supports filtering by context (project/space path), name, and kind (model, texture, workflow, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context_filter": {
                    "type": "string",
                    "description": "Filter by project or space path. Supports wildcards like 'project-*' or '*/characters/*'",
                    "default": "",
                },
                "name_filter": {
                    "type": "string",
                    "description": "Filter by item name. Supports wildcards like 'hero*'",
                    "default": "",
                },
                "kind_filter": {
                    "type": "string",
                    "description": "Filter by item kind (e.g., 'model', 'texture', 'workflow')",
                    "default": "",
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Whether to include full metadata for each item. Default: false",
                    "default": False,
                },
                "auth_token": {
                    "type": "string",
                    "description": "Internal: bearer token to use for this call (overrides subprocess credentials). Pass the current session token to enable cross-project access.",
                    "default": "",
                },
            },
            "required": [],
        },
    },
    {
        "name": "kumiho_fulltext_search",
        "description": "Full-text fuzzy search across items (Google-like search). Supports automatic typo tolerance and multi-word queries. Results are ranked by relevance score. For STUDIO+ tiers, uses hybrid search (fulltext + vector similarity) when searching revision metadata for improved semantic accuracy. Use this for natural language queries instead of kumiho_search_items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms (supports fuzzy matching). E.g., 'hero model', 'texture character'. Typos are automatically tolerated.",
                },
                "context": {
                    "type": "string",
                    "description": "Restrict to kref prefix (e.g., 'myproject' or 'myproject/assets'). Leave empty to search all.",
                    "default": "",
                },
                "kind": {
                    "type": "string",
                    "description": "Exact kind match (e.g., 'model', 'texture', 'conversation', 'bundle')",
                    "default": "",
                },
                "include_deprecated": {
                    "type": "boolean",
                    "description": "Include soft-deleted items. Default: false",
                    "default": False,
                },
                "include_revision_metadata": {
                    "type": "boolean",
                    "description": "Also search revision tags/metadata (slower but more comprehensive). Default: false",
                    "default": False,
                },
                "include_artifact_metadata": {
                    "type": "boolean",
                    "description": "Also search artifact names/metadata (slower). Default: false",
                    "default": False,
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include full item metadata in results. Default: false",
                    "default": False,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return. Default: 20",
                    "default": 20,
                },
                "auth_token": {
                    "type": "string",
                    "description": "Internal: bearer token to use for this call (overrides subprocess credentials). Pass the current session token to enable cross-project access.",
                    "default": "",
                },
            },
            "required": ["query"],
        },
    },
    # Memory operations (production)
    {
        "name": "kumiho_memory_store",
        "description": "Store a memory entry with one call (space + item + revision + artifact + bundle + edges). By default, searches for an existing similar item and stacks a new revision instead of creating a duplicate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Project name (default: CognitiveMemory)",
                    "default": "CognitiveMemory",
                },
                "space_path": {
                    "type": "string",
                    "description": "Taxonomy space path (e.g., 'friend/john-doe' or '/CognitiveMemory/friend')",
                },
                "space_hint": {
                    "type": "string",
                    "description": "Short taxonomy hint if space_path is not provided",
                },
                "policy_kref": {
                    "type": "string",
                    "description": "Schema item or revision kref to load defaults",
                },
                "memory_item_kind": {
                    "type": "string",
                    "description": (
                        "Item kind for memory entries. Recommended vocabulary: "
                        + ", ".join(DEFAULT_MEMORY_KINDS)
                        + " (a policy_kref may widen it via a 'memory_kinds' "
                        "list, so this is not enforced as a strict enum)."
                    ),
                    "default": "conversation",
                },
                "bundle_name": {
                    "type": "string",
                    "description": "Bundle name (defaults to topic slug)",
                },
                "memory_type": {
                    "type": "string",
                    "description": "Memory type (summary | decision | fact | reflection | error)",
                    "default": "summary",
                },
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "user_text": {"type": "string"},
                "assistant_text": {"type": "string"},
                "artifact_location": {"type": "string"},
                "artifact_name": {"type": "string", "default": "chat_io"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "source_revision_krefs": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata (string values only)",
                },
                "edge_type": {
                    "type": "string",
                    "description": "Edge type for dependencies (default: DERIVED_FROM)",
                    "default": "DERIVED_FROM",
                },
                "stack_revisions": {
                    "type": "boolean",
                    "default": True,
                    "description": (
                        "When true (default), search for existing item with "
                        "similar content and stack revision. False = always "
                        "create new item."
                    ),
                },
            },
            "required": ["user_text"],
        },
    },
    {
        "name": "kumiho_memory_retrieve",
        "description": "Retrieve memory using Google-like fuzzy search with relevance ranking. Supports natural language queries with automatic typo tolerance. Falls back to bundle and pattern search when needed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Project name (default: CognitiveMemory)",
                    "default": "CognitiveMemory",
                },
                "query": {
                    "type": "string",
                    "description": "Natural language search query. Supports fuzzy matching and multi-word queries (e.g., 'conversation about travel', 'meeting notes')",
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional keywords to include in search",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topic names to search for",
                },
                "space_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Restrict search to specific space paths",
                },
                "bundle_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Search within specific bundles",
                },
                "memory_item_kind": {
                    "type": "string",
                    "description": "Item kind for memory entries (default: conversation)",
                    "default": "conversation",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return (default: 5)",
                    "default": 5,
                },
                "mode": {
                    "type": "string",
                    "description": "search (fuzzy) | first (oldest by date) | latest (default: search)",
                    "default": "search",
                },
                "include_revision_metadata": {
                    "type": "boolean",
                    "description": "Also search revision metadata for deeper matching (default: true)",
                    "default": True,
                },
                "memory_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by memory type (e.g. ['decision', 'summary', 'error'])",
                },
            },
            "required": [],
        },
    },
    {
        "name": "kumiho_get_item_revisions",
        "description": "Get all revisions for a Kumiho item. Shows version history with tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item",
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Whether to include full metadata for each revision. Default: false",
                    "default": False,
                },
            },
            "required": ["item_kref"],
        },
    },
    # Read operations - Revisions
    {
        "name": "kumiho_get_revision",
        "description": "Get a specific revision by its kref URI. Example: kref://project/space/item.kind?r=1",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kref": {
                    "type": "string",
                    "description": "The kref URI of the revision (e.g., kref://project/space/item.kind?r=1)",
                },
            },
            "required": ["kref"],
        },
    },
    {
        "name": "kumiho_get_revision_by_tag",
        "description": "Get a revision by its tag (e.g., 'latest', 'published', 'approved').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item",
                },
                "tag": {
                    "type": "string",
                    "description": "The tag to look for (e.g., 'latest', 'published', 'approved')",
                },
            },
            "required": ["item_kref", "tag"],
        },
    },
    {
        "name": "kumiho_get_revision_as_of",
        "description": "Get the revision that had a specific tag at a given point in time. Enables time-travel queries for reproducible builds and historical analysis. Example: 'What was the published revision on June 1st, 2025?'",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item",
                },
                "tag": {
                    "type": "string",
                    "description": "The tag to query (e.g., 'published', 'approved', 'latest')",
                },
                "time": {
                    "type": "string",
                    "description": "Timestamp in YYYYMMDDHHMM format (e.g., '202506011430') or ISO 8601 format (e.g., '2025-06-01T14:30:00Z')",
                },
            },
            "required": ["item_kref", "tag", "time"],
        },
    },
    {
        "name": "kumiho_batch_get_revisions",
        "description": "Batch-fetch multiple revisions in a single call. Two modes: (1) provide revision_krefs to fetch specific revisions, or (2) provide item_krefs + tag to resolve that tag for each item. Returns found revisions and a list of krefs that could not be resolved.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_krefs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of revision kref URIs to fetch directly (e.g., ['kref://proj/space/item.kind?r=1', ...])",
                },
                "item_krefs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of item kref URIs to resolve a tag for (e.g., ['kref://proj/space/item.kind', ...])",
                },
                "tag": {
                    "type": "string",
                    "description": "Tag to resolve when using item_krefs mode (default: 'latest')",
                    "default": "latest",
                },
                "allow_partial": {
                    "type": "boolean",
                    "description": "If true, return partial results when some krefs are not found (default: true)",
                    "default": True,
                },
            },
        },
    },
    # Read operations - Artifacts
    {
        "name": "kumiho_get_artifacts",
        "description": "Get all artifacts (file references) for a revision. Shows file paths/locations without uploading files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision",
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_get_artifact",
        "description": "Get a single artifact by its kref URI. Example: kref://project/space/item.kind?r=1&a=mesh.fbx",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artifact_kref": {
                    "type": "string",
                    "description": "The kref URI of the artifact",
                },
            },
            "required": ["artifact_kref"],
        },
    },
    {
        "name": "kumiho_get_bundle",
        "description": "Get a bundle by its kref URI. Bundles group related items together.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_kref": {
                    "type": "string",
                    "description": "The kref URI of the bundle (e.g., kref://project/space/name.bundle)",
                },
            },
            "required": ["bundle_kref"],
        },
    },
    {
        "name": "kumiho_resolve_kref",
        "description": "Resolve a kref URI to a file location. Returns the actual file path for an artifact or revision's default artifact.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kref": {
                    "type": "string",
                    "description": "The kref URI to resolve",
                },
            },
            "required": ["kref"],
        },
    },
    {
        "name": "kumiho_get_artifacts_by_location",
        "description": "Find all Kumiho artifacts that reference a specific file location. Useful for reverse lookups.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The file path or URI to search for",
                },
            },
            "required": ["location"],
        },
    },
    # Graph traversal - Dependencies and Lineage
    {
        "name": "kumiho_get_dependencies",
        "description": "Get all dependencies of a revision (what it depends on). Traverses the graph to find direct and indirect dependencies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth (1-20). Default: 5",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                },
                "edge_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by edge types (e.g., ['DEPENDS_ON', 'DERIVED_FROM']). Default: all types",
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_get_dependents",
        "description": "Get all dependents of a revision (what depends on it). Useful for understanding downstream impact.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth (1-20). Default: 5",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                },
                "edge_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by edge types. Default: all types",
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_get_provenance_summary",
        "description": "Get a summary of the provenance (lineage) of a revision, including used models, seeds, and parameters from upstream dependencies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision to analyze",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth. Default: 10",
                    "default": 10,
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_analyze_impact",
        "description": "Analyze the impact of changes to a revision. Returns all revisions that would be affected, sorted by proximity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision to analyze",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth. Default: 10",
                    "default": 10,
                },
                "edge_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by edge types. Default: all types",
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_find_path",
        "description": "Find the shortest path between two revisions in the dependency graph. Useful for understanding how assets are connected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_kref": {
                    "type": "string",
                    "description": "The kref URI of the source revision",
                },
                "target_kref": {
                    "type": "string",
                    "description": "The kref URI of the target revision",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum path length to search. Default: 10",
                    "default": 10,
                },
                "edge_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by edge types. Default: all types",
                },
            },
            "required": ["source_kref", "target_kref"],
        },
    },
    {
        "name": "kumiho_get_edges",
        "description": "Get edges (relationships) for a revision. Can filter by direction and edge type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision",
                },
                "direction": {
                    "type": "string",
                    "enum": ["outgoing", "incoming", "both"],
                    "description": "Edge direction: 'outgoing' (what this depends on), 'incoming' (what depends on this), or 'both'. Default: 'both'",
                    "default": "both",
                },
                "edge_type": {
                    "type": "string",
                    "description": "Filter by edge type (e.g., 'DEPENDS_ON', 'DERIVED_FROM')",
                },
            },
            "required": ["revision_kref"],
        },
    },
    # Write operations
    {
        "name": "kumiho_create_revision",
        "description": "Create a new revision for an item. Use this to version an asset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item to create a revision for",
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Optional metadata key-value pairs (e.g., {'artist': 'name', 'software': 'maya'})",
                },
            },
            "required": ["item_kref"],
        },
    },
    {
        "name": "kumiho_tag_revision",
        "description": "Apply a tag to a revision. Common tags: 'approved', 'published', 'ready-for-review'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision to tag",
                },
                "tag": {
                    "type": "string",
                    "description": "The tag to apply",
                },
            },
            "required": ["revision_kref", "tag"],
        },
    },
    {
        "name": "kumiho_create_edge",
        "description": "Create an edge (relationship) between two revisions. Creative provenance uses CREATED_FROM, PRODUCED_BY, DERIVED_FROM, and MIGRATED_FROM. SUPPORTS points from corroborating evidence to the claim it supports. SUPERSEDES is deliberately not offered here: belief revision also demotes the superseded revision and ripples grounding staleness to what depended on it, so it belongs to the memory layer rather than to a bare edge write.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_kref": {
                    "type": "string",
                    "description": "The kref URI of the source revision",
                },
                "target_kref": {
                    "type": "string",
                    "description": "The kref URI of the target revision",
                },
                "edge_type": {
                    "type": "string",
                    "enum": [
                        "DEPENDS_ON",
                        "DERIVED_FROM",
                        "REFERENCED",
                        "CONTAINS",
                        "CREATED_FROM",
                        "PRODUCED_BY",
                        "MIGRATED_FROM",
                        "BELONGS_TO",
                        "SUPPORTS",
                    ],
                    "description": "The type of relationship",
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Optional metadata for the edge",
                },
            },
            "required": ["source_kref", "target_kref", "edge_type"],
        },
    },
    # Create operations
    {
        "name": "kumiho_create_project",
        "description": "Create a new Kumiho project. Projects are top-level containers for spaces and items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the project (URL-safe, e.g., 'my-vfx-project')",
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of the project",
                    "default": "",
                },
                "allow_public": {
                    "type": "boolean",
                    "description": "Whether to allow public access. Default: false",
                    "default": False,
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "kumiho_create_space",
        "description": "Create a new space (folder) within a project. Spaces organize items hierarchically.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "space_name": {
                    "type": "string",
                    "description": "The name of the space to create",
                },
                "parent_path": {
                    "type": "string",
                    "description": "Optional parent path for nested spaces (e.g., '/project/parent-space')",
                },
            },
            "required": ["project_name", "space_name"],
        },
    },
    {
        "name": "kumiho_create_item",
        "description": "Create a new item (versioned asset) within a space. Items can be models, textures, workflows, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_path": {
                    "type": "string",
                    "description": "The path to the space (e.g., 'project/space' or '/project/space')",
                },
                "item_name": {
                    "type": "string",
                    "description": "The name of the item (e.g., 'hero-character')",
                },
                "kind": {
                    "type": "string",
                    "description": "The kind of item (e.g., 'model', 'texture', 'workflow', 'rig')",
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Optional metadata key-value pairs",
                },
            },
            "required": ["space_path", "item_name", "kind"],
        },
    },
    {
        "name": "kumiho_create_artifact",
        "description": "Create an artifact (file reference) for a revision. Files stay on your storage - only the path is tracked.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision to add the artifact to",
                },
                "name": {
                    "type": "string",
                    "description": "The name of the artifact (e.g., 'mesh', 'textures', 'hero.fbx')",
                },
                "location": {
                    "type": "string",
                    "description": "The file path or URI (e.g., '/assets/hero.fbx', 'smb://server/assets/hero.fbx')",
                },
            },
            "required": ["revision_kref", "name", "location"],
        },
    },
    {
        "name": "kumiho_create_bundle",
        "description": "Create a bundle to group related items together. Bundles track membership history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_path": {
                    "type": "string",
                    "description": "The path to the space (e.g., 'project/space')",
                },
                "bundle_name": {
                    "type": "string",
                    "description": "The name of the bundle",
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Optional metadata key-value pairs",
                },
            },
            "required": ["space_path", "bundle_name"],
        },
    },
    # Delete operations
    {
        "name": "kumiho_delete_project",
        "description": "Archive a Project. With force=true, the first call returns an impact snapshot; repeat only after review with that snapshot and confirmed=true.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project to delete",
                },
                "force": {
                    "type": "boolean",
                    "description": "If true, permanently delete. If false, soft-delete (deprecate). Default: false",
                    "default": False,
                },
                "impact_snapshot_id": {
                    "type": "string",
                    "description": "Server-issued UUIDv7 from the preceding force=true preview",
                },
                "impact_snapshot_hash": {
                    "type": "string",
                    "description": "Server-issued sha256 digest from the preceding force=true preview",
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "Explicitly confirms the reviewed impact snapshot",
                    "default": False,
                },
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "kumiho_delete_space",
        "description": "Delete a space. Use force=true to delete even if it contains items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_path": {
                    "type": "string",
                    "description": "The path of the space to delete (e.g., '/project/space')",
                },
                "force": {
                    "type": "boolean",
                    "description": "If true, force delete with contents. Default: false",
                    "default": False,
                },
            },
            "required": ["space_path"],
        },
    },
    {
        "name": "kumiho_delete_item",
        "description": "Delete an item. Use force=true to delete even if it has revisions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item to delete",
                },
                "force": {
                    "type": "boolean",
                    "description": "If true, force delete with all revisions. Default: false",
                    "default": False,
                },
            },
            "required": ["item_kref"],
        },
    },
    {
        "name": "kumiho_delete_revision",
        "description": "Delete a specific revision of an item. Use force=true to delete even if it is published or has artifacts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision to delete",
                },
                "force": {
                    "type": "boolean",
                    "description": "If true, force delete. Default: false",
                    "default": False,
                },
            },
            "required": ["revision_kref"],
        },
    },
    {
        "name": "kumiho_delete_artifact",
        "description": "Delete an artifact from a revision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artifact_kref": {
                    "type": "string",
                    "description": "The kref URI of the artifact to delete",
                },
            },
            "required": ["artifact_kref"],
        },
    },
    {
        "name": "kumiho_delete_edge",
        "description": "Delete an edge (relationship) between two revisions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_kref": {
                    "type": "string",
                    "description": "The kref URI of the source revision",
                },
                "target_kref": {
                    "type": "string",
                    "description": "The kref URI of the target revision",
                },
                "edge_type": {
                    "type": "string",
                    "enum": [
                        "DEPENDS_ON",
                        "DERIVED_FROM",
                        "REFERENCED",
                        "CONTAINS",
                        "CREATED_FROM",
                        "PRODUCED_BY",
                        "MIGRATED_FROM",
                        "BELONGS_TO",
                    ],
                    "description": "The type of relationship to delete",
                },
            },
            "required": ["source_kref", "target_kref", "edge_type"],
        },
    },
    # Update operations
    {
        "name": "kumiho_untag_revision",
        "description": "Remove a tag from a revision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": "The kref URI of the revision",
                },
                "tag": {
                    "type": "string",
                    "description": "The tag to remove",
                },
            },
            "required": ["revision_kref", "tag"],
        },
    },
    {
        "name": "kumiho_set_metadata",
        "description": "Set or update metadata on an item or revision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kref": {
                    "type": "string",
                    "description": "The kref URI of the item or revision",
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Metadata key-value pairs to set",
                },
            },
            "required": ["kref", "metadata"],
        },
    },
    {
        "name": "kumiho_deprecate_item",
        "description": "Set the deprecated status of an item. Deprecated items are hidden from searches.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item",
                },
                "deprecated": {
                    "type": "boolean",
                    "description": "True to deprecate, False to restore. Default: true",
                    "default": True,
                },
            },
            "required": ["item_kref"],
        },
    },
    # Bundle operations
    {
        "name": "kumiho_add_bundle_member",
        "description": "Add an item to a bundle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_kref": {
                    "type": "string",
                    "description": "The kref URI of the bundle",
                },
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item to add",
                },
            },
            "required": ["bundle_kref", "item_kref"],
        },
    },
    {
        "name": "kumiho_remove_bundle_member",
        "description": "Remove an item from a bundle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_kref": {
                    "type": "string",
                    "description": "The kref URI of the bundle",
                },
                "item_kref": {
                    "type": "string",
                    "description": "The kref URI of the item to remove",
                },
            },
            "required": ["bundle_kref", "item_kref"],
        },
    },
    {
        "name": "kumiho_get_bundle_members",
        "description": "Get all items in a bundle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_kref": {
                    "type": "string",
                    "description": "The kref URI of the bundle",
                },
            },
            "required": ["bundle_kref"],
        },
    },
]


# Tool handler dispatch
TOOL_HANDLERS = {
    "kumiho_list_projects": lambda args: tool_list_projects(),
    "kumiho_get_project": lambda args: tool_get_project(args["name"]),
    "kumiho_get_spaces": lambda args: tool_get_spaces(
        args["project_name"],
        args.get("recursive", False),
    ),
    "kumiho_get_space": lambda args: tool_get_space(args["space_path"]),
    "kumiho_get_item": lambda args: tool_get_item(args["kref"]),
    "kumiho_search_items": lambda args: tool_search_items(
        args.get("context_filter", ""),
        args.get("name_filter", ""),
        args.get("kind_filter", ""),
        args.get("include_metadata", False),
        args.get("auth_token", ""),
    ),
    "kumiho_fulltext_search": lambda args: tool_fulltext_search(
        args["query"],
        args.get("context", ""),
        args.get("kind", ""),
        args.get("include_deprecated", False),
        args.get("include_revision_metadata", False),
        args.get("include_artifact_metadata", False),
        args.get("include_metadata", False),
        args.get("limit", 20),
        args.get("auth_token", ""),
    ),
    "kumiho_memory_store": lambda args: tool_memory_store(
        args.get("project", "CognitiveMemory"),
        args.get("space_path", ""),
        args.get("space_hint", ""),
        args.get("policy_kref"),
        args.get("memory_item_kind", "conversation"),
        args.get("bundle_name", ""),
        args.get("memory_type", "summary"),
        args.get("title", ""),
        args.get("summary", ""),
        args.get("user_text", ""),
        args.get("assistant_text", ""),
        args.get("artifact_location", ""),
        args.get("artifact_name", "chat_io"),
        args.get("tags"),
        args.get("source_revision_krefs"),
        args.get("metadata"),
        args.get("edge_type", DERIVED_FROM),
        args.get("stack_revisions", True),
    ),
    "kumiho_memory_retrieve": lambda args: tool_memory_retrieve(
        args.get("project", "CognitiveMemory"),
        args.get("query", ""),
        args.get("keywords"),
        args.get("topics"),
        args.get("space_paths"),
        args.get("bundle_names"),
        args.get("memory_item_kind", "conversation"),
        args.get("limit", 5),
        args.get("mode", "search"),
        args.get("include_revision_metadata", True),
        memory_types=args.get("memory_types"),
    ),
    "kumiho_get_item_revisions": lambda args: tool_get_item_revisions(
        args["item_kref"],
        args.get("include_metadata", False),
    ),
    "kumiho_get_revision": lambda args: tool_get_revision(args["kref"]),
    "kumiho_get_revision_by_tag": lambda args: tool_get_revision_by_tag(
        args["item_kref"],
        args["tag"],
    ),
    "kumiho_get_revision_as_of": lambda args: tool_get_revision_as_of(
        args["item_kref"],
        args["tag"],
        args["time"],
    ),
    "kumiho_batch_get_revisions": lambda args: tool_batch_get_revisions(
        args.get("revision_krefs"),
        args.get("item_krefs"),
        args.get("tag", "latest"),
        args.get("allow_partial", True),
    ),
    "kumiho_get_artifacts": lambda args: tool_get_artifacts(args["revision_kref"]),
    "kumiho_get_artifact": lambda args: tool_get_artifact(args["artifact_kref"]),
    "kumiho_get_bundle": lambda args: tool_get_bundle(args["bundle_kref"]),
    "kumiho_resolve_kref": lambda args: tool_resolve_kref(args["kref"]),
    "kumiho_get_artifacts_by_location": lambda args: tool_get_artifacts_by_location(
        args["location"]
    ),
    "kumiho_get_dependencies": lambda args: tool_get_dependencies(
        args["revision_kref"],
        args.get("max_depth", 5),
        args.get("edge_types"),
    ),
    "kumiho_get_dependents": lambda args: tool_get_dependents(
        args["revision_kref"],
        args.get("max_depth", 5),
        args.get("edge_types"),
    ),
    "kumiho_get_provenance_summary": lambda args: tool_get_provenance_summary(
        args["revision_kref"],
        args.get("max_depth", 10),
    ),
    "kumiho_analyze_impact": lambda args: tool_analyze_impact(
        args["revision_kref"],
        args.get("max_depth", 10),
        args.get("edge_types"),
    ),
    "kumiho_find_path": lambda args: tool_find_path(
        args["source_kref"],
        args["target_kref"],
        args.get("max_depth", 10),
        args.get("edge_types"),
    ),
    "kumiho_get_edges": lambda args: tool_get_edges(
        args["revision_kref"],
        args.get("direction", "both"),
        args.get("edge_type"),
    ),
    "kumiho_create_revision": lambda args: tool_create_revision(
        args["item_kref"],
        args.get("metadata"),
    ),
    "kumiho_tag_revision": lambda args: tool_tag_revision(
        args["revision_kref"],
        args["tag"],
    ),
    "kumiho_create_edge": lambda args: tool_create_edge(
        args["source_kref"],
        args["target_kref"],
        args["edge_type"],
        args.get("metadata"),
    ),
    # Create operations
    "kumiho_create_project": lambda args: tool_create_project(
        args["name"],
        args.get("description", ""),
        args.get("allow_public", False),
    ),
    "kumiho_create_space": lambda args: tool_create_space(
        args["project_name"],
        args["space_name"],
        args.get("parent_path"),
    ),
    "kumiho_create_item": lambda args: tool_create_item(
        args["space_path"],
        args["item_name"],
        args["kind"],
        args.get("metadata"),
    ),
    "kumiho_create_artifact": lambda args: tool_create_artifact(
        args["revision_kref"],
        args["name"],
        args["location"],
    ),
    "kumiho_create_bundle": lambda args: tool_create_bundle(
        args["space_path"],
        args["bundle_name"],
        args.get("metadata"),
    ),
    # Delete operations
    "kumiho_delete_project": lambda args: tool_delete_project(
        args["project_name"],
        args.get("force", False),
        args.get("impact_snapshot_id", ""),
        args.get("impact_snapshot_hash", ""),
        args.get("confirmed", False),
    ),
    "kumiho_delete_space": lambda args: tool_delete_space(
        args["space_path"],
        args.get("force", False),
    ),
    "kumiho_delete_item": lambda args: tool_delete_item(
        args["item_kref"],
        args.get("force", False),
    ),
    "kumiho_delete_revision": lambda args: tool_delete_revision(
        args["revision_kref"],
        args.get("force", False),
    ),
    "kumiho_delete_artifact": lambda args: tool_delete_artifact(
        args["artifact_kref"],
    ),
    "kumiho_delete_edge": lambda args: tool_delete_edge(
        args["source_kref"],
        args["target_kref"],
        args["edge_type"],
    ),
    # Update operations
    "kumiho_untag_revision": lambda args: tool_untag_revision(
        args["revision_kref"],
        args["tag"],
    ),
    "kumiho_set_metadata": lambda args: tool_set_metadata(
        args["kref"],
        args["metadata"],
    ),
    "kumiho_deprecate_item": lambda args: tool_deprecate_item(
        args["item_kref"],
        args.get("deprecated", True),
    ),
    # Bundle operations
    "kumiho_add_bundle_member": lambda args: tool_add_bundle_member(
        args["bundle_kref"],
        args["item_kref"],
    ),
    "kumiho_remove_bundle_member": lambda args: tool_remove_bundle_member(
        args["bundle_kref"],
        args["item_kref"],
    ),
    "kumiho_get_bundle_members": lambda args: tool_get_bundle_members(
        args["bundle_kref"],
    ),
}

# Auto-discover kumiho-memory tools if installed
try:
    from kumiho_memory.mcp_tools import MEMORY_TOOLS, MEMORY_TOOL_HANDLERS  # type: ignore
    TOOLS.extend(MEMORY_TOOLS)
    TOOL_HANDLERS.update(MEMORY_TOOL_HANDLERS)
except ImportError:
    pass
except Exception as _exc:
    import logging as _logging
    _logging.getLogger("kumiho.mcp_server").warning(
        "kumiho-memory auto-discovery failed (non-ImportError): %s", _exc
    )


# ============================================================================
# Tool annotations
# ============================================================================

# MCP tool annotations (MCP spec "Tool Annotations"; Anthropic's connector
# directory requires a ``title`` plus ``readOnlyHint`` or ``destructiveHint``
# on every listed tool). They are advisory hints a client uses to decide how
# much ceremony a call deserves — read-only calls can run unprompted, a
# destructive one should be confirmed — so a wrong hint is not cosmetic.
#
# The four booleans, per spec:
#   readOnlyHint     - does not modify its environment.
#   destructiveHint  - may perform *non-additive* updates (delete, overwrite,
#                      deprecate). Meaningful only when readOnlyHint is false.
#   idempotentHint   - repeating the call with the same arguments adds no
#                      further effect. Meaningful only when readOnlyHint is
#                      false.
#   openWorldHint    - talks to an open, unbounded external world. Uniformly
#                      False here: every tool addresses one closed system, the
#                      caller's own Kumiho graph.
#
# The table covers every tool that can appear in :data:`TOOLS`, including the
# kumiho-memory tools that are appended at import time and the ones gated
# behind env flags (the four ``kumiho_code_*``), so the map does not go blank
# on a deployment where a gate happens to be open. Tests assert the two
# directions: no tool without an annotation, no annotation without a tool.
#
# Two entries deliberately disagree with the hint columns of the connector
# plan's §2.2 table, because the tools disagree with them:
#   * kumiho_memory_space_profile persists versioned space-profile items
#     unless dry_run is passed, so it is not readOnly.
#   * kumiho_memory_dream_state "applies deprecation, tagging, metadata
#     enrichment" — deprecation is the destructive case by definition.
# Both remain in the connector profile exactly as specified; only the honesty
# of their hints changes.

TOOL_ANNOTATIONS: Dict[str, Dict[str, Any]] = {
    # -- Core: read ---------------------------------------------------------
    "kumiho_list_projects": {
        "title": "List projects",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_project": {
        "title": "Get a project",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_spaces": {
        "title": "List spaces",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_space": {
        "title": "Get a space",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_item": {
        "title": "Get an item",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_search_items": {
        "title": "Search items",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_fulltext_search": {
        "title": "Full-text search",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_memory_retrieve": {
        "title": "Retrieve memories",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_item_revisions": {
        "title": "List an item's revisions",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_revision": {
        "title": "Get a revision",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_revision_by_tag": {
        "title": "Get a revision by tag",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_revision_as_of": {
        "title": "Get a revision as of a time",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_batch_get_revisions": {
        "title": "Get several revisions at once",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_artifacts": {
        "title": "List a revision's artifacts",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_artifact": {
        "title": "Get an artifact",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_bundle": {
        "title": "Get a bundle",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_resolve_kref": {
        "title": "Resolve a kref",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_artifacts_by_location": {
        "title": "Find artifacts by file location",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_dependencies": {
        "title": "Get dependencies",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_dependents": {
        "title": "Get dependents",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_provenance_summary": {
        "title": "Summarize provenance",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_analyze_impact": {
        "title": "Analyze change impact",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_find_path": {
        "title": "Find a path between revisions",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_edges": {
        "title": "List edges",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_get_bundle_members": {
        "title": "List bundle members",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    # -- Core: additive writes ---------------------------------------------
    "kumiho_memory_store": {
        "title": "Store a memory",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_create_revision": {
        "title": "Create a revision",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_tag_revision": {
        "title": "Tag a revision",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_create_edge": {
        "title": "Create an edge",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_create_project": {
        "title": "Create a project",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_create_space": {
        "title": "Create a space",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_create_item": {
        "title": "Create an item",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_create_artifact": {
        "title": "Create an artifact",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_create_bundle": {
        "title": "Create a bundle",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_add_bundle_member": {
        "title": "Add a bundle member",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    # -- Core: destructive --------------------------------------------------
    "kumiho_delete_project": {
        "title": "Delete a project",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_delete_space": {
        "title": "Delete a space",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_delete_item": {
        "title": "Delete an item",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_delete_revision": {
        "title": "Delete a revision",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_delete_artifact": {
        "title": "Delete an artifact",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_delete_edge": {
        "title": "Delete an edge",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_untag_revision": {
        "title": "Remove a revision tag",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_set_metadata": {
        # Overwrites the named keys rather than merging beside them.
        "title": "Set metadata",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_deprecate_item": {
        # Title fixed by the connector plan: this is the user-facing "forget"
        # verb, and the directory shows the title, not the tool name.
        "title": "Forget a memory",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_remove_bundle_member": {
        "title": "Remove a bundle member",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    # -- kumiho-memory: working memory --------------------------------------
    "kumiho_chat_add": {
        "title": "Add to the chat buffer",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_chat_get": {
        "title": "Read the chat buffer",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_chat_clear": {
        "title": "Clear the chat buffer",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": True, "openWorldHint": False,
    },
    # -- kumiho-memory: lifecycle -------------------------------------------
    "kumiho_memory_engage": {
        "title": "Engage memory before responding",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_memory_recall": {
        "title": "Recall memories",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_memory_reflect": {
        "title": "Reflect and capture memories",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_ingest": {
        "title": "Ingest a user message",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_add_response": {
        "title": "Buffer an assistant response",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_consolidate": {
        "title": "Consolidate the session into long-term memory",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_discover_edges": {
        "title": "Discover memory relationships",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_store_execution": {
        "title": "Store an execution outcome",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_dream_state": {
        # Deprecates, retags and rewrites metadata across the graph. See the
        # §2.2 note above: additive it is not.
        "title": "Run a Dream State consolidation cycle",
        "readOnlyHint": False, "destructiveHint": True,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_space_profile": {
        # Persists versioned space-profile items unless dry_run is set, so it
        # is an additive write, not a read. See the §2.2 note above.
        "title": "Profile memory spaces",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_memory_decompose": {
        "title": "Decompose a memory into the typed graph",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    # -- kumiho-memory: Decision Memory (code) ------------------------------
    "kumiho_code_why": {
        "title": "Explain why code is the way it is",
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    },
    "kumiho_code_capture": {
        "title": "Capture a code decision",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_code_ingest": {
        "title": "Mine a commit range for decisions",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
    "kumiho_code_mine_session": {
        "title": "Mine this session for code decisions",
        "readOnlyHint": False, "destructiveHint": False,
        "idempotentHint": False, "openWorldHint": False,
    },
}

#: The keys every :data:`TOOL_ANNOTATIONS` entry must carry.
_ANNOTATION_FIELDS = (
    "title",
    "readOnlyHint",
    "destructiveHint",
    "idempotentHint",
    "openWorldHint",
)

# ``ToolAnnotations`` and ``Tool.title`` arrived after the oldest mcp this
# package supports (>=1.10.0), and mcp 2.x renamed model fields wholesale. Both
# are detected by introspection rather than by version, exactly as
# ``_MCP_HAS_DECORATORS`` is: an old or vendored SDK then serves unannotated
# tools instead of failing to construct.
if MCP_AVAILABLE:
    try:
        from mcp.types import ToolAnnotations as _ToolAnnotations  # type: ignore
    except Exception:  # pragma: no cover - only on pre-annotation mcp builds
        _ToolAnnotations = None  # type: ignore[assignment]
    _TOOL_MODEL_FIELDS = set(getattr(Tool, "model_fields", {}) or {})
else:  # pragma: no cover - exercised only without the mcp extra
    _ToolAnnotations = None  # type: ignore[assignment]
    _TOOL_MODEL_FIELDS = set()

_TOOL_SUPPORTS_ANNOTATIONS = _ToolAnnotations is not None and "annotations" in _TOOL_MODEL_FIELDS
_TOOL_SUPPORTS_TITLE = "title" in _TOOL_MODEL_FIELDS


def _tool_annotations(name: str) -> Optional[Any]:
    """Build the ``ToolAnnotations`` model for *name*, or ``None``."""
    spec = TOOL_ANNOTATIONS.get(name)
    if spec is None or not _TOOL_SUPPORTS_ANNOTATIONS:
        return None
    try:
        # camelCase keyword names: they are the field names on mcp 1.x and the
        # aliases on 2.x, so one spelling populates both.
        return _ToolAnnotations(  # type: ignore[misc]
            title=spec["title"],
            readOnlyHint=spec["readOnlyHint"],
            destructiveHint=spec["destructiveHint"],
            idempotentHint=spec["idempotentHint"],
            openWorldHint=spec["openWorldHint"],
        )
    except Exception as exc:  # pragma: no cover - shape change in a future mcp
        logger.warning("Could not build annotations for tool '%s': %s", name, exc)
        return None


def _build_tool(spec: Dict[str, Any]) -> "Tool":
    """Turn one :data:`TOOLS` entry into an mcp ``Tool``, annotations included.

    Used by both registration branches, so the 1.x decorator path and the 2.x
    ``on_*`` path cannot advertise different metadata for the same tool.
    """
    kwargs: Dict[str, Any] = {
        "name": spec["name"],
        "description": spec["description"],
        "inputSchema": spec["inputSchema"],
    }
    annotation = TOOL_ANNOTATIONS.get(spec["name"])
    if annotation is not None:
        if _TOOL_SUPPORTS_TITLE:
            kwargs["title"] = annotation["title"]
        built = _tool_annotations(spec["name"])
        if built is not None:
            kwargs["annotations"] = built
    else:
        # Not fatal — a third party can append to TOOLS — but the directory
        # requires a title on everything listed, so say so once.
        logger.warning("Tool '%s' has no entry in TOOL_ANNOTATIONS", spec["name"])
    return Tool(**kwargs)


# ============================================================================
# Tool profiles
# ============================================================================

#: The hosted connector's curated surface (connector plan §2.2). Ordered
#: read / additive-write / destructive, which is also the order the directory
#: listing presents them in.
CONNECTOR_PROFILE_TOOLS: Tuple[str, ...] = (
    # Read
    "kumiho_memory_engage",
    "kumiho_memory_recall",
    "kumiho_memory_retrieve",
    "kumiho_memory_space_profile",
    "kumiho_chat_get",
    "kumiho_search_items",
    "kumiho_get_item",
    "kumiho_get_revision_by_tag",
    "kumiho_list_projects",
    "kumiho_get_spaces",
    "kumiho_get_provenance_summary",
    # Write
    "kumiho_memory_reflect",
    "kumiho_memory_store",
    "kumiho_memory_consolidate",
    "kumiho_memory_decompose",
    "kumiho_memory_dream_state",
    "kumiho_create_space",
    # Destructive
    "kumiho_deprecate_item",
    "kumiho_chat_clear",
)

PROFILE_FULL = "full"
PROFILE_CONNECTOR = "connector"

#: Every accepted value of the ``profile`` argument / ``KUMIHO_MCP_TOOL_PROFILE``.
TOOL_PROFILES: Tuple[str, ...] = (PROFILE_FULL, PROFILE_CONNECTOR)

_PROFILE_TOOL_NAMES: Dict[str, frozenset] = {
    PROFILE_CONNECTOR: frozenset(CONNECTOR_PROFILE_TOOLS),
}


def resolve_tool_profile(profile: Optional[str] = None) -> str:
    """Normalize an explicit profile, falling back to the environment.

    ``None`` means "unspecified", not "full": it defers to
    ``KUMIHO_MCP_TOOL_PROFILE`` so a deployment can pick the profile without
    touching the code that constructs the server. An empty or whitespace-only
    value on either path means full, which keeps ``KUMIHO_MCP_TOOL_PROFILE=``
    from being a silent misconfiguration.
    """
    raw = profile if profile is not None else os.environ.get("KUMIHO_MCP_TOOL_PROFILE", "")
    name = (raw or "").strip().lower()
    if not name:
        return PROFILE_FULL
    if name not in TOOL_PROFILES:
        raise ValueError(
            f"Unknown MCP tool profile {raw!r}. "
            f"Valid profiles: {', '.join(repr(p) for p in TOOL_PROFILES)}."
        )
    return name


def profile_tool_names(profile: str) -> Optional[frozenset]:
    """The names *profile* admits, or ``None`` for "everything in TOOLS"."""
    return _PROFILE_TOOL_NAMES.get(profile)


def tools_for_profile(profile: str) -> List[Dict[str, Any]]:
    """The :data:`TOOLS` entries *profile* exposes.

    Read from :data:`TOOLS` on every call rather than snapshotted at server
    construction. ``TOOLS`` is a module-level list that kumiho-memory *extends
    at import time* — with a further two extensions gated behind env flags —
    so a snapshot would silently depend on import order, and a filter built
    from one would go stale.
    """
    allowed = profile_tool_names(profile)
    if allowed is None:
        return list(TOOLS)
    return [t for t in TOOLS if t["name"] in allowed]


# ============================================================================
# Connector instructions
# ============================================================================

# Server ``instructions`` are handed to the model once, at initialize. On the
# stdio plugin path the engage/reflect protocol arrives as a skill plus
# SessionStart hooks; a remote connector has neither, so the protocol has to
# travel with the server or it does not travel at all. Distilled from
# kumiho-plugins/claude/skills/kumiho-memory/SKILL.md ("Two Reflexes",
# "Memory Discipline"), minus everything that assumes a local host: artifact
# files, transcript mining, the session-id card, skill discovery.
CONNECTOR_INSTRUCTIONS = """\
Kumiho Memory gives you persistent, graph-native memory across conversations. \
This is a remote connector: there are no hooks, no skills and no local files, \
so this protocol is the whole of it. Run it yourself.

FIRST TURN — identity bootstrap, once per conversation.
Before answering the first message, call kumiho_get_revision_by_tag(
item_kref="kref://CognitiveMemory/personal/agent.instruction", tag="published").
Adopt whatever it returns: your name, the user's name, language, tone, \
verbosity, standing rules. If it is not found, this is a first meeting: ask \
the user three short questions in chat — what to call them, how they want you \
to work (tone, length, language), and what they are working on — wait for the \
answers, then store them with kumiho_memory_reflect using space_hint \
"personal". Never invent the answers and never re-run this check later in the \
conversation. An auth or connection error is not a first meeting: say memory \
is unavailable and carry on without it.

ENGAGE — before you respond.
When the user's message touches anything that might have history, call \
kumiho_memory_engage(query: <derived from their message>) once, before \
answering. At most one engage per response; identical queries within five \
seconds are deduplicated server-side. Skip it when the answer is already \
visible in this conversation. Use graph_augmented: true for indirect or \
chain-of-decision questions. Keep the returned source_krefs for reflect. \
Compare each result's created_at with today's date and express age naturally \
("last Tuesday", "about two weeks ago"); recent memories outrank stale ones.

REFLECT — after you respond.
After a substantive answer, call kumiho_memory_reflect(response: <your reply>, \
captures: [...], source_krefs: [...]). Each capture is {type, title, content, \
space_hint}, where type is one of decision, preference, fact, correction, \
architecture, skill, creative. Capture the user's decisions, preferences, \
facts and corrections, and your own substantive output — architecture calls, \
bug resolutions, long drafts. Skip trivia, uncommitted brainstorming, \
credentials and secrets; on a trivial turn call reflect with no captures, to \
buffer the response only.
space_hint is not optional. An unrouted capture lands at the project root, \
where automatic revision stacking can fuse it onto an unrelated months-old \
item. Reuse a space the graph already shows you — engage results come back as \
krefs shaped kref://<project>/<space>/<item>.<kind> — and copy the name \
exactly, capitalization included. When none fits, use the capture's type: \
decisions, facts, preferences, corrections, personal.
Titles carry absolute dates — "Chose gRPC on 2026-03-27", never "today".

SPEAK, DON'T NARRATE.
Weave memory into the answer: "Since you prefer concise output...". Never say \
"let me check my memory", "my memory shows", "I've saved that", or otherwise \
describe the plumbing. You simply know, and you simply remember.

SESSIONS.
Never invent a session_id. Omit it and the server resolves one; every result \
echoes back the session_id and session_id_source it used. Pass one only when a \
tool already reported it to you in this conversation.

CONSOLIDATE.
When the user signals the end (goodbye, "that's all", "thanks, done") or after \
roughly twenty exchanges, call kumiho_memory_consolidate(summary: {...}) with a \
summary you write yourself — you have the whole conversation, and this path \
needs no external model. Include title, summary, key events, knowledge (facts, \
decisions, actions, open questions) and classification (topics, entities). \
Close by naming what is still open.

FORGETTING.
When the user says "forget X", locate the item and call \
kumiho_deprecate_item(item_kref=...) right away, then confirm plainly. Be \
honest about what you remember; only summaries are stored, never raw \
transcripts.

WHEN IT PAYS.
After a substantive exchange, kumiho_memory_decompose(kref: <from reflect or \
consolidate>, entities, facts, relations) builds the typed graph so later \
recall can bridge memories through shared entities. Distill from the stored \
summary, a handful of each.\
"""


# ============================================================================
# MCP Server Implementation
# ============================================================================

_RESOURCE_MIME_TYPE = "application/json"


def _validate_tool_input(name: str, arguments: dict) -> Optional[str]:
    """Check ``arguments`` against a tool's inputSchema, mcp 1.x style.

    Returns the client-facing error message, or ``None`` when the arguments
    are acceptable. Only the mcp 2.x branch calls this; on 1.x the SDK does it
    for us (see ``_MCP_HAS_DECORATORS``) — but only from mcp 1.10.0, which is
    why that is the declared floor in pyproject rather than a rounder number.

    The schema is read from :data:`TOOLS` rather than off a constructed
    ``Tool`` model on purpose. mcp 2.0 renamed the model fields camelCase to
    snake_case (``inputSchema`` to ``input_schema``), so any code that *reads*
    a field off an mcp model needs a version-agnostic accessor; reading the
    plain dict we built the model from needs none.

    Mirrors mcp 1.x on the two edge cases: a tool that isn't listed is passed
    through unvalidated with a warning, and only the first failure is reported.
    """
    if _jsonschema is None:  # pragma: no cover - jsonschema ships with mcp
        return None

    schema = next((t["inputSchema"] for t in TOOLS if t["name"] == name), None)
    if schema is None:
        logger.warning("Tool '%s' not listed, no validation will be performed", name)
        return None

    try:
        _jsonschema.validate(instance=arguments, schema=schema)
    except _jsonschema.ValidationError as e:
        return f"Input validation error: {e.message}"
    except Exception as e:
        # An unusable schema (SchemaError, unresolvable $ref) must not escape:
        # mcp 1.x wrapped the whole dispatch in a try and turned this into an
        # error result, so letting it propagate here would be a 1.x/2.x
        # divergence — the client would get a JSON-RPC error instead of a tool
        # result. Every schema in TOOLS is well-formed, but the kumiho-memory
        # auto-discovery block appends third-party tools at import time.
        logger.warning("Tool '%s' has an unusable inputSchema: %s", name, e)
        return f"Input validation error: {e}"
    return None


def create_mcp_server(
    profile: Optional[str] = None,
    instructions: Optional[str] = None,
) -> "Server":
    """Create and configure the Kumiho MCP server.

    The six handlers are defined once, in the shapes mcp 1.x expects, and are
    either registered through the 1.x decorators or wrapped into the
    ``(ctx, params) -> ResultModel`` shape mcp 2.0 wants. Keeping one copy of
    each body is what stops the two branches from drifting apart.

    Args:
        profile: Which tool surface to expose. ``None`` defers to
            ``KUMIHO_MCP_TOOL_PROFILE`` and then to ``"full"`` — today's whole
            tool list, which is what the stdio plugin gets. ``"connector"``
            exposes the curated hosted set (:data:`CONNECTOR_PROFILE_TOOLS`).
            An unrecognized name raises ``ValueError`` rather than silently
            serving everything: a typo in a deployment's env would otherwise
            publish every destructive tool to a public connector.
        instructions: Server instructions returned in the MCP ``initialize``
            result. Defaults to :data:`CONNECTOR_INSTRUCTIONS` for the
            connector profile and to nothing otherwise, because the stdio
            plugin already carries the protocol as a skill and a second copy
            would just spend the user's context twice.

    Nothing here starts the orphan watchdog or otherwise assumes a stdio child
    process — that belongs to :func:`main`. A hosted server builds many of
    these inside a long-lived web process, where a watchdog would watch the
    wrong parent and ``os._exit`` the whole service.
    """
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP SDK not installed. Install with: pip install mcp"
        )

    active_profile = resolve_tool_profile(profile)
    if instructions is None and active_profile == PROFILE_CONNECTOR:
        instructions = CONNECTOR_INSTRUCTIONS

    allowed_names = profile_tool_names(active_profile)
    if allowed_names is not None:
        # Named-but-absent means an optional dependency is missing or a gate is
        # closed (the kumiho-memory tools are appended at import time, and some
        # only when their env flag is set). Serving the rest is right; doing it
        # silently is not — a connector quietly short of kumiho_memory_reflect
        # looks like a model failure, not a deployment one.
        missing = sorted(n for n in allowed_names if n not in TOOL_HANDLERS)
        if missing:
            logger.warning(
                "Tool profile '%s' names %d tool(s) that are not registered: %s",
                active_profile, len(missing), ", ".join(missing),
            )

    async def list_tools() -> List[Tool]:
        """List the tools the active profile exposes."""
        return [_build_tool(t) for t in tools_for_profile(active_profile)]

    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        """Handle tool invocations."""
        logger.debug(f"Tool call: {name} with args: {arguments}")

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}),
            )]

        # Filtering the listing is not access control: a client can call any
        # name it likes, and a model that saw the full surface in an earlier
        # session will. Checked *after* the handler lookup so the two answers
        # stay distinguishable — "no such tool" and "that tool exists but this
        # deployment does not offer it" call for different next moves, and the
        # tool list is public either way.
        if allowed_names is not None and name not in allowed_names:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": (
                        f"Tool '{name}' is not available in the "
                        f"'{active_profile}' tool profile."
                    ),
                    "profile": active_profile,
                }),
            )]

        try:
            # Run the tool handler (may be blocking gRPC call)
            # Use asyncio.to_thread to propagate contextvars (like kumiho.use_client)
            result = await asyncio.to_thread(handler, arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str),
            )]
        except Exception as e:
            logger.exception(f"Tool {name} failed")
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}),
            )]

    async def list_resources() -> List[Resource]:
        """List available resources (projects as resources)."""
        try:
            _ensure_configured()
            projects = kumiho.get_projects()
            return [
                Resource(
                    uri=f"kumiho://project/{p.name}",
                    name=p.name,
                    description=p.description or f"Kumiho project: {p.name}",
                    mimeType=_RESOURCE_MIME_TYPE,
                )
                for p in projects
            ]
        except Exception as e:
            logger.warning(f"Failed to list resources: {e}")
            return []

    async def read_resource(uri: Any) -> List[ReadResourceContents]:
        """Read a resource by URI.

        ``uri`` arrives as a pydantic ``AnyUrl``, not a ``str`` — both majors
        hand over ``params.uri`` untouched, and ``AnyUrl`` has no ``.startswith``
        (kumiho-SDKs#146). Coerce before matching.

        Returning ``ReadResourceContents`` rather than a bare ``str`` keeps the
        declared ``application/json`` mime type on the wire (a bare ``str``
        becomes ``text/plain``) and is the non-deprecated 1.x shape.

        The name is percent-decoded because the two majors stringify ``AnyUrl``
        differently: mcp 1.x escapes non-ASCII and spaces, so a Hangul or
        spaced project name slices out as ``%ED%95%9C...`` and never matches,
        while mcp 2.x returns it verbatim. Decoding normalizes both.
        """
        uri = str(uri)
        if uri.startswith("kumiho://project/"):
            project_name = unquote(uri[len("kumiho://project/"):])
            # Use asyncio.to_thread to propagate contextvars
            result = await asyncio.to_thread(tool_get_project, project_name)
            return [ReadResourceContents(
                content=json.dumps(result, indent=2, default=str),
                mime_type=_RESOURCE_MIME_TYPE,
            )]

        raise ValueError(f"Unknown resource URI: {uri}")

    async def list_prompts() -> List[Prompt]:
        """List available prompts."""
        return [
            Prompt(
                name="analyze_asset",
                description="Analyze a Kumiho asset's dependencies and impact",
                arguments=[
                    PromptArgument(
                        name="kref",
                        description="The kref URI of the asset to analyze",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="find_assets",
                description="Find assets matching criteria",
                arguments=[
                    PromptArgument(
                        name="kind",
                        description="Asset kind (model, texture, workflow, etc.)",
                        required=False,
                    ),
                    PromptArgument(
                        name="project",
                        description="Project name to search in",
                        required=False,
                    ),
                ],
            ),
        ]
    
    async def get_prompt(name: str, arguments: Optional[dict] = None) -> GetPromptResult:
        """Get a prompt by name."""
        args = arguments or {}
        
        if name == "analyze_asset":
            kref = args.get("kref", "")
            return GetPromptResult(
                description=f"Analyze asset: {kref}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"""Analyze the Kumiho asset at {kref}:

1. First, get the revision details using kumiho_get_revision
2. Get all artifacts using kumiho_get_artifacts  
3. Analyze dependencies using kumiho_get_dependencies
4. Check impact using kumiho_analyze_impact
5. Summarize the asset's role in the dependency graph"""
                        ),
                    ),
                ],
            )
        
        if name == "find_assets":
            kind = args.get("kind", "")
            project = args.get("project", "")
            return GetPromptResult(
                description=f"Find assets: kind={kind}, project={project}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"""Find Kumiho assets with these criteria:
- Kind: {kind or 'any'}
- Project: {project or 'all projects'}

Use kumiho_search_items to find matching assets and summarize the results."""
                        ),
                    ),
                ],
            )
        
        raise ValueError(f"Unknown prompt: {name}")

    # ``version`` is kumiho's own. Passing none makes mcp 1.x advertise the mcp
    # SDK's version as kumiho's, and mcp 2.0 advertise an empty string
    # (kumiho-SDKs#147). Both majors accept it as a keyword.
    server_kwargs: Dict[str, Any] = {"version": kumiho.__version__}
    if instructions:
        if _SERVER_SUPPORTS_INSTRUCTIONS:
            server_kwargs["instructions"] = instructions
        else:  # pragma: no cover - only on mcp builds without the keyword
            logger.warning(
                "The installed mcp SDK's Server takes no 'instructions' "
                "keyword; the connector protocol will not reach the client."
            )

    if _MCP_HAS_DECORATORS:
        server = Server("kumiho-mcp", **server_kwargs)
        server.list_tools()(list_tools)
        server.call_tool()(call_tool)
        server.list_resources()(list_resources)
        server.read_resource()(read_resource)
        server.list_prompts()(list_prompts)
        server.get_prompt()(get_prompt)
        return server

    if _jsonschema is None:  # pragma: no cover - jsonschema ships with mcp
        logger.warning(
            "jsonschema is unavailable: tool input will NOT be validated. "
            "Reinstall with: pip install 'kumiho[mcp]'"
        )

    # mcp 2.x. Every handler takes (ctx, params) and must return the full
    # result model — the runner rejects a bare list or string with
    # "handler returned {type}; expected BaseModel, dict, or None". ``params``
    # is None for the un-parameterized list methods.
    async def on_list_tools(ctx: Any, params: Any) -> "ListToolsResult":
        return ListToolsResult(tools=await list_tools())

    async def on_call_tool(ctx: Any, params: Any) -> "CallToolResult":
        arguments = params.arguments or {}
        # Skip validation for a tool this profile hides, so both majors answer
        # a hidden call the same way: with the profile rejection ``call_tool``
        # produces, never with a schema complaint about a tool that is not on
        # offer in the first place.
        if allowed_names is None or params.name in allowed_names:
            error = _validate_tool_input(params.name, arguments)
            if error is not None:
                return CallToolResult(
                    content=[TextContent(type="text", text=error)],
                    isError=True,
                )
        return CallToolResult(
            content=list(await call_tool(params.name, arguments)),
            isError=False,
        )

    async def on_list_resources(ctx: Any, params: Any) -> "ListResourcesResult":
        return ListResourcesResult(resources=await list_resources())

    async def on_read_resource(ctx: Any, params: Any) -> "ReadResourceResult":
        contents = await read_resource(params.uri)
        return ReadResourceResult(contents=[
            TextResourceContents(
                uri=params.uri,
                text=c.content,
                mimeType=c.mime_type or "text/plain",
            )
            for c in contents
        ])

    async def on_list_prompts(ctx: Any, params: Any) -> "ListPromptsResult":
        return ListPromptsResult(prompts=await list_prompts())

    async def on_get_prompt(ctx: Any, params: Any) -> "GetPromptResult":
        return await get_prompt(params.name, params.arguments)

    # Registering all six advertises the same capabilities as the 1.x branch:
    # get_capabilities still derives them from which methods are registered.
    return Server(
        "kumiho-mcp",
        **server_kwargs,
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
        on_list_resources=on_list_resources,
        on_read_resource=on_read_resource,
        on_list_prompts=on_list_prompts,
        on_get_prompt=on_get_prompt,
    )


# ============================================================================
# Process lifecycle hardening
# ============================================================================

def _windows_parent_pid() -> Optional[int]:
    """Return the parent PID via NtQueryInformationProcess (Windows only)."""
    import ctypes
    from ctypes import wintypes

    class _PROCESS_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("Reserved1", ctypes.c_void_p),
            ("PebBaseAddress", ctypes.c_void_p),
            ("Reserved2", ctypes.c_void_p * 2),
            ("UniqueProcessId", ctypes.c_void_p),
            ("InheritedFromUniqueProcessId", ctypes.c_void_p),
        ]

    try:
        ntdll = ctypes.WinDLL("ntdll")
        kernel32 = ctypes.WinDLL("kernel32")
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        ntdll.NtQueryInformationProcess.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.ULONG,
            ctypes.POINTER(wintypes.ULONG),
        ]
        pbi = _PROCESS_BASIC_INFORMATION()
        ret_len = wintypes.ULONG()
        status = ntdll.NtQueryInformationProcess(
            kernel32.GetCurrentProcess(),
            0,  # ProcessBasicInformation
            ctypes.byref(pbi),
            ctypes.sizeof(pbi),
            ctypes.byref(ret_len),
        )
        if status != 0 or not pbi.InheritedFromUniqueProcessId:
            return None
        return int(pbi.InheritedFromUniqueProcessId)
    except Exception:
        return None


def _exit_orphaned(pid: int) -> None:
    # A dead ancestor usually means dead stderr too: the farewell message
    # is best-effort, and os._exit must run no matter what the print does.
    try:
        print(
            f"[kumiho-mcp] Watched ancestor process {pid} exited; shutting down.",
            file=sys.stderr,
            flush=True,
        )
    except BaseException:
        pass
    finally:
        os._exit(0)


def _select_watch_pids(
    table: Dict[int, Tuple[int, str]],
    own_pid: int,
    max_depth: int = 6,
) -> Tuple[List[int], Optional[int]]:
    """Pick which ancestor PIDs the Windows watchdog must watch.

    ``table`` maps pid -> (parent pid, lowercase exe basename) for every
    live process (a Toolhelp snapshot). Watching only the direct parent is
    not enough: on python.org Windows installs the venv's
    ``Scripts\\python.exe`` is a redirecting stub that runs the base
    interpreter as a separate child, so the real server is a *grandchild*
    (or deeper) of the launcher::

        client (claude/node)                 <- watched (last hop)
          └─ run_kumiho_mcp.py launcher      <- watched
               └─ venv Scripts\\python.exe   <- watched (redirector stub)
                    └─ base python.exe -m kumiho.mcp_server   <- this process

    We watch the contiguous run of python-named ancestors (stubs and
    launcher hops — session plumbing whose death always means the session
    is dead) plus the first non-python ancestor (the client), and stop
    there: anything further (terminal, explorer) can die and restart
    without invalidating the session.

    Returns ``(watch_pids, broken_pid)``; a non-None ``broken_pid`` means
    a recorded ancestor is already gone — the chain is broken and this
    process is already orphaned.
    """
    watch: List[int] = []
    seen = {own_pid}
    child = own_pid
    for _ in range(max_depth):
        entry = table.get(child)
        if entry is None:
            break
        ppid = entry[0]
        if not ppid or ppid in seen:
            break  # unknown or cyclic (recycled-PID loop): stop here
        if ppid not in table:
            return watch, ppid
        watch.append(ppid)
        seen.add(ppid)
        exe = table[ppid][1]
        if not exe.startswith(("python", "py.exe")):
            break
        child = ppid
    return watch, None


def _windows_process_table() -> Dict[int, Tuple[int, str]]:
    """pid -> (parent pid, lowercase exe basename) via a Toolhelp snapshot."""
    import ctypes
    from ctypes import wintypes

    class _PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),  # ULONG_PTR
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    table: Dict[int, Tuple[int, str]] = {}
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        kernel32.Process32FirstW.restype = wintypes.BOOL
        kernel32.Process32FirstW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        kernel32.Process32NextW.restype = wintypes.BOOL
        kernel32.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]

        TH32CS_SNAPPROCESS = 0x00000002
        snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if not snap or snap == ctypes.c_void_p(-1).value:
            return {}
        try:
            entry = _PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
            ok = kernel32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                table[int(entry.th32ProcessID)] = (
                    int(entry.th32ParentProcessID),
                    entry.szExeFile.lower(),
                )
                ok = kernel32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            kernel32.CloseHandle(snap)
    except Exception:
        return {}
    return table


def _start_windows_watchdog() -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.WaitForMultipleObjects.restype = wintypes.DWORD
    kernel32.WaitForMultipleObjects.argtypes = [
        wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p),
        wintypes.BOOL, wintypes.DWORD,
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.GetProcessTimes.argtypes = [ctypes.c_void_p] + (
        [ctypes.POINTER(wintypes.FILETIME)] * 4
    )
    SYNCHRONIZE = 0x00100000
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    INFINITE = 0xFFFFFFFF
    ERROR_INVALID_PARAMETER = 87

    def _creation_time(proc_handle: int) -> Optional[int]:
        times = (wintypes.FILETIME * 4)()
        ok = kernel32.GetProcessTimes(
            proc_handle,
            ctypes.byref(times[0]), ctypes.byref(times[1]),
            ctypes.byref(times[2]), ctypes.byref(times[3]),
        )
        if not ok:
            return None
        return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime

    watch_pids, broken_pid = _select_watch_pids(
        _windows_process_table(), os.getpid()
    )
    if broken_pid is not None:
        # A recorded ancestor no longer exists: the launch chain broke
        # while this module was importing — already the orphan case.
        _exit_orphaned(broken_pid)
    if not watch_pids:
        # Snapshot unavailable: fall back to watching the direct parent.
        ppid = _windows_parent_pid()
        if not ppid:
            return
        watch_pids = [ppid]

    own_created = _creation_time(kernel32.GetCurrentProcess())
    handles: List[int] = []
    watched: List[int] = []
    for pid in watch_pids:
        handle = kernel32.OpenProcess(
            SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            if ctypes.get_last_error() == ERROR_INVALID_PARAMETER:
                # No such PID: that ancestor died since the snapshot.
                _exit_orphaned(pid)
            continue  # unopenable (access denied, ...): skip this hop
        created = _creation_time(handle)
        if created and own_created and created > own_created:
            # A real ancestor is strictly older than this process, so
            # this PID was recycled: the actual ancestor is already gone.
            _exit_orphaned(pid)
        handles.append(handle)
        watched.append(pid)

    if not handles:
        return
    handle_array = (ctypes.c_void_p * len(handles))(*handles)

    def _watch() -> None:
        ret = kernel32.WaitForMultipleObjects(
            len(handles), handle_array, False, INFINITE
        )
        if 0 <= ret < len(handles):  # WAIT_OBJECT_0 + index
            _exit_orphaned(watched[ret])
        # Any other result (e.g. WAIT_FAILED) is an ambiguous signal:
        # fail open rather than ever self-killing a healthy server.

    threading.Thread(
        target=_watch, name="kumiho-orphan-watchdog", daemon=True
    ).start()


def _start_orphan_watchdog() -> None:
    """Exit when the parent process dies, so a dead client or launcher can
    never strand a live server.

    On Windows, MCP clients spawn this server behind a launcher process
    (e.g. kumiho-plugins' ``run_kumiho_mcp.py``), and a venv's
    ``Scripts\\python.exe`` adds a further redirector-stub hop, so the
    real server can be a grandchild or deeper. ``TerminateProcess`` on
    any hop does not kill its children, and a pipe handle leaked by a
    still-running client suppresses the stdin EOF a well-behaved server
    would exit on — so orphaned servers accumulate across session
    restarts (kumiho-plugins#25). Coverage:

    - Windows: block on the launching ancestor chain's process handles
      (event-driven, ``WaitForMultipleObjects``); the chain is the
      contiguous python-named ancestors plus the first non-python one
      (the client) — see :func:`_select_watch_pids`.
    - POSIX: poll ``getppid()``; reparenting (to init or a subreaper)
      means the parent died.

    If an ancestor died while this module was still importing, Windows
    detects it at arm time (missing PID, or a recycled PID younger than
    this process) and exits immediately; POSIX cannot distinguish that
    from a legitimate init/subreaper parent, so it disarms and relies on
    the stdin-EOF backstop, as before. Disable with
    ``KUMIHO_MCP_DISABLE_ORPHAN_WATCHDOG=1``.
    """
    disable = os.environ.get("KUMIHO_MCP_DISABLE_ORPHAN_WATCHDOG", "")
    if disable.strip().lower() in ("1", "true", "yes"):
        return

    if os.name == "nt":
        try:
            _start_windows_watchdog()
        except Exception:
            pass  # degrade to no-watchdog, never block startup
        return

    initial_ppid = os.getppid()
    if initial_ppid <= 1:
        # Direct child of init/subreaper (e.g. a container top process):
        # reparenting can never be observed. stdin EOF remains the
        # shutdown signal, as before.
        return
    try:
        poll = float(os.environ.get("KUMIHO_MCP_ORPHAN_WATCHDOG_POLL", "5.0"))
    except ValueError:
        poll = 5.0
    if not math.isfinite(poll):
        poll = 5.0
    poll = min(max(poll, 0.05), 3600.0)

    def _watch() -> None:
        while os.getppid() == initial_ppid:
            time.sleep(poll)
        _exit_orphaned(initial_ppid)

    threading.Thread(
        target=_watch, name="kumiho-orphan-watchdog", daemon=True
    ).start()


async def run_server() -> None:
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        print(
            "Error: MCP SDK not installed.\n"
            "Install with: pip install 'kumiho[mcp]' or pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)
    
    logger.info("Starting Kumiho MCP server...")
    server = create_mcp_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for the MCP server CLI.

    Ends with ``os._exit``: once the stdio transport is gone there is
    nothing left for this process to do, and lingering non-daemon threads
    (thread pools, gRPC channels) must never keep a dead server alive —
    orphaned servers accumulate across client restarts (kumiho-plugins#25).
    """
    _start_orphan_watchdog()
    exit_code = 0
    try:
        asyncio.run(run_server())
    except SystemExit as exc:
        if isinstance(exc.code, int):
            exit_code = exc.code
        elif exc.code is not None:
            # Match the interpreter's behavior for sys.exit("message").
            try:
                print(exc.code, file=sys.stderr)
            except Exception:
                pass
            exit_code = 1
    except KeyboardInterrupt:
        exit_code = 130
    except BaseException:
        traceback.print_exc()
        exit_code = 1
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except Exception:
            # The mcp stdio transport closes the real stdio on shutdown
            # (modelcontextprotocol/python-sdk#1933).
            pass
    os._exit(exit_code)


if __name__ == "__main__":
    main()
