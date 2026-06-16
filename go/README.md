# Kumiho Go SDK

Go client for [Kumiho Cloud](https://kumiho.io) — a graph-native creative & AI
asset-management system. Kumiho tracks revisions, relationships, and lineage
**without uploading your files** ("BYO storage"); it stores paths, metadata, and
the dependency graph.

It mirrors the Python gold-standard SDK: a low-level `Client` wrapping every
gRPC method, plus fluent domain types (`Project`, `Space`, `Item`, `Revision`,
`Artifact`, `Edge`, `Bundle`).

## Install

```sh
go get github.com/KumihoIO/kumiho-SDKs/go
```

```go
import kumiho "github.com/KumihoIO/kumiho-SDKs/go"
```

## Quick start

```go
package main

import (
	"context"
	"log"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
)

func main() {
	ctx := context.Background()

	// Explicit endpoint, or kumiho.Auto(ctx) for control-plane discovery.
	client, err := kumiho.Connect(ctx, "https://us-central.kumiho.cloud")
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	project, _ := client.CreateProject(ctx, "my-vfx-project", "VFX assets")
	space, _ := project.CreateSpace(ctx, "characters", "")
	item, _ := space.CreateItem(ctx, "hero", "model")

	rev, _ := item.CreateRevision(ctx, nil, 0)
	rev.CreateArtifact(ctx, "mesh", "/assets/hero.fbx", nil)
	rev.Tag(ctx, "approved")

	// Lineage: this revision depends on a texture revision.
	tex, _ := client.GetRevision(ctx, "kref://my-vfx-project/tex/skin.texture?r=1")
	rev.CreateEdge(ctx, tex, kumiho.EdgeDependsOn, nil)
}
```

Run the example:

```sh
KUMIHO_SERVER_ENDPOINT=localhost:8080 go run ./examples/quickstart
```

## Connecting

| Function | Use |
| --- | --- |
| `kumiho.Connect(ctx, "host:port" \| "https://host")` | Explicit endpoint (token auto-loaded). |
| `kumiho.Auto(ctx)` | Discovery from cached credentials, or a local self-hosted CE server. |
| `kumiho.Builder()…Build(ctx)` | Full control: endpoint, token, tenant hint, discovery, metadata. |

```go
client, err := kumiho.Builder().
	Endpoint("https://eu-west.kumiho.cloud").
	Token(os.Getenv("KUMIHO_TOKEN")).
	TenantHint("my-studio").
	Build(ctx)
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
`kref://project/space/item.kind?r=REVISION&a=ARTIFACT`. Validate with
`kumiho.NewKref`/`ValidateKref` (path traversal and control characters are
rejected; Unicode path segments are accepted), then use the accessors:

```go
k, _ := kumiho.NewKref("kref://film/characters/hero.model?r=3&a=mesh")
k.Project()      // "film"
k.Space()        // "characters"
k.Kind()         // "model"
k.Revision()     // 3
k.ArtifactName() // "mesh"
```

## Features

- Projects, spaces, items, revisions, artifacts, edges, bundles — full CRUD.
- Tags (`Tag`/`Untag`/`HasTag`/`WasTagged`) incl. time-travel resolution.
- Graph traversal: dependencies, dependents, shortest path, impact analysis.
- Full-text search + server-side revision scoring; batch revision fetch.
- Granular attribute get/set/delete on any entity.
- Real-time event streaming (`EventStream`) with cursor resume.
- Transient-failure retry with backoff, HTTP/2 keepalive, per-call deadlines,
  and auth/tenant/correlation-id metadata injection.
- Control-plane discovery with an encrypted on-disk routing cache and local
  self-hosted CE auto-detection.

## Reliability semantics

Unary RPCs retry automatically on `UNAVAILABLE`, `DEADLINE_EXCEEDED`,
`INTERNAL`, and `RESOURCE_EXHAUSTED` with exponential backoff + jitter (default
3 attempts; tune via `KUMIHO_GRPC_RETRY_MAX_ATTEMPTS`). Streaming RPCs are not
auto-retried. Every call carries a unique `x-correlation-id` for tracing.

## Regenerating protobuf code

The generated `kumihopb/` package is checked in. To regenerate after a proto
change (requires `protoc`, `protoc-gen-go`, `protoc-gen-go-grpc`):

```sh
make generate
```

## License

MIT — see [LICENSE](LICENSE).
