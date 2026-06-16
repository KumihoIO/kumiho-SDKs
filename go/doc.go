// Package kumiho is the Go client for Kumiho Cloud — a graph-native creative &
// AI asset-management system. Kumiho tracks revisions, relationships, and
// lineage without uploading your files ("BYO storage"); it stores paths,
// metadata, and the dependency graph.
//
// It mirrors the Python gold-standard SDK: a low-level [Client] wrapping every
// gRPC method, plus fluent domain types ([Project], [Space], [Item],
// [Revision], [Artifact], [Edge], [Bundle]).
//
// # Quick start
//
//	ctx := context.Background()
//	client, err := kumiho.Connect(ctx, "https://us-central.kumiho.cloud")
//	if err != nil { log.Fatal(err) }
//	defer client.Close()
//
//	project, _ := client.CreateProject(ctx, "my-vfx-project", "VFX assets")
//	space, _   := project.CreateSpace(ctx, "characters", "")
//	item, _    := space.CreateItem(ctx, "hero", "model")
//	rev, _     := item.CreateRevision(ctx, nil, 0)
//	rev.CreateArtifact(ctx, "mesh", "/assets/hero.fbx", nil)
//	rev.Tag(ctx, "approved")
//
// A [Kref] is a URI identifying any object:
// kref://project/space/item.kind?r=REVISION&a=ARTIFACT.
package kumiho

// Version is the SDK version.
const Version = "0.10.0"

// Standard tags.
const (
	// LatestTag points at the newest revision of an item.
	LatestTag = "latest"
	// PublishedTag marks a published / released revision.
	PublishedTag = "published"
)
