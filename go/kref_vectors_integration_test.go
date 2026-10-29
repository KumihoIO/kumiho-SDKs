package kumiho_test

// The shared kref conformance corpus (spec/kref/vectors.json): the GetItem
// requests the client sends, case by case, through the fake server.
//
// sdk_current_request is what the SDK sent at a7f155e; sdk_fix_request is what
// the structured parser makes of the same kref. A request may differ only where
// the corpus proves it server-equivalent, or where owner decision 2 refuses a
// leaf with no '.' before sending. Validation is unchanged, so a kref this
// SDK's validator refuses still never reaches the server.

import (
	"context"
	"errors"
	"strings"
	"testing"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
)

// refusedByDecision2: a leaf with no '.' where an item is required is refused.
var refusedByDecision2 = map[string]bool{"dotted-space-leaf-without-dot": true}

// bundleRefetchFixedByDecision1: a7f155e re-fetched a different node.
var bundleRefetchFixedByDecision1 = map[string]bool{
	"bundle-dotted-name":     true,
	"bundle-in-dotted-space": true,
}

// takeGetItems returns the GetItem requests the server saw and forgets them.
func (s *fakeServer) takeGetItems() []vectorTuple {
	s.mu.Lock()
	defer s.mu.Unlock()
	var out []vectorTuple
	for _, r := range s.getItemReqs {
		out = append(out, vectorTuple{r.GetParentPath(), r.GetItemName(), r.GetKind()})
	}
	s.getItemReqs = nil
	return out
}

// assertChangeAllowed: a request that differs from a7f155e's must be one the
// owner decisions allow.
func assertChangeAllowed(t *testing.T, c vectorCase, slot string, current, fixed vectorRequest) {
	t.Helper()
	cur, fix := current.tuple(), fixed.tuple()
	switch {
	case cur != nil && fix != nil && *cur == *fix:
		// byte-identical to a7f155e
	case cur != nil && fix != nil:
		equivalent := false
		if eq := c.ServerEquivalentOldNew; eq != nil {
			if slot == "get_item_by_kref" && eq.GetItemByKref != nil {
				equivalent = eq.GetItemByKref.Equivalent
			}
			if slot == "get_bundle_by_kref_refetch" && eq.GetBundleByKrefRefetch != nil {
				equivalent = eq.GetBundleByKrefRefetch.Equivalent
			}
		}
		if !equivalent && !(slot == "get_bundle_by_kref_refetch" && bundleRefetchFixedByDecision1[c.ID]) {
			t.Errorf("%s: %s changed %+v -> %+v but is not server-equivalent", c.ID, slot, *cur, *fix)
		}
	case cur != nil && fix == nil:
		if !refusedByDecision2[c.ID] {
			t.Errorf("%s: %s is newly refused", c.ID, slot)
		}
	case cur == nil && fix != nil:
		t.Errorf("%s: %s now sends where a7f155e raised", c.ID, slot)
	}
}

func isInvalidArgument(err error) bool {
	var iae *kumiho.InvalidArgumentError
	return errors.As(err, &iae)
}

func isKrefValidation(err error) bool {
	var kve *kumiho.KrefValidationError
	return errors.As(err, &kve)
}

func TestKrefVectorsGetItemByKrefRequests(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()
	sentCases := 0
	for _, c := range loadVectors(t) {
		fake.takeGetItems()
		_, err := client.GetItemByKref(ctx, c.Input)
		sent := fake.takeGetItems()

		if !kumiho.IsValidKref(c.Input) {
			// Validation is unchanged: still refused before any RPC.
			if !isKrefValidation(err) || len(sent) != 0 {
				t.Errorf("%s: err=%v sent=%v, want a validation error and no request", c.ID, err, sent)
			}
			continue
		}
		fixed := c.SDKFixRequest.GetItemByKref
		if want := fixed.tuple(); want != nil {
			if err != nil {
				t.Errorf("%s: %v", c.ID, err)
			} else if len(sent) != 1 || sent[0] != *want {
				t.Errorf("%s: sent %v, want [%+v]", c.ID, sent, *want)
			}
			sentCases++
		} else if !isInvalidArgument(err) || len(sent) != 0 {
			t.Errorf("%s: err=%v sent=%v, want InvalidArgumentError before sending", c.ID, err, sent)
		}
		assertChangeAllowed(t, c, "get_item_by_kref", c.SDKCurrentRequest.GetItemByKref, fixed)
	}
	if sentCases < 50 {
		t.Errorf("only %d requests were sent", sentCases)
	}
}

func TestKrefVectorsGetItemFromRevisionRequests(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()
	for _, c := range loadVectors(t) {
		// The fake's GetRevision names the part of the kref before '?' as the
		// item kref, so use item krefs without a query.
		if strings.Contains(c.Input, "?") || !kumiho.IsValidKref(c.Input) {
			continue
		}
		fake.takeGetItems()
		_, err := client.GetItemFromRevision(ctx, c.Input+"?r=3")
		sent := fake.takeGetItems()
		if want := c.SDKFixRequest.GetItemByKref.tuple(); want != nil {
			if err != nil {
				t.Errorf("%s: %v", c.ID, err)
			} else if len(sent) != 1 || sent[0] != *want {
				t.Errorf("%s: sent %v, want [%+v]", c.ID, sent, *want)
			}
		} else if !isInvalidArgument(err) || len(sent) != 0 {
			t.Errorf("%s: err=%v sent=%v, want InvalidArgumentError before sending", c.ID, err, sent)
		}
	}
}

func TestKrefVectorsGetBundleByKrefRequests(t *testing.T) {
	fake, client := startFake(t)
	ctx := context.Background()
	bundles := 0
	for _, c := range loadVectors(t) {
		if !kumiho.IsValidKref(c.Input) {
			continue
		}
		fake.takeGetItems()
		bundle, err := client.GetBundleByKref(ctx, c.Input)
		sent := fake.takeGetItems()
		lookup := c.SDKFixRequest.GetItemByKref.tuple()
		refetch := c.SDKFixRequest.GetBundleByKrefRefetch.tuple()
		if lookup != nil && refetch != nil {
			// A bundle: the bundle the kref names is the one fetched.
			if err != nil {
				t.Errorf("%s: %v", c.ID, err)
				continue
			}
			if len(sent) != 1 || sent[0] != *refetch {
				t.Errorf("%s: sent %v, want [%+v]", c.ID, sent, *refetch)
			}
			if bundle.ItemName != refetch.ItemName {
				t.Errorf("%s: bundle item name = %q, want %q", c.ID, bundle.ItemName, refetch.ItemName)
			}
			assertChangeAllowed(t, c, "get_bundle_by_kref_refetch",
				c.SDKCurrentRequest.GetBundleByKrefRefetch, c.SDKFixRequest.GetBundleByKrefRefetch)
			bundles++
		} else if !isInvalidArgument(err) || len(sent) != 0 {
			// Not a bundle, or no item at all: refused before sending.
			t.Errorf("%s: err=%v sent=%v, want InvalidArgumentError before sending", c.ID, err, sent)
		}
	}
	if bundles != 7 {
		t.Errorf("fetched %d bundle krefs, want the corpus's 7", bundles)
	}
}
