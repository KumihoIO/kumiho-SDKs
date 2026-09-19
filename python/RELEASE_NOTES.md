# Kumiho Python SDK - Release Notes

> **This file is the release record.** It is the narrative, user-facing history:
> what changed, why it mattered, and what you have to do about it.
> `python/docs/changelog.md` is the terse Keep a Changelog companion — same
> releases, one screen each, no upgrade guidance. Every release needs an entry
> here; a changelog entry alone is not enough, and the two drifting apart is
> what produced the gaps backfilled in KumihoIO/kumiho-SDKs#155 and #157.


## kumiho 0.14.0 (September 2026) — `evaluate()`: Judging What Recall Found 🧪

Recall has always had to choose its own width. Ask for five memories and you
get the five the vector search liked best — which is the right five only when
the query happens to sit where the embedding is sharp. Widen it to twenty and
the good ones are in there, along with fifteen that merely share vocabulary.
There was no step between "retrieved" and "returned" that could tell those
apart, so the width had to be the answer.

This release adds that step. `kumiho.evaluate()` takes text you already have
and questions you write, and asks a server-managed provider to answer them
per fragment. It is not a search and it is not a retrieval — it judges what
you hand it, nothing more.

```python
result = kumiho.evaluate(
    query="What did we decide about the release cadence?",
    fragments=[
        {"id": "m1", "text": "We ship on the first Tuesday."},
        {"id": "m2", "text": "The logo is green."},
    ],
    questions=[{
        "id": "relevant",
        "type": "noul",
        "instructions": "Does {fragment} answer the query?",
    }],
)
result.by_id()["m1"].answers["relevant"].noul
```

### ✨ What changed

- **`kumiho.evaluate(...)`, and `Client.evaluate(...)` behind it.** Positional
  `query`, `fragments` and `questions`; keyword `extra_context`, `mode`,
  `rubric_version`, `timeout_ms` and `allow_cache`. Three question types:
  `"noul"` gives a float in [0, 1], `"choice"` picks a named option and
  reports the odds over all of them, `"score"` returns a level with the
  legend it indexes. You get one `FragmentEvaluation` per fragment in request
  order, and `result.by_id()` if you would rather have them keyed by your own
  id.
- **Your ids never leave the server.** What the provider sees is the query,
  `extra_context`, each question's instructions and criteria, and each
  fragment's text and metadata. Fragment ids are replaced with the server's
  own private labels before the request is built — which is also why the
  literal `{fragment}` placeholder in your instructions is passed through
  untouched rather than rendered here. Write it and let the server fill it.
- **Frozen dataclasses, or plain dicts, whichever you have.**
  `EvaluationFragment` and `EvaluationQuestion` are re-exported from
  `kumiho`, and mappings with the same keys build exactly the same request.
  The result types — `EvaluationResult`, `FragmentEvaluation`,
  `EvaluationUsage`, `NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer` — are
  exported too.
- **`usage` tells you where the month stands.** Input and output tokens,
  provider requests actually sent, fragments served from cache and therefore
  not metered, and the monthly total after this call against its limit
  (`-1` for unlimited). Reading it is how a caller decides whether to widen
  the next recall or narrow it.
- **The client checks only what it can check cheaply.** A non-empty query,
  non-empty unique fragment ids, a known question type, and no `__` in a
  question id — the server reserves that for its own per-fragment ids. Those
  are the mistakes worth catching before a call costs provider tokens.
  Everything about shape and size is the server's call, because it is the
  only side that knows the current limits. Mode and question type are
  translated rather than forwarded: a typo in either would otherwise arrive
  as the enum's zero value and quietly change what you asked for.
- **`timeout_ms` sets both deadlines.** The server gets it as its own hint,
  and the gRPC call gets it plus a two-second margin, so a slow-but-answering
  server's status — including a non-OK one — reaches you instead of being
  overwritten by `DEADLINE_EXCEEDED`.

### ⚠️ Availability

Evaluation is a **Kumiho Cloud feature on paid tiers**. There is nothing to
configure and nothing new to authenticate; the entitlement rides on the
credentials you already use.

- **Self-hosted CE, and any server older than this RPC**, does not implement
  it and answers `UNIMPLEMENTED`.
- **A tenant without the entitlement** gets `PERMISSION_DENIED`, or an
  in-band `"not_entitled"` result when the server prefers to answer that way.
  Branch on `result.status` if you want to treat the in-band form as data.
- Both raise `grpc.RpcError` the way every other RPC's failures do. The SDK
  has no exception hierarchy to fit them into and this release does not
  invent one.

### 📋 Upgrading

Nothing to do. `evaluate()` is new surface; no existing call changes
behaviour, and the generated stubs move only by the `Evaluate` additions and
the descriptor offsets they shift.

There is deliberately **no MCP tool** for this. Evaluation is the ranking step
the memory layer runs over candidates it has already retrieved — its caller is
kumiho-memory's recall path, not a model holding a tool list. The other
language SDKs do not have `evaluate` yet; the proto is shared, the bindings
are not.


## kumiho 0.13.2 (September 2026) — Corrections Name What They Correct ✍️

When you tell an assistant it got something wrong, the memory it already
stored has to change. Until now the store had no way to be told *which* one.
It looked for a similar-looking memory and, if the resemblance was strong
enough, filed the new text as a revision of it; otherwise it created a second
memory beside the first. Both outcomes are wrong for a correction. The first
is a guess, and the second leaves the stale version exactly where recall will
find it.

The guess could not be tuned into a right answer either. The similarity gate
was calibrated on real captures: a restated memory about the same subject
scores 0.58-0.68, while hosted deployments run the gate in strong-only mode at
0.75. A correction goes through that gate and misses. Widening it to catch
corrections would start displacing unrelated memories that merely sit in the
same topic. And the search the gate runs is scoped by a *prefix*, so it could
reach into a differently-named space and revise something there.

So this release stops guessing when it does not have to. A caller that knows
which memory it is correcting says so.

### ✨ What changed

- **`item_kref` names the memory being revised.** `tool_memory_store` takes
  it as a keyword; `tool_memory_store_batch` takes the same key per capture.
  Give it an item kref or a revision kref — if you have the kref of the
  revision you are correcting, that works, its selectors are stripped for you.
  Then nothing is inferred: the similarity search does not run, the new text
  becomes a revision of that item, and the item's own space is where it lands
  and what gets recorded in its metadata. Any `space_path` or `space_hint`
  passed alongside is ignored for placement, and the item's bundle membership
  is left exactly as it was. The result reads like a stacked store — `stacked`
  true, and `previous_revision_kref` pointing at what the correction
  supersedes. Batch rows report `previous_revision_kref` on this path; they
  never had the field at all.
- **A kref that does not resolve is an error.** It does not quietly fall back
  to searching, and it does not mint a new memory. A correction aimed at
  nothing should say so, not scatter.
- **The `published` tag follows the correction — and only then.** `published`
  is the approval marker: revisions are immutable once published, downstream
  consumers rely on them not changing, and the server keeps a single active
  `published` tag per item, moving it when another revision is tagged. Recall
  resolves `published` before `latest`, so a correction that does not move the
  tag is invisible. When the named item already had a published revision, the
  new one takes it — your own tags are applied first and `published` last,
  because the server freezes a published revision and refuses tags applied
  after it. When the item had no published revision, nothing is published.
  **Nothing is ever published on the store's own initiative.** The tag is only
  ever carried forward, never created, and only when a caller revised a
  specific item that already had one.
- **On this path, a failed `published` call is a failed store.** Elsewhere a
  tag that will not apply is swallowed as best-effort. Here it is the whole
  point of the call: if the tag stays on the old revision, recall keeps
  serving the text you just corrected. You get an error instead of a success
  that did not happen.
- **`item_kref` is not in the `kumiho_memory_store` MCP schema.** kumiho-memory's
  reflect is the caller that fills it, from a capture that says what it
  revises. A model calling the tool directly still has only the old surface.

### 🐛 Also fixed

- **`space_paths` was not actually isolating spaces.** The server filters by
  context as a plain string prefix, so asking for `9miho` also returned
  project-root memories whose *name* starts with `9miho-`, and asking for
  `work` returned memories from `work-infra`. Retrieval now checks each
  result's space one path segment at a time — on the search, bundle, listing
  and latest paths alike — so a real sub-space still counts and a lookalike
  does not. The stacking search is checked the same way, which closes the
  other half of the problem: a store could otherwise displace a published
  revision in a space nobody addressed.
- **`mode="latest"` could hide the very memory you asked for.** 0.13.1 walked
  items by `modified_at`, treating it as an upper bound on revision dates, and
  stopped early once enough results were newer than the next item's bound.
  That reasoning has a hole: it is only sound if the bound holds for the items
  the stop never resolves. On a server whose `modified_at` does not advance
  with a new revision, the item that should have come back first sits *below*
  the stop point — so it is never resolved, so it never disproves the bound,
  so it never appears. The early stop is gone. The window is the same as
  before: the `max(limit * 4, 20)` items with the newest `modified_at`
  (falling back to item `created_at`) are resolved, and results are ordered by
  their revision's own date. The cost is bounded by that window either way.
- **`mode="first"` could resolve the whole project.** When the `memory_types`
  filter matched nothing, the fallback walked every scoped item at 1-2 RPCs
  each — 2,157 resolutions measured. It is bounded by the same window now.
- **`"most recent"` did not select latest mode.** Only the exact alias
  spellings did, so the phrasing a model reaches for first fell through to
  search. Mode text is now lowercased, stripped, and runs of spaces and
  hyphens folded to `_` before the aliases are matched.
- **An unreachable fallback removed.** A widen-to-the-whole-project branch in
  retrieval required both `contexts != [project_name]` and no `space_paths` —
  conditions that cannot both hold. It is deleted; the scoped listing above it
  already covered the case.
- `_most_recent_items` now normalizes timestamps to UTC the way every other
  ordering path does, instead of discarding the offset.

### 📋 Upgrading

Nothing to do. A store without `item_kref` behaves exactly as it did in
0.13.1, including the `tags or ["published"]` default for an untagged new
memory. Retrieval results change only where they were wrong: scoped queries no
longer include same-prefixed spaces, and latest mode no longer omits an item
the early stop had skipped.

Downstream, kumiho-memory's `kumiho_memory_reflect` gains a `revises` capture
field that passes `item_kref` through — a separate PR. The hosted connector at
`mcp.kumiho.cloud` picks both up when its pins move.


## kumiho 0.13.1 (September 2026) — Retrieval Modes That Do What They Say 🕒

`kumiho_memory_retrieve` advertised three modes in its schema — search, first
and latest — and only search behaved as described. There was no branch for
`latest`, so the value fell straight through to search, and `first` ignored
both the query and `space_paths`. Separately, `spaces_used` was never filled
from search hits. Both the hosted connector and the local plugin serve this
tool, and models are told to reach for `mode="latest"` when a user asks for the
most recent memory, so those questions were being answered from a list that
was not in date order:

- **With a query**, results were relevance-ranked, exactly as in search mode.
- **Without a query**, the pattern fallback happened to return the newest
  *items* first — by item `created_at`. An old memory that had just received
  a newer stacked revision kept its original position, so the update a user
  had most recently made was the one least likely to come back.

### ✨ What changed

- **`mode="latest"` orders newest first by the revision it returns.** The key
  is the `created_at` of each item's `published` revision (else `latest`) —
  the same resolution every retrieval path already uses — so a stacked update
  counts as recent. Missing timestamps sort last; ties break by relevance score,
  then kref.
- **With a query, relevance filters and date orders.** The same fuzzy search
  as search mode (space scoping, `memory_types`, the deep-then-shallow retry,
  `unroll_revisions`) selects the candidates, widened from `limit * 2` to
  `max(limit * 4, 20)` hits because date order promotes hits relevance order
  would have cut. `scores` still carries each result's relevance score; it is
  simply no longer the sort key. With `unroll_revisions`, each revision is
  ordered by its own date. If the query matches nothing, the name-pattern
  fallback search mode uses applies here too (score `0.0`), in date order.
- **Without a query, a bounded walk that still finds restacked items.**
  Resolving an item's revision costs 1-2 RPCs, so resolving a whole project
  is not an option (the 457-item incident behind 0.10.3's fallback bound).
  `ItemResponse` already carried `modified_at`, and creating a revision
  advances it, so it is an upper bound on every revision's `created_at` —
  measured on a live graph, no resolved revision was newer than its item's
  `modified_at` (312 items, 131 of them multi-revision). The walk goes through
  every in-scope item by `modified_at`, newest first, and stops once `limit`
  results are all newer than the next item's bound. Nothing further down can
  displace them, so the result is exact. On that graph it resolved 5 of
  2,106 items for `limit=5`, and a brute-force check agreed with the result.
  A hard cap of `max(limit * 4, 20)` resolutions holds regardless.
- **`created_at` on latest results** — a list aligned with `revision_krefs`,
  so a model can say *when*, not just *what*. Search and first results do not
  gain the key.
- **Aliases:** `"newest"`, `"recent"` and `"most_recent"` select latest. Mode
  matching ignores case and surrounding whitespace.
- **`mode="first"` respects the query and `space_paths`.** It used to list
  the whole project and return its oldest item, whatever was asked. Auto-detect
  selects `first` only when a query is present, so "what was the first
  decision about auth?" returned the oldest memory of any kind, anywhere. It
  now searches within the same scope contexts as the other modes, with no
  cross-space fallback. With a query, the top `max(limit * 4, 20)` relevance
  hits are the candidates, and the oldest of them by *item* `created_at` (when
  the memory was first created) that passes `memory_types` is returned.
  Ordering needs no RPC, so revisions are resolved one candidate at a time
  until one passes. If none does, first mode falls back to the scoped listing,
  as search and latest do. Without a query, the scoped items are walked oldest
  first until one passes, as before. It still returns at most one result, with
  the same three keys. A revision-less item no longer satisfies a
  `memory_types` filter.
- **`spaces_used` is populated from search hits.** The search loop read
  `item.space.path`, but `Item.space` is the kref's space as a `str`, so the
  `AttributeError` was swallowed right after each result was appended.
  Results were unaffected; `spaces_used` just stayed empty for every search
  hit. Search hits now report their space in the form the scope contexts
  already use: project-prefixed, e.g. `"CognitiveMemory/personal"`, or the
  project name for an item at the root. Only hits that survive into the
  returned results count. The bundle and listing fallbacks still report the
  scope they searched, and first mode reports the returned item's space
  instead of the project name.
- **`Item.modified_at`** is now exposed on the SDK's `Item`.

### ⚠️ Limits worth knowing

- **The cap can bind.** With a `memory_types` filter that rejects most of the
  newest items, the walk stops after `max(limit * 4, 20)` resolutions and can
  return fewer than `limit` results even though older matches exist.
- **Servers that do not report a usable `modified_at`** fall back to item
  `created_at` for the walk — the old window — which misses an old item whose
  only recent change is a new revision. If a resolved revision ever turns out
  newer than its item's `modified_at`, early stopping switches off and the cap
  alone bounds the walk.
- **Bundles** keep search mode's rules for *when* members are added (only
  while there are fewer than `limit` results); members that are added are
  ordered by date like everything else.
- **First mode's relevance pool is a pool.** An older relevant memory ranked
  below the top `max(limit * 4, 20)` hits is not considered; raise `limit` to
  widen it.

### ✅ Compatibility

- **`spaces_used` is not aligned with `revision_krefs`, and never was.** It is
  a deduped list of spaces. A client reading `spaces_used[i]` as the i-th
  result's space was relying on an accident: for search hits the list was
  empty, and otherwise it held a scope context or two. Now that search hits
  fill it, that reading returns the wrong space. Derive a result's space from
  its own kref instead. The openclaw client in kumiho-plugins reads the list by
  index and is being fixed there.
- **`mode="first"` answers differently when given a query or `space_paths`**;
  that is the fix. Called with neither, it returns the same item as before,
  and only `spaces_used` changes, from the project name to that item's space.
- **Otherwise, no upgrade action is needed.** Search mode returns the same
  krefs and scores in the same order as before, and so does a caller that
  omits `mode`, because the function and the MCP dispatcher both default it
  to `"search"`. Only an explicitly empty `mode` auto-detects `first`, and that
  detection is unchanged. There is deliberately no query-text detection for
  latest: kumiho-memory's recall calls this function without a `mode` and must
  keep relevance ranking, even when the user's message says "latest". It reads
  `revision_krefs` and `scores`, not `spaces_used`.
- The MCP `mode` parameter is still a free string, not a JSON-Schema `enum`.
  Tool schemas are validated on dispatch, so an enum would reject spellings
  the code accepts, such as `"earliest"` and the latest aliases.
- **Downstream:** the hosted connector (mcp.kumiho.cloud) picks this up when
  its `kumiho` pin moves to 0.13.1.

### 🧪 Testing

- `python/python/tests/test_mcp_server.py::TestMemoryRetrieveLatestMode`:
  date order over relevance with scores retained, the widened pool, unrolled
  revisions, a restacked old item winning without a query, `published` pinned
  to an older revision, `space_paths` / `memory_types` with no cross-space
  fallback, `limit` and aligned `created_at` with missing timestamps last and
  mixed UTC offsets, aliases, search-mode and mode-less regressions (through
  MCP dispatch too), the resolution cap on 457 items, the `modified_at` walk
  finding a restacked item and stopping at `limit`, the untrustworthy-bound
  guard, and date-ordered bundle members. 17 of the 19 fail against 0.13.0;
  the two that pass are the search-mode regression and the resolution cap,
  which 0.13.0 already satisfied.
- `TestMemoryRetrieveSpacesUsed`: the project-prefixed form (nested spaces,
  root items); search hits deduped in result order, with a hit cut by `limit`
  contributing nothing in search or latest mode; the unroll path; and the
  listing fallback still reporting its scope.
- `TestMemoryRetrieveFirstMode`: no query walks the project oldest first and
  stops at the first passing item; `space_paths` stays inside the space on
  both paths; an auto-detected query returns the oldest relevant match rather
  than the oldest item, never resolving hits past the pool; `memory_types` on
  both paths, including revision-less items.
- Full suite from `python/python/`: 393 passed, 100 skipped, with and without
  the real `kumiho_memory` source on `PYTHONPATH` (Windows, mcp 2.2.0). First
  mode and `spaces_used` were also checked read-only against a live graph.

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
- **`KUMIHO_STACK_MIDDLE_BAND`** — a switch for the revision-stacking gate
  0.12.2 introduced. Set it to `0` and a capture stacks only when it clears the
  0.75 strong threshold **and** the lexical floor; the 0.55 type-match band is
  withheld. The default is unchanged. Every `kumiho_memory_store` and
  `kumiho_memory_store_batch` result now also carries `stack_mode` next to
  `stack_score`, so a deployment can tell which gate produced a number before
  it decides whether to change the gate.

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
- **Set `KUMIHO_STACK_MIDDLE_BAND=0` when you host.** The two-band stacking
  gate was calibrated on one corpus, and its middle band is the contested one:
  every false positive measured there was an unrelated same-type neighbour
  scoring 0.58-0.62 in a topically homogeneous space. A false stack moves the
  `published` tag onto an unrelated item, and every recall path resolves
  `published` first — so the displaced memory leaves the default retrieval
  surface silently. A shared multi-tenant server has not measured its own
  distribution yet, so it should run strong-only: near-duplicates still stack,
  the contested band stays shut, and the `stack_mode` / `stack_score` fields on
  every store result are the telemetry that tells you when to open it. The
  stdio plugin keeps the default.

### 🧪 Testing

- `python/python/tests/test_mcp_connector_profile.py`: the 18-tool profile
  pinned by name, annotation coverage and honesty for all 63 tools, the
  out-of-profile refusal on both mcp legs, and hosted-mode tenancy — cache
  keying, the `auth_token` no-op, and the discovery-fallback refusal.
- The same file also pins the two features against each other: a
  `kumiho_memory_store` dispatched through the **connector** server still
  carries `stack_mode`, and `KUMIHO_STACK_MIDDLE_BAND=0` still withholds the
  middle band there — with the default-gate control alongside it, so a search
  stub returning nothing cannot pass for a withheld band.
- The store path is pinned **fail-closed** at the tool boundary, not only at
  the helper: hosted with no bound client, `kumiho_memory_store` and
  `kumiho_memory_store_batch` raise before anything reaches a graph; with
  `kumiho.use_client(...)` bound, the bound client is the one that sees the
  call and `~/.kumiho` is never read.
- Full suite from `python/python/`: 368 passed, 98 skipped, with and without
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
