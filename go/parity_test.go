package kumiho

// White-box unit tests for the discovery/token helper logic that backs
// Python-parity behavior (Firebase-fallback candidate selection, tenant slug).

import (
	"encoding/base64"
	"encoding/json"
	"errors"
	"testing"
)

func TestKumihoErrorCatchAll(t *testing.T) {
	for _, err := range []error{
		&KrefValidationError{Msg: "x"},
		&EdgeTypeValidationError{Msg: "x"},
		&ReservedKindError{Kind: "bundle", Msg: "x"},
		&ProjectLimitError{Msg: "x"},
		&InvalidArgumentError{Msg: "x"},
		&DiscoveryError{Msg: "x"},
	} {
		var ke KumihoError
		if !errors.As(err, &ke) {
			t.Errorf("%T should satisfy the KumihoError catch-all interface", err)
		}
	}
}

func makeJWT(claims map[string]any) string {
	payload, _ := json.Marshal(claims)
	return "h." + base64.RawURLEncoding.EncodeToString(payload) + ".s"
}

func TestIsControlPlaneToken(t *testing.T) {
	cases := []struct {
		name   string
		claims map[string]any
		want   bool
	}{
		{"tenant_id claim", map[string]any{"tenant_id": "t1"}, true},
		{"control-plane iss", map[string]any{"iss": "https://control.kumiho.cloud/x"}, true},
		{"kumiho-server aud", map[string]any{"aud": "kumiho-server-prod"}, true},
		{"firebase token", map[string]any{"iss": "https://securetoken.google.com/p", "user_id": "u"}, false},
	}
	for _, c := range cases {
		if got := isControlPlaneToken(makeJWT(c.claims)); got != c.want {
			t.Errorf("%s: isControlPlaneToken = %v, want %v", c.name, got, c.want)
		}
	}
	if isControlPlaneToken("not-a-jwt") {
		t.Error("a non-JWT string must not be treated as a control-plane token")
	}
}

func TestDiscoveryTokenCandidates(t *testing.T) {
	// A non-control-plane (Firebase) token yields only itself — no fallback.
	fb := makeJWT(map[string]any{"iss": "https://securetoken.google.com/p"})
	if got := discoveryTokenCandidates(fb); len(got) != 1 || got[0] != fb {
		t.Errorf("firebase candidates = %v, want exactly [the token]", got)
	}

	// A control-plane token appends the Firebase token as a fallback candidate.
	t.Setenv("KUMIHO_FIREBASE_ID_TOKEN", "a.b.c")
	cp := makeJWT(map[string]any{"tenant_id": "t1"})
	got := discoveryTokenCandidates(cp)
	if len(got) != 2 || got[0] != cp || got[1] != "a.b.c" {
		t.Errorf("control-plane candidates = %v, want [cp, firebase]", got)
	}
}

func TestIsURLSafeSlug(t *testing.T) {
	for _, s := range []string{"kumihoclouds", "my-studio", "abc123"} {
		if !isURLSafeSlug(s) {
			t.Errorf("isURLSafeSlug(%q) = false, want true", s)
		}
	}
	for _, s := range []string{"", "has space", "under_score", "dot.dot", "café"} {
		if isURLSafeSlug(s) {
			t.Errorf("isURLSafeSlug(%q) = true, want false", s)
		}
	}
}
