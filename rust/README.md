# Kumiho Rust SDK

Async Rust client for [Kumiho Cloud](https://kumiho.io) — a graph-native
creative & AI asset-management system. Kumiho tracks revisions, relationships,
and lineage **without uploading your files** ("BYO storage"); it stores paths,
metadata, and the dependency graph.

This crate mirrors the Python gold-standard SDK: a low-level [`Client`] that
wraps every gRPC method, plus fluent domain types (`Project`, `Space`, `Item`,
`Revision`, `Artifact`, `Edge`, `Bundle`).

## Install

```toml
[dependencies]
kumiho = { path = "../rust" }          # or the published version
tokio = { version = "1", features = ["full"] }
```

Building requires `protoc` (Protocol Buffers compiler) on `PATH`; the shared
`proto/kumiho.proto` git submodule is compiled at build time via `tonic-build`.

```sh
git submodule update --init   # fetch proto/
cargo build
```

## Quick start

```rust,no_run
use kumiho::{Client, EdgeType};

#[tokio::main]
async fn main() -> kumiho::Result<()> {
    // Auto-discovery from ~/.kumiho credentials, or an explicit endpoint.
    let client = Client::connect("https://us-central.kumiho.cloud").await?;

    let project = client.create_project("my-vfx-project", "VFX assets").await?;
    let space = project.create_space("characters", None).await?;
    let item = space.create_item("hero", "model").await?;

    let rev = item.create_revision(None, 0).await?;
    rev.create_artifact("mesh", "/assets/hero.fbx", None).await?;
    rev.tag("approved").await?;

    // Lineage: this revision depends on a texture revision.
    let texture = client.get_revision("kref://my-vfx-project/tex/skin.texture?r=1").await?;
    rev.create_edge(&texture, EdgeType::DEPENDS_ON, None).await?;
    Ok(())
}
```

See [`examples/quickstart.rs`](examples/quickstart.rs):

```sh
KUMIHO_SERVER_ENDPOINT=localhost:8080 cargo run --example quickstart
```

## Connecting

| Method | Use |
| --- | --- |
| `Client::connect("host:port" \| "https://host")` | Explicit endpoint (token auto-loaded). |
| `Client::auto()` | Control-plane discovery from cached credentials, or a local self-hosted CE server. |
| `Client::builder()…build()` | Full control: endpoint, token, tenant hint, discovery, extra metadata. |

```rust,no_run
# async fn f() -> kumiho::Result<()> {
let client = kumiho::Client::builder()
    .endpoint("https://eu-west.kumiho.cloud")
    .token(std::env::var("KUMIHO_TOKEN").unwrap())
    .tenant_hint("my-studio")
    .build()
    .await?;
# Ok(()) }
```

### Environment variables

- `KUMIHO_AUTH_TOKEN` — bearer token (overrides `~/.kumiho/kumiho_authentication.json`).
- `KUMIHO_SERVER_ENDPOINT` / `KUMIHO_SERVER_ADDRESS` — fallback endpoint.
- `KUMIHO_CONTROL_PLANE_URL` — discovery control plane (default `https://control.kumiho.cloud`).
- `KUMIHO_DISABLE_AUTO_DISCOVERY` — set to disable discovery.
- `KUMIHO_SERVER_USE_TLS`, `KUMIHO_SERVER_AUTHORITY`, `KUMIHO_SERVER_CA_FILE` — TLS overrides.
- `KUMIHO_RPC_TIMEOUT_SECS`, `KUMIHO_GRPC_RETRY_MAX_ATTEMPTS` — per-call deadline & retry tuning.

## Krefs

A `Kref` is a URI identifying any object:
`kref://project/space/item.kind?r=REVISION&a=ARTIFACT`. It validates on
construction (rejecting path traversal and control characters), accepts Unicode
path segments, and exposes accessors:

```rust
use kumiho::Kref;
let k = Kref::new("kref://film/characters/hero.model?r=3&a=mesh").unwrap();
assert_eq!(k.project(), "film");
assert_eq!(k.space(), "characters");
assert_eq!(k.kind(), "model");
assert_eq!(k.revision(), 3);
assert_eq!(k.artifact_name().as_deref(), Some("mesh"));
```

## Features

- Projects, spaces, items, revisions, artifacts, edges, bundles — full CRUD.
- Tags (`tag` / `untag` / `has_tag` / `was_tagged`) incl. time-travel resolution.
- Graph traversal: dependencies, dependents, shortest path, impact analysis.
- Full-text search + server-side revision scoring; batch revision fetch.
- Granular attribute get/set/delete on any entity.
- Real-time event streaming (`event_stream`) with cursor resume.
- Transient-failure retry with backoff, HTTP/2 keepalive, per-call deadlines,
  auth/tenant/correlation-id metadata injection.
- Control-plane discovery with an encrypted on-disk routing cache and local
  self-hosted CE auto-detection.

## Reliability semantics

Unary RPCs retry automatically on `UNAVAILABLE`, `DEADLINE_EXCEEDED`,
`INTERNAL`, and `RESOURCE_EXHAUSTED` with exponential backoff + jitter (default
3 attempts). Streaming RPCs are not auto-retried. Every call carries a unique
`x-correlation-id` for tracing.

## License

MIT — see [LICENSE](LICENSE).
