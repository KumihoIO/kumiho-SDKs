# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are the release tag's date (`sdk-v*` in KumihoIO/kumiho-SDKs). Entries are
in descending version order, which is also descending date order.

`../../RELEASE_NOTES.md` is the release record: the same releases with the
narrative — why a change mattered and what you have to do about it. This file is
its terse companion. Entries belong in both.

## [0.13.0] - 2026-09-02

### Added
- **`kumiho.request_context`** — `RequestContext`, `current_request()`,
  `request_context()` and `hosted_mode()`. A `contextvars`-carried per-request
  identity (tenant, user, token, session) for deployments where one process
  serves many tenants. `asyncio.to_thread` copies the context, so it follows a
  request across the async/sync boundary without being threaded through every
  call site. `RequestContext`, `current_request` and `hosted_mode` are
  re-exported from `kumiho`; the context manager is reachable as
  `from kumiho.request_context import request_context` or as
  `kumiho.use_request_context` — re-exporting it under its own name would
  shadow the submodule, since a submodule and a package attribute share one
  namespace and `import kumiho.request_context as rc` resolves through
  `getattr`, not `sys.modules`.
- **`create_mcp_server(profile=..., instructions=...)`** — `profile="connector"`
  exposes a curated 18-tool surface for the hosted Claude connector; `None` or
  `"full"` keeps today's whole tool list, which is what the stdio plugin gets.
  Falls back to `KUMIHO_MCP_TOOL_PROFILE`. An unrecognized name raises
  `ValueError` naming the valid profiles rather than silently serving
  everything — a typo in a deployment's environment would otherwise publish
  every destructive tool to a public connector.
- **`kumiho.mcp_server.TOOL_ANNOTATIONS`** — MCP tool annotations (`title`,
  `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) for all
  63 tools, the kumiho-memory ones included. Applied on both the mcp 1.x
  decorator path and the 2.x `on_*` path, with `Tool.title` and
  `ToolAnnotations` detected by introspection so an older SDK degrades to
  unannotated tools instead of failing to construct.
- **`kumiho.mcp_server.ToolNotInProfileError`** — raised by `call_tool` when a
  client asks for a tool the active profile withholds, so the refusal reaches
  the client as a real MCP tool error (`isError: true`) rather than a
  successful result whose text merely contains the word "error". Clients and
  models branch on `isError`; a refusal that reports success reads as "the call
  went through". mcp 1.x turns the raise into an error result on its own, and
  the 2.x branch catches the type and builds the same one.
- **`kumiho.mcp_server.CONNECTOR_INSTRUCTIONS`** — the engage/reflect protocol
  as server `instructions`, returned in the MCP `initialize` result for the
  connector profile. A remote connector has no skill and no hooks, so this is
  the only channel the protocol has.
- **`KUMIHO_STACK_MIDDLE_BAND`** — set to `0` to run the revision-stacking
  gate in strong-only mode, where a capture stacks only when its score clears
  the 0.75 strong threshold **and** the lexical floor; the 0.55 type-match band
  is withheld. Default is unchanged (two-band). Every `kumiho_memory_store` and
  `kumiho_memory_store_batch` result also reports `stack_mode` (`"two-band"` or
  `"strong-only"`) next to `stack_score` / `stack_runner_up` / `stack_overlap`,
  so per-tenant telemetry can say which gate produced the number.

### Changed
- **The MCP server's process-global caches are keyed by tenant.**
  `_project_cache`, `_known_spaces`, `_bundle_cache` and `_space_registry_cache`
  were keyed by project name alone. Two tenants routinely have a project called
  `CognitiveMemory`, and the cached value is a live handle bound to one
  tenant's client and credentials.
- **Hosted mode never mutates `os.environ`.** The `auth_token` argument to
  `kumiho_search_items` / `kumiho_fulltext_search` used to be published into
  `KUMIHO_AUTH_TOKEN`; hosted, that is a credential swap visible to every other
  in-flight request, and a persistent one. It is now ignored (with a warning)
  when a request context is active or `KUMIHO_MCP_HOSTED=1`. Unchanged locally.
- **Hosted mode never reads `~/.kumiho`.** `_ensure_configured()` raises instead
  of falling back to `auto_configure_from_discovery()` when no request-scoped
  client is bound: the fallback would serve the operator's own graph to a remote
  caller. Local memory-artifact writes are likewise a no-op when hosted — the
  root is on the server's shared disk and the recorded path resolves for nobody.

### Notes
- **Hosted deployments run with `KUMIHO_STACK_MIDDLE_BAND=0`.** The two-band
  gate was calibrated on one corpus. A shared multi-tenant server has not
  measured its own score distribution, and a middle-band false positive moves
  the `published` tag onto an unrelated item — which every recall path then
  resolves first, so the displaced memory disappears from the default retrieval
  surface without anything reporting it. Strong-only keeps stacking for
  near-duplicates and withholds the contested band until the `stack_mode` /
  `stack_score` telemetry says a tenant's distribution supports turning it back
  on. The stdio plugin keeps the two-band default.
- The stdio plugin path is unchanged in behavior: the default
  `create_mcp_server()` still exposes every tool, with the same names and
  schemas. Tools now additionally carry `title` and `annotations`, which the
  plugin benefits from as much as the directory does.
- Two annotations deliberately disagree with the connector plan's §2.2 hint
  columns, because the tools disagree with them:
  `kumiho_memory_space_profile` persists versioned profile items unless
  `dry_run` is set (so it is not read-only), and `kumiho_memory_dream_state`
  applies deprecation (so it is destructive). `space_profile` keeps its place
  in the connector profile; only the honesty of its hints changed.
- `kumiho_memory_dream_state` is annotated but **withheld from the connector
  profile** for v1. Its assessment pass needs an LLM key and hosted tenants are
  keyless (plan §1.10), so listing it would publish a tool that fails at call
  time — which directory review catches head-on, since it asks the submitter to
  confirm every listed tool has been run. The full profile still serves it.

## [0.12.2] - 2026-09-02

### Fixed
- **Revision stacking in `kumiho_memory_store` never fired.** The 0.92 fuzzy
  threshold sat above the scorer's ceiling: an item scores 0.72-0.83 against
  its own exact title, so no input could ever stack and every capture minted a
  new item. The gate is now a lexical-overlap floor (token Jaccard >= 0.17 over
  Latin words and CJK bigrams, refusing texts under 8 tokens) combined with two
  score bands (>= 0.75 alone, or >= 0.55 with matching `memory_type`),
  calibrated on 17 labelled pairs from a live graph that are pinned as tests.
  The search now uses title and summary, is capped at 180 characters with a
  title-only retry (long CJK queries hit Lucene's 1024-clause limit), and logs
  failures at warning instead of debug.
- **Dart `EdgeType.isValid` rejected valid types.** It checked membership in a
  seven-item list rather than the regex every other SDK uses, so `SUPPORTS`,
  `PRODUCED_BY` and `MIGRATED_FROM` returned false. Constants added; `isValid`
  now delegates to `isValidEdgeType`.

### Added
- `stack_score`, `stack_runner_up` and `stack_overlap` on every
  `kumiho_memory_store` and `kumiho_memory_store_batch` result, reported whether
  or not the capture stacked, so a caller can tell a broken search from a
  near-miss.
- The 21-file `python/tests/` suite is now collected by CI (moved under
  `python/python/tests/`), together with the `kumiho-cli` tests; a layout guard
  fails the build if a test directory under `python/` is not run by any job.

### Removed
- `python/.github/workflows/`: dead copies that GitHub never read and that
  documented a stale version gate.

## [0.12.1] - 2026-09-02

### Added
- **`SUPPORTS` is reachable from `kumiho_create_edge`** — the tool's
  `edge_type` enum listed 8 of the 10 `EdgeType` members. The enum is enforced
  by `jsonschema.validate` in the MCP dispatcher, so the omitted types could not
  be written through this tool at all, even though `EdgeType` defines them,
  `__init__` re-exports them, `validate_edge_type` accepts them, and the proto
  field is a plain string.
- `SUPERSEDES` and `SUPPORTS` are now listed in `kumiho.__all__`, matching the
  aliases that were already defined.

### Changed
- The `kumiho_create_edge` description and the MCP docs now state the direction
  of each type rather than naming only the four creative-provenance ones.

### Notes
- `SUPERSEDES` is deliberately still withheld from both edge tools. Belief
  revision is a protocol rather than a lone edge: its producers also demote the
  superseded revision and ripple grounding staleness to dependents. A bare edge
  write performs only part of that, so explicit belief revision belongs in the
  memory layer. `kumiho_delete_edge` keeps the vocabulary it shipped with, since
  edge deletion has no repair path.

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

## [0.10.7] - 2026-07-15

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

## [0.10.5] - 2026-07-11

### Added
- **`kumiho._text.slugify()`** — one canonical slug helper shared by the SDK and
  kumiho-memory, so a fix (Unicode handling in particular) cannot land in one
  copy and silently miss another. `\w` is Unicode-aware, so Hangul, CJK and
  Cyrillic names slug to themselves rather than to the empty string, matching
  the kref path segments the server accepts. Optional `hash_on_truncate` appends
  a short digest of the full normalized string so two long names sharing a
  prefix keep distinct slugs.
- **MCP space registry** — the MCP server records space aliases and resolves
  space hints against a short-lived per-project registry of existing space
  paths, with stem matching, so a near-miss space name resolves to the existing
  space instead of creating a near-duplicate.

## [0.10.4] - 2026-07-03

### Fixed
- **`memory_type` never round-tripped** — the server reserves the `type`
  metadata key, which made the `memory_types` filter dead code (#21).
- **Interactive login prompt inside headless processes** — the SDK could open a
  login prompt in a process with no console, hanging the MCP server
  indefinitely (#22). Both fixed in #23.

## [0.10.3] - 2026-07-03

### Fixed
- **Memory-retrieve RPC storm** (#20) — `search` now retries shallow when
  `include_revision_metadata=True` returns nothing, and the pattern-fallback and
  bundle-expansion loops are bounded at `limit * 2`. This removes the ~185s MCP
  timeout on unscoped recall against large cloud projects.

## [0.10.2] - 2026-07-03

### Fixed
- **`__version__` drift left over from 0.10.1** — `kumiho/__init__.py` was never
  bumped when `pyproject.toml` went to 0.10.1, so the published wheel's metadata
  correctly said 0.10.1 while `kumiho.__version__` still read `"0.10.0"` at
  runtime.

### Added
- `tests/test_version.py` asserts `kumiho.__version__` matches `pyproject.toml`,
  so this class of drift fails a test instead of silently shipping again.

## [0.10.1] - 2026-07-03

### Fixed
- **`tool_memory_store` never applied tags** — it called a nonexistent
  module-level `kumiho.tag_revision(...)` instead of the `revision.tag(...)`
  method, and a bare `except` swallowed the failure. No tag, including the
  default `published` tag, was ever actually applied through this path, which
  broke Dream State's published-revision deprecation protection for every
  consumer relying on the default store backend.

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

## [0.9.24] - 2026-04-17

### Fixed
- **Unicode kref path segments** — `Kref` rejected non-ASCII letters in path
  segments even though the server accepts them, so a Hangul or CJK space or item
  name could not be addressed from the SDK.

## [0.9.23] - 2026-04-17

### Changed
- **gRPC reliability hardening** — a per-RPC default deadline, so a call can no
  longer hang indefinitely against an unresponsive gateway.
- Recall defaults to summarized mode, and summarized recall skips sibling
  unrolling.

## [0.9.22] - 2026-04-02

### Fixed
- `tool_memory_retrieve` accepts a `memory_types` parameter, which the tool
  schema had omitted.

## [0.9.21] - 2026-04-02

### Added
- **`kumiho_batch_get_revisions` MCP tool** — exposes the SDK's batch revision
  fetch to MCP clients, replacing N serial `get_revision` calls.

## [0.9.20] - 2026-03-15

### Fixed
- Dream State consolidation returned data the ingest path could not use. The
  consolidation and Dream State responses are now shaped correctly for ingest,
  and the OpenAI response object is parsed as JSON rather than passed through
  as an object.

## [0.9.19] - 2026-03-10

### Added
- **Per-call `auth_token` on the search tools**, enabling cross-project search
  without rebuilding the client.

## [0.9.18] - 2026-03-10

### Fixed
- `assistant_text` removed from `required` in the `kumiho_memory_store` schema;
  it was never mandatory to the handler, so the schema rejected valid calls.

## [0.9.17] - 2026-03-09

### Added
- **`TransientRetryInterceptor`** — retries transient gRPC failures, so a
  gateway restart no longer surfaces as a hard error to the caller.

## [0.9.16] - 2026-03-08

### Fixed
- **Dream State** replaced its event-stream collection with a revision query,
  decoupled its collection window from the gRPC deadline, and handles
  `DEADLINE_EXCEEDED` gracefully instead of aborting the pass.

## [0.9.15] - 2026-03-07

### Fixed
- The chat tool handlers respect the client's `project` parameter, and the
  replay tier gate was removed.

<!--
Releases 0.4.1 through 0.9.14 are intentionally absent from this file.

The `python/` tree was subtree-imported into kumiho-SDKs on 2026-03-03, and the
first release tag in this repository is `sdk-v0.9.15`. There is no tag — and so
no reliable version boundary — for any release before it, and the imported
commits cannot be partitioned into releases without guessing: several versions
(0.9.10-0.9.12, 0.9.14) have no identifiable bump commit at all.

Rather than invent entries, see ../../RELEASE_NOTES.md, which carries
hand-written notes for 0.4.0-0.4.4, 0.7.0, 0.8.0-0.8.6, 0.9.0-0.9.2 and
0.9.4-0.9.7. 0.9.3 and 0.9.8-0.9.14 are undocumented in both files. No 0.5.x or
0.6.x release is attested anywhere in this repository.
-->

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
