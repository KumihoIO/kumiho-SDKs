package kumiho

import (
	"context"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Artifact is a file reference (path/URI) within a revision. Kumiho tracks the
// location, never the bytes ("BYO storage").
type Artifact struct {
	Kref         Kref
	Location     string
	RevisionKref Kref
	ItemKref     Kref // empty if not provided by the server
	CreatedAt    string
	Author       string
	Metadata     map[string]string
	Deprecated   bool
	Username     string

	client *Client
}

func newArtifact(p *pb.ArtifactResponse, c *Client) *Artifact {
	return &Artifact{
		Kref:         krefFromPB(p.GetKref()),
		Location:     p.GetLocation(),
		RevisionKref: krefFromPB(p.GetRevisionKref()),
		ItemKref:     krefFromPB(p.GetItemKref()),
		CreatedAt:    p.GetCreatedAt(),
		Author:       p.GetAuthor(),
		Metadata:     p.GetMetadata(),
		Deprecated:   p.GetDeprecated(),
		Username:     p.GetUsername(),
		client:       c,
	}
}

// Name returns the artifact name (from the kref's &a=).
func (a *Artifact) Name() string { return a.Kref.ArtifactName() }

// SetMetadata merges metadata into this artifact.
func (a *Artifact) SetMetadata(ctx context.Context, metadata map[string]string) (*Artifact, error) {
	return a.client.UpdateArtifactMetadata(ctx, a.Kref, metadata)
}

// SetAttribute sets a single metadata attribute.
func (a *Artifact) SetAttribute(ctx context.Context, key, value string) (bool, error) {
	return a.client.SetAttribute(ctx, a.Kref, key, value)
}

// GetAttribute gets a single metadata attribute (ok=false if unset).
func (a *Artifact) GetAttribute(ctx context.Context, key string) (string, bool, error) {
	return a.client.GetAttribute(ctx, a.Kref, key)
}

// DeleteAttribute deletes a single metadata attribute.
func (a *Artifact) DeleteAttribute(ctx context.Context, key string) (bool, error) {
	return a.client.DeleteAttribute(ctx, a.Kref, key)
}

// Delete deletes this artifact.
func (a *Artifact) Delete(ctx context.Context, force bool) error {
	return a.client.DeleteArtifact(ctx, a.Kref, force)
}

// SetDeprecated deprecates/restores this artifact.
func (a *Artifact) SetDeprecated(ctx context.Context, status bool) error {
	return a.client.SetDeprecated(ctx, a.Kref, status)
}

// SetDefault makes this artifact the default for its revision.
func (a *Artifact) SetDefault(ctx context.Context) error {
	return a.client.SetDefaultArtifact(ctx, a.RevisionKref, a.Name())
}

// GetRevision returns the parent revision.
func (a *Artifact) GetRevision(ctx context.Context) (*Revision, error) {
	return a.client.GetRevision(ctx, a.RevisionKref.URI())
}

// GetItem returns the owning item.
func (a *Artifact) GetItem(ctx context.Context) (*Item, error) {
	if a.ItemKref != "" {
		return a.client.GetItemByKref(ctx, a.ItemKref.URI())
	}
	rev, err := a.GetRevision(ctx)
	if err != nil {
		return nil, err
	}
	return rev.GetItem(ctx)
}

// GetSpace returns the containing space.
func (a *Artifact) GetSpace(ctx context.Context) (*Space, error) {
	item, err := a.GetItem(ctx)
	if err != nil {
		return nil, err
	}
	return item.GetSpace(ctx)
}

// GetProject returns the containing project.
func (a *Artifact) GetProject(ctx context.Context) (*Project, error) {
	sp, err := a.GetSpace(ctx)
	if err != nil {
		return nil, err
	}
	return sp.Project(ctx)
}
