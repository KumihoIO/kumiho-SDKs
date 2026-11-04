package kumiho

import (
	"context"
	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc"
	"testing"
)

type inventoryStub struct {
	pb.KumihoServiceClient
	spaces       *pb.GetChildSpacesResponse
	items        *pb.GetItemsResponse
	spaceRequest *pb.GetChildSpacesRequest
	itemRequest  *pb.GetItemsRequest
}

func (s *inventoryStub) GetChildSpaces(_ context.Context, r *pb.GetChildSpacesRequest, _ ...grpc.CallOption) (*pb.GetChildSpacesResponse, error) {
	s.spaceRequest = r
	return s.spaces, nil
}
func (s *inventoryStub) GetItems(_ context.Context, r *pb.GetItemsRequest, _ ...grpc.CallOption) (*pb.GetItemsResponse, error) {
	s.itemRequest = r
	return s.items, nil
}

func TestInventoryEmptyFinalPageDiffersFromMissingMetadata(t *testing.T) {
	s := &inventoryStub{spaces: &pb.GetChildSpacesResponse{Pagination: &pb.PaginationResponse{}}, items: &pb.GetItemsResponse{Pagination: &pb.PaginationResponse{}}}
	c := &Client{grpc: s}
	p, err := c.GetChildSpacesPaged(context.Background(), "/p", true, 0, "")
	if err != nil || !p.PaginationPresent || p.HasMore || p.TotalCount != 0 || p.NextCursor != "" {
		t.Fatalf("empty final page: %+v %v", p, err)
	}
	if s.spaceRequest.Pagination != nil {
		t.Fatal("default request must remain unpaged")
	}
	s.spaces = &pb.GetChildSpacesResponse{}
	p, err = c.GetChildSpacesPaged(context.Background(), "/p", true, 0, "")
	if err != nil || p.PaginationPresent {
		t.Fatalf("metadata must remain unknown: %+v %v", p, err)
	}
	s.items.Pagination = &pb.PaginationResponse{TotalCount: 8, HasMore: true, NextCursor: "opaque-next"}
	space := newSpace(&pb.SpaceResponse{Path: "/p"}, c)
	items, err := space.GetItemsPaged(context.Background(), "", "", 2, "opaque-before", true)
	if err != nil || !items.HasMore || !items.PaginationPresent || items.NextCursor != "opaque-next" || items.TotalCount != 8 {
		t.Fatalf("page metadata: %+v %v", items, err)
	}
	if !s.itemRequest.IncludeDeprecated || s.itemRequest.Pagination.Cursor != "opaque-before" || s.itemRequest.Pagination.PageSize != 2 {
		t.Fatalf("forwarded request: %+v", s.itemRequest)
	}
	_, err = space.GetItems(context.Background(), "", "", 0, "")
	if err != nil || s.itemRequest.IncludeDeprecated || s.itemRequest.Pagination != nil {
		t.Fatal("old convenience defaults changed")
	}
	// Preserve even existing unkeyed downstream Page literals.
	legacy := Page[int]{[]int{1}, "", 1}
	if legacy.TotalCount != 1 {
		t.Fatal("legacy Page layout changed")
	}
}
