# Kumiho Python SDK - Release Notes

> **This file is the release record.** It is the narrative, user-facing history:
> what changed, why it mattered, and what you have to do about it.
> `python/docs/changelog.md` is the terse Keep a Changelog companion — same
> releases, one screen each, no upgrade guidance. Every release needs an entry
> here; a changelog entry alone is not enough, and the two drifting apart is
> what produced the gaps backfilled in KumihoIO/kumiho-SDKs#155 and #157.


## kumiho 0.13.0 (September 2026) — Hosted Connector Surface 🔌

The stdio MCP server is single-tenant by construction: one process, one user,
one set of credentials in the environment. Serving the same tools as a hosted
Claude connector inverts every one of those assumptions, and this release is
the seam that makes it safe — a per-request identity, a curated tool surface,
annotations the connector directory requires, and hosted guards on the paths
that used to reach for process-global state.

### ✨ What changed

- **`kumiho.request_context`** — a `contextvars`-carried per-request identity
  (tenant, user, bearer token, memory session/context). `asyncio.to_thread`
  copies the context, so it follows a request across the async/sync boundary
  without being threaded through every call site. `RequestContext`,
  `current_request` and `hosted_mode` are re-exported from `kumiho`; the
  context manager is `kumiho.use_request_context`, or
  `from kumiho.request_context import request_context`.
- **`create_mcp_server(profile=..., instructions=...)`.** `profile="connector"`
  exposes a curated **18-tool** surface; `None` or `"full"` keeps the whole
  63-tool list, which is what the stdio plugin gets. The value falls back to
  `KUMIHO_MCP_TOOL_PROFILE`, and an unrecognized name raises `ValueError`
  naming the valid profiles — a typo in a deployment's environment would
  otherwise publish every destructive tool to a public connector.
- **`TOOL_ANNOTATIONS` for all 63 tools** (`title`, `readOnlyHint`,
  `destructiveHint`, `idempotentHint`, `openWorldHint`), applied on both the
  mcp 1.x decorator path and the 2.x `on_*` path. `Tool.title` and
  `ToolAnnotations` are detected by introspection, so an older mcp degrades to
  unannotated tools instead of failing to construct.
- **`CONNECTOR_INSTRUCTIONS`** — the engage/reflect protocol returned as server
  `instructions` in the MCP `initialize` result for the connector profile. A
  remote connector has no skill and no hooks, so this is the only channel the
  protocol has.
- **`ToolNotInProfileError`** — a withheld tool is refused as a real MCP tool
  error (`isError: true`), not a successful result whose text merely contains
  the word "error". Clients and models branch on `isError`; a refusal that
  reports success reads as "the call went through".

### ⚠️ Read this before hosting

- **Process-global caches are now keyed by tenant.** `_project_cache`,
  `_known_spaces`, `_bundle_cache` and `_space_registry_cache` were keyed by
  project name alone. Two tenants routinely have a project called
  `CognitiveMemory`, and the cached value is a live handle bound to one
  tenant's client and credentials.
- **Hosted mode never mutates `os.environ`.** The `auth_token` argument to
  `kumiho_search_items` / `kumiho_fulltext_search` used to be published into
  `KUMIHO_AUTH_TOKEN` — hosted, a credential swap visible to every other
  in-flight request, and a persistent one. It is ignored (with a warning) when
  a request context is active or `KUMIHO_MCP_HOSTED=1`. Local behaviour is
  unchanged.
- **Hosted mode never reads `~/.kumiho`.** `_ensure_configured()` raises rather
  than falling back to `auto_configure_from_discovery()` when no request-scoped
  client is bound; the fallback would serve the operator's own graph to a
  remote caller. Local memory-artifact writes are likewise a no-op when hosted.
- **`kumiho_memory_dream_state` is withheld from the connector profile** for
  v1, and two annotations deliberately disagree with the connector plan's hint
  columns because the tools do: `kumiho_memory_space_profile` persists
  versioned profile items unless `dry_run` is set (not read-only), and
  `kumiho_memory_dream_state` applies deprecation (destructive).

### 🧪 Testing

- `python/python/tests/test_mcp_connector_profile.py`: the 18-tool profile
  pinned by name, annotation coverage and honesty for all 63 tools, the
  out-of-profile refusal on both mcp legs, and hosted-mode tenancy — cache
  keying, the `auth_token` no-op, and the discovery-fallback refusal.
- Full suite from `python/python/`: 350 passed, 98 skipped, with and without
  the real `kumiho_memory` source on `PYTHONPATH`.

### 🎯 Also in this release

- The stdio plugin path is unchanged in behavior: the default
  `create_mcp_server()` still exposes every tool under the same names and
  schemas. Tools now additionally carry `title` and `annotations`, which the
  plugin benefits from as much as the directory does.

## kumiho 0.12.2 (September 2026) — Revision Stacking Actually Stacks 🧱

Revision stacking is the mechanism that lets one subject accumulate history on
one item instead of fragmenting into many: when a new capture covers a topic an
existing item already covers, the new content should land as a new revision on
that item. **It had never fired.** Measured on a live graph, an item scores
0.72-0.83 against its *own exact title*; the gate was 0.92. Every capture ever
written through `kumiho_memory_store` minted a fresh item at `r=1`, which also
meant the revision operator the belief-revision model rests on had nothing to
revise.

### ✨ What changed

- **A gate that can be reached, and that discriminates.** Fuzzy-search scores
  alone cannot separate a genuine duplicate from an unrelated neighbour in a
  topically homogeneous space (duplicates 0.58-0.68, unrelated up to 0.62, and
  an unrelated item can win top-1 outright). The new gate requires token-Jaccard
  overlap >= 0.17 between the incoming title+summary and the candidate's
  (Latin words plus CJK character bigrams; texts under 8 tokens are refused),
  and then either score >= 0.75, or score >= 0.55 with a matching
  `memory_type`. A runner-up margin rule was measured and rejected: an impostor
  had a wider margin than a true duplicate. All 17 measured pairs are pinned as
  a parametrized test driving the gate as a pure function.
- **Search on title and summary,** capped at 180 characters with a title-only
  retry. A ~230-character Korean query was failing server-side with Lucene
  `maxClauseCount is set to 1024`, and the failure was being swallowed at debug
  level as if nothing similar existed. Search failures now log at warning.
- **Inspectable results.** `stack_score`, `stack_runner_up` and `stack_overlap`
  are reported on every store result, stacked or not.

### ⚠️ Read this before relying on stacking

A stacked write tags the *new* revision `published`, and every recall path
resolves `published` first. The prior revision leaves the default retrieval
surface and is reachable only via `unroll_revisions`. That is a tag move in the
sense of the belief-revision model, without a `SUPERSEDES` edge. A **false
stack is therefore a false belief revision**, not a harmless grouping — which
is why the gate errs toward *not* stacking, and why the lexical floor binds in
both score bands.

### 🧪 Testing

- `python/python/tests/test_mcp_revision_stacking.py`: the measured table, the
  gate, reachability (restoring 0.92 fails), and negative controls showing that
  score alone, type alone, and the margin rule each fail to separate.
- The 21-file suite formerly at `python/tests/` is now collected by CI
  (157 passed / 98 skipped on all three mcp legs), plus the `kumiho-cli` tests
  and a layout guard that fails the build on any uncollected test directory.

### 🎯 Also in this release

- **Dart:** `EdgeType.isValid` now agrees with the regex validator the other
  SDKs use; `SUPPORTS`, `PRODUCED_BY` and `MIGRATED_FROM` constants added.
  (The Dart package has no publish path from this repo yet — #164.)
- Release record backfilled: 0.12.0, 0.12.1, 0.10.7 and 0.10.8 in this file;
  changelog dates and ordering repaired.
- Dead workflow copies under `python/.github/workflows/` removed.

## kumiho 0.12.1 (September 2026) — `SUPPORTS` Reachable from `kumiho_create_edge` 🔗

`kumiho_create_edge` advertised **8 of the 10** `EdgeType` members in its
`edge_type` JSON-Schema enum, and that enum is enforced rather than advisory:
the MCP dispatcher runs `jsonschema.validate` against the tool schema, so an
omitted type could not be written through the tool at all — even though
`EdgeType` defines it, `__init__` re-exports it, `validate_edge_type` accepts
any well-formed uppercase name, and the proto field is a plain `string`.

### ✨ What changed

- **`SUPPORTS` added to the `kumiho_create_edge` enum.** Evidence chains —
  corroborating revision → the claim it supports — are writable from MCP.
- **`SUPERSEDES` and `SUPPORTS` added to `kumiho.__all__`**, matching aliases
  that already existed but were not exported.
- **Edge-type documentation completed.** The tool description and the
  `docs/mcp.md` table now state the *direction* of each type rather than naming
  only the four creative-provenance ones.

### 🧭 Why `SUPERSEDES` is still withheld

Belief revision is a protocol, not a lone edge. Every in-system producer pairs
the `SUPERSEDES` edge with a status demotion on the superseded revision and a
grounding-staleness ripple to whatever depended on it. A bare edge write
performs the first third of that, silently, so recall would keep serving
decisions built on a retracted fact as if their grounding were intact. Explicit
belief revision belongs in the memory layer, where the companions run.

It is withheld from `kumiho_delete_edge` for the same reason in reverse: nothing
re-creates a deleted edge, so a stranded revision keeps `status=superseded`
while `superseded_by` goes empty. `kumiho_delete_edge` keeps the vocabulary it
shipped with.

### 🧪 Testing

`tests/test_mcp_edge_ontology.py` derives its expectations from `EdgeType`, so
the tool schema cannot drift from the ontology again, and pins the deliberate
create/delete asymmetry so a future reader does not "fix" the exclusions back in
without reading why.


## kumiho 0.12.0 (August 2026) — Creative Project Lifecycle 🗂️

Targets the Project lifecycle contract shipped by **kumiho-server 1.7.0**.
Projects gain a full archive → restore → delete lifecycle, and deletion becomes
a two-step operation you can inspect before committing.

### ✨ New Features

- **Project lifecycle APIs** — project metadata, archived-project listing and
  restoration, deletion-impact analysis, deletion guards, external reference
  resolution, and Item moves between Projects.
- **Snapshot-bound permanent deletion** — `hard_delete_project()` uses the new
  confirmation and impact-snapshot contract: analyze the impact, then commit
  against that snapshot, so a Project that changed underneath you is not
  destroyed on stale information.
- **Space metadata** — Space creation and metadata updates carry
  application-defined display labels without changing canonical identity, so a
  human-readable name no longer forces a rename of the thing krefs point at.

### ✅ Compatibility Notes

- **`delete_project(project_id, force=False)` is unchanged.** `hard_delete_project()`
  is additive; existing calls keep working exactly as before.
- **Archived canonical Project names stay reserved.** Restoration is
  identity-safe, so creating another Project with the same canonical name while
  the original is archived returns a conflict rather than silently taking the
  name.
- Generated protobuf and gRPC bindings were regenerated for the 1.7.0 contract.


## kumiho 0.11.0 (August 2026) — MCP 2.0 Support 🔌

`kumiho[mcp]` now works on **both mcp 1.x and mcp 2.x**.

### 🔴 If you installed `kumiho[mcp]` after mcp 2.0.0 was published, upgrade

mcp 2.0.0 removed the low-level `Server` handler decorators the MCP server was built on, and `kumiho` declared `mcp>=1.0.0` with no upper bound — so a fresh install resolved to 2.0.0 and produced a server that **could not start**:

```
AttributeError: 'Server' object has no attribute 'list_tools'
```

This release supports both majors and bounds the dependency at `mcp>=1.10.0,<3`. If you pinned `mcp<2` as a workaround, you can drop the pin.

The floor is bounded too, and is not a round number: `mcp.server.lowlevel.helper_types` only exists from mcp 1.3.0, and the `call_tool` decorator's `validate_input` only from 1.10.0 — below that the SDK does not validate tool arguments at all. 1.10.0 is the oldest release where everything this code relies on actually holds, and CI runs the suite against exactly that version. **If you are pinned below mcp 1.10.0, installing this release will upgrade you.**

### ✨ What changed

- **Dual-major MCP server.** The six handlers (`tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`) are registered through the 1.x decorators or 2.0's `on_*` constructor keywords, chosen by capability detection rather than a version number — so editable installs, forks and vendored copies of `mcp` are detected correctly. Capabilities, wire format and tool behavior are identical on both.
- **Tool input validation preserved on 2.x.** mcp 1.x validated tool arguments against each tool's `inputSchema` before dispatch; mcp 2.0's low-level path does not. The SDK now performs that check itself, so a schema-violating call is still rejected with `Input validation error: ...` rather than reaching the handler.
- **`resources/read` fixed.** It had never worked on any version: the handler assumed a `str` URI but MCP passes a pydantic `AnyUrl`, so every read raised `AttributeError`. Resource bodies now also keep their declared `application/json` content type instead of being served as `text/plain`.
- **`serverInfo.version` reports kumiho's version.** It previously reported the *mcp SDK's* version.

### 🧪 Testing

The MCP server is now covered by construction and dispatch tests that run against **both mcp majors in CI**, so a future major bump fails the build rather than reaching users.


## kumiho 0.10.8 (July 2026) — MCP Server Orphan Watchdog 🐕

`python -m kumiho.mcp_server` processes accumulated without bound
(KumihoIO/kumiho-plugins#25). This release makes the server exit when the client
that launched it dies.

### 🐛 The bug

On Windows, MCP clients restart a session by **terminating the launcher
process**, which does not kill its children. Worse, a venv's
`Scripts\python.exe` is a redirector stub that runs the base interpreter as a
*separate child*, so the real server is a grandchild or deeper — watching only
the direct parent would not have caught it.

### 🔧 The fix

- **Ancestor-chain watchdog.** The whole contiguous python-named ancestor chain,
  plus the client, is watched: event-driven on Windows (a thread blocks on the
  ancestor process handles via `WaitForMultipleObjects`), ppid-reparent polling
  on POSIX.
- **Hard exit on transport close.** `main()` now hard-exits once the stdio
  transport closes, so lingering non-daemon threads — thread pools, gRPC
  channels — can never keep a dead server alive.
- Opt out with `KUMIHO_MCP_DISABLE_ORPHAN_WATCHDOG=1`.


## kumiho 0.10.7 (July 2026) — Batch Reflect Writes: `tool_memory_store_batch` 📚

The bulk counterpart of `tool_memory_store` for the MCP write path, built on
0.10.6's `batch_create_revisions`.

### ✨ `tool_memory_store_batch`

N captures land in **one `batch_create_revisions` transaction**, which removes
the neo4j relationship-group deadlock that per-capture concurrency triggers and
collapses the heaviest create/revision writes into a single round trip.

Every per-capture semantic of the single path is preserved: credential
screening, space resolution, fuzzy-stack, `event_date`/metadata, tags, `topic`
bundle, and `DERIVED_FROM` edges. Tag, bundle and edge writes stay per-item —
the server has no batch RPC for them.

`kumiho_memory_reflect` routes writes of **2 or more captures** through it; a
single capture keeps the byte-identical per-capture path.


## kumiho 0.10.6 (July 2026) — Bulk Ingest: `batch_create_revisions` 🚚

Adds the missing **bulk write** operation (pairs with `kumiho-server` ≥ 1.6.3): one call writes up to **200 captures in a single server transaction and one batched embedding pass**, replacing N serial `create_item` + `create_revision` (+ `create_artifact`) calls. Built for onboarding backfill, dream state, session mining, and migrations — and safer than fanning out singles, which can deadlock at bulk volume.

### ✨ `batch_create_revisions()`

Each row is one **capture** — an item, a revision, and optionally its artifacts — created (or rejected) as a unit:

```python
results, failures = kumiho.batch_create_revisions(
    [
        # two revisions of the SAME item -> r=1, r=2 ("latest")
        {"item_kref": "kref://proj/space/mem1.memory",
         "metadata": {"title": "first draft"}},
        {"item_kref": "kref://proj/space/mem1.memory",
         "metadata": {"title": "revised"}},
        # a different item, auto-created, with its artifact chain
        {"item_kref": "kref://proj/space/mem2.memory",
         "metadata": {"title": "second memory"},
         "artifacts": [{"name": "transcript",
                        "location": "s3://bucket/mem2.md",
                        "default": True}]},
    ],
    idempotency_prefix="backfill-20260714-chunk0",
)
created = [r for r in results if r is not None]   # positional with the input
```

- **Items auto-created** from each row's `item_kref` — no separate batch item call needed (parent *space* must exist; a row pointing at a missing space fails individually).
- **Same-item rows stack in order**: consecutive numbers, the last row becomes `latest`, `SUPERSEDES` chained.
- **Artifacts attach in the same transaction**; `"default": True` (at most one per row) makes `get_artifact(item_kref)` and location resolution work immediately after ingest.
- **Idempotent resume**: with a stable `idempotency_prefix`, each row is keyed `{prefix}:{index}` server-side — re-submitting the same batch returns the already-created revisions instead of duplicating. Chunk in a stable order and resume by re-sending.
- **Positional failures**: `failures` is `[(row_index, reason)]` for rows rejected by validation; all valid rows commit atomically.

### 📖 Docs

New **Bulk Ingest** section in the SDK concepts guide, plus the server-side reference (`docs/batch-create-revisions.md` in kumiho-server) covering semantics, limits, and the recommended chunked pipeline.


## kumiho 0.10.0 (June 2026) — Self-Hosted Community Edition Fallback 🦊

Adds first-class support for the self-hosted **Community Edition (CE)** server (`kumiho-server` CE v1.3.0). When the SDK has **no auth token and no explicit target**, it auto-discovers a local CE server and connects tokenlessly — so local, single-user development works with no login.

### ✨ Local CE auto-discovery

- With no token (no `KUMIHO_AUTH_TOKEN`, no cached `~/.kumiho/kumiho_authentication.json`) **and** no explicit target, the SDK probes `GET http://127.0.0.1:9190/api/_live`. If it finds a `deployment_mode: self_hosted_ce` server, it builds a **tokenless** client with discovery and auto-login disabled.
- `kumiho.client_from_local_ce()` creates such a client explicitly.

### ☁️ Cloud behaviour is unchanged

The CE probe **only** fires when there is no token and no explicit target. Any cached/env token, or an explicit `KUMIHO_SERVER_ENDPOINT` / `target=`, sends the SDK down the normal control-plane / discovery path exactly as before. A pre-existing cloud token therefore takes precedence over CE — rename `~/.kumiho/kumiho_authentication.json` to use CE auto-discovery.

### Configuration

| Env var | Purpose | Default |
| --- | --- | --- |
| `KUMIHO_LOCAL_SERVER_ENDPOINT` | Override the CE probe target (loopback only) | `127.0.0.1:9190` |
| `KUMIHO_LOCAL_SERVER_PORT` | Override just the CE port | `9190` |
| `KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS` | CE probe timeout (seconds) | `0.5` |

## kumiho 0.9.7 (February 2026) - Graph-Augmented Recall & Revision Stacking 🧠

This release introduces graph-augmented memory retrieval, server-side revision scoring, and intelligent revision stacking — closing the gap between isolated vector search and true graph-native reasoning. Ships alongside `kumiho-memory` 0.3.0.

### ✨ New Features

**`ScoreRevisions` gRPC RPC** *(Server-side embedding + fulltext scoring)*:

- New `kumiho.score_revisions()` and `Client.score_revisions()` methods.
- Scores specific revisions against a query using server-side embeddings and/or fulltext — no external embedding API needed on the client.
- Returns `score`, `score_method` (`"vector"`, `"fulltext"`, or `"hybrid"`), and the matched kref.

```python
import kumiho

results = kumiho.score_revisions(
    query="deployment architecture",
    revision_krefs=["kref://project/space/item.kind?r=1", ...],
    score_fields=["title", "summary"],
)
# [{"kref": "...", "score": 0.85, "score_method": "hybrid"}, ...]
```

**`embedding_text` parameter on `create_revision`**:

- `client.create_revision()` now accepts optional `embedding_text`.
- Overrides the server's default auto-generated embedding (which concatenates all metadata) with a focused string for more semantically distinctive vectors.

```python
item.create_revision(
    metadata={"title": "Auth migration plan", "summary": "..."},
    embedding_text="Auth migration plan: move from JWT to session-based auth",
)
```

### 🧩 MCP Server Improvements

**Revision stacking in `kumiho_memory_store`**:

- When `stack_revisions=True` (default), the tool now searches for an existing item with similar content before creating a new one.
- Uses fuzzy search with a 0.85 similarity threshold. If a match is found, stacks a new revision on the existing item instead of proliferating duplicates.
- Response includes `"stacked": true/false` and `"previous_revision_kref"` when stacking occurs.
- Title max length increased to 120 characters; summary max length increased to 2000 characters.

**Auto-artifact generation**:

- When no explicit `artifact_location` is provided, `kumiho_memory_store` now writes a Markdown artifact to `{KUMIHO_MEMORY_ARTIFACT_ROOT}/{project}/{space}/{item_name}.md`.
- Artifact root defaults to `~/.kumiho/artifacts/` and is configurable via `KUMIHO_MEMORY_ARTIFACT_ROOT` env var.
- Includes YAML frontmatter with title, type, date, and summary.

**In-process caching**:

- Added caches for projects, spaces, and bundles to avoid redundant gRPC round-trips within a session.
- `_get_project_cached()` replaces direct `kumiho.get_project()` calls in hot paths.

**Improved `kumiho_memory_retrieve`**:

- New `unroll_revisions` parameter — when True, returns ALL revisions of stacked items (useful for history browsing or Dream State). Defaults to False (latest/published only).
- Per-space context searching — `space_paths` filtering is now properly honored.
- Fixed cross-space data leak — the whole-project fallback search is disabled when the caller explicitly scoped to specific spaces.

**Better error handling**:

- `tool_get_item`, `tool_get_revision`, `tool_get_revision_by_tag`, and `tool_create_revision` now return `{"error": "...", "not_found": true}` for `NOT_FOUND` gRPC errors, enabling agents to distinguish "not found" from other failures.

### 📦 Proto Sync

- New messages: `ScoreRevisionsRequest`, `ScoredRevision`, `ScoreRevisionsResponse`.
- New RPC: `KumihoService.ScoreRevisions`.
- `CreateRevisionRequest` gains `embedding_text` field.

---

## kumiho-memory 0.3.0 (February 2026) - Graph-Augmented Recall & Enriched Summarization 🔮

Major release introducing graph-augmented memory retrieval, LLM-based sibling reranking, enriched summarization with structured event extraction, and post-consolidation edge discovery.

### ✨ New Features

**Graph-Augmented Recall** *(new module: `graph_augmentation.py`)*:

A multi-stage retrieval strategy that goes beyond vector similarity:

1. **Multi-query reformulation** — LLM generates 2-3 alternative queries capturing different semantic angles (emotions, causal events, consequences).
2. **Parallel recall + merge** — all queries run in parallel, results merged by best score per kref.
3. **Edge traversal** — follows graph edges from top-K results to discover connected memories that vector search alone would miss.
4. **Semantic fallback** — when no graph edges exist, falls back to multi-hop semantic recall using titles/summaries of initial results.

```python
# Enable via environment variable
# KUMIHO_GRAPH_AUGMENTED_RECALL=1

# Or via kumiho_memory_recall MCP tool
result = kumiho_memory_recall(
    query="should I use gRPC here?",
    graph_augmented=True,
)
```

Configuration via `GraphAugmentationConfig`:

- `max_hops` (default 1), `edge_types` (6 types), `top_k_for_traversal` (default 5)
- `max_total` (caps augmented results), `reformulate_queries` (bool)
- `traversal_timeout` (30s), `edge_creation_timeout` (60s)

**Post-consolidation edge discovery** (`kumiho_memory_discover_edges` MCP tool):

- After storing a memory, generates LLM "implication queries" — future scenarios where the memory would be relevant.
- Searches for matching existing memories and creates graph edges to top candidates.
- Parameters: `revision_kref`, `summary`, `max_queries`, `max_edges`, `min_score`, `edge_type`, `space_paths`.

**LLM-based sibling reranking**:

- When a stacked item has many revisions, the LLM selects the 1-3 most relevant siblings.
- Handles **semantic inversion** — where the user refers to the opposite of what's stored (e.g., "I've been dining out a lot" matching a memory about "meal prepping").
- Three-phase sibling selection: embedding mode → server-scored mode → BM25-light keyword fallback.

**`build_recalled_context()` method**:

- Builds ready-to-use text context from recalled memories for an answering LLM.
- `"full"` mode includes artifact content (truncated to 4000 chars); `"summarized"` mode uses title + summary only.
- Controlled via `recall_mode` parameter on `kumiho_memory_recall`.

### 🧠 Enhanced Summarization

**Enriched conversation summaries**:

- Summary expanded from "1-2 sentences" to "5-10 sentences preserving ALL concrete details".
- New structured extraction fields in summarization output:
  - `events` — array with `event`, `when`, `participants`, `consequence`
  - `implications` — 3-5 forward-looking statements for bridging semantic gaps in future recall
- Explicit instructions to preserve ALL dates, timestamps, temporal markers, names, places, brands, measurements.
- `max_tokens` increased from 1024 to 2560; fallback snippet from 180 to 500 chars.

**`generate_implications()` method**:

- Generates prospective statements using the light model — hypothetical future situations that only make sense because of the conversation.
- Uses different vocabulary than the original text to bridge semantic gaps in vector search.
- Runs independently from summarization and can be parallelized with it.

### 🔧 Improvements

**Session identity propagation**:

- `user_id` and `context` are now persisted as Redis session metadata on first message via `set_session_metadata()`.
- `consolidate_session()` auto-derives the storage space from session metadata when called without explicit parameters.
- Priority chain: explicit `space_path` > `user_id` + `context` > Redis metadata > topic-derived hint.

**Embedding adapter protocol**:

- New `EmbeddingAdapter` runtime-checkable protocol for text embedding providers.
- `OpenAICompatEmbeddingAdapter` concrete implementation for OpenAI and compatible APIs (default: `text-embedding-3-small`).
- Lazy initialization — LLM SDK import and API key validation deferred until first use.

**Parallel consolidation**:

- `consolidate_session()` now runs `summarize_conversation()` and `generate_implications()` concurrently via `asyncio.gather()`.

### 📦 New Exports

```python
from kumiho_memory import (
    GraphAugmentedRecall,
    GraphAugmentationConfig,
    EmbeddingAdapter,
    OpenAICompatEmbeddingAdapter,
)
```

### ✅ Paper Compliance Summary

| Paper Claim | Section | Implementation | Status |
| --- | --- | --- | --- |
| Graph-augmented retrieval beyond vector similarity | §7.3 | `GraphAugmentedRecall` with edge traversal | ✅ |
| Multi-query reformulation | §7.3.2 | LLM generates alternative search queries | ✅ |
| Immutable revisions, mutable pointers | §5, Principle 5 | Revision stacking in `kumiho_memory_store` | ✅ |
| Metadata over content (BYO-storage) | §5.4.2, Principle 11 | Auto-artifact generation for local files | ✅ |
| Structured event extraction | §9.2 | Events, implications in summarization output | ✅ |
| Post-consolidation edge enrichment | §9.4 | `kumiho_memory_discover_edges` tool | ✅ |
| Server-side scoring without external API | §7.5 | `ScoreRevisions` gRPC RPC | ✅ |

---

## kumiho 0.9.6 (February 2026) - Belief Revision & Privacy Boundary 🛡️

This release closes the gap between the paper's formal model and the SDK's runtime behavior. Every change maps to a specific claim in *Graph-Native Cognitive Memory for AI Agents* (v16).

### ✨ New Features

**`SUPERSEDES` edge type** *(Paper §7.4, Definition 7.4)*:

- Exposed `kumiho.SUPERSEDES` as a first-class edge type constant.
- Completes the belief revision vocabulary: when a revision replaces another, the SDK can now express `(r_new, SUPERSEDES, r_old)` as required by Definition 7.4.
- Available in both the Python SDK (`kumiho.SUPERSEDES`) and Dream State's LLM relationship analysis.

```python
import kumiho

# Express that a new decision supersedes the prior one
new_rev.create_edge(old_rev, kumiho.SUPERSEDES)
```

### 🔒 Privacy & Security

**Credential rejection boundary** *(Paper §10.4.5)*:

- New `PIIRedactor.reject_credentials()` method blocks secrets from crossing the local→cloud boundary.
- The MCP `memory_store` tool now scans `user_text`, `assistant_text`, `summary`, and `title` fields before any cloud graph write.
- Detected patterns raise `CredentialDetectedError` with a clear message — the write is rejected, not silently redacted.
- Six credential pattern categories are detected:

| Pattern | Examples |
| --- | --- |
| AWS access keys | `AKIA...`, `ASIA...` |
| Bearer tokens | `Bearer eyJ...` |
| API keys | `sk-...`, `pk-...`, `rk-...` (20+ chars) |
| PEM private keys | `-----BEGIN RSA PRIVATE KEY-----` |
| GitHub tokens | `ghp_...`, `gho_...`, `ghs_...` |
| Generic secrets | `api_key="..."`, `password="..."` |

- The same gate is enforced in `MemoryManager.consolidate_session()` and `store_tool_execution()` — all write paths to the cloud graph are covered.

### 🧠 Dream State Consolidation *(Paper §9)*

**Configurable safety parameters**:

- `max_deprecation_ratio` (float, 0.1–0.9, default 0.5) — controls the circuit-breaker threshold per run. Previously hardcoded at 50%.
- `allow_published_deprecation` (bool, default `False`) — when enabled, the Dream State *can* deprecate published items, with a WARNING-level audit entry. Previously these were unconditionally protected.
- Both parameters are exposed via the `kumiho_memory_dream_state` MCP tool for agent-accessible tuning.

**`SUPERSEDES` in relationship analysis**:

- The Dream State LLM prompt now includes `SUPERSEDES` as a candidate relationship type alongside `DERIVED_FROM`, `REFERENCED`, and `DEPENDS_ON`.
- This enables automatic detection of supersession chains during offline consolidation.

### 🔧 Improvements

**Discovery User-Agent tracking**:

- Discovery HTTP requests now include `User-Agent: kumiho-python/{version}` for control-plane observability and debugging.

### 📦 Companion Release: kumiho-memory 0.2.0

This SDK release ships alongside `kumiho-memory` 0.2.0, which contains the runtime implementations referenced above:

- `kumiho_memory.privacy` module (`PIIRedactor`, `CredentialDetectedError`)
- Credential rejection gates in `MemoryManager`
- Configurable Dream State safety parameters
- Updated MCP tool schemas

### ✅ Paper Compliance Summary

| Paper Claim | Section | SDK Implementation | Status |
| --- | --- | --- | --- |
| Revision creates SUPERSEDES edge | §7.4, Def 7.4 | `kumiho.SUPERSEDES` edge type | ✅ |
| Secrets must not cross privacy boundary | §10.4.5 | `PIIRedactor.reject_credentials()` | ✅ |
| Dream State circuit breaker configurable | §9.3 | `max_deprecation_ratio` param | ✅ |
| Published protection override with audit | §9.3 | `allow_published_deprecation` param | ✅ |
| Dream State detects supersession | §9, §7.4 | SUPERSEDES in LLM assessment prompt | ✅ |

## kumiho 0.9.5 (February 2026) - API Token Bootstrap for Discovery 🔑

### ✨ New Behavior

**`auto_configure_from_discovery()` now supports API-token-first flows**:
- When `KUMIHO_AUTH_TOKEN` is explicitly set, the SDK now bootstraps discovery directly from that token.
- No cached `kumiho-auth login` credentials are required for this path.

### 🔧 Reliability Improvements

**Bootstrap and discovery token handling hardened**:
- Default-client bootstrap now prefers an explicit env token before attempting cached credential refresh.
- Discovery routing now supports control-plane JWT-first behavior with Firebase fallback when needed.

## kumiho 0.9.4 (February 2026) - Hybrid Search Mode + Kref Validation 🔍

### ✨ New Behavior

**MCP full-text search now reports search mode**:
- `kumiho_fulltext_search` responses now include `search_mode`.
- Reported values are `"fulltext"` or `"hybrid"` (when STUDIO+ vector-backed hybrid search is available).

### 🐛 Bug Fixes

**Kref validation accepts underscore-prefixed segments**:
- Updated Kref URI validation regex to allow `_` at the start of project/space path segments.
- Fixes false-negative validation for valid krefs containing underscore-prefixed segments.

### 📦 Proto Sync

- Synced generated protobufs to include `SearchResponse.search_mode`.

### ✅ Compatibility Notes

- `search_mode` in MCP search output depends on server support; it falls back to `"fulltext"` when unavailable.

## kumiho 0.9.2 (February 2026) - Batch Revision Fetch (Proto Sync) 📦

### ✨ New Features

- Added `batch_get_revisions` to fetch multiple revisions by revision krefs or item krefs + tag, with optional partial results.

## kumiho 0.9.1 (January 2026) - MCP Full-Text Search Tool 🔎

### ✨ New Features

**MCP full-text search tool**:
- Added `kumiho_fulltext_search` MCP tool for fuzzy search across items (Google-like search).
- Supports `context`, `kind`, and `include_deprecated` filters for scoping results.
- Optional deep search across revision tags/metadata and artifact names/metadata via `include_revision_metadata` and `include_artifact_metadata`.
- Results include relevance `score` and `matched_in`, with `limit` and `include_metadata` for output control.

## kumiho 0.9.0 (January 2026) - Full-Text Search 🔎

### ✨ New Features

**Full-text fuzzy search API**:
- Added `kumiho.search()` and `Client.search()` for Google-like fuzzy search across item names and kinds.
- Supports `context_filter`, `kind_filter`, and `min_score` to scope and tune relevance.
- Optional deep search across revision tags/metadata and artifact names/metadata via `include_revision_metadata` and `include_artifact_metadata`.
- Results include relevance score and `matched_in` source, with pagination via `page_size` and `cursor`.

### ✅ Compatibility Notes

- Requires a kumiho-server build that exposes the `Search` gRPC endpoint and full-text indexes.

## kumiho 0.8.6 (January 2026) - Kref Ergonomics for Artifacts 🔗

### ✨ New Behavior

**`get_artifact()` default artifact resolution**:
- `kumiho.get_artifact("kref://project/space/item.kind")` now resolves the *default artifact* on the latest revision.
- `kumiho.get_artifact("kref://project/space/item.kind?r=REV")` now resolves the *default artifact* on that specific revision.
- If no default artifact is set, the SDK raises a `ValueError` prompting the caller to supply an explicit `&a=name`.

### ✅ Compatibility Notes

- This workflow expects a `kumiho-server` that can return a revision when given an item kref (latest revision resolution).

## kumiho 0.8.5 (January 2026) - Revision Delete & System Tag Consistency 🏷️

### 🔧 Behavior Updates

**Server-authoritative `latest` on deletion**:
- Removed SDK-side logic that attempted to re-tag `latest` after deleting a revision.
- `Revision.delete(force=...)` now issues `DeleteRevision` and relies on the server to keep the system-managed `latest` tag consistent.

### 🧪 Tests

- Updated unit tests to assert the SDK does not call tag operations as part of revision deletion.

### ✅ Compatibility Notes

- For tag-based latest resolution (e.g. resolving with `tag="latest"`) after hard deletes, use with a `kumiho-server` version that re-points `latest` after deleting the latest-tagged revision.

## kumiho 0.8.4 (January 2026) - Item Metadata Fix & Packaging Cleanup 🧰

### 🐛 Bug Fixes

**Create Item with Metadata**:
- Fixed `AttributeError: to_pb` when calling `create_item(..., metadata=...)`.
- The SDK now correctly converts the returned protobuf Kref into a `kumiho.Kref` before calling `UpdateItemMetadata`.

### 📦 Packaging

**License & Distribution Metadata**:
- Updated README/package metadata to reflect MIT licensing.
- Ensured the wheel includes a license file.

## kumiho 0.8.3 (December 2025) - Authentication Resilience 🛡️

### 🐛 Bug Fixes

**Auto-refresh on JWKS Errors**:
- Fixed an issue where the client would fail with `UNAVAILABLE` status and "jwks fetch error" when the server rotated keys.
- The client now correctly identifies this specific error pattern and forces a token refresh, ensuring seamless connectivity during control plane updates.

## kumiho 0.8.2 (December 2025) - MCP Token Optimization 📉

### 🚀 Performance Improvements

**MCP Token Usage Reduction**:
- Optimized MCP tools to significantly reduce token consumption in LLM contexts.
- **New Tool**: `kumiho_get_provenance_summary` provides a lightweight summary of AI provenance (seed, model, prompt) without the full revision overhead.
- **Metadata Stripping**: `kumiho_search_items` and `kumiho_get_item_revisions` now default to `include_metadata=False`.
- Added `include_metadata` parameter to these tools for cases where full metadata is explicitly needed.
- Solves "Quota exceeded" errors when listing large directories or search results containing heavy ComfyUI workflows.

## kumiho 0.8.1 (December 2025) - MCP Multi-tenancy & Stability 🛠️

### 🐛 Bug Fixes

**MCP Context Propagation**:
- Fixed `EOF when reading a line` error in MCP tool handlers when running in non-interactive environments (like Cloud Run).
- Switched tool handlers to use `asyncio.to_thread` to ensure `contextvars` (like `kumiho.use_client`) are correctly propagated to the execution thread.
- This enables multi-tenant MCP support where tools are executed with the user's specific credentials.

**Non-interactive Bootstrapping**:
- Updated internal bootstrapping to default to `interactive=False`, preventing the SDK from attempting to prompt for credentials in server environments.

## kumiho 0.8.0 (December 2025) - Event Streaming Enhancements ⚡

### ✨ New Features

**Event Stream Timeouts**:
- Added `timeout` parameter to `event_stream()` and `Client.event_stream()`.
- Allows the gRPC stream to close gracefully after a specified duration.
- Essential for polling-based integrations (like n8n) and serverless environments.

```python
# Stream events for 30 seconds then stop
try:
    for event in kumiho.event_stream(routing_key_filter="revision.*", timeout=30):
        print(f"New revision: {event.kref}")
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        print("Polling window finished")
```

### 📦 API Changes

- `kumiho.event_stream()`: Added `timeout: Optional[float]` argument.
- `Client.event_stream()`: Added `timeout: Optional[float]` argument.

### 🛠️ Bug Fixes

- Fixed an issue where `event_stream` would hang indefinitely in certain network conditions.
- Improved cleanup of gRPC stream resources when the iterator is exhausted or timed out.

---

## kumiho 0.7.0 (December 2025) - Deprecation Support 🗑️

### ✨ New Features

**Deprecation Filtering**:
- Added `include_deprecated` parameter to `get_items()` and `item_search()` methods.
- Allows retrieving items that have been marked as deprecated (soft deleted/hidden).
- Default behavior remains to exclude deprecated items.

```python
# Search including deprecated items
items = client.item_search(
    context_filter="my-project",
    include_deprecated=True
)
```

### 📦 API Changes

- `Client.get_items()`: Added `include_deprecated` argument (default: `False`).
- `Client.item_search()`: Added `include_deprecated` argument (default: `False`).
- `Space.get_items()`: Added `include_deprecated` argument (default: `False`).
- Updated Protobuf definitions to match server version 0.7.0.

---

## kumiho 0.4.4 (December 2025) - Pagination & Search Improvements 🔍

### ✨ New Features

**Pagination Support**:
- Added pagination to item listing and search methods.
- New `PagedList` return type containing `next_cursor` and `total_count`.

```python
# Pagination in Project
page1 = project.get_items(page_size=10)
if page1.next_cursor:
    page2 = project.get_items(page_size=10, cursor=page1.next_cursor)
```

**Project Search**:
- Added `project.get_items()` method for searching items within a project context.
- Updated `project.get_items()` to support pagination.

### 📦 API Changes

- `Space.get_items()` now accepts `page_size` and `cursor`.
- `Project.get_items()` now accepts `page_size` and `cursor`.
- `Client.item_search()` and `Client.get_items()` now return `PagedList` when pagination is active.

---

## kumiho 0.4.3 (December 2025) - Stability & Performance 🚀

### ✨ New Features

- **Improved Connection Handling**: Better retry logic for transient network failures
- **Enhanced Error Messages**: More descriptive error messages for common failure scenarios

### 🐛 Bug Fixes

- Fixed race condition in concurrent revision creation
- Fixed memory leak in long-running sessions with many graph traversals
- Fixed edge case where `get_space()` returned incorrect path for root-level items

### 🔧 Improvements

- Reduced gRPC connection overhead by reusing channels
- Optimized batch operations for large artifact lists
- Improved type hints coverage across all public APIs

### 📦 Dependencies

- Updated `grpcio` to 1.60.0+
- Updated `protobuf` to 4.25.0+

---

## kumiho 0.4.2 (December 2025) - Item Properties & Kref Improvements 🎯

### ✨ New Features

**Item Class Properties**:
- `item.project` - Get the project name the item belongs to
- `item.space` - Get the space path the item belongs to

```python
import kumiho

# Get an item and access its project/space
item = kumiho.get_item("kref://my-project/models/characters/hero.model")
print(item.project)  # "my-project"
print(item.space)    # "models/characters"
print(item.kref)     # "kref://my-project/models/characters/hero.model"
```

**Kref Class Improvements**:
- `kref.get_project()` - Extract just the project name from a kref URI
- `kref.get_space()` - Now returns space path **without** the project prefix

```python
from kumiho import Kref

kref = Kref("kref://my-project/assets/textures/hero-diffuse.texture")
print(kref.get_project())  # "my-project"
print(kref.get_space())    # "assets/textures" (previously: "my-project/assets/textures")
```

### ⚠️ Breaking Changes

- **`Kref.get_space()` behavior changed**: Previously returned `project/space`, now returns just `space` without the project prefix. Use `kref.get_project()` to get the project separately.

### 📦 Updated Exports

`Item` class now has:
- `project` property → `str`
- `space` property → `str`

`Kref` class now has:
- `get_project()` method → `str`
- Updated `get_space()` method → `str` (space only, no project)

---

## kumiho 0.4.1 (December 2025) - Tenant Info & Bug Fixes 🔧

### ✨ New Features

**Tenant Information Functions**:
- `kumiho.get_tenant_info()` - Get full tenant info from discovery cache
- `kumiho.get_tenant_slug()` - Get URL-safe tenant identifier for project naming

```python
import kumiho

# Get full tenant info
info = kumiho.get_tenant_info()
print(info["tenant_id"])    # "22fac7c8-5daf-4ad6-9b7e-70606b1d0c92"
print(info["tenant_name"])  # "My Studio"
print(info["roles"])        # ["owner", "editor"]

# Get URL-safe slug for project naming
slug = kumiho.get_tenant_slug()  # "22fac7c8" (falls back to tenant_id prefix if name has special chars)
project_name = f"ComfyUI@{slug}"
```

### 🐛 Bug Fixes

- **Reduced Logging Verbosity**: Sensitive metadata no longer logged at INFO level
  - Changed gRPC interceptor logging from INFO to DEBUG
  - Metadata keys logged instead of full values

### 📦 New Exports

Added to `kumiho` module:
- `get_tenant_info(tenant_hint=None)` → `Dict` or `None`
- `get_tenant_slug(tenant_hint=None)` → `str` or `None`

---

## kumiho 0.4.0 (December 2025) - Package Restructuring 📦

### 🎯 Overview

This release restructures the Kumiho Python SDK into two separate PyPI packages for better modularity and independent versioning.

### 📦 Package Split

Starting with v0.4.0, Kumiho is distributed as **two separate packages**:

| Package | Version | Description | Install |
|---------|---------|-------------|---------|
| **kumiho** | 0.4.0 | Core SDK library | `pip install kumiho` |
| **kumiho-cli** | 1.0.0 | CLI tools & MCP server | `pip install kumiho-cli` |

### ⚠️ Breaking Changes

**Removed from `kumiho` package**:
- `kumiho-auth` CLI command (moved to `kumiho-cli` package)

**Migration**:
```bash
# Before (v0.3.0)
pip install kumiho
kumiho-auth login  # This worked

# After (v0.4.0)
pip install kumiho kumiho-cli
kumiho-cli login   # New command name

# Or install with CLI extra
pip install kumiho[cli]
kumiho-cli login
```

### ✨ What's New

- **Optional CLI Dependency**: Install `kumiho[cli]` to get both packages
- **Cleaner SDK**: Core SDK no longer includes CLI dependencies
- **Independent Versioning**: CLI tools can be updated without SDK changes

### 📦 Installation

```bash
# Core SDK only (for programmatic use)
pip install kumiho

# SDK + CLI tools (for interactive development)
pip install kumiho[cli]

# Or install separately
pip install kumiho kumiho-cli
```

### 🔧 Usage

**SDK (unchanged)**:
```python
import kumiho

# Auto-configure from cached credentials
kumiho.auto_configure_from_discovery()

# Create and manage assets
project = kumiho.create_project("my-project")
space = project.create_space("assets")
item = space.create_item("hero", "model")
```

**CLI (new package)**:
```bash
# Authentication
kumiho-cli login
kumiho-cli refresh
kumiho-cli whoami

# MCP Server (unchanged)
kumiho-mcp
```

### 📋 Requirements

- Python 3.10+
- `kumiho-cli` package for authentication (optional)

### 📚 Documentation

- **SDK Documentation**: [docs.kumiho.io/python](https://docs.kumiho.io/python)
- **CLI Documentation**: See `kumiho-cli` package README

### 🔗 Related Packages

- [kumiho-cli](https://pypi.org/project/kumiho-cli/) - CLI tools (v1.0.0)

---

## kumiho-cli 1.0.0 (December 2025) - Initial Release 🎉

### 🎯 Overview

First standalone release of Kumiho CLI tools, extracted from the main `kumiho` package for independent versioning and lighter dependencies.

### ✨ Features

**Authentication Commands**:
- `kumiho-cli login` - Interactive Firebase authentication
- `kumiho-cli refresh` - Refresh cached tokens
- `kumiho-cli whoami` - Display current user info

**MCP Server** (Model Context Protocol):
- `kumiho-mcp` - Start MCP server for AI assistants
- 39 tools for GitHub Copilot, Claude, Cursor integration
- Graph traversal and asset management capabilities

**Credential Management**:
- Secure storage in `~/.kumiho/kumiho_authentication.json`
- Automatic token refresh
- Firebase ID token + Control Plane JWT exchange
- Environment variable support

### 📦 Installation

```bash
# Standalone installation
pip install kumiho-cli

# Or with pipx (recommended for CLI tools)
pipx install kumiho-cli

# Or as part of kumiho SDK
pip install kumiho[cli]
```

### 🔧 Quick Start

```bash
# Login to Kumiho Cloud
kumiho-cli login

# Check authentication status
kumiho-cli whoami

# Refresh tokens
kumiho-cli refresh

# Start MCP server for AI assistants
kumiho-mcp
```

### 🌐 Cross-SDK Support

The `kumiho-cli` package provides authentication for **all Kumiho SDKs**:

**Python**:
```python
import kumiho
kumiho.auto_configure_from_discovery()  # Uses ~/.kumiho/ credentials
```

**C++**:
```cpp
auto client = kumiho::Client::createFromEnv();  // Reads ~/.kumiho/
```

**Dart**:
```dart
final client = await KumihoClient.fromEnv();  // Reads ~/.kumiho/
```

**FastAPI**:
```bash
export KUMIHO_TOKEN=$(kumiho-cli get-token)  # For deployment
```

### 📋 Requirements

- Python 3.8+ (lower requirement than SDK)
- `requests>=2.31.0` (lightweight dependencies)

### 🌐 Supported Platforms

- Windows
- macOS
- Linux

### � Security

- Credentials stored with `0600` permissions
- Supports environment variable overrides
- No credentials in code or version control

### 📚 Documentation

- **Full README**: [GitHub](https://github.com/kumihoclouds/kumiho-python/tree/main/kumiho-cli)
- **Environment Variables**: See README for `KUMIHO_*` variables

### 📄 License

Apache License 2.0

---

## Previous Releases

### v0.3.0 (November 2025)

- Initial development release
- Integrated authentication CLI
- MCP server support
- Graph traversal features

---

**Repository**: https://github.com/kumihoclouds/kumiho-python  
**Issues**: https://github.com/kumihoclouds/kumiho-python/issues
