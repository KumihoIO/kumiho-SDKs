package kumiho

import (
	"context"
	"fmt"
	"regexp"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Standard, semantically-meaningful edge types (UPPERCASE, as required by the
// Neo4j-backed graph).
const (
	EdgeBelongsTo   = "BELONGS_TO"
	EdgeCreatedFrom = "CREATED_FROM"
	EdgeReferenced  = "REFERENCED"
	EdgeDependsOn   = "DEPENDS_ON"
	EdgeDerivedFrom = "DERIVED_FROM"
	EdgeContains    = "CONTAINS"
	EdgeSupersedes  = "SUPERSEDES"
)

// EdgeDirection selects which edges a query traverses.
type EdgeDirection int32

const (
	// Outgoing: edges where the queried revision is the source.
	Outgoing EdgeDirection = 0
	// Incoming: edges where the queried revision is the target.
	Incoming EdgeDirection = 1
	// Both directions.
	Both EdgeDirection = 2
)

func (d EdgeDirection) pb() pb.EdgeDirection { return pb.EdgeDirection(d) }

var edgeTypePattern = regexp.MustCompile(`^[A-Z][A-Z0-9_]{0,49}$`)

// ValidateEdgeType checks an edge type (uppercase, [A-Z0-9_], 1-50 chars).
func ValidateEdgeType(edgeType string) error {
	if !edgeTypePattern.MatchString(edgeType) {
		return &EdgeTypeValidationError{Msg: fmt.Sprintf(
			"invalid edge_type %q: must start with an uppercase letter, contain only uppercase letters, digits, underscores, and be 1-50 chars",
			edgeType)}
	}
	return nil
}

// IsValidEdgeType reports whether edgeType is valid.
func IsValidEdgeType(edgeType string) bool { return edgeTypePattern.MatchString(edgeType) }

// Edge is a directed, typed relationship between two revisions.
type Edge struct {
	SourceKref Kref
	TargetKref Kref
	EdgeType   string
	Metadata   map[string]string
	CreatedAt  string
	Author     string
	Username   string

	client *Client
}

func newEdge(p *pb.Edge, c *Client) *Edge {
	return &Edge{
		SourceKref: krefFromPB(p.GetSourceKref()),
		TargetKref: krefFromPB(p.GetTargetKref()),
		EdgeType:   p.GetEdgeType(),
		Metadata:   p.GetMetadata(),
		CreatedAt:  p.GetCreatedAt(),
		Author:     p.GetAuthor(),
		Username:   p.GetUsername(),
		client:     c,
	}
}

// Delete removes this edge.
func (e *Edge) Delete(ctx context.Context) error {
	return e.client.DeleteEdge(ctx, e.SourceKref, e.TargetKref, e.EdgeType)
}

// PathStep is a single hop in a traversal path.
type PathStep struct {
	RevisionKref Kref
	EdgeType     string
	Depth        int32
}

// RevisionPath is a complete path between two revisions.
type RevisionPath struct {
	Steps      []PathStep
	TotalDepth int32
}

// ImpactedRevision is a revision impacted by changes to another revision.
type ImpactedRevision struct {
	RevisionKref    Kref
	ItemKref        Kref
	ImpactDepth     int32
	ImpactPathTypes []string
}

// TraversalResult is the outcome of a transitive edge traversal.
type TraversalResult struct {
	RevisionKrefs []Kref
	Paths         []RevisionPath
	Edges         []*Edge
	TotalCount    int32
	Truncated     bool

	client *Client
}

// GetRevisions fetches full Revision objects for every discovered revision.
func (t *TraversalResult) GetRevisions(ctx context.Context) ([]*Revision, error) {
	out := make([]*Revision, 0, len(t.RevisionKrefs))
	for _, k := range t.RevisionKrefs {
		r, err := t.client.GetRevision(ctx, k.URI())
		if err != nil {
			return nil, err
		}
		out = append(out, r)
	}
	return out, nil
}

// ShortestPathResult is the outcome of a shortest-path query.
type ShortestPathResult struct {
	Paths      []RevisionPath
	PathExists bool
	PathLength int32
}

// FirstPath returns the first shortest path, or nil if none.
func (s *ShortestPathResult) FirstPath() *RevisionPath {
	if len(s.Paths) == 0 {
		return nil
	}
	return &s.Paths[0]
}

func mapPath(p *pb.RevisionPath) RevisionPath {
	steps := make([]PathStep, 0, len(p.GetSteps()))
	for _, s := range p.GetSteps() {
		steps = append(steps, PathStep{
			RevisionKref: krefFromPB(s.GetRevisionKref()),
			EdgeType:     s.GetEdgeType(),
			Depth:        s.GetDepth(),
		})
	}
	return RevisionPath{Steps: steps, TotalDepth: p.GetTotalDepth()}
}
