package kumiho

import (
	"context"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Revision is a specific, immutable iteration of an item.
//
// Tags is a snapshot from when the revision was fetched; call Refresh to
// re-read server-managed tags (e.g. "latest").
type Revision struct {
	Kref            Kref
	ItemKref        Kref
	Number          int32
	Latest          bool
	Tags            []string
	Metadata        map[string]string
	CreatedAt       string
	Author          string
	Deprecated      bool
	Published       bool
	Username        string
	DefaultArtifact string

	client *Client
}

func newRevision(p *pb.RevisionResponse, c *Client) *Revision {
	return &Revision{
		Kref:            krefFromPB(p.GetKref()),
		ItemKref:        krefFromPB(p.GetItemKref()),
		Number:          p.GetNumber(),
		Latest:          p.GetLatest(),
		Tags:            p.GetTags(),
		Metadata:        p.GetMetadata(),
		CreatedAt:       p.GetCreatedAt(),
		Author:          p.GetAuthor(),
		Deprecated:      p.GetDeprecated(),
		Published:       p.GetPublished(),
		Username:        p.GetUsername(),
		DefaultArtifact: p.GetDefaultArtifact(),
		client:          c,
	}
}

// CreateArtifact creates a file-reference artifact on this revision.
func (r *Revision) CreateArtifact(ctx context.Context, name, location string, metadata map[string]string) (*Artifact, error) {
	return r.client.CreateArtifact(ctx, r.Kref, name, location, metadata)
}

// SetMetadata merges metadata into this revision.
func (r *Revision) SetMetadata(ctx context.Context, metadata map[string]string) (*Revision, error) {
	return r.client.UpdateRevisionMetadata(ctx, r.Kref, metadata)
}

// SetAttribute sets a single metadata attribute.
func (r *Revision) SetAttribute(ctx context.Context, key, value string) (bool, error) {
	return r.client.SetAttribute(ctx, r.Kref, key, value)
}

// GetAttribute gets a single metadata attribute (ok=false if unset).
func (r *Revision) GetAttribute(ctx context.Context, key string) (string, bool, error) {
	return r.client.GetAttribute(ctx, r.Kref, key)
}

// DeleteAttribute deletes a single metadata attribute.
func (r *Revision) DeleteAttribute(ctx context.Context, key string) (bool, error) {
	return r.client.DeleteAttribute(ctx, r.Kref, key)
}

// HasTag reports whether this revision currently has a tag (server call).
func (r *Revision) HasTag(ctx context.Context, tag string) (bool, error) {
	return r.client.HasTag(ctx, r.Kref, tag)
}

// Tag applies a tag.
func (r *Revision) Tag(ctx context.Context, tag string) error {
	return r.client.TagRevision(ctx, r.Kref, tag)
}

// Untag removes a tag.
func (r *Revision) Untag(ctx context.Context, tag string) error {
	return r.client.UntagRevision(ctx, r.Kref, tag)
}

// WasTagged reports whether this revision was ever tagged with tag.
func (r *Revision) WasTagged(ctx context.Context, tag string) (bool, error) {
	return r.client.WasTagged(ctx, r.Kref, tag)
}

// GetArtifact gets an artifact by name.
func (r *Revision) GetArtifact(ctx context.Context, name string) (*Artifact, error) {
	return r.client.GetArtifact(ctx, r.Kref, name)
}

// GetArtifacts gets all artifacts.
func (r *Revision) GetArtifacts(ctx context.Context) ([]*Artifact, error) {
	return r.client.GetArtifacts(ctx, r.Kref)
}

// GetLocations returns the file locations of all artifacts.
func (r *Revision) GetLocations(ctx context.Context) ([]string, error) {
	arts, err := r.GetArtifacts(ctx)
	if err != nil {
		return nil, err
	}
	locs := make([]string, 0, len(arts))
	for _, a := range arts {
		locs = append(locs, a.Location)
	}
	return locs, nil
}

// GetItem returns the parent item.
func (r *Revision) GetItem(ctx context.Context) (*Item, error) {
	return r.client.GetItemByKref(ctx, r.ItemKref.URI())
}

// GetSpace returns the containing space.
func (r *Revision) GetSpace(ctx context.Context) (*Space, error) {
	space := r.ItemKref.Space()
	path := "/" + r.ItemKref.Project()
	if space != "" {
		path = "/" + r.ItemKref.Project() + "/" + space
	}
	return r.client.GetSpace(ctx, path)
}

// GetProject returns the containing project.
func (r *Revision) GetProject(ctx context.Context) (*Project, error) {
	sp, err := r.GetSpace(ctx)
	if err != nil {
		return nil, err
	}
	return sp.Project(ctx)
}

// Refresh re-reads this revision from the server (returns a fresh copy).
func (r *Revision) Refresh(ctx context.Context) (*Revision, error) {
	return r.client.GetRevision(ctx, r.Kref.URI())
}

// SetDefaultArtifact sets the default artifact (used when resolving without &a=).
func (r *Revision) SetDefaultArtifact(ctx context.Context, artifactName string) error {
	return r.client.SetDefaultArtifact(ctx, r.Kref, artifactName)
}

// Delete deletes this revision.
func (r *Revision) Delete(ctx context.Context, force bool) error {
	return r.client.DeleteRevision(ctx, r.Kref, force)
}

// SetDeprecated deprecates/restores this revision.
func (r *Revision) SetDeprecated(ctx context.Context, status bool) error {
	return r.client.SetDeprecated(ctx, r.Kref, status)
}

// CreateEdge creates an edge from this revision to target.
func (r *Revision) CreateEdge(ctx context.Context, target *Revision, edgeType string, metadata map[string]string) (*Edge, error) {
	return r.client.CreateEdge(ctx, r, target, edgeType, metadata)
}

// GetEdges gets edges for this revision (edgeTypeFilter "" = all).
func (r *Revision) GetEdges(ctx context.Context, edgeTypeFilter string, direction EdgeDirection) ([]*Edge, error) {
	return r.client.GetEdges(ctx, r.Kref, edgeTypeFilter, direction)
}

// DeleteEdge deletes an edge from this revision to target.
func (r *Revision) DeleteEdge(ctx context.Context, target *Revision, edgeType string) error {
	return r.client.DeleteEdge(ctx, r.Kref, target.Kref, edgeType)
}

// GetAllDependencies returns all transitive dependencies (outgoing).
func (r *Revision) GetAllDependencies(ctx context.Context, edgeTypeFilter []string, maxDepth, limit int32) (*TraversalResult, error) {
	return r.client.TraverseEdges(ctx, r.Kref, Outgoing, edgeTypeFilter, maxDepth, limit, false)
}

// GetAllDependents returns all transitive dependents (incoming).
func (r *Revision) GetAllDependents(ctx context.Context, edgeTypeFilter []string, maxDepth, limit int32) (*TraversalResult, error) {
	return r.client.TraverseEdges(ctx, r.Kref, Incoming, edgeTypeFilter, maxDepth, limit, false)
}

// FindPathTo returns the shortest path to target, or (nil, nil) if none.
func (r *Revision) FindPathTo(ctx context.Context, target *Revision, edgeTypeFilter []string, maxDepth int32) (*RevisionPath, error) {
	res, err := r.client.FindShortestPath(ctx, r.Kref, target.Kref, edgeTypeFilter, maxDepth, false)
	if err != nil {
		return nil, err
	}
	return res.FirstPath(), nil
}

// AnalyzeImpact returns revisions impacted by changes to this revision.
func (r *Revision) AnalyzeImpact(ctx context.Context, edgeTypeFilter []string, maxDepth, limit int32) ([]ImpactedRevision, error) {
	return r.client.AnalyzeImpact(ctx, r.Kref, edgeTypeFilter, maxDepth, limit)
}
