package kumiho

import (
	"context"
	"fmt"
	"strings"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Item is a versioned asset identified by a Kref.
type Item struct {
	Kref       Kref
	Name       string
	ItemName   string
	Kind       string
	CreatedAt  string
	Author     string
	Metadata   map[string]string
	Deprecated bool
	Username   string

	client *Client
}

func newItem(p *pb.ItemResponse, c *Client) *Item {
	return &Item{
		Kref:       krefFromPB(p.GetKref()),
		Name:       p.GetName(),
		ItemName:   p.GetItemName(),
		Kind:       p.GetKind(),
		CreatedAt:  p.GetCreatedAt(),
		Author:     p.GetAuthor(),
		Metadata:   p.GetMetadata(),
		Deprecated: p.GetDeprecated(),
		Username:   p.GetUsername(),
		client:     c,
	}
}

// Project returns the project name this item belongs to.
func (i *Item) Project() string { return i.Kref.Project() }

// Space returns the space path this item belongs to.
func (i *Item) Space() string { return i.Kref.Space() }

func (i *Item) spacePath() string {
	space := i.Kref.Space()
	if space == "" {
		return "/" + i.Kref.Project()
	}
	return "/" + i.Kref.Project() + "/" + space
}

// CreateRevision creates a revision (number=0 auto-increments).
func (i *Item) CreateRevision(ctx context.Context, metadata map[string]string, number int32) (*Revision, error) {
	return i.client.CreateRevision(ctx, i.Kref, metadata, number, "")
}

// GetRevisions lists all revisions.
func (i *Item) GetRevisions(ctx context.Context) ([]*Revision, error) {
	return i.client.GetRevisions(ctx, i.Kref)
}

// GetRevision gets a revision by number.
func (i *Item) GetRevision(ctx context.Context, number int32) (*Revision, error) {
	return i.client.GetRevision(ctx, fmt.Sprintf("%s?r=%d", i.Kref.URI(), number))
}

// GetLatestRevision returns the latest revision, or (nil, nil) if none.
//
// Mirrors the Python Item.get_latest_revision: prefer the revision flagged
// "latest", otherwise fall back to the highest-numbered revision.
func (i *Item) GetLatestRevision(ctx context.Context) (*Revision, error) {
	revisions, err := i.GetRevisions(ctx)
	if err != nil {
		return nil, err
	}
	if len(revisions) == 0 {
		return nil, nil
	}
	latest := revisions[0]
	for _, r := range revisions {
		if r.Latest {
			return r, nil
		}
		if r.Number > latest.Number {
			latest = r
		}
	}
	return latest, nil
}

// GetRevisionByTag returns the revision currently carrying tag, or (nil, nil).
func (i *Item) GetRevisionByTag(ctx context.Context, tag string) (*Revision, error) {
	rev, err := i.client.ResolveKref(ctx, i.Kref.URI(), &tag, nil)
	if err != nil {
		if IsNotFound(err) {
			return nil, nil
		}
		return nil, err
	}
	return rev, nil
}

// GetRevisionByTime returns the revision that held tag (or latest) at time.
// time may be "YYYYMMDDHHMM" or an RFC3339 timestamp; tag "" means latest.
func (i *Item) GetRevisionByTime(ctx context.Context, time string, tag string) (*Revision, error) {
	var timeStr string
	switch {
	case strings.ContainsRune(time, 'T'):
		timeStr = time
	case len(time) >= 12:
		timeStr = fmt.Sprintf("%s-%s-%sT%s:%s:59+00:00", time[0:4], time[4:6], time[6:8], time[8:10], time[10:12])
	default:
		timeStr = time
	}
	var tagPtr *string
	if tag != "" {
		tagPtr = &tag
	}
	rev, err := i.client.ResolveKref(ctx, i.Kref.URI(), tagPtr, &timeStr)
	if err != nil {
		if IsNotFound(err) {
			return nil, nil
		}
		return nil, err
	}
	return rev, nil
}

// PeekNextRevision returns the next revision number.
func (i *Item) PeekNextRevision(ctx context.Context) (int32, error) {
	return i.client.PeekNextRevision(ctx, i.Kref)
}

// GetSpace returns the containing space.
func (i *Item) GetSpace(ctx context.Context) (*Space, error) {
	return i.client.GetSpace(ctx, i.spacePath())
}

// GetProject returns the containing project.
func (i *Item) GetProject(ctx context.Context) (*Project, error) {
	sp, err := i.GetSpace(ctx)
	if err != nil {
		return nil, err
	}
	return sp.Project(ctx)
}

// SetMetadata merges metadata into this item.
func (i *Item) SetMetadata(ctx context.Context, metadata map[string]string) (*Item, error) {
	return i.client.UpdateItemMetadata(ctx, i.Kref, metadata)
}

// SetAttribute sets a single metadata attribute (updates the in-memory cache on
// success, matching Python).
func (i *Item) SetAttribute(ctx context.Context, key, value string) (bool, error) {
	ok, err := i.client.SetAttribute(ctx, i.Kref, key, value)
	if err == nil && ok {
		setMeta(&i.Metadata, key, value)
	}
	return ok, err
}

// GetAttribute gets a single metadata attribute (ok=false if unset).
func (i *Item) GetAttribute(ctx context.Context, key string) (string, bool, error) {
	return i.client.GetAttribute(ctx, i.Kref, key)
}

// DeleteAttribute deletes a single metadata attribute (updates the in-memory
// cache on success, matching Python).
func (i *Item) DeleteAttribute(ctx context.Context, key string) (bool, error) {
	ok, err := i.client.DeleteAttribute(ctx, i.Kref, key)
	if err == nil && ok {
		delete(i.Metadata, key)
	}
	return ok, err
}

// Delete deletes this item (force=true to delete with revisions).
func (i *Item) Delete(ctx context.Context, force bool) error {
	return i.client.DeleteItem(ctx, i.Kref, force)
}

// SetDeprecated deprecates/restores this item (updates the in-memory flag).
func (i *Item) SetDeprecated(ctx context.Context, status bool) error {
	err := i.client.SetDeprecated(ctx, i.Kref, status)
	if err == nil {
		i.Deprecated = status
	}
	return err
}
