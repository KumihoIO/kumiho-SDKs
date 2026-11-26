package kumiho

import (
	"context"
	"fmt"
	"reflect"
	"strings"
	"testing"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc"
)

// pagingStub serves scripted GetRevisions/GetEdges responses in order and
// records every request.
type pagingStub struct {
	pb.KumihoServiceClient
	revPages  []*pb.GetRevisionsResponse
	edgePages []*pb.GetEdgesResponse
	revReqs   []*pb.GetRevisionsRequest
	edgeReqs  []*pb.GetEdgesRequest
}

func (s *pagingStub) GetRevisions(_ context.Context, r *pb.GetRevisionsRequest, _ ...grpc.CallOption) (*pb.GetRevisionsResponse, error) {
	s.revReqs = append(s.revReqs, r)
	if len(s.revPages) == 0 {
		return nil, fmt.Errorf("unexpected GetRevisions call %d", len(s.revReqs))
	}
	page := s.revPages[0]
	s.revPages = s.revPages[1:]
	return page, nil
}

func (s *pagingStub) GetEdges(_ context.Context, r *pb.GetEdgesRequest, _ ...grpc.CallOption) (*pb.GetEdgesResponse, error) {
	s.edgeReqs = append(s.edgeReqs, r)
	if len(s.edgePages) == 0 {
		return nil, fmt.Errorf("unexpected GetEdges call %d", len(s.edgeReqs))
	}
	page := s.edgePages[0]
	s.edgePages = s.edgePages[1:]
	return page, nil
}

func pgMore(cursor string) *pb.PaginationResponse {
	return &pb.PaginationResponse{NextCursor: cursor, HasMore: true, TotalCount: -1}
}

func pgDone() *pb.PaginationResponse {
	return &pb.PaginationResponse{TotalCount: -1}
}

func revsPage(p *pb.PaginationResponse, numbers ...int32) *pb.GetRevisionsResponse {
	resp := &pb.GetRevisionsResponse{Pagination: p}
	for _, n := range numbers {
		resp.Revisions = append(resp.Revisions, &pb.RevisionResponse{
			Kref:     &pb.Kref{Uri: fmt.Sprintf("kref://p/s/x.k?r=%d", n)},
			ItemKref: &pb.Kref{Uri: "kref://p/s/x.k"},
			Number:   n,
		})
	}
	return resp
}

func edgesPage(p *pb.PaginationResponse, targets ...int) *pb.GetEdgesResponse {
	resp := &pb.GetEdgesResponse{Pagination: p}
	for _, n := range targets {
		resp.Edges = append(resp.Edges, &pb.Edge{
			SourceKref: &pb.Kref{Uri: "kref://p/s/x.k?r=1"},
			TargetKref: &pb.Kref{Uri: fmt.Sprintf("kref://p/s/y.k?r=%d", n)},
			EdgeType:   "DEPENDS_ON",
		})
	}
	return resp
}

func revisionNumbers(t *testing.T, c *Client) ([]int32, error) {
	t.Helper()
	revs, err := c.GetRevisions(context.Background(), Kref("kref://p/s/x.k"))
	if err != nil {
		return nil, err
	}
	out := []int32{}
	for _, r := range revs {
		out = append(out, r.Number)
	}
	return out, nil
}

func edgeTargets(t *testing.T, c *Client) ([]string, error) {
	t.Helper()
	edges, err := c.GetEdges(context.Background(), Kref("kref://p/s/x.k?r=1"), "", Both)
	if err != nil {
		return nil, err
	}
	out := []string{}
	for _, e := range edges {
		out = append(out, e.TargetKref.URI())
	}
	return out, nil
}

type sentPage struct {
	size   int32
	cursor string
}

func TestGetRevisionsFollowsEveryPageIncludingAnEmptyMiddlePage(t *testing.T) {
	s := &pagingStub{revPages: []*pb.GetRevisionsResponse{
		revsPage(pgMore("c1"), 5, 4),
		revsPage(pgMore("c2")),
		revsPage(pgDone(), 3, 2, 1),
	}}
	got, err := revisionNumbers(t, &Client{grpc: s})
	if err != nil || !reflect.DeepEqual(got, []int32{5, 4, 3, 2, 1}) {
		t.Fatalf("revisions = %v, %v", got, err)
	}
	var sent []sentPage
	for _, r := range s.revReqs {
		sent = append(sent, sentPage{r.GetPagination().GetPageSize(), r.GetPagination().GetCursor()})
	}
	want := []sentPage{{1000, ""}, {1000, "c1"}, {1000, "c2"}}
	if !reflect.DeepEqual(sent, want) {
		t.Fatalf("requests = %v, want %v", sent, want)
	}
}

func TestGetEdgesFollowsEveryPageIncludingAnEmptyMiddlePage(t *testing.T) {
	s := &pagingStub{edgePages: []*pb.GetEdgesResponse{
		edgesPage(pgMore("c1"), 1, 2),
		edgesPage(pgMore("c2")),
		edgesPage(pgDone(), 3),
	}}
	got, err := edgeTargets(t, &Client{grpc: s})
	want := []string{"kref://p/s/y.k?r=1", "kref://p/s/y.k?r=2", "kref://p/s/y.k?r=3"}
	if err != nil || !reflect.DeepEqual(got, want) {
		t.Fatalf("edges = %v, %v", got, err)
	}
	var sent []sentPage
	for _, r := range s.edgeReqs {
		sent = append(sent, sentPage{r.GetPagination().GetPageSize(), r.GetPagination().GetCursor()})
	}
	wantSent := []sentPage{{1000, ""}, {1000, "c1"}, {1000, "c2"}}
	if !reflect.DeepEqual(sent, wantSent) {
		t.Fatalf("requests = %v, want %v", sent, wantSent)
	}
}

func TestMissingPaginationFieldIsOneCompleteResponse(t *testing.T) {
	// kumiho-server CE answers GetEdges with every edge and no pagination.
	s := &pagingStub{
		edgePages: []*pb.GetEdgesResponse{edgesPage(nil, 1, 2, 3)},
		revPages:  []*pb.GetRevisionsResponse{revsPage(nil, 2, 1)},
	}
	c := &Client{grpc: s}
	edges, err := edgeTargets(t, c)
	if err != nil || len(edges) != 3 {
		t.Fatalf("edges = %v, %v", edges, err)
	}
	revs, err := revisionNumbers(t, c)
	if err != nil || !reflect.DeepEqual(revs, []int32{2, 1}) {
		t.Fatalf("revisions = %v, %v", revs, err)
	}
	if len(s.edgeReqs) != 1 || len(s.revReqs) != 1 {
		t.Fatalf("calls: edges %d, revisions %d", len(s.edgeReqs), len(s.revReqs))
	}
}

func TestRepeatedCursorIsAnErrorNotALoop(t *testing.T) {
	s := &pagingStub{
		edgePages: []*pb.GetEdgesResponse{
			edgesPage(pgMore("c1"), 1),
			edgesPage(pgMore("c1"), 2),
		},
		revPages: []*pb.GetRevisionsResponse{
			revsPage(pgMore("a"), 3),
			revsPage(pgMore("b"), 2),
			revsPage(pgMore("a"), 1),
		},
	}
	c := &Client{grpc: s}
	if _, err := edgeTargets(t, c); err == nil || !strings.Contains(err.Error(), "did not advance") {
		t.Fatalf("edges error = %v", err)
	}
	if _, err := revisionNumbers(t, c); err == nil || !strings.Contains(err.Error(), "did not advance") {
		t.Fatalf("revisions error = %v", err)
	}
}

func TestHasMoreWithoutACursorIsAnError(t *testing.T) {
	s := &pagingStub{
		edgePages: []*pb.GetEdgesResponse{edgesPage(pgMore(""), 1)},
		revPages:  []*pb.GetRevisionsResponse{revsPage(pgMore(""), 1)},
	}
	c := &Client{grpc: s}
	if _, err := edgeTargets(t, c); err == nil || !strings.Contains(err.Error(), "no pagination cursor") {
		t.Fatalf("edges error = %v", err)
	}
	if _, err := revisionNumbers(t, c); err == nil || !strings.Contains(err.Error(), "no pagination cursor") {
		t.Fatalf("revisions error = %v", err)
	}
}

func TestCEOffsetShiftDoesNotRepeatARevision(t *testing.T) {
	// CE pages GetRevisions by offset, newest first. Revision 4 is created
	// after the first page, so the second page starts one row later and
	// repeats revision 2.
	s := &pagingStub{revPages: []*pb.GetRevisionsResponse{
		revsPage(pgMore("offset:2"), 3, 2),
		revsPage(pgDone(), 2, 1),
	}}
	got, err := revisionNumbers(t, &Client{grpc: s})
	if err != nil || !reflect.DeepEqual(got, []int32{3, 2, 1}) {
		t.Fatalf("revisions = %v, %v", got, err)
	}
}

func TestSinglePageAPIsReturnOnePageWithItsCursor(t *testing.T) {
	s := &pagingStub{
		revPages:  []*pb.GetRevisionsResponse{revsPage(pgMore("r-next"), 2)},
		edgePages: []*pb.GetEdgesResponse{edgesPage(pgMore("e-next"), 1)},
	}
	c := &Client{grpc: s}
	rp, err := c.GetRevisionsPaged(context.Background(), Kref("kref://p/s/x.k"), 1, "r-prev")
	if err != nil || len(rp.Items) != 1 || !rp.HasMore || !rp.PaginationPresent || rp.NextCursor != "r-next" {
		t.Fatalf("revision page = %+v, %v", rp, err)
	}
	if p := s.revReqs[0].GetPagination(); p.GetPageSize() != 1 || p.GetCursor() != "r-prev" {
		t.Fatalf("revision request pagination = %+v", p)
	}
	ep, err := c.GetEdgesPaged(context.Background(), Kref("kref://p/s/x.k?r=1"), "", Outgoing, 5, "")
	if err != nil || ep.NextCursor != "e-next" || !ep.HasMore {
		t.Fatalf("edge page = %+v, %v", ep, err)
	}
	if p := s.edgeReqs[0].GetPagination(); p.GetPageSize() != 5 || p.GetCursor() != "" {
		t.Fatalf("edge request pagination = %+v", p)
	}
}
