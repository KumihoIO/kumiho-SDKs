package kumiho_test

// In-process integration tests: a fake KumihoService gRPC server is started on a
// loopback port and the real SDK client is pointed at it. This exercises the
// actual request construction, metadata/correlation-id injection, retry
// interceptor and response parsing — no credentials or network required.

import (
	"context"
	"net"
	"strings"
	"sync"
	"testing"
	"time"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

type fakeServer struct {
	pb.UnimplementedKumihoServiceServer

	mu               sync.Mutex
	lastItemReq      *pb.CreateItemRequest
	lastRevisionKref string
	sawCorrelationID bool
}

func (s *fakeServer) recordCorrelation(ctx context.Context) {
	if md, ok := metadata.FromIncomingContext(ctx); ok {
		if vals := md.Get("x-correlation-id"); len(vals) > 0 && vals[0] != "" {
			s.mu.Lock()
			s.sawCorrelationID = true
			s.mu.Unlock()
		}
	}
}

func (s *fakeServer) CreateProject(ctx context.Context, req *pb.CreateProjectRequest) (*pb.ProjectResponse, error) {
	s.recordCorrelation(ctx)
	return &pb.ProjectResponse{
		ProjectId:   "proj-123",
		Name:        req.GetName(),
		Description: req.GetDescription(),
	}, nil
}

func (s *fakeServer) GetProjects(context.Context, *pb.GetProjectsRequest) (*pb.GetProjectsResponse, error) {
	return &pb.GetProjectsResponse{Projects: []*pb.ProjectResponse{
		{ProjectId: "p1", Name: "alpha"},
		{ProjectId: "p2", Name: "beta"},
	}}, nil
}

func (s *fakeServer) CreateItem(ctx context.Context, req *pb.CreateItemRequest) (*pb.ItemResponse, error) {
	s.mu.Lock()
	s.lastItemReq = req
	s.mu.Unlock()
	uri := "kref://" + strings.TrimPrefix(req.GetParentPath(), "/") + "/" + req.GetItemName() + "." + req.GetKind()
	return &pb.ItemResponse{
		Kref:     &pb.Kref{Uri: uri},
		Name:     req.GetItemName() + "." + req.GetKind(),
		ItemName: req.GetItemName(),
		Kind:     req.GetKind(),
	}, nil
}

func (s *fakeServer) GetRevision(ctx context.Context, req *pb.KrefRequest) (*pb.RevisionResponse, error) {
	s.mu.Lock()
	s.lastRevisionKref = req.GetKref().GetUri()
	s.mu.Unlock()
	return &pb.RevisionResponse{Kref: req.GetKref(), Number: 3, Latest: true}, nil
}

func (s *fakeServer) ResolveLocation(ctx context.Context, req *pb.ResolveLocationRequest) (*pb.ResolveLocationResponse, error) {
	if strings.Contains(req.GetKref(), "missing") {
		return nil, status.Error(codes.NotFound, "revision not found")
	}
	return &pb.ResolveLocationResponse{Location: "/data/hero.fbx"}, nil
}

// startFake spins up the fake server and returns a connected SDK client.
func startFake(t *testing.T) (*fakeServer, *kumiho.Client) {
	t.Helper()
	// Isolate from any real ~/.kumiho credentials on the dev machine.
	t.Setenv("KUMIHO_CONFIG_DIR", t.TempDir())
	t.Setenv("KUMIHO_AUTH_TOKEN", "")

	lis, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen: %v", err)
	}
	srv := grpc.NewServer()
	fake := &fakeServer{}
	pb.RegisterKumihoServiceServer(srv, fake)
	go func() { _ = srv.Serve(lis) }()
	t.Cleanup(srv.Stop)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	t.Cleanup(cancel)
	client, err := kumiho.Connect(ctx, lis.Addr().String())
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	t.Cleanup(func() { _ = client.Close() })
	return fake, client
}

func TestIntegrationProjects(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()

	p, err := client.CreateProject(ctx, "vfx", "VFX assets")
	if err != nil {
		t.Fatalf("CreateProject: %v", err)
	}
	if p.ProjectID != "proj-123" || p.Name != "vfx" || p.Description != "VFX assets" {
		t.Errorf("project = %+v", p)
	}

	projs, err := client.GetProjects(ctx)
	if err != nil {
		t.Fatalf("GetProjects: %v", err)
	}
	if len(projs) != 2 || projs[0].Name != "alpha" || projs[1].Name != "beta" {
		t.Errorf("projects = %+v", projs)
	}

	fake.mu.Lock()
	saw := fake.sawCorrelationID
	fake.mu.Unlock()
	if !saw {
		t.Error("server did not receive an x-correlation-id header (interceptor not applied)")
	}
}

func TestIntegrationCreateItemFieldsAndReservedKind(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()

	item, err := client.CreateItem(ctx, "/vfx/chars", "hero", "model", nil)
	if err != nil {
		t.Fatalf("CreateItem: %v", err)
	}
	if item.Kind != "model" || item.ItemName != "hero" {
		t.Errorf("item = %+v", item)
	}
	fake.mu.Lock()
	req := fake.lastItemReq
	fake.mu.Unlock()
	if req == nil || req.GetParentPath() != "/vfx/chars" || req.GetItemName() != "hero" || req.GetKind() != "model" {
		t.Errorf("server CreateItemRequest = %+v", req)
	}

	// The reserved "bundle" kind must be rejected client-side, before any RPC.
	fake.mu.Lock()
	fake.lastItemReq = nil
	fake.mu.Unlock()
	if _, err := client.CreateItem(ctx, "/vfx/chars", "pack", "bundle", nil); err == nil {
		t.Error("expected an error creating an item with reserved kind 'bundle'")
	}
	fake.mu.Lock()
	leaked := fake.lastItemReq
	fake.mu.Unlock()
	if leaked != nil {
		t.Error("reserved-kind CreateItem must not reach the server")
	}
}

func TestIntegrationGetRevisionCarriesRevisionQuery(t *testing.T) {
	fake, client := startFake(t)

	rev, err := client.GetRevision(context.Background(), "kref://vfx/chars/hero.model?r=3")
	if err != nil {
		t.Fatalf("GetRevision: %v", err)
	}
	if rev.Number != 3 || !rev.Latest {
		t.Errorf("revision = %+v", rev)
	}
	fake.mu.Lock()
	uri := fake.lastRevisionKref
	fake.mu.Unlock()
	if !strings.Contains(uri, "?r=3") {
		t.Errorf("server GetRevision kref = %q, want it to contain ?r=3", uri)
	}
}

func TestIntegrationResolveSwallowsRPCError(t *testing.T) {
	_, client := startFake(t)
	ctx := context.Background()

	loc, err := client.Resolve(ctx, "kref://vfx/chars/hero.model")
	if err != nil {
		t.Fatalf("Resolve: %v", err)
	}
	if loc != "/data/hero.fbx" {
		t.Errorf("location = %q, want /data/hero.fbx", loc)
	}

	// A failed resolution returns ("", nil) — not an error — per the SDK fix.
	loc, err = client.Resolve(ctx, "kref://vfx/chars/missing.model")
	if err != nil {
		t.Errorf("Resolve should swallow the RPC error, got %v", err)
	}
	if loc != "" {
		t.Errorf("failed resolve location = %q, want empty", loc)
	}
}
