package kumiho

import (
	"context"
	"strings"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Project is the top-level container for assets.
type Project struct {
	ProjectID   string
	Name        string
	Description string
	CreatedAt   string
	UpdatedAt   string
	Deprecated  bool
	AllowPublic bool

	client *Client
}

func newProject(p *pb.ProjectResponse, c *Client) *Project {
	return &Project{
		ProjectID:   p.GetProjectId(),
		Name:        p.GetName(),
		Description: p.GetDescription(),
		CreatedAt:   p.GetCreatedAt(),
		UpdatedAt:   p.GetUpdatedAt(),
		Deprecated:  p.GetDeprecated(),
		AllowPublic: p.GetAllowPublic(),
		client:      c,
	}
}

func (p *Project) baseParent(parentPath string) string {
	if parentPath != "" {
		return parentPath
	}
	return "/" + p.Name
}

// CreateSpace creates a space (parentPath "" defaults to the project root).
func (p *Project) CreateSpace(ctx context.Context, name, parentPath string) (*Space, error) {
	return p.client.CreateSpace(ctx, p.baseParent(parentPath), name)
}

// CreateItem creates an item (parentPath "" defaults to the project root).
func (p *Project) CreateItem(ctx context.Context, itemName, kind, parentPath string, metadata map[string]string) (*Item, error) {
	return p.client.CreateItem(ctx, p.baseParent(parentPath), itemName, kind, metadata)
}

// CreateBundle creates a bundle (parentPath "" defaults to the project root).
func (p *Project) CreateBundle(ctx context.Context, bundleName, parentPath string, metadata map[string]string) (*Bundle, error) {
	return p.client.CreateBundle(ctx, p.baseParent(parentPath), bundleName, metadata)
}

// GetItem gets an item by name + kind (parentPath "" = project root).
func (p *Project) GetItem(ctx context.Context, itemName, kind, parentPath string) (*Item, error) {
	uri := "kref://" + strings.Trim(p.baseParent(parentPath), "/") + "/" + itemName + "." + kind
	return p.client.GetItemByKref(ctx, uri)
}

// GetBundle gets a bundle by name (parentPath "" = project root).
func (p *Project) GetBundle(ctx context.Context, bundleName, parentPath string) (*Bundle, error) {
	uri := "kref://" + strings.Trim(p.baseParent(parentPath), "/") + "/" + bundleName + ".bundle"
	return p.client.GetBundleByKref(ctx, uri)
}

// GetSpace gets a space by relative name or absolute "/path".
func (p *Project) GetSpace(ctx context.Context, name, parentPath string) (*Space, error) {
	path := name
	if !strings.HasPrefix(name, "/") {
		path = strings.TrimRight(p.baseParent(parentPath), "/") + "/" + name
	}
	return p.client.GetSpace(ctx, path)
}

// GetSpaces lists spaces in this project.
func (p *Project) GetSpaces(ctx context.Context, parentPath string, recursive bool, pageSize int, cursor string) (*Page[*Space], error) {
	return p.client.GetChildSpaces(ctx, p.baseParent(parentPath), recursive, pageSize, cursor)
}

// GetItems searches items within this project.
func (p *Project) GetItems(ctx context.Context, nameFilter, kindFilter string, pageSize int, cursor string) (*Page[*Item], error) {
	return p.client.ItemSearch(ctx, p.Name, nameFilter, kindFilter, pageSize, cursor, false)
}

// Delete deletes (force=true) or deprecates this project.
func (p *Project) Delete(ctx context.Context, force bool) error {
	return p.client.DeleteProject(ctx, p.ProjectID, force)
}

// SetPublic enables/disables anonymous read access.
func (p *Project) SetPublic(ctx context.Context, public bool) (*Project, error) {
	return p.client.UpdateProject(ctx, p.ProjectID, &public, nil)
}

// SetAllowPublic is an alias for SetPublic (matching Python). The AllowPublic
// field is read-only — assigning it does not persist; call this instead.
func (p *Project) SetAllowPublic(ctx context.Context, allowPublic bool) (*Project, error) {
	return p.SetPublic(ctx, allowPublic)
}

// Update updates description and/or public flag (nil = leave unchanged).
func (p *Project) Update(ctx context.Context, description *string, allowPublic *bool) (*Project, error) {
	return p.client.UpdateProject(ctx, p.ProjectID, allowPublic, description)
}
