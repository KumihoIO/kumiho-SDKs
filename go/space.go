package kumiho

import (
	"context"
	"strings"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Space is a hierarchical folder within a project.
type Space struct {
	Path      string
	Name      string
	Type      string // "root" or "sub"
	CreatedAt string
	Author    string
	Metadata  map[string]string
	Username  string

	client *Client
}

func newSpace(p *pb.SpaceResponse, c *Client) *Space {
	return &Space{
		Path:      p.GetPath(),
		Name:      p.GetName(),
		Type:      p.GetType(),
		CreatedAt: p.GetCreatedAt(),
		Author:    p.GetAuthor(),
		Metadata:  p.GetMetadata(),
		Username:  p.GetUsername(),
		client:    c,
	}
}

// CreateSpace creates a subspace.
func (s *Space) CreateSpace(ctx context.Context, name string) (*Space, error) {
	return s.client.CreateSpace(ctx, s.Path, name)
}

// GetSpace gets a subspace by name.
func (s *Space) GetSpace(ctx context.Context, name string) (*Space, error) {
	return s.client.GetSpace(ctx, strings.TrimRight(s.Path, "/")+"/"+name)
}

// GetSpaces lists child spaces.
func (s *Space) GetSpaces(ctx context.Context, recursive bool, pageSize int, cursor string) (*Page[*Space], error) {
	return s.client.GetChildSpaces(ctx, s.Path, recursive, pageSize, cursor)
}

// GetChildSpaces lists the immediate child spaces (Python get_child_spaces).
func (s *Space) GetChildSpaces(ctx context.Context) (*Page[*Space], error) {
	return s.client.GetChildSpaces(ctx, s.Path, false, 0, "")
}

// CreateItem creates an item in this space.
func (s *Space) CreateItem(ctx context.Context, itemName, kind string) (*Item, error) {
	return s.client.CreateItem(ctx, s.Path, itemName, kind, nil)
}

// CreateBundle creates a bundle in this space.
func (s *Space) CreateBundle(ctx context.Context, bundleName string, metadata map[string]string) (*Bundle, error) {
	return s.client.CreateBundle(ctx, s.Path, bundleName, metadata)
}

// GetItems lists items in this space.
func (s *Space) GetItems(ctx context.Context, nameFilter, kindFilter string, pageSize int, cursor string) (*Page[*Item], error) {
	return s.client.GetItems(ctx, s.Path, nameFilter, kindFilter, pageSize, cursor, false)
}

// GetItem gets an item by name + kind.
func (s *Space) GetItem(ctx context.Context, itemName, kind string) (*Item, error) {
	return s.client.GetItem(ctx, s.Path, itemName, kind)
}

// GetBundle gets a bundle by name.
func (s *Space) GetBundle(ctx context.Context, bundleName string) (*Bundle, error) {
	uri := "kref://" + strings.TrimLeft(s.Path, "/") + "/" + bundleName + ".bundle"
	return s.client.GetBundleByKref(ctx, uri)
}

// SetMetadata replaces/merges this space's metadata. Spaces are addressed by
// raw path (not a kref:// URI), so kref validation is bypassed.
func (s *Space) SetMetadata(ctx context.Context, metadata map[string]string) (*Space, error) {
	return s.client.UpdateSpaceMetadata(ctx, Kref(s.Path), metadata)
}

// SetAttribute sets a single metadata attribute (updates the in-memory cache on
// success, matching Python).
func (s *Space) SetAttribute(ctx context.Context, key, value string) (bool, error) {
	ok, err := s.client.SetAttribute(ctx, Kref(s.Path), key, value)
	if err == nil && ok {
		setMeta(&s.Metadata, key, value)
	}
	return ok, err
}

// GetAttribute gets a single metadata attribute (ok=false if unset).
func (s *Space) GetAttribute(ctx context.Context, key string) (string, bool, error) {
	return s.client.GetAttribute(ctx, Kref(s.Path), key)
}

// DeleteAttribute deletes a single metadata attribute (updates the in-memory
// cache on success, matching Python).
func (s *Space) DeleteAttribute(ctx context.Context, key string) (bool, error) {
	ok, err := s.client.DeleteAttribute(ctx, Kref(s.Path), key)
	if err == nil && ok {
		delete(s.Metadata, key)
	}
	return ok, err
}

// Delete deletes this space (force=true for a non-empty space).
func (s *Space) Delete(ctx context.Context, force bool) error {
	return s.client.DeleteSpace(ctx, s.Path, force)
}

// ParentSpace returns the parent space, or (nil, nil) for a project root.
func (s *Space) ParentSpace(ctx context.Context) (*Space, error) {
	if s.Path == "/" {
		return nil, nil
	}
	parts := splitNonEmpty(s.Path, "/")
	if len(parts) <= 1 {
		return nil, nil
	}
	return s.client.GetSpace(ctx, "/"+strings.Join(parts[:len(parts)-1], "/"))
}

// Project returns the owning project.
func (s *Space) Project(ctx context.Context) (*Project, error) {
	parts := splitNonEmpty(s.Path, "/")
	if len(parts) == 0 {
		return nil, &InvalidArgumentError{Msg: "root space has no project"}
	}
	proj, err := s.client.GetProject(ctx, parts[0])
	if err != nil {
		return nil, err
	}
	if proj == nil {
		return nil, &InvalidArgumentError{Msg: "project '" + parts[0] + "' not found"}
	}
	return proj, nil
}

func splitNonEmpty(s, sep string) []string {
	out := []string{}
	for _, p := range strings.Split(s, sep) {
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}
