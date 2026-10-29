package kumiho_test

// Server-returned item krefs and huge inputs.
//
// kumiho-server rebuilds the key it matches as normalize_space_path(parent) +
// "/" + name + "." + kind, and normalize_space_path trims whitespace and "/".
// A kref the server returns is not checked by its own read RPCs, so it can hold
// a space segment that ends in whitespace, or an empty segment, and splitting
// such a kref at its last "/" would move the parent to another space.
//
// The Go client validates every item kref before it splits it (ValidateKref),
// as it did at a7f155e, so those krefs are refused before any RPC and never
// reach normalize_space_path. These tests pin that, and that a revision with
// thousands of digits is a refused revision rather than a failure of the
// lookup.

import (
	"context"
	"strings"
	"testing"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
)

func TestGetItemFromRevisionRefusesServerKrefsTheValidatorRefuses(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()
	for _, itemKref := range []string{
		"kref://p/s /x.k",
		"kref://p/s\t/x.k",
		"kref://p/s /x.k",
		"kref://p/s　/x.k",
		"kref://p/a/b /x.k",
		"kref://p//x.k",
		"kref://p/s//x.k",
		"kref://p /s/x.k",
	} {
		fake.takeGetItems()
		_, err := client.GetItemFromRevision(ctx, itemKref+"?r=3")
		if !isKrefValidation(err) {
			t.Errorf("%q: err=%v, want a KrefValidationError", itemKref, err)
		}
		if sent := fake.takeGetItems(); len(sent) != 0 {
			t.Errorf("%q: sent %v, want no request", itemKref, sent)
		}
	}
}

func TestAHugeRevisionIsRefusedWithoutBreakingTheLookup(t *testing.T) {
	huge := strings.Repeat("1", 5000)

	parts := kumiho.ParseKref("kref://p/s/x.k?r=" + huge)
	if parts.ErrorClass != kumiho.KrefErrRevisionNumber || parts.Revision != nil {
		t.Errorf("ErrorClass=%q Revision=%v, want revision_number and no revision", parts.ErrorClass, parts.Revision)
	}
	parent, name, kind, err := parts.GetItemTuple()
	if err != nil || parent != "/p/s" || name != "x" || kind != "k" {
		t.Errorf("GetItemTuple = %q %q %q %v, want /p/s x k", parent, name, kind, err)
	}

	fake, client := startFake(t)
	ctx := context.Background()
	if _, err := client.GetItemByKref(ctx, "kref://p/s/x.k?r="+huge); err != nil {
		t.Fatal(err)
	}
	if _, err := client.GetBundleByKref(ctx, "kref://p/s/x.bundle?r="+huge); err != nil {
		t.Fatal(err)
	}
	sent := fake.takeGetItems()
	want := []vectorTuple{{"/p/s", "x", "k"}, {"/p/s", "x", "bundle"}}
	if len(sent) != len(want) || sent[0] != want[0] || sent[1] != want[1] {
		t.Errorf("sent %v, want %v", sent, want)
	}
}

func TestParseKrefNeverPanicsOnOddInput(t *testing.T) {
	for _, uri := range []string{
		"",
		"kref://",
		"\x00",
		"kref://p/s/x.k?r=",
		"kref://" + strings.Repeat("a/", 5000) + "x.k",
		"kref://p/s/x.k?" + strings.Repeat("&", 3000),
		"kref://　　",
		"kref://p/s/\xff.k",
	} {
		parts := kumiho.ParseKref(uri)
		if parts.URI != uri {
			t.Errorf("%q: URI = %q", uri, parts.URI)
		}
		_, _, _, _ = parts.GetItemTuple()
	}
}
