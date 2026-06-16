package kumiho

import (
	"context"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"encoding/hex"
	"fmt"
	"math"
	mathrand "math/rand"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

const (
	defaultRPCTimeout = 30 * time.Second
	retryMaxAttempts  = 3
	retryBaseDelay    = 500 * time.Millisecond
	retryMaxDelay     = 5 * time.Second
)

// Client is the low-level gRPC client for Kumiho. It is safe for concurrent use.
type Client struct {
	conn *grpc.ClientConn
	grpc pb.KumihoServiceClient
}

// ClientBuilder configures a Client. Obtain one via Builder().
type ClientBuilder struct {
	endpoint     string
	token        string
	tokenSet     bool
	tenantHint   string
	useDiscovery *bool
	forceRefresh bool
	metadata     []string // key,value pairs
}

// Builder starts a new ClientBuilder.
func Builder() *ClientBuilder { return &ClientBuilder{} }

// Endpoint sets an explicit gRPC endpoint (host:port, https://host, grpcs://host:port).
func (b *ClientBuilder) Endpoint(ep string) *ClientBuilder { b.endpoint = ep; return b }

// Token sets an explicit bearer token (otherwise loaded from env / ~/.kumiho).
func (b *ClientBuilder) Token(t string) *ClientBuilder { b.token = t; b.tokenSet = true; return b }

// TenantHint sets a tenant slug/id for discovery or the x-tenant-id header.
func (b *ClientBuilder) TenantHint(h string) *ClientBuilder { b.tenantHint = h; return b }

// UseDiscovery forces control-plane discovery on/off.
func (b *ClientBuilder) UseDiscovery(yes bool) *ClientBuilder { b.useDiscovery = &yes; return b }

// ForceDiscoveryRefresh bypasses the discovery cache.
func (b *ClientBuilder) ForceDiscoveryRefresh(yes bool) *ClientBuilder {
	b.forceRefresh = yes
	return b
}

// Metadata adds a static header sent on every RPC.
func (b *ClientBuilder) Metadata(key, value string) *ClientBuilder {
	b.metadata = append(b.metadata, key, value)
	return b
}

// Connect builds a Client for an explicit endpoint (token auto-loaded).
func Connect(ctx context.Context, endpoint string) (*Client, error) {
	return Builder().Endpoint(endpoint).Build(ctx)
}

// Auto builds a Client following the standard Kumiho bootstrap chain:
//
//  1. Load a bearer token (KUMIHO_AUTH_TOKEN, else ~/.kumiho/kumiho_authentication.json).
//  2. Token present -> control-plane discovery resolves the tenant's regional
//     cloud kumiho-server (errors propagate).
//  3. No token -> probe the loopback self-hosted CE server and use it.
//  4. Neither available -> returns an error.
//
// For an explicit endpoint or a localhost dev fallback, use Connect or Builder.
func Auto(ctx context.Context) (*Client, error) {
	return AutoWithTenant(ctx, "")
}

// AutoWithTenant is like Auto but pins discovery to a tenant slug/id.
func AutoWithTenant(ctx context.Context, tenantHint string) (*Client, error) {
	token, err := loadBearerToken()
	if err != nil {
		return nil, err
	}
	if token != "" {
		// Token present -> control-plane discovery -> tenant's cloud server.
		rec, derr := resolveDiscovery(ctx, token, tenantHint, false)
		if derr != nil {
			return nil, derr
		}
		return Builder().
			Endpoint(rec.Target()).
			Token(token).
			UseDiscovery(false).
			Metadata("x-tenant-id", rec.TenantID).
			Build(ctx)
	}
	// No token -> fall back to a local self-hosted CE server if present.
	local, lerr := resolveLocalCEEndpoint(ctx)
	if lerr != nil {
		return nil, lerr
	}
	if local != "" {
		return Builder().Endpoint(local).UseDiscovery(false).Build(ctx)
	}
	return nil, &DiscoveryError{Msg: "no credentials found: set KUMIHO_AUTH_TOKEN or run `kumiho-cli login`; no local self-hosted CE server detected on loopback"}
}

// Build resolves routing/auth and dials the server (lazily).
func (b *ClientBuilder) Build(ctx context.Context) (*Client, error) {
	// 1. Token.
	token := b.token
	if !b.tokenSet {
		t, err := loadBearerToken()
		if err != nil {
			return nil, err
		}
		token = t
	}

	endpoint := b.endpoint
	useDiscovery := !envTruthy("KUMIHO_DISABLE_AUTO_DISCOVERY")
	if b.useDiscovery != nil {
		useDiscovery = *b.useDiscovery
	}

	// 2. No endpoint + no token -> try local CE.
	if endpoint == "" && token == "" {
		local, lerr := resolveLocalCEEndpoint(ctx)
		if lerr != nil {
			return nil, lerr
		}
		if local != "" {
			endpoint = local
			useDiscovery = false
		}
	}

	md := append([]string{}, b.metadata...)

	// 3. Discovery.
	if endpoint == "" && useDiscovery {
		if token != "" {
			if rec, err := resolveDiscovery(ctx, token, b.tenantHint, b.forceRefresh); err == nil {
				endpoint = rec.Target()
				md = append(md, "x-tenant-id", rec.TenantID)
			} else if b.tenantHint != "" {
				md = append(md, "x-tenant-id", b.tenantHint)
			}
		} else if b.tenantHint != "" {
			md = append(md, "x-tenant-id", b.tenantHint)
		}
	}

	// 4. Fallback.
	if endpoint == "" {
		endpoint = firstNonEmpty(os.Getenv("KUMIHO_SERVER_ENDPOINT"), os.Getenv("KUMIHO_SERVER_ADDRESS"), "localhost:8080")
	}

	// 5. Normalize + creds.
	host, port, useTLS, err := normalizeTarget(endpoint)
	if err != nil {
		return nil, err
	}
	if v := os.Getenv("KUMIHO_SERVER_USE_TLS"); v != "" {
		useTLS = envFlag("KUMIHO_SERVER_USE_TLS")
	}
	authority := firstNonEmpty(os.Getenv("KUMIHO_SERVER_AUTHORITY"), host)

	var creds credentials.TransportCredentials
	if useTLS {
		tlsCfg := &tls.Config{ServerName: authority, MinVersion: tls.VersionTLS12}
		if caFile := os.Getenv("KUMIHO_SERVER_CA_FILE"); caFile != "" {
			pem, rerr := os.ReadFile(caFile)
			if rerr != nil {
				return nil, rerr
			}
			pool := x509.NewCertPool()
			if !pool.AppendCertsFromPEM(pem) {
				return nil, fmt.Errorf("failed to parse CA bundle %q", caFile)
			}
			tlsCfg.RootCAs = pool
		}
		creds = credentials.NewTLS(tlsCfg)
	} else {
		creds = insecure.NewCredentials()
	}

	// 6. Auth header.
	if token != "" {
		md = append(md, "authorization", "Bearer "+token)
	}

	rpcTimeout := defaultRPCTimeout
	if v := os.Getenv("KUMIHO_RPC_TIMEOUT_SECS"); v != "" {
		if f, perr := strconv.ParseFloat(v, 64); perr == nil {
			rpcTimeout = time.Duration(f * float64(time.Second))
		}
	}
	maxAttempts := retryMaxAttempts
	if v := os.Getenv("KUMIHO_GRPC_RETRY_MAX_ATTEMPTS"); v != "" {
		if n, perr := strconv.Atoi(v); perr == nil && n > 0 {
			maxAttempts = n
		}
	}

	target := net.JoinHostPort(host, strconv.Itoa(int(port)))
	conn, err := grpc.NewClient(
		target,
		grpc.WithTransportCredentials(creds),
		grpc.WithAuthority(authority),
		grpc.WithKeepaliveParams(keepalive.ClientParameters{
			Time:                30 * time.Second,
			Timeout:             10 * time.Second,
			PermitWithoutStream: true,
		}),
		grpc.WithChainUnaryInterceptor(unaryInterceptor(md, maxAttempts, rpcTimeout)),
		grpc.WithChainStreamInterceptor(streamInterceptor(md)),
		grpc.WithDefaultCallOptions(grpc.MaxCallRecvMsgSize(64*1024*1024)),
	)
	if err != nil {
		return nil, err
	}
	return &Client{conn: conn, grpc: pb.NewKumihoServiceClient(conn)}, nil
}

// Close releases the underlying connection.
func (c *Client) Close() error { return c.conn.Close() }

// ----------------------------------------------------------------- interceptors

func injectMeta(ctx context.Context, md []string) context.Context {
	pairs := make([]string, 0, len(md)+2)
	pairs = append(pairs, md...)
	pairs = append(pairs, "x-correlation-id", "kumiho-"+randHex(8))
	return metadata.AppendToOutgoingContext(ctx, pairs...)
}

func unaryInterceptor(md []string, maxAttempts int, timeout time.Duration) grpc.UnaryClientInterceptor {
	return func(ctx context.Context, method string, req, reply any, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		var lastErr error
		for attempt := 0; attempt < maxAttempts; attempt++ {
			// Inject static metadata + a fresh correlation id on every attempt,
			// mirroring the Python client where the retry interceptor is outermost.
			callCtx := injectMeta(ctx, md)
			var cancel context.CancelFunc
			if timeout > 0 {
				callCtx, cancel = context.WithTimeout(callCtx, timeout)
			}
			err := invoker(callCtx, method, req, reply, cc, opts...)
			if cancel != nil {
				cancel()
			}
			if err == nil {
				return nil
			}
			lastErr = err
			if isTransient(status.Code(err)) && attempt+1 < maxAttempts {
				time.Sleep(backoff(attempt + 1))
				continue
			}
			return err
		}
		return lastErr
	}
}

func streamInterceptor(md []string) grpc.StreamClientInterceptor {
	return func(ctx context.Context, desc *grpc.StreamDesc, cc *grpc.ClientConn, method string, streamer grpc.Streamer, opts ...grpc.CallOption) (grpc.ClientStream, error) {
		return streamer(injectMeta(ctx, md), desc, cc, method, opts...)
	}
}

func isTransient(code codes.Code) bool {
	switch code {
	case codes.Unavailable, codes.DeadlineExceeded, codes.Internal, codes.ResourceExhausted:
		return true
	default:
		return false
	}
}

func backoff(attempt int) time.Duration {
	base := float64(retryBaseDelay) * math.Pow(2, float64(attempt-1))
	if base > float64(retryMaxDelay) {
		base = float64(retryMaxDelay)
	}
	jitter := mathrand.Float64() * base * 0.25
	return time.Duration(base + jitter)
}

func randHex(n int) string {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return strconv.FormatInt(time.Now().UnixNano(), 16)
	}
	return hex.EncodeToString(b)
}

// ------------------------------------------------------------------- value types

// Page is a slice of list results plus an optional pagination cursor.
type Page[T any] struct {
	Items      []T
	NextCursor string
	TotalCount int32
}

func pageFrom[T any](items []T, p *pb.PaginationResponse) *Page[T] {
	pg := &Page[T]{Items: items}
	if p != nil {
		pg.NextCursor = p.GetNextCursor()
		pg.TotalCount = p.GetTotalCount()
	}
	return pg
}

// SearchResult is a full-text search hit.
type SearchResult struct {
	Item      *Item
	Score     float32
	MatchedIn []string
}

// ScoredRevision is a revision scored against a query by the server.
type ScoredRevision struct {
	Kref        string
	Score       float32
	ScoreMethod string
}

// TenantUsage reports the current tenant's node usage and limit.
type TenantUsage struct {
	NodeCount int64
	NodeLimit int64
	TenantID  string
}

// ------------------------------------------------------------------- free helpers

func firstNonEmpty(vals ...string) string {
	for _, v := range vals {
		if v != "" {
			return v
		}
	}
	return ""
}

func normalizeTarget(raw string) (host string, port uint16, useTLS bool, err error) {
	target := strings.TrimSpace(raw)
	if target == "" {
		return "", 0, false, &InvalidArgumentError{Msg: "endpoint cannot be empty"}
	}
	scheme := ""
	if i := strings.Index(target, "://"); i >= 0 {
		scheme = strings.ToLower(target[:i])
		target = target[i+3:]
	}
	if i := strings.IndexByte(target, '/'); i >= 0 {
		target = target[:i]
	}
	var portStr string
	if h, p, e := net.SplitHostPort(target); e == nil {
		host, portStr = h, p
	} else {
		host = target
	}
	if host == "" {
		return "", 0, false, &InvalidArgumentError{Msg: "invalid endpoint: " + raw}
	}
	tlsScheme := scheme == "https" || scheme == "grpcs"
	if portStr == "" {
		switch scheme {
		case "https", "grpcs":
			port = 443
		case "http", "grpc":
			port = 80
		default:
			port = 8080
		}
	} else {
		n, e := strconv.Atoi(portStr)
		if e != nil {
			return "", 0, false, &InvalidArgumentError{Msg: "invalid port in endpoint: " + raw}
		}
		port = uint16(n)
	}
	useTLS = tlsScheme || port == 443
	return host, port, useTLS, nil
}

func strPtr(s string) *string { return &s }

func parseTagTime(krefURI string) (base string, tag, t *string, err error) {
	i := strings.IndexByte(krefURI, '?')
	if i < 0 {
		return krefURI, nil, nil, nil
	}
	base = krefURI[:i]
	for _, param := range strings.Split(krefURI[i+1:], "&") {
		switch {
		case strings.HasPrefix(param, "t="):
			tag = strPtr(param[2:])
		case strings.HasPrefix(param, "tag="):
			tag = strPtr(param[4:])
		case strings.HasPrefix(param, "time="):
			v := param[5:]
			if len(v) != 12 || !isAllDigits(v) {
				return "", nil, nil, &InvalidArgumentError{Msg: "time must be in YYYYMMDDHHMM format"}
			}
			t = strPtr(v)
		}
	}
	return base, tag, t, nil
}

func isAllDigits(s string) bool {
	for _, r := range s {
		if r < '0' || r > '9' {
			return false
		}
	}
	return len(s) > 0
}

// splitItemKref splits an item kref URI into (parentPath, name, kind).
func splitItemKref(krefURI string) (parentPath, name, kind string, err error) {
	if verr := ValidateKref(krefURI); verr != nil {
		return "", "", "", verr
	}
	k := Kref(krefURI)
	path := k.Path()
	slash := strings.IndexByte(path, '/')
	if slash < 0 {
		return "", "", "", &InvalidArgumentError{Msg: "invalid item kref: " + krefURI}
	}
	spacePath, nameKind := path[:slash], path[slash+1:]
	dot := strings.IndexByte(nameKind, '.')
	if dot < 0 {
		return "", "", "", &InvalidArgumentError{Msg: "invalid item name.kind: " + nameKind}
	}
	return "/" + spacePath, nameKind[:dot], nameKind[dot+1:], nil
}
