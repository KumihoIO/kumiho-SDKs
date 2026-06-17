# Getting Started

This guide walks through installing the Kumiho Go SDK and creating your first
assets. For the complete, generated API reference see [API Reference](api.md).

## Install

```bash
go get github.com/KumihoIO/kumiho-SDKs/go
```

```go
import kumiho "github.com/KumihoIO/kumiho-SDKs/go"
```

## Connect & authenticate

`Connect` dials a Kumiho data-plane endpoint. Authentication is loaded
automatically from the `KUMIHO_AUTH_TOKEN` environment variable or from the
credentials file written by `kumiho-cli login`.

```go
ctx := context.Background()
client, err := kumiho.Connect(ctx, "https://us-central.kumiho.cloud")
if err != nil {
    log.Fatal(err)
}
defer client.Close()
```

## Create assets

The fluent domain types mirror the Python SDK:

```go
project, _ := client.CreateProject(ctx, "my-vfx-project", "VFX assets")
space, _   := project.CreateSpace(ctx, "characters", "")
item, _    := space.CreateItem(ctx, "hero", "model")
rev, _     := item.CreateRevision(ctx, nil, 0)
art, _     := rev.CreateArtifact(ctx, "mesh", "/assets/hero.fbx", nil)
rev.Tag(ctx, "approved")
```

A **Kref** is a URI that identifies any object:
`kref://project/space/item.kind?r=REVISION&a=ARTIFACT`.

## Search & discovery

The Go SDK has full parity with Python, including the newer retrieval features:

```go
// Full-text fuzzy search (typo-tolerant), ranked by relevance.
page, _ := client.Search(ctx, "hero", kumiho.SearchOptions{KindFilter: "model"})

// Semantic scoring of specific revisions against a query.
// (scoreFields = nil uses the stored embeddings.)
scored, _ := client.ScoreRevisions(ctx, "approved hero",
    []string{"kref://my-vfx-project/characters/hero.model?r=1"}, nil)

// Fetch many revisions in one round-trip (by item kref + tag here).
revs, notFound, _ := client.BatchGetRevisions(ctx,
    nil,                                                   // revisionKrefs
    []string{"kref://my-vfx-project/characters/hero.model"}, // itemKrefs
    "latest",                                              // tag
    true,                                                  // allowPartial
)
```

These mirror the Python `search`, `score_revisions`, and `batch_get_revisions`.

## Next steps

- Browse the full [API Reference](api.md).
- See the other SDKs at [docs.kumiho.io](https://docs.kumiho.io).
- The canonical Go package docs are also on
  [pkg.go.dev](https://pkg.go.dev/github.com/KumihoIO/kumiho-SDKs/go).
