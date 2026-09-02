# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.1] - 2026-09-02

### Fixed
- **MCP edge tools advertise the full edge ontology** — `kumiho_create_edge`
  and `kumiho_delete_edge` listed only 8 of the 10 `EdgeType` values, omitting
  `SUPERSEDES` (belief revision) and `SUPPORTS` (evidence chains). Both have
  been defined on `EdgeType` and accepted by `validate_edge_type` all along, so
  an MCP host could never record a belief revision itself even though
  server-side passes create those edges.

## [0.12.0] - 2026-08-13

### Added
- **Creative Project lifecycle APIs** — Projects now expose metadata, archived
  listing and restoration, deletion-impact analysis, deletion guards, external
  reference resolution, Item moves, and snapshot-bound permanent deletion.
- **Space metadata support** — Space creation and metadata updates can carry
  application-defined display labels without changing canonical identity.
- **Additive hard-delete RPC** — `hard_delete_project()` uses the new
  confirmation and impact-snapshot contract while the established
  `delete_project(project_id, force=False)` signature remains available.

### Changed
- Generated protobuf and gRPC bindings now target the Project lifecycle contract
  shipped by kumiho-server 1.7.0.
- Archived canonical Project names are reserved for identity-safe restoration.
  Creating another Project with the same canonical name returns a conflict.

## [0.11.0] - 2026-08-01

### Added
- **mcp 2.x support** — `kumiho[mcp]` now runs on both mcp 1.x and mcp 2.x.
  mcp 2.0.0 removed the low-level `Server` handler decorators and replaced them
  with `on_*` constructor keywords; the six handlers are registered through
  whichever shape the installed SDK provides, selected by capability detection
  rather than a version number so editable installs, forks and vendored copies
  resolve correctly. Capabilities, wire format and tool behavior are identical
  on both majors.
- **Tool input validation on the 2.x path** — mcp 1.x validated tool arguments
  against each tool's `inputSchema` before dispatch and mcp 2.0's low-level path
  does not, so the SDK now performs that check itself. A schema-violating call
  is still rejected with `Input validation error: ...` rather than reaching the
  handler.

### Fixed
- **`kumiho[mcp]` installed a server that could not start.** The `mcp` extra
  declared `mcp>=1.0.0` with no upper bound, so once mcp 2.0.0 published, every
  fresh install resolved to it and `create_mcp_server()` raised
  `AttributeError: 'Server' object has no attribute 'list_tools'` at
  construction (KumihoIO/kumiho-SDKs#145).
- **`resources/read` had never worked**, on any version: the handler assumed a
  `str` URI but MCP passes a pydantic `AnyUrl`, so every read raised
  `AttributeError` on its first line (#146). Resource bodies now also keep their
  declared `application/json` content type instead of being served as
  `text/plain`, and the project name is percent-decoded — mcp 1.x escapes
  non-ASCII when an `AnyUrl` is stringified and mcp 2.x does not, so without
  decoding a Hangul or spaced project name resolved on one major only.
- **`serverInfo.version` reported the mcp SDK's version** as kumiho's under
  mcp 1.x, and would have reported an empty string under 2.0 (#147). It now
  reports kumiho's own version.

### Changed
- The `mcp` extra is now bounded at **both** ends: `mcp>=1.10.0,<3`. The floor
  is the oldest release where every assumption in the code actually holds —
  `mcp.server.lowlevel.helper_types` landed in 1.3.0 and the `call_tool`
  decorator's `validate_input` in 1.10.0, below which the 1.x path would
  silently skip tool-argument validation. **Installs pinned below mcp 1.10.0
  will be upgraded.** CI now runs the suite against the declared floor and both
  majors, so a future major bump fails the build rather than reaching users.
- `jsonschema` is declared directly in the `mcp` extra, since the SDK now
  imports it rather than relying on it transitively.

## [0.10.8] - 2026-07-15

### Fixed
- **MCP server orphan hardening** — `kumiho.mcp_server` now exits when its
  launching ancestor chain dies: event-driven on Windows (a watchdog thread
  blocks on the ancestor process handles via `WaitForMultipleObjects`),
  ppid-reparent polling on POSIX. On Windows, MCP clients restart sessions
  by terminating the launcher process, which does **not** kill its children
  — and because a venv's `Scripts\python.exe` is a redirector stub that runs
  the base interpreter as a separate child, the real server is a grandchild
  or deeper, so the whole contiguous python-named ancestor chain plus the
  client is watched, not just the direct parent. The stranded
  `python -m kumiho.mcp_server` processes previously accumulated without
  bound (KumihoIO/kumiho-plugins#25). Additionally, `main()` now hard-exits
  once the stdio transport closes, so lingering non-daemon threads (thread
  pools, gRPC channels) can never keep a dead server alive. Opt out with
  `KUMIHO_MCP_DISABLE_ORPHAN_WATCHDOG=1`.

## [0.10.7] - 2026-07-14

### Added
- **`tool_memory_store_batch`** — the bulk counterpart of `tool_memory_store` for
  the MCP write path. N captures land in **one `batch_create_revisions`
  transaction** (removing the neo4j relationship-group deadlock that per-capture
  concurrency triggers, and collapsing the heaviest create/revision writes) while
  preserving every per-capture semantic of the single path: credential screening,
  space resolution, fuzzy-stack, `event_date`/metadata, tags, `topic` bundle, and
  `DERIVED_FROM` edges (tag/bundle/edge stay per-item — the server has no batch RPC
  for them). `kumiho_memory_reflect` routes ≥2-capture writes through it; a single
  capture keeps the byte-identical per-capture path.

## [0.10.6] - 2026-07-15

### Added
- **Batch revision creation** — `batch_create_revisions(revisions, idempotency_prefix=...)`
  writes up to 200 captures (item + revision + optional artifacts) in a single
  server transaction, returning positional `(results, failures)`. Missing items
  are auto-created from each row's `item_kref`; rows targeting the same item
  stack in order (last becomes `latest`); per-row artifacts can mark one
  `"default": True` so the chain resolves straight from the item kref; a stable
  `idempotency_prefix` makes re-submission a safe no-op. Requires
  kumiho-server >= 1.6.3.

## [0.10.0] - 2026-06-17

### Added
- **Full-text fuzzy search** — `search(query, ...)` returns ranked items
  (`SearchResult` with `item`, `score`, `matched_in`), with automatic typo tolerance.
- **Semantic revision scoring** — `score_revisions(query, revision_krefs)` scores
  revisions against a query using server-side embeddings and/or fulltext.
- **Batch revision fetch** — `batch_get_revisions(revision_krefs=..., item_krefs=..., tag=...)`
  fetches many revisions in a single call, returning `(revisions, not_found)`.
- **By-kref accessors** — `get_artifact_by_kref()`, `get_bundle_by_kref()`, and
  `client.get_item_from_revision()`.

### Changed
- The advanced `event_stream()` parameters (`cursor`, `consumer_group`,
  `from_beginning`) and `get_event_capabilities()` are now generally available.
- The C++ and Dart SDKs now have full feature parity with the Python SDK.

## [0.4.0] - 2025-12-03

### Added
- **Event streaming cursor support**: `Event.cursor` attribute for resumable streaming
- **EventCapabilities API**: `get_event_capabilities()` to query tier-based streaming features
- **New event_stream() parameters**:
  - `cursor`: Resume from last position (Creator+ tiers, Coming Soon)
  - `consumer_group`: Load-balanced consumption (Enterprise tier, Coming Soon)
  - `from_beginning`: Replay entire buffer (Creator+ tiers, Coming Soon)
- Tier capability documentation with Coming Soon markers

### Changed
- Updated event streaming documentation with tier matrix
- Event object now includes `cursor` attribute (None for Free tier)

### Notes
- Creator tier and above streaming features are planned but not yet deployed
- Free tier provides real-time streaming without persistence

## [0.3.0] - 2024-XX-XX

### Added
- Comprehensive Google-style docstrings for all public APIs
- Sphinx documentation with ReadTheDocs theme
- `get_artifact()` top-level function for fetching artifacts by Kref
- `get_artifact_by_kref()` method in Client class
- Type hints throughout the codebase

### Changed
- Updated `pyproject.toml` with full PyPI metadata
- Improved error messages with more context

### Fixed
- Kref parsing for artifact URIs with special characters

## [0.2.0] - 2024-XX-XX

### Added
- Event streaming support with `stream_events()`
- Link traversal for lineage tracking
- Batch operations for multiple artifacts

### Changed
- Switched to context-variable-based client management
- Improved connection pooling for gRPC channels

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Core entity classes: Project, Space, Item, Revision, Artifact, Edge
- Kref URI parsing and generation
- Discovery-based authentication
- CLI authentication tool (`kumiho-auth`)
