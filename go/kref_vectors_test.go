package kumiho_test

// The shared kref conformance corpus (spec/kref/vectors.json), case by case.
//
// The corpus is the single source: it is read from the repository root at run
// time, never copied. Every one of its 133 cases goes through the structured
// parser, kumiho.ParseKref; these tests check the kernel verdict, the error
// class, every field of the reading, the GetItem tuple, the Kref accessors and
// that the validator accepts what it did before (decision 3 changes only
// Kref.Kind()).
//
// The requests the client sends for these cases are checked against the same
// corpus in integration_test.go, which has the fake server.

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
)

type vectorTuple struct {
	ParentPath string `json:"parent_path"`
	ItemName   string `json:"item_name"`
	Kind       string `json:"kind"`
}

// vectorRequest is a corpus request entry: a GetItem request, an error, or a
// "skipped" note.
type vectorRequest struct {
	RPC        *string `json:"rpc"`
	ParentPath string  `json:"parent_path"`
	ItemName   string  `json:"item_name"`
	Kind       string  `json:"kind"`
	Error      *string `json:"error"`
	Message    string  `json:"message"`
	Skipped    *string `json:"skipped"`
}

func (r vectorRequest) tuple() *vectorTuple {
	if r.RPC == nil {
		return nil
	}
	return &vectorTuple{r.ParentPath, r.ItemName, r.Kind}
}

type vectorEquivalence struct {
	Equivalent bool `json:"equivalent"`
}

type vectorCase struct {
	ID                string       `json:"id"`
	Input             string       `json:"input"`
	Valid             bool         `json:"valid"`
	ErrorClass        *string      `json:"error_class"`
	Base              *string      `json:"base"`
	Shapes            []string     `json:"shapes"`
	Project           *string      `json:"project"`
	SpacePath         []string     `json:"space_path"`
	ItemName          *string      `json:"item_name"`
	Kind              *string      `json:"kind"`
	IsProjectRootItem *bool        `json:"is_project_root_item"`
	Revision          *uint64      `json:"revision"`
	Tag               *string      `json:"tag"`
	Artifact          *string      `json:"artifact"`
	GetItemTuple      *vectorTuple `json:"get_item_tuple"`
	SDKCurrentAccepts bool         `json:"sdk_current_accepts"`
	SDKCurrentRequest struct {
		GetItemByKref          vectorRequest `json:"get_item_by_kref"`
		GetBundleByKrefRefetch vectorRequest `json:"get_bundle_by_kref_refetch"`
	} `json:"sdk_current_request"`
	SDKFixRequest struct {
		GetItemByKref          vectorRequest `json:"get_item_by_kref"`
		GetBundleByKrefRefetch vectorRequest `json:"get_bundle_by_kref_refetch"`
	} `json:"sdk_fix_request"`
	ServerEquivalentOldNew *struct {
		GetItemByKref          *vectorEquivalence `json:"get_item_by_kref"`
		GetBundleByKrefRefetch *vectorEquivalence `json:"get_bundle_by_kref_refetch"`
	} `json:"server_equivalent_old_new"`
	SDKCurrentAccessors   map[string]any `json:"sdk_current_accessors"`
	SDKFixAccessorChanges map[string]struct {
		Fix any `json:"fix"`
	} `json:"sdk_fix_accessor_changes"`
}

func loadVectors(t testing.TB) []vectorCase {
	t.Helper()
	path := filepath.Join("..", "spec", "kref", "vectors.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s: %v", path, err)
	}
	var doc struct {
		Schema string       `json:"schema"`
		Cases  []vectorCase `json:"cases"`
	}
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatalf("parse %s: %v", path, err)
	}
	if doc.Schema != "kumiho-kref-vectors/1" {
		t.Fatalf("schema = %q", doc.Schema)
	}
	return doc.Cases
}

func deref[T any](p *T) any {
	if p == nil {
		return nil
	}
	return *p
}

func TestKrefVectorsCorpusIsTheSharedOne(t *testing.T) {
	cases := loadVectors(t)
	if len(cases) != 133 {
		t.Fatalf("got %d cases, want 133", len(cases))
	}
	seen := map[string]bool{}
	for _, c := range cases {
		if seen[c.ID] {
			t.Errorf("duplicate case id %q", c.ID)
		}
		seen[c.ID] = true
	}
}

func TestKrefVectorsParseMatchesTheKernelReading(t *testing.T) {
	for _, c := range loadVectors(t) {
		t.Run(c.ID, func(t *testing.T) {
			p := kumiho.ParseKref(c.Input)
			if p.Valid() != c.Valid {
				t.Errorf("valid = %v, want %v", p.Valid(), c.Valid)
			}
			wantClass := ""
			if c.ErrorClass != nil {
				wantClass = *c.ErrorClass
			}
			if string(p.ErrorClass) != wantClass {
				t.Errorf("error_class = %q, want %q", p.ErrorClass, wantClass)
			}
			if !c.Valid {
				if p.Base != nil || p.Project != nil || len(p.Shapes) != 0 || p.SpacePath != nil ||
					p.ItemName != nil || p.Kind != nil || p.IsProjectRootItem != nil ||
					p.Revision != nil || p.Tag != nil || p.Artifact != nil {
					t.Errorf("a refused kref has no reading: %+v", p)
				}
				return
			}
			got := map[string]any{
				"base":                 deref(p.Base),
				"project":              deref(p.Project),
				"item_name":            deref(p.ItemName),
				"kind":                 deref(p.Kind),
				"is_project_root_item": deref(p.IsProjectRootItem),
				"revision":             deref(p.Revision),
				"tag":                  deref(p.Tag),
				"artifact":             deref(p.Artifact),
			}
			want := map[string]any{
				"base":                 deref(c.Base),
				"project":              deref(c.Project),
				"item_name":            deref(c.ItemName),
				"kind":                 deref(c.Kind),
				"is_project_root_item": deref(c.IsProjectRootItem),
				"revision":             deref(c.Revision),
				"tag":                  deref(c.Tag),
				"artifact":             deref(c.Artifact),
			}
			for field, w := range want {
				if got[field] != w {
					t.Errorf("%s = %v, want %v", field, got[field], w)
				}
			}
			shapes := make([]string, len(p.Shapes))
			for i, s := range p.Shapes {
				shapes[i] = string(s)
			}
			if !reflect.DeepEqual(shapes, c.Shapes) {
				t.Errorf("shapes = %v, want %v", shapes, c.Shapes)
			}
			if !reflect.DeepEqual(p.SpacePath, c.SpacePath) {
				t.Errorf("space_path = %#v, want %#v", p.SpacePath, c.SpacePath)
			}
		})
	}
}

func TestKrefVectorsGetItemTupleMatchesTheGrammar(t *testing.T) {
	checked := 0
	for _, c := range loadVectors(t) {
		if c.GetItemTuple == nil {
			continue
		}
		parent, name, kind, err := kumiho.ParseKref(c.Input).GetItemTuple()
		if err != nil {
			t.Errorf("%s: %v", c.ID, err)
			continue
		}
		if got := (vectorTuple{parent, name, kind}); got != *c.GetItemTuple {
			t.Errorf("%s: tuple = %+v, want %+v", c.ID, got, *c.GetItemTuple)
		}
		checked++
	}
	if checked != 55 {
		t.Errorf("checked %d tuples, want 55", checked)
	}
}

// validatorDiffersFromPython lists the cases where this package's own validator
// (unchanged by the parser) differs from Python's at a7f155e, which is what
// sdk_current_accepts records. Go's RE2 `\d` is ASCII-only, so it refuses the
// Unicode digit in `?r=٣` that Python accepts. The list is the baseline
// behavior of this package, pinned so the parser change cannot move it.
var validatorDiffersFromPython = map[string]bool{
	"r-unicode-digit": true,
}

func TestKrefVectorsValidationIsUnchanged(t *testing.T) {
	for _, c := range loadVectors(t) {
		want := c.SDKCurrentAccepts
		if validatorDiffersFromPython[c.ID] {
			want = !want
		}
		if got := kumiho.IsValidKref(c.Input); got != want {
			t.Errorf("%s: IsValidKref = %v, want %v", c.ID, got, want)
		}
		if _, err := kumiho.NewKref(c.Input); (err == nil) != want {
			t.Errorf("%s: NewKref error = %v, want accepted=%v", c.ID, err, want)
		}
	}
}

func TestKrefVectorsAccessorsMatchA7f155eExceptKind(t *testing.T) {
	checked := 0
	for _, c := range loadVectors(t) {
		k, err := kumiho.NewKref(c.Input)
		if err != nil {
			continue
		}
		want := map[string]any{}
		for name, v := range c.SDKCurrentAccessors {
			want[name] = v
		}
		for name, change := range c.SDKFixAccessorChanges {
			if name != "get_kind" {
				t.Errorf("%s: only get_kind may change, got %s", c.ID, name)
			}
			want[name] = change.Fix
		}
		got := map[string]any{
			"get_path":      k.Path(),
			"get_project":   k.Project(),
			"get_space":     k.Space(),
			"get_item_name": k.ItemName(),
			"get_kind":      k.Kind(),
		}
		for name, g := range got {
			if g != want[name] {
				t.Errorf("%s: %s = %q, want %q", c.ID, name, g, want[name])
			}
		}
		checked++
	}
	if checked != 59 {
		t.Errorf("checked %d accepted cases, want 59 (60 in Python, minus the Unicode digit)", checked)
	}
}

func TestKrefKindSplitsAtTheLastDot(t *testing.T) {
	for kref, want := range map[string]string{
		"kref://p/s/my.file.v2.k": "k",
		"kref://p/s/x.tar.gz":     "gz",
		"kref://p/s/x":            "",
	} {
		if got := kumiho.Kref(kref).Kind(); got != want {
			t.Errorf("Kind(%q) = %q, want %q", kref, got, want)
		}
	}
}
