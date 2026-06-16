package kumiho

import (
	"context"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func pagination(pageSize int, cursor string) *pb.PaginationRequest {
	if pageSize <= 0 && cursor == "" {
		return nil
	}
	ps := int32(pageSize)
	if ps == 0 {
		ps = 100
	}
	return &pb.PaginationRequest{PageSize: ps, Cursor: cursor}
}

// ----------------------------------------------------------------------- Projects

// CreateProject creates a new project.
func (c *Client) CreateProject(ctx context.Context, name, description string) (*Project, error) {
	resp, err := c.grpc.CreateProject(ctx, &pb.CreateProjectRequest{Name: name, Description: description})
	if err != nil {
		if status.Code(err) == codes.ResourceExhausted {
			return nil, &ProjectLimitError{Msg: status.Convert(err).Message()}
		}
		return nil, err
	}
	return newProject(resp, c), nil
}

// GetProjects lists all accessible projects.
func (c *Client) GetProjects(ctx context.Context) ([]*Project, error) {
	resp, err := c.grpc.GetProjects(ctx, &pb.GetProjectsRequest{})
	if err != nil {
		return nil, err
	}
	out := make([]*Project, 0, len(resp.GetProjects()))
	for _, p := range resp.GetProjects() {
		out = append(out, newProject(p, c))
	}
	return out, nil
}

// GetProject returns the project with the given name, or (nil, nil) if absent.
func (c *Client) GetProject(ctx context.Context, name string) (*Project, error) {
	projects, err := c.GetProjects(ctx)
	if err != nil {
		return nil, err
	}
	for _, p := range projects {
		if p.Name == name {
			return p, nil
		}
	}
	return nil, nil
}

// DeleteProject deletes (force=true) or deprecates a project.
func (c *Client) DeleteProject(ctx context.Context, projectID string, force bool) error {
	_, err := c.grpc.DeleteProject(ctx, &pb.DeleteProjectRequest{ProjectId: projectID, Force: force})
	return err
}

// UpdateProject updates a project's description and/or public flag.
func (c *Client) UpdateProject(ctx context.Context, projectID string, allowPublic *bool, description *string) (*Project, error) {
	resp, err := c.grpc.UpdateProject(ctx, &pb.UpdateProjectRequest{
		ProjectId: projectID, AllowPublic: allowPublic, Description: description,
	})
	if err != nil {
		return nil, err
	}
	return newProject(resp, c), nil
}

// ------------------------------------------------------------------------- Spaces

// CreateSpace creates a space under parentPath.
func (c *Client) CreateSpace(ctx context.Context, parentPath, spaceName string) (*Space, error) {
	resp, err := c.grpc.CreateSpace(ctx, &pb.CreateSpaceRequest{ParentPath: parentPath, SpaceName: spaceName})
	if err != nil {
		return nil, err
	}
	return newSpace(resp, c), nil
}

// GetSpace gets a space by path or kref.
func (c *Client) GetSpace(ctx context.Context, path string) (*Space, error) {
	resp, err := c.grpc.GetSpace(ctx, &pb.GetSpaceRequest{PathOrKref: path})
	if err != nil {
		return nil, err
	}
	return newSpace(resp, c), nil
}

// GetChildSpaces lists child spaces under parentPath.
func (c *Client) GetChildSpaces(ctx context.Context, parentPath string, recursive bool, pageSize int, cursor string) (*Page[*Space], error) {
	resp, err := c.grpc.GetChildSpaces(ctx, &pb.GetChildSpacesRequest{
		ParentPath: parentPath, Recursive: recursive, Pagination: pagination(pageSize, cursor),
	})
	if err != nil {
		return nil, err
	}
	items := make([]*Space, 0, len(resp.GetSpaces()))
	for _, s := range resp.GetSpaces() {
		items = append(items, newSpace(s, c))
	}
	return pageFrom(items, resp.GetPagination()), nil
}

// UpdateSpaceMetadata replaces/merges a space's metadata.
func (c *Client) UpdateSpaceMetadata(ctx context.Context, kref Kref, metadata map[string]string) (*Space, error) {
	resp, err := c.grpc.UpdateSpaceMetadata(ctx, &pb.UpdateMetadataRequest{Kref: kref.pb(), Metadata: metadata})
	if err != nil {
		return nil, err
	}
	return newSpace(resp, c), nil
}

// DeleteSpace deletes a space by path (force=true for a non-empty space).
func (c *Client) DeleteSpace(ctx context.Context, path string, force bool) error {
	_, err := c.grpc.DeleteSpace(ctx, &pb.DeleteSpaceRequest{Path: path, Force: force})
	return err
}

// -------------------------------------------------------------------------- Items

// CreateItem creates an item. The reserved "bundle" kind is rejected.
func (c *Client) CreateItem(ctx context.Context, parentPath, itemName, kind string, metadata map[string]string) (*Item, error) {
	if isReservedKind(kind) {
		return nil, &InvalidArgumentError{Msg: "item kind '" + kind + "' is reserved; use CreateBundle instead"}
	}
	resp, err := c.grpc.CreateItem(ctx, &pb.CreateItemRequest{ParentPath: parentPath, ItemName: itemName, Kind: kind})
	if err != nil {
		return nil, err
	}
	item := newItem(resp, c)
	if len(metadata) > 0 {
		return c.UpdateItemMetadata(ctx, item.Kref, metadata)
	}
	return item, nil
}

// GetItem gets an item by parent path, name and kind.
func (c *Client) GetItem(ctx context.Context, parentPath, itemName, kind string) (*Item, error) {
	resp, err := c.grpc.GetItem(ctx, &pb.GetItemRequest{ParentPath: parentPath, ItemName: itemName, Kind: kind})
	if err != nil {
		return nil, err
	}
	return newItem(resp, c), nil
}

// GetItemByKref gets an item by its kref URI.
func (c *Client) GetItemByKref(ctx context.Context, krefURI string) (*Item, error) {
	parent, name, kind, err := splitItemKref(krefURI)
	if err != nil {
		return nil, err
	}
	return c.GetItem(ctx, parent, name, kind)
}

// GetBundleByKref gets a bundle by kref URI (verifies kind == bundle).
func (c *Client) GetBundleByKref(ctx context.Context, krefURI string) (*Bundle, error) {
	parent, name, kind, err := splitItemKref(krefURI)
	if err != nil {
		return nil, err
	}
	if kind != "bundle" {
		return nil, &InvalidArgumentError{Msg: "'" + krefURI + "' is not a bundle (kind='" + kind + "')"}
	}
	resp, err := c.grpc.GetItem(ctx, &pb.GetItemRequest{ParentPath: parent, ItemName: name, Kind: "bundle"})
	if err != nil {
		return nil, err
	}
	return newBundle(resp, c)
}

// GetItems lists items in a space.
func (c *Client) GetItems(ctx context.Context, parentPath, nameFilter, kindFilter string, pageSize int, cursor string, includeDeprecated bool) (*Page[*Item], error) {
	resp, err := c.grpc.GetItems(ctx, &pb.GetItemsRequest{
		ParentPath: parentPath, ItemNameFilter: nameFilter, KindFilter: kindFilter,
		Pagination: pagination(pageSize, cursor), IncludeDeprecated: includeDeprecated,
	})
	if err != nil {
		return nil, err
	}
	return pageOfItems(resp.GetItems(), resp.GetPagination(), c), nil
}

// ItemSearch searches items across the system by filters.
func (c *Client) ItemSearch(ctx context.Context, contextFilter, nameFilter, kindFilter string, pageSize int, cursor string, includeDeprecated bool) (*Page[*Item], error) {
	resp, err := c.grpc.ItemSearch(ctx, &pb.ItemSearchRequest{
		ContextFilter: contextFilter, ItemNameFilter: nameFilter, KindFilter: kindFilter,
		Pagination: pagination(pageSize, cursor), IncludeDeprecated: includeDeprecated,
	})
	if err != nil {
		return nil, err
	}
	return pageOfItems(resp.GetItems(), resp.GetPagination(), c), nil
}

func pageOfItems(in []*pb.ItemResponse, p *pb.PaginationResponse, c *Client) *Page[*Item] {
	items := make([]*Item, 0, len(in))
	for _, it := range in {
		items = append(items, newItem(it, c))
	}
	return pageFrom(items, p)
}

// SearchOptions configures a full-text Search.
type SearchOptions struct {
	ContextFilter           string
	KindFilter              string
	IncludeDeprecated       bool
	IncludeRevisionMetadata bool
	IncludeArtifactMetadata bool
	MinScore                float32
	PageSize                int
	Cursor                  string
}

// Search runs a full-text fuzzy search returning ranked results.
func (c *Client) Search(ctx context.Context, query string, opts SearchOptions) (*Page[*SearchResult], error) {
	resp, err := c.grpc.Search(ctx, &pb.SearchRequest{
		Query:                   query,
		ContextFilter:           opts.ContextFilter,
		KindFilter:              opts.KindFilter,
		IncludeDeprecated:       opts.IncludeDeprecated,
		Pagination:              pagination(opts.PageSize, opts.Cursor),
		MinScore:                opts.MinScore,
		IncludeRevisionMetadata: opts.IncludeRevisionMetadata,
		IncludeArtifactMetadata: opts.IncludeArtifactMetadata,
	})
	if err != nil {
		return nil, err
	}
	results := make([]*SearchResult, 0, len(resp.GetResults()))
	for _, r := range resp.GetResults() {
		if r.GetItem() == nil {
			continue
		}
		results = append(results, &SearchResult{
			Item:      newItem(r.GetItem(), c),
			Score:     r.GetScore(),
			MatchedIn: r.GetMatchedIn(),
		})
	}
	return pageFrom(results, resp.GetPagination()), nil
}

// ScoreRevisions scores specific revisions against a query (server-side).
func (c *Client) ScoreRevisions(ctx context.Context, query string, revisionKrefs, scoreFields []string) ([]ScoredRevision, error) {
	krefs := make([]*pb.Kref, 0, len(revisionKrefs))
	for _, k := range revisionKrefs {
		krefs = append(krefs, &pb.Kref{Uri: k})
	}
	resp, err := c.grpc.ScoreRevisions(ctx, &pb.ScoreRevisionsRequest{
		Query: query, RevisionKrefs: krefs, ScoreFields: scoreFields,
	})
	if err != nil {
		return nil, err
	}
	out := make([]ScoredRevision, 0, len(resp.GetScoredRevisions()))
	for _, sr := range resp.GetScoredRevisions() {
		out = append(out, ScoredRevision{
			Kref: sr.GetKref().GetUri(), Score: sr.GetScore(), ScoreMethod: sr.GetScoreMethod(),
		})
	}
	return out, nil
}

// UpdateItemMetadata merges metadata into an item.
func (c *Client) UpdateItemMetadata(ctx context.Context, kref Kref, metadata map[string]string) (*Item, error) {
	resp, err := c.grpc.UpdateItemMetadata(ctx, &pb.UpdateMetadataRequest{Kref: kref.pb(), Metadata: metadata})
	if err != nil {
		return nil, err
	}
	return newItem(resp, c), nil
}

// DeleteItem deletes an item (force=true to delete with revisions).
func (c *Client) DeleteItem(ctx context.Context, kref Kref, force bool) error {
	_, err := c.grpc.DeleteItem(ctx, &pb.DeleteItemRequest{Kref: kref.pb(), Force: force})
	return err
}

// ---------------------------------------------------------------------- Revisions

// CreateRevision creates a revision for an item (number=0 auto-increments).
func (c *Client) CreateRevision(ctx context.Context, itemKref Kref, metadata map[string]string, number int32, embeddingText string) (*Revision, error) {
	resp, err := c.grpc.CreateRevision(ctx, &pb.CreateRevisionRequest{
		ItemKref: itemKref.pb(), Metadata: metadata, Number: number, EmbeddingText: embeddingText,
	})
	if err != nil {
		return nil, err
	}
	return newRevision(resp, c), nil
}

// GetRevision gets a revision by kref URI (supports ?t=tag / ?time=YYYYMMDDHHMM).
func (c *Client) GetRevision(ctx context.Context, krefURI string) (*Revision, error) {
	base, tag, t, err := parseTagTime(krefURI)
	if err != nil {
		return nil, err
	}
	if tag != nil || t != nil {
		resp, rerr := c.grpc.ResolveKref(ctx, &pb.ResolveKrefRequest{Kref: base, Tag: tag, Time: t})
		if rerr != nil {
			return nil, rerr
		}
		return newRevision(resp, c), nil
	}
	resp, err := c.grpc.GetRevision(ctx, &pb.KrefRequest{Kref: &pb.Kref{Uri: krefURI}})
	if err != nil {
		return nil, err
	}
	return newRevision(resp, c), nil
}

// ResolveKref resolves an item kref to a revision by tag and/or time.
func (c *Client) ResolveKref(ctx context.Context, kref string, tag, t *string) (*Revision, error) {
	resp, err := c.grpc.ResolveKref(ctx, &pb.ResolveKrefRequest{Kref: kref, Tag: tag, Time: t})
	if err != nil {
		return nil, err
	}
	return newRevision(resp, c), nil
}

// GetRevisions lists all revisions of an item.
func (c *Client) GetRevisions(ctx context.Context, itemKref Kref) ([]*Revision, error) {
	resp, err := c.grpc.GetRevisions(ctx, &pb.GetRevisionsRequest{ItemKref: itemKref.pb()})
	if err != nil {
		return nil, err
	}
	out := make([]*Revision, 0, len(resp.GetRevisions()))
	for _, r := range resp.GetRevisions() {
		out = append(out, newRevision(r, c))
	}
	return out, nil
}

// GetLatestRevision resolves the latest revision, or (nil, nil) if none.
func (c *Client) GetLatestRevision(ctx context.Context, itemKref Kref) (*Revision, error) {
	resp, err := c.grpc.ResolveKref(ctx, &pb.ResolveKrefRequest{Kref: itemKref.URI()})
	if err != nil {
		if IsNotFound(err) {
			return nil, nil
		}
		return nil, err
	}
	return newRevision(resp, c), nil
}

// BatchGetRevisions fetches revisions by revision krefs and/or item krefs + tag.
func (c *Client) BatchGetRevisions(ctx context.Context, revisionKrefs, itemKrefs []string, tag string, allowPartial bool) ([]*Revision, []string, error) {
	toPB := func(ks []string) []*pb.Kref {
		out := make([]*pb.Kref, 0, len(ks))
		for _, k := range ks {
			out = append(out, &pb.Kref{Uri: k})
		}
		return out
	}
	resp, err := c.grpc.BatchGetRevisions(ctx, &pb.BatchGetRevisionsRequest{
		RevisionKrefs: toPB(revisionKrefs), ItemKrefs: toPB(itemKrefs), Tag: tag, AllowPartial: allowPartial,
	})
	if err != nil {
		return nil, nil, err
	}
	revs := make([]*Revision, 0, len(resp.GetRevisions()))
	for _, r := range resp.GetRevisions() {
		revs = append(revs, newRevision(r, c))
	}
	return revs, resp.GetNotFound(), nil
}

// DeleteRevision deletes a revision.
func (c *Client) DeleteRevision(ctx context.Context, kref Kref, force bool) error {
	_, err := c.grpc.DeleteRevision(ctx, &pb.DeleteRevisionRequest{Kref: kref.pb(), Force: force})
	return err
}

// UpdateRevisionMetadata merges metadata into a revision.
func (c *Client) UpdateRevisionMetadata(ctx context.Context, kref Kref, metadata map[string]string) (*Revision, error) {
	resp, err := c.grpc.UpdateRevisionMetadata(ctx, &pb.UpdateMetadataRequest{Kref: kref.pb(), Metadata: metadata})
	if err != nil {
		return nil, err
	}
	return newRevision(resp, c), nil
}

// PeekNextRevision returns the next revision number for an item.
func (c *Client) PeekNextRevision(ctx context.Context, itemKref Kref) (int32, error) {
	resp, err := c.grpc.PeekNextRevision(ctx, &pb.PeekNextRevisionRequest{ItemKref: itemKref.pb()})
	if err != nil {
		return 0, err
	}
	return resp.GetNumber(), nil
}

// TagRevision applies a tag to a revision.
func (c *Client) TagRevision(ctx context.Context, kref Kref, tag string) error {
	_, err := c.grpc.TagRevision(ctx, &pb.TagRevisionRequest{Kref: kref.pb(), Tag: tag})
	return err
}

// UntagRevision removes a tag from a revision.
func (c *Client) UntagRevision(ctx context.Context, kref Kref, tag string) error {
	_, err := c.grpc.UnTagRevision(ctx, &pb.UnTagRevisionRequest{Kref: kref.pb(), Tag: tag})
	return err
}

// HasTag reports whether a revision currently has a tag.
func (c *Client) HasTag(ctx context.Context, kref Kref, tag string) (bool, error) {
	resp, err := c.grpc.HasTag(ctx, &pb.HasTagRequest{Kref: kref.pb(), Tag: tag})
	if err != nil {
		return false, err
	}
	return resp.GetHasTag(), nil
}

// WasTagged reports whether a revision was ever tagged with a tag.
func (c *Client) WasTagged(ctx context.Context, kref Kref, tag string) (bool, error) {
	resp, err := c.grpc.WasTagged(ctx, &pb.WasTaggedRequest{Kref: kref.pb(), Tag: tag})
	if err != nil {
		return false, err
	}
	return resp.GetWasTagged(), nil
}

// SetDefaultArtifact sets a revision's default artifact.
func (c *Client) SetDefaultArtifact(ctx context.Context, revisionKref Kref, artifactName string) error {
	_, err := c.grpc.SetDefaultArtifact(ctx, &pb.SetDefaultArtifactRequest{
		RevisionKref: revisionKref.pb(), ArtifactName: artifactName,
	})
	return err
}

// ---------------------------------------------------------------------- Artifacts

// CreateArtifact creates a file-reference artifact on a revision.
func (c *Client) CreateArtifact(ctx context.Context, revisionKref Kref, name, location string, metadata map[string]string) (*Artifact, error) {
	resp, err := c.grpc.CreateArtifact(ctx, &pb.CreateArtifactRequest{
		RevisionKref: revisionKref.pb(), Name: name, Location: location, Metadata: metadata,
	})
	if err != nil {
		return nil, err
	}
	return newArtifact(resp, c), nil
}

// GetArtifact gets an artifact by revision kref + name.
func (c *Client) GetArtifact(ctx context.Context, revisionKref Kref, name string) (*Artifact, error) {
	resp, err := c.grpc.GetArtifact(ctx, &pb.GetArtifactRequest{RevisionKref: revisionKref.pb(), Name: name})
	if err != nil {
		return nil, err
	}
	return newArtifact(resp, c), nil
}

// GetArtifactByKref gets an artifact by kref URI, falling back to the revision's
// default artifact when no &a= is present.
func (c *Client) GetArtifactByKref(ctx context.Context, krefURI string) (*Artifact, error) {
	if err := ValidateKref(krefURI); err != nil {
		return nil, err
	}
	k := Kref(krefURI)
	if name := k.ArtifactName(); name != "" {
		revURI := krefURI
		if i := indexOf(krefURI, "&a="); i >= 0 {
			revURI = krefURI[:i]
		}
		return c.GetArtifact(ctx, Kref(revURI), name)
	}
	rev, err := c.GetRevision(ctx, krefURI)
	if err != nil {
		return nil, err
	}
	if rev.DefaultArtifact == "" {
		return nil, &InvalidArgumentError{Msg: "artifact kref '" + krefURI + "' missing &a= and no default_artifact set"}
	}
	return c.GetArtifact(ctx, rev.Kref, rev.DefaultArtifact)
}

// GetArtifacts gets all artifacts on a revision.
func (c *Client) GetArtifacts(ctx context.Context, revisionKref Kref) ([]*Artifact, error) {
	resp, err := c.grpc.GetArtifacts(ctx, &pb.GetArtifactsRequest{RevisionKref: revisionKref.pb()})
	if err != nil {
		return nil, err
	}
	return artifactSlice(resp.GetArtifacts(), c), nil
}

// GetArtifactsByLocation reverse-looks-up artifacts referencing a file location.
func (c *Client) GetArtifactsByLocation(ctx context.Context, location string) ([]*Artifact, error) {
	resp, err := c.grpc.GetArtifactsByLocation(ctx, &pb.GetArtifactsByLocationRequest{Location: location})
	if err != nil {
		return nil, err
	}
	return artifactSlice(resp.GetArtifacts(), c), nil
}

func artifactSlice(in []*pb.ArtifactResponse, c *Client) []*Artifact {
	out := make([]*Artifact, 0, len(in))
	for _, a := range in {
		out = append(out, newArtifact(a, c))
	}
	return out
}

// DeleteArtifact deletes an artifact.
func (c *Client) DeleteArtifact(ctx context.Context, kref Kref, force bool) error {
	_, err := c.grpc.DeleteArtifact(ctx, &pb.DeleteArtifactRequest{Kref: kref.pb(), Force: force})
	return err
}

// UpdateArtifactMetadata merges metadata into an artifact.
func (c *Client) UpdateArtifactMetadata(ctx context.Context, kref Kref, metadata map[string]string) (*Artifact, error) {
	resp, err := c.grpc.UpdateArtifactMetadata(ctx, &pb.UpdateMetadataRequest{Kref: kref.pb(), Metadata: metadata})
	if err != nil {
		return nil, err
	}
	return newArtifact(resp, c), nil
}

// SetDeprecated deprecates/restores any node (item, revision, artifact).
func (c *Client) SetDeprecated(ctx context.Context, kref Kref, deprecated bool) error {
	_, err := c.grpc.SetDeprecated(ctx, &pb.SetDeprecatedRequest{Kref: kref.pb(), Deprecated: deprecated})
	return err
}

// Resolve resolves a kref to a file location.
func (c *Client) Resolve(ctx context.Context, kref string) (string, error) {
	_, tag, t, err := parseTagTime(kref)
	if err != nil {
		return "", err
	}
	resp, err := c.grpc.ResolveLocation(ctx, &pb.ResolveLocationRequest{Kref: kref, Tag: tag, Time: t})
	if err != nil {
		return "", err
	}
	return resp.GetLocation(), nil
}

// --------------------------------------------------------------------- Attributes

// SetAttribute sets a single metadata attribute on any entity.
func (c *Client) SetAttribute(ctx context.Context, kref Kref, key, value string) (bool, error) {
	resp, err := c.grpc.SetAttribute(ctx, &pb.SetAttributeRequest{Kref: kref.pb(), Key: key, Value: value})
	if err != nil {
		return false, err
	}
	return resp.GetSuccess(), nil
}

// GetAttribute gets a single metadata attribute (ok=false if unset).
func (c *Client) GetAttribute(ctx context.Context, kref Kref, key string) (value string, ok bool, err error) {
	resp, err := c.grpc.GetAttribute(ctx, &pb.GetAttributeRequest{Kref: kref.pb(), Key: key})
	if err != nil {
		return "", false, err
	}
	return resp.GetValue(), resp.GetExists(), nil
}

// DeleteAttribute deletes a single metadata attribute.
func (c *Client) DeleteAttribute(ctx context.Context, kref Kref, key string) (bool, error) {
	resp, err := c.grpc.DeleteAttribute(ctx, &pb.DeleteAttributeRequest{Kref: kref.pb(), Key: key})
	if err != nil {
		return false, err
	}
	return resp.GetSuccess(), nil
}

// -------------------------------------------------------------------------- Edges

// CreateEdge creates a typed edge between two revisions.
func (c *Client) CreateEdge(ctx context.Context, source, target *Revision, edgeType string, metadata map[string]string) (*Edge, error) {
	if err := ValidateEdgeType(edgeType); err != nil {
		return nil, err
	}
	_, err := c.grpc.CreateEdge(ctx, &pb.CreateEdgeRequest{
		SourceRevisionKref: source.Kref.pb(), TargetRevisionKref: target.Kref.pb(),
		EdgeType: edgeType, Metadata: metadata,
	})
	if err != nil {
		return nil, err
	}
	return newEdge(&pb.Edge{
		SourceKref: source.Kref.pb(), TargetKref: target.Kref.pb(), EdgeType: edgeType, Metadata: metadata,
	}, c), nil
}

// GetEdges gets edges for a revision, filtered by type and direction.
func (c *Client) GetEdges(ctx context.Context, kref Kref, edgeTypeFilter string, direction EdgeDirection) ([]*Edge, error) {
	resp, err := c.grpc.GetEdges(ctx, &pb.GetEdgesRequest{
		Kref: kref.pb(), EdgeTypeFilter: edgeTypeFilter, Direction: direction.pb(),
	})
	if err != nil {
		return nil, err
	}
	out := make([]*Edge, 0, len(resp.GetEdges()))
	for _, e := range resp.GetEdges() {
		out = append(out, newEdge(e, c))
	}
	return out, nil
}

// DeleteEdge deletes an edge.
func (c *Client) DeleteEdge(ctx context.Context, sourceKref, targetKref Kref, edgeType string) error {
	if err := ValidateEdgeType(edgeType); err != nil {
		return err
	}
	_, err := c.grpc.DeleteEdge(ctx, &pb.DeleteEdgeRequest{
		SourceKref: sourceKref.pb(), TargetKref: targetKref.pb(), EdgeType: edgeType,
	})
	return err
}

// --------------------------------------------------------------- Graph traversal

// TraverseEdges transitively traverses edges from an origin revision.
func (c *Client) TraverseEdges(ctx context.Context, originKref Kref, direction EdgeDirection, edgeTypeFilter []string, maxDepth, limit int32, includePath bool) (*TraversalResult, error) {
	resp, err := c.grpc.TraverseEdges(ctx, &pb.TraverseEdgesRequest{
		OriginKref: originKref.pb(), Direction: direction.pb(), EdgeTypeFilter: edgeTypeFilter,
		MaxDepth: maxDepth, Limit: limit, IncludePath: includePath,
	})
	if err != nil {
		return nil, err
	}
	krefs := make([]Kref, 0, len(resp.GetRevisionKrefs()))
	for _, k := range resp.GetRevisionKrefs() {
		krefs = append(krefs, Kref(k.GetUri()))
	}
	paths := make([]RevisionPath, 0, len(resp.GetPaths()))
	for _, p := range resp.GetPaths() {
		paths = append(paths, mapPath(p))
	}
	edges := make([]*Edge, 0, len(resp.GetEdges()))
	for _, e := range resp.GetEdges() {
		edges = append(edges, newEdge(e, c))
	}
	return &TraversalResult{
		RevisionKrefs: krefs, Paths: paths, Edges: edges,
		TotalCount: resp.GetTotalCount(), Truncated: resp.GetTruncated(), client: c,
	}, nil
}

// FindShortestPath finds the shortest path between two revisions.
func (c *Client) FindShortestPath(ctx context.Context, sourceKref, targetKref Kref, edgeTypeFilter []string, maxDepth int32, allShortest bool) (*ShortestPathResult, error) {
	resp, err := c.grpc.FindShortestPath(ctx, &pb.ShortestPathRequest{
		SourceKref: sourceKref.pb(), TargetKref: targetKref.pb(), EdgeTypeFilter: edgeTypeFilter,
		MaxDepth: maxDepth, AllShortest: allShortest,
	})
	if err != nil {
		return nil, err
	}
	paths := make([]RevisionPath, 0, len(resp.GetPaths()))
	for _, p := range resp.GetPaths() {
		paths = append(paths, mapPath(p))
	}
	return &ShortestPathResult{Paths: paths, PathExists: resp.GetPathExists(), PathLength: resp.GetPathLength()}, nil
}

// AnalyzeImpact analyzes which revisions are impacted by changes to a revision.
func (c *Client) AnalyzeImpact(ctx context.Context, revisionKref Kref, edgeTypeFilter []string, maxDepth, limit int32) ([]ImpactedRevision, error) {
	resp, err := c.grpc.AnalyzeImpact(ctx, &pb.ImpactAnalysisRequest{
		RevisionKref: revisionKref.pb(), EdgeTypeFilter: edgeTypeFilter, MaxDepth: maxDepth, Limit: limit,
	})
	if err != nil {
		return nil, err
	}
	out := make([]ImpactedRevision, 0, len(resp.GetImpactedRevisions()))
	for _, iv := range resp.GetImpactedRevisions() {
		out = append(out, ImpactedRevision{
			RevisionKref:    krefFromPB(iv.GetRevisionKref()),
			ItemKref:        krefFromPB(iv.GetItemKref()),
			ImpactDepth:     iv.GetImpactDepth(),
			ImpactPathTypes: iv.GetImpactPathTypes(),
		})
	}
	return out, nil
}

// ------------------------------------------------------------------------ Bundles

// CreateBundle creates a bundle (the reserved "bundle" kind).
func (c *Client) CreateBundle(ctx context.Context, parentPath, bundleName string, metadata map[string]string) (*Bundle, error) {
	resp, err := c.grpc.CreateBundle(ctx, &pb.CreateBundleRequest{
		ParentPath: parentPath, BundleName: bundleName, Metadata: metadata,
	})
	if err != nil {
		return nil, err
	}
	return newBundle(resp, c)
}

// AddBundleMember adds an item to a bundle.
func (c *Client) AddBundleMember(ctx context.Context, bundleKref, memberItemKref Kref, metadata map[string]string) (success bool, message string, newRev *Revision, err error) {
	resp, err := c.grpc.AddBundleMember(ctx, &pb.AddBundleMemberRequest{
		BundleKref: bundleKref.pb(), MemberItemKref: memberItemKref.pb(), Metadata: metadata,
	})
	if err != nil {
		return false, "", nil, err
	}
	if r := resp.GetNewRevision(); r != nil {
		newRev = newRevision(r, c)
	}
	return resp.GetSuccess(), resp.GetMessage(), newRev, nil
}

// RemoveBundleMember removes an item from a bundle.
func (c *Client) RemoveBundleMember(ctx context.Context, bundleKref, memberItemKref Kref, metadata map[string]string) (success bool, message string, newRev *Revision, err error) {
	resp, err := c.grpc.RemoveBundleMember(ctx, &pb.RemoveBundleMemberRequest{
		BundleKref: bundleKref.pb(), MemberItemKref: memberItemKref.pb(), Metadata: metadata,
	})
	if err != nil {
		return false, "", nil, err
	}
	if r := resp.GetNewRevision(); r != nil {
		newRev = newRevision(r, c)
	}
	return resp.GetSuccess(), resp.GetMessage(), newRev, nil
}

// GetBundleMembers returns a bundle's members (optionally at a revision).
func (c *Client) GetBundleMembers(ctx context.Context, bundleKref Kref, revisionNumber *int32) (members []BundleMember, revNumber, totalCount int32, err error) {
	resp, err := c.grpc.GetBundleMembers(ctx, &pb.GetBundleMembersRequest{
		BundleKref: bundleKref.pb(), RevisionNumber: revisionNumber,
	})
	if err != nil {
		return nil, 0, 0, err
	}
	for _, m := range resp.GetMembers() {
		members = append(members, BundleMember{
			ItemKref:        krefFromPB(m.GetItemKref()),
			AddedAt:         m.GetAddedAt(),
			AddedBy:         m.GetAddedBy(),
			AddedByUsername: m.GetAddedByUsername(),
			AddedInRevision: m.GetAddedInRevision(),
		})
	}
	return members, resp.GetRevisionNumber(), resp.GetTotalCount(), nil
}

// GetBundleHistory returns a bundle's immutable membership-change history.
func (c *Client) GetBundleHistory(ctx context.Context, bundleKref Kref) ([]BundleRevisionHistory, error) {
	resp, err := c.grpc.GetBundleHistory(ctx, &pb.GetBundleHistoryRequest{BundleKref: bundleKref.pb()})
	if err != nil {
		return nil, err
	}
	out := make([]BundleRevisionHistory, 0, len(resp.GetHistory()))
	for _, h := range resp.GetHistory() {
		out = append(out, BundleRevisionHistory{
			RevisionNumber: h.GetRevisionNumber(),
			Action:         h.GetAction(),
			MemberItemKref: krefFromPB(h.GetMemberItemKref()),
			Author:         h.GetAuthor(),
			Username:       h.GetUsername(),
			CreatedAt:      h.GetCreatedAt(),
			Metadata:       h.GetMetadata(),
		})
	}
	return out, nil
}

// ------------------------------------------------------------------------- Tenant

// GetTenantUsage returns the current tenant's node usage and limit.
func (c *Client) GetTenantUsage(ctx context.Context) (*TenantUsage, error) {
	resp, err := c.grpc.GetTenantUsage(ctx, &pb.GetTenantUsageRequest{})
	if err != nil {
		return nil, err
	}
	return &TenantUsage{NodeCount: resp.GetNodeCount(), NodeLimit: resp.GetNodeLimit(), TenantID: resp.GetTenantId()}, nil
}

// ------------------------------------------------------------------------- Events

// GetEventCapabilities returns this tenant tier's event-streaming capabilities.
func (c *Client) GetEventCapabilities(ctx context.Context) (*EventCapabilities, error) {
	resp, err := c.grpc.GetEventCapabilities(ctx, &pb.GetEventCapabilitiesRequest{})
	if err != nil {
		return nil, err
	}
	return &EventCapabilities{
		SupportsReplay:         resp.GetSupportsReplay(),
		SupportsCursor:         resp.GetSupportsCursor(),
		SupportsConsumerGroups: resp.GetSupportsConsumerGroups(),
		MaxRetentionHours:      resp.GetMaxRetentionHours(),
		MaxBufferSize:          resp.GetMaxBufferSize(),
		Tier:                   resp.GetTier(),
	}, nil
}

func indexOf(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}

func isReservedKind(kind string) bool {
	for _, r := range ReservedKinds {
		if r == toLower(kind) {
			return true
		}
	}
	return false
}

func toLower(s string) string {
	b := []byte(s)
	for i := range b {
		if b[i] >= 'A' && b[i] <= 'Z' {
			b[i] += 'a' - 'A'
		}
	}
	return string(b)
}
