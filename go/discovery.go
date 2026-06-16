package kumiho

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

const (
	defaultControlPlane = "https://control.kumiho.cloud"
	defaultCacheKey     = "__default__"
	defaultLocalCEPort  = 9190
)

// DiscoveryError indicates a control-plane discovery / bootstrap failure.
type DiscoveryError struct{ Msg string }

func (e *DiscoveryError) Error() string { return "discovery: " + e.Msg }

func (e *DiscoveryError) kumihoError() {}

// RegionRouting is the regional gRPC routing returned by the control plane.
type RegionRouting struct {
	RegionCode    string `json:"region_code"`
	ServerURL     string `json:"server_url"`
	GRPCAuthority string `json:"grpc_authority,omitempty"`
}

// CacheControl is the cache window emitted by the control plane.
type CacheControl struct {
	IssuedAt            string `json:"issued_at"`
	RefreshAt           string `json:"refresh_at"`
	ExpiresAt           string `json:"expires_at"`
	ExpiresInSeconds    int64  `json:"expires_in_seconds"`
	RefreshAfterSeconds int64  `json:"refresh_after_seconds"`
}

func parseTS(raw string) (time.Time, bool) {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return time.Time{}, false
	}
	if strings.HasSuffix(raw, "Z") {
		raw = strings.TrimSuffix(raw, "Z") + "+00:00"
	}
	if t, err := time.Parse(time.RFC3339, raw); err == nil {
		return t.UTC(), true
	}
	if t, err := time.Parse("2006-01-02T15:04:05", raw); err == nil {
		return t.UTC(), true
	}
	return time.Time{}, false
}

func (c CacheControl) isExpired() bool {
	t, ok := parseTS(c.ExpiresAt)
	return !ok || !time.Now().UTC().Before(t)
}

func (c CacheControl) shouldRefresh() bool {
	t, ok := parseTS(c.RefreshAt)
	return !ok || !time.Now().UTC().Before(t)
}

// DiscoveryRecord is a resolved tenant routing record.
type DiscoveryRecord struct {
	TenantID     string          `json:"tenant_id"`
	TenantName   string          `json:"tenant_name,omitempty"`
	Roles        []string        `json:"roles,omitempty"`
	Guardrails   json.RawMessage `json:"guardrails,omitempty"`
	Region       RegionRouting   `json:"region"`
	CacheControl CacheControl    `json:"cache_control"`
}

// Target is the gRPC endpoint to dial (authority preferred over server URL).
func (r *DiscoveryRecord) Target() string {
	if r.Region.GRPCAuthority != "" {
		return r.Region.GRPCAuthority
	}
	return r.Region.ServerURL
}

// ---- at-rest cache encryption (machine-bound, defense-in-depth) ----

func machineID() string {
	switch runtime.GOOS {
	case "linux":
		for _, p := range []string{"/etc/machine-id", "/var/lib/dbus/machine-id"} {
			if b, err := os.ReadFile(p); err == nil {
				if s := strings.TrimSpace(string(b)); s != "" {
					return s
				}
			}
		}
	case "darwin":
		if out, err := exec.Command("ioreg", "-rd1", "-c", "IOPlatformExpertDevice").Output(); err == nil {
			for _, line := range strings.Split(string(out), "\n") {
				if strings.Contains(line, "IOPlatformUUID") {
					parts := strings.Split(line, `"`)
					if len(parts) >= 2 {
						return parts[len(parts)-2]
					}
				}
			}
		}
	}
	idFile := filepath.Join(configDir(), ".machine_id")
	if b, err := os.ReadFile(idFile); err == nil {
		if s := strings.TrimSpace(string(b)); s != "" {
			return s
		}
	}
	buf := make([]byte, 16)
	_, _ = rand.Read(buf)
	id := fmt.Sprintf("%x", buf)
	_ = os.MkdirAll(configDir(), 0o700)
	_ = os.WriteFile(idFile, []byte(id), 0o600)
	return id
}

func deriveKey() []byte {
	login := os.Getenv("USER")
	if login == "" {
		login = os.Getenv("LOGNAME")
	}
	uid := strconv.Itoa(os.Getuid())
	material := fmt.Sprintf("kumiho-discovery-cache-v1:%s:%s%s", machineID(), login, uid)
	sum := sha256.Sum256([]byte(material))
	return sum[:]
}

func keystream(key, iv []byte, n int) []byte {
	first := sha256.Sum256(append(append([]byte{}, key...), iv...))
	stream := append([]byte{}, first[:]...)
	for len(stream) < n {
		tail := stream[len(stream)-32:]
		next := sha256.Sum256(append(append([]byte{}, key...), tail...))
		stream = append(stream, next[:]...)
	}
	return stream
}

func encryptCache(plaintext string) string {
	key := deriveKey()
	iv := make([]byte, 16)
	_, _ = rand.Read(iv)
	pt := []byte(plaintext)
	ks := keystream(key, iv, len(pt))
	ct := make([]byte, len(pt))
	for i := range pt {
		ct[i] = pt[i] ^ ks[i]
	}
	mac := hmac.New(sha256.New, key)
	mac.Write(iv)
	mac.Write(ct)
	tag := mac.Sum(nil)[:16]
	blob := append(append(append([]byte{}, iv...), ct...), tag...)
	return "enc:v1:" + base64.StdEncoding.EncodeToString(blob)
}

func decryptCache(encrypted string) (string, bool) {
	rest, ok := strings.CutPrefix(encrypted, "enc:v1:")
	if !ok {
		return encrypted, true // legacy plaintext
	}
	key := deriveKey()
	raw, err := base64.StdEncoding.DecodeString(rest)
	if err != nil || len(raw) < 32 {
		return "", false
	}
	iv, ct, tag := raw[:16], raw[16:len(raw)-16], raw[len(raw)-16:]
	mac := hmac.New(sha256.New, key)
	mac.Write(iv)
	mac.Write(ct)
	if !hmac.Equal(mac.Sum(nil)[:16], tag) {
		return "", false
	}
	ks := keystream(key, iv, len(ct))
	pt := make([]byte, len(ct))
	for i := range ct {
		pt[i] = ct[i] ^ ks[i]
	}
	return string(pt), true
}

func cachePath() string {
	if p := os.Getenv("KUMIHO_DISCOVERY_CACHE_FILE"); p != "" {
		return p
	}
	// Namespaced to avoid clashing with other SDKs' caches on the same key.
	return filepath.Join(configDir(), "discovery-cache.go.json")
}

func cacheReadAll() map[string]DiscoveryRecord {
	out := map[string]DiscoveryRecord{}
	data, err := os.ReadFile(cachePath())
	if err != nil {
		return out
	}
	plain, ok := decryptCache(string(data))
	if !ok {
		return out
	}
	_ = json.Unmarshal([]byte(plain), &out)
	return out
}

func cacheStore(key string, rec DiscoveryRecord) {
	all := cacheReadAll()
	all[key] = rec
	data, err := json.MarshalIndent(all, "", "  ")
	if err != nil {
		return
	}
	_ = os.MkdirAll(filepath.Dir(cachePath()), 0o700)
	_ = os.WriteFile(cachePath(), []byte(encryptCache(string(data))), 0o600)
}

func buildDiscoveryURL(base string) string {
	base = strings.TrimRight(base, "/")
	switch {
	case strings.HasSuffix(base, "/api/discovery/tenant"):
		return base
	case strings.HasSuffix(base, "/api/discovery"):
		return base + "/tenant"
	case strings.HasSuffix(base, "/api"):
		return base + "/discovery/tenant"
	default:
		return base + "/api/discovery/tenant"
	}
}

func fetchRemote(ctx context.Context, baseURL, idToken, tenantHint string) (DiscoveryRecord, error) {
	body := map[string]string{}
	if tenantHint != "" {
		body["tenant_hint"] = tenantHint
	}
	payload, _ := json.Marshal(body)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, buildDiscoveryURL(baseURL), bytes.NewReader(payload))
	if err != nil {
		return DiscoveryRecord{}, &DiscoveryError{Msg: err.Error()}
	}
	req.Header.Set("Authorization", "Bearer "+idToken)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "kumiho-go/"+Version)
	resp, err := (&http.Client{Timeout: discoveryTimeout()}).Do(req)
	if err != nil {
		return DiscoveryRecord{}, &DiscoveryError{Msg: err.Error()}
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		return DiscoveryRecord{}, &DiscoveryError{Msg: fmt.Sprintf("discovery endpoint returned %d", resp.StatusCode)}
	}
	var rec DiscoveryRecord
	if err := json.NewDecoder(resp.Body).Decode(&rec); err != nil {
		return DiscoveryRecord{}, &DiscoveryError{Msg: "invalid discovery payload: " + err.Error()}
	}
	return rec, nil
}

// fetchFresh fetches a discovery record, trying each token candidate in turn
// (the bearer token, plus a Firebase fallback when it's a control-plane token)
// and returning the last error if all fail. Mirrors Python's fetch_fresh.
func fetchFresh(ctx context.Context, base, idToken, tenantHint string) (DiscoveryRecord, error) {
	var lastErr error
	for _, tok := range discoveryTokenCandidates(idToken) {
		rec, err := fetchRemote(ctx, base, tok, tenantHint)
		if err == nil {
			return rec, nil
		}
		lastErr = err
	}
	if lastErr != nil {
		return DiscoveryRecord{}, lastErr
	}
	return DiscoveryRecord{}, &DiscoveryError{Msg: "discovery failed without a usable bearer token"}
}

// resolveDiscovery resolves a DiscoveryRecord, using the encrypted cache when fresh.
func resolveDiscovery(ctx context.Context, idToken, tenantHint string, forceRefresh bool) (DiscoveryRecord, error) {
	base := os.Getenv("KUMIHO_CONTROL_PLANE_URL")
	if base == "" {
		base = defaultControlPlane
	}
	key := tenantHint
	if key == "" {
		key = defaultCacheKey
	}

	if !forceRefresh {
		if cached, ok := cacheReadAll()[key]; ok && !cached.CacheControl.isExpired() {
			if cached.CacheControl.shouldRefresh() {
				if fresh, err := fetchFresh(ctx, base, idToken, tenantHint); err == nil {
					cacheStore(key, fresh)
					return fresh, nil
				} else if !cached.CacheControl.isExpired() {
					return cached, nil
				} else {
					return DiscoveryRecord{}, err
				}
			}
			return cached, nil
		}
	}
	fresh, err := fetchFresh(ctx, base, idToken, tenantHint)
	if err != nil {
		return DiscoveryRecord{}, err
	}
	cacheStore(key, fresh)
	return fresh, nil
}

// TenantInfo returns the cached discovery record for the given tenant hint (or
// the default tenant), or nil if no cache entry exists. Mirrors Python
// get_tenant_info (tenant id, name, roles, region, guardrails).
func TenantInfo(tenantHint string) *DiscoveryRecord {
	key := tenantHint
	if key == "" {
		key = defaultCacheKey
	}
	if rec, ok := cacheReadAll()[key]; ok {
		return &rec
	}
	return nil
}

// TenantSlug returns a URL-safe tenant slug (or a shortened tenant id) for the
// given tenant hint, or "" if no cached tenant info exists. Mirrors Python
// get_tenant_slug.
func TenantSlug(tenantHint string) string {
	rec := TenantInfo(tenantHint)
	if rec == nil {
		return ""
	}
	if rec.TenantName != "" && isURLSafeSlug(rec.TenantName) {
		return strings.ToLower(rec.TenantName)
	}
	if rec.TenantID != "" {
		return strings.SplitN(rec.TenantID, "-", 2)[0]
	}
	return rec.TenantName
}

func isURLSafeSlug(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if !((r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-') {
			return false
		}
	}
	return true
}

// resolveLocalCEEndpoint probes loopback ports for a self-hosted CE server.
// It returns an error when KUMIHO_LOCAL_SERVER_ENDPOINT / KUMIHO_LOCAL_SERVER_PORT
// is set to a non-loopback or otherwise invalid value, mirroring the Python SDK.
func resolveLocalCEEndpoint(ctx context.Context) (string, error) {
	var candidates []string
	if ep := strings.TrimSpace(os.Getenv("KUMIHO_LOCAL_SERVER_ENDPOINT")); ep != "" {
		t, err := normalizeLocalTarget(ep)
		if err != nil {
			return "", err
		}
		candidates = []string{t}
	} else if port := strings.TrimSpace(os.Getenv("KUMIHO_LOCAL_SERVER_PORT")); port != "" {
		n, err := strconv.Atoi(port)
		if err != nil || n <= 0 || n > 65535 {
			return "", &DiscoveryError{Msg: "KUMIHO_LOCAL_SERVER_PORT must be a numeric loopback port"}
		}
		candidates = []string{fmt.Sprintf("127.0.0.1:%d", n)}
	} else {
		candidates = []string{fmt.Sprintf("127.0.0.1:%d", defaultLocalCEPort)}
	}
	for _, t := range candidates {
		if probeCE(ctx, t) {
			return t, nil
		}
	}
	return "", nil
}

// normalizeLocalTarget strips the scheme/path from a local CE endpoint and
// enforces that it points at a loopback host (localhost, 127.0.0.1, ::1) so a
// tokenless client can never be routed to a remote server. Mirrors the Python
// _normalise_local_ce_target guard.
func normalizeLocalTarget(raw string) (string, error) {
	raw = strings.TrimSpace(raw)
	if i := strings.Index(raw, "://"); i >= 0 {
		raw = raw[i+3:]
	}
	if i := strings.IndexByte(raw, '/'); i >= 0 {
		raw = raw[:i] // strip any trailing path
	}
	host := raw
	port := defaultLocalCEPort
	if h, p, err := net.SplitHostPort(raw); err == nil {
		host = h
		n, perr := strconv.Atoi(p)
		if perr != nil || n <= 0 || n > 65535 {
			return "", &DiscoveryError{Msg: "KUMIHO_LOCAL_SERVER_ENDPOINT port must be between 1 and 65535"}
		}
		port = n
	} else {
		host = strings.TrimSuffix(strings.TrimPrefix(host, "["), "]") // bare/bracketed IPv6
	}
	if host == "" {
		return "", &DiscoveryError{Msg: "KUMIHO_LOCAL_SERVER_ENDPOINT must include a loopback host"}
	}
	if !isLoopbackHost(host) {
		return "", &DiscoveryError{Msg: "KUMIHO_LOCAL_SERVER_ENDPOINT must point to localhost, 127.0.0.1, or ::1"}
	}
	return net.JoinHostPort(host, strconv.Itoa(port)), nil
}

func isLoopbackHost(host string) bool {
	if strings.EqualFold(host, "localhost") {
		return true
	}
	if ip := net.ParseIP(host); ip != nil {
		return ip.IsLoopback()
	}
	return false
}

// discoveryTimeout is the control-plane HTTP timeout (KUMIHO_DISCOVERY_TIMEOUT_SECONDS,
// default 10s).
func discoveryTimeout() time.Duration {
	if v := os.Getenv("KUMIHO_DISCOVERY_TIMEOUT_SECONDS"); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil && f > 0 {
			return time.Duration(f * float64(time.Second))
		}
	}
	return 10 * time.Second
}

// localCETimeout is the local-CE probe timeout (KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS,
// default 0.5s, floor 0.05s).
func localCETimeout() time.Duration {
	if v := os.Getenv("KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS"); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			if f < 0.05 {
				f = 0.05
			}
			return time.Duration(f * float64(time.Second))
		}
	}
	return 500 * time.Millisecond
}

func probeCE(ctx context.Context, target string) bool {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "http://"+target+"/api/_live", nil)
	if err != nil {
		return false
	}
	resp, err := (&http.Client{Timeout: localCETimeout()}).Do(req)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		return false
	}
	var body map[string]any
	if json.NewDecoder(resp.Body).Decode(&body) != nil {
		return false
	}
	mode, _ := body["deployment_mode"].(string)
	return mode == "self_hosted_ce"
}
