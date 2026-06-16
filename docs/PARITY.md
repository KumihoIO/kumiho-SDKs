# Go & Rust SDK parity with the Python SDK

The Go and Rust SDKs mirror the Python SDK (the gold standard). This records the
parity status and the few intentional, idiomatic differences. Every PR builds and
tests both SDKs (`sdk-ci.yml`), including in-process mock-server integration tests
and unit tests that assert behavior matches Python.

## Feature parity

All Python client methods, domain-model methods (Project, Space, Item, Revision,
Artifact, Edge, Bundle, Event), kref parsing/validation, discovery, token loading,
and error types have Go and Rust equivalents. Parity work explicitly added:

- **Firebase-token discovery fallback** — discovery retries with a Firebase id
  token when the bearer is a control-plane token (Go + Rust).
- **`find_all_paths_to`** — all shortest paths, not just the first (Go + Rust).
- **`get_item_from_revision`**, **`get_child_spaces`**, **`set_allow_public`** (Go + Rust).
- **Typed reserved-kind error** — `ReservedKindError` (Go) / `Error::ReservedKind`
  (Rust), discriminable by callers.
- **`TenantInfo` / `TenantSlug`** — cached tenant info / URL-safe slug (Go + Rust).
- **`FromLocalCE` / `Client::from_local_ce`** — explicit local-CE constructor (Go + Rust).
- **Configurable timeouts** — `KUMIHO_DISCOVERY_TIMEOUT_SECONDS` and
  `KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS` (Go + Rust; Rust previously had none).
- **Traversal/path defaults** — `max_depth=10`, `limit=100` (Go + Rust).
- **`KumihoError` catch-all interface** (Go) and **named `EdgeTypeValidationError`**
  produced by `validate_edge_type` (Rust), matching Python's error model.
- **Go models sync in-memory state** after a successful `set_attribute` /
  `delete_attribute` / `tag` / `untag` / `set_deprecated` / `set_default_artifact`.

## Intentional differences (parity-or-better)

- **No global/default client.** Python's module-level functions
  (`kumiho.create_project()`, `use_client`, `get_client`, …) wrap a hidden,
  process-global client. Go and Rust instead take an explicit `*Client` / `Client`
  receiver — the idiomatic, testable, concurrency-safe equivalent. Every operation
  exposed by the global layer is available as a client method.
- **Rust models are immutable snapshots.** Go models update their local state
  after a mutation (matching Python); Rust models are `Clone` value snapshots —
  re-fetch (or use a returned model) for fresh state. This avoids hidden mutation
  and is the idiomatic Rust choice.
- **Discovery configured via env.** Python's `client_from_discovery` takes
  `control_plane_url` / `cache_path` params; Go/Rust read `KUMIHO_CONTROL_PLANE_URL`
  and `KUMIHO_DISCOVERY_CACHE_FILE` (same capability, idiomatic shape).
- **`event_stream` timeout.** Python takes a `timeout`; Go uses `context` deadlines
  (idiomatic), Rust callers wrap the stream with `tokio::time::timeout`.
- Minor: Go `ReservedKinds` is a slice (single value); Go `Page.TotalCount` is a
  plain `int32`; the Rust routing-cache key omits the Unix uid (the cache file is
  namespaced per-SDK, so cross-SDK sharing never applies).
