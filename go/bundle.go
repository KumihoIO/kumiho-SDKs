package kumiho

import (
	"context"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// ReservedKinds are item kinds that cannot be created via CreateItem.
var ReservedKinds = []string{"bundle"}

// BundleMember is an item that belongs to a bundle.
type BundleMember struct {
	ItemKref        Kref
	AddedAt         string
	AddedBy         string
	AddedByUsername string
	AddedInRevision int32
}

// BundleRevisionHistory is one immutable membership-change record.
type BundleRevisionHistory struct {
	RevisionNumber int32
	Action         string // "CREATED", "ADDED", or "REMOVED"
	MemberItemKref Kref
	Author         string
	Username       string
	CreatedAt      string
	Metadata       map[string]string
}

// Bundle is a reserved-kind item that aggregates other items with a full,
// immutable audit trail. It embeds *Item, so Item fields/methods are available.
type Bundle struct {
	*Item
}

func newBundle(p *pb.ItemResponse, c *Client) (*Bundle, error) {
	item := newItem(p, c)
	if item.Kind != "bundle" {
		return nil, &InvalidArgumentError{Msg: "expected kind 'bundle', got '" + item.Kind + "'"}
	}
	return &Bundle{Item: item}, nil
}

// AddMember adds an item to this bundle.
func (b *Bundle) AddMember(ctx context.Context, member *Item, metadata map[string]string) (success bool, message string, newRev *Revision, err error) {
	if member.Kref == b.Kref {
		return false, "", nil, &InvalidArgumentError{Msg: "a bundle cannot contain itself"}
	}
	return b.client.AddBundleMember(ctx, b.Kref, member.Kref, metadata)
}

// RemoveMember removes an item from this bundle.
func (b *Bundle) RemoveMember(ctx context.Context, member *Item, metadata map[string]string) (success bool, message string, newRev *Revision, err error) {
	return b.client.RemoveBundleMember(ctx, b.Kref, member.Kref, metadata)
}

// Members returns current members (or those at revisionNumber when non-nil).
func (b *Bundle) Members(ctx context.Context, revisionNumber *int32) ([]BundleMember, error) {
	members, _, _, err := b.client.GetBundleMembers(ctx, b.Kref, revisionNumber)
	return members, err
}

// History returns the bundle's immutable membership-change history.
func (b *Bundle) History(ctx context.Context) ([]BundleRevisionHistory, error) {
	return b.client.GetBundleHistory(ctx, b.Kref)
}
