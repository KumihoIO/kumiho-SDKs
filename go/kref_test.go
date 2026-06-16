package kumiho

import "testing"

func TestParseFullArtifactKref(t *testing.T) {
	k, err := NewKref("kref://film-2024/characters/hero.model?r=3&a=mesh")
	if err != nil {
		t.Fatal(err)
	}
	checks := map[string]string{
		"project":   k.Project(),
		"space":     k.Space(),
		"item_name": k.ItemName(),
		"kind":      k.Kind(),
		"artifact":  k.ArtifactName(),
	}
	want := map[string]string{
		"project": "film-2024", "space": "characters", "item_name": "hero.model",
		"kind": "model", "artifact": "mesh",
	}
	for key, got := range checks {
		if got != want[key] {
			t.Errorf("%s = %q, want %q", key, got, want[key])
		}
	}
	if k.Revision() != 3 {
		t.Errorf("revision = %d, want 3", k.Revision())
	}
}

func TestNestedSpaceAndDefaults(t *testing.T) {
	k := Kref("kref://proj/models/characters/hero.model")
	if k.Space() != "models/characters" {
		t.Errorf("space = %q", k.Space())
	}
	if k.Revision() != 1 {
		t.Errorf("default revision = %d, want 1", k.Revision())
	}
	if k.ArtifactName() != "" {
		t.Errorf("artifact = %q, want empty", k.ArtifactName())
	}
}

func TestProjectRootItem(t *testing.T) {
	k := Kref("kref://proj/hero.model")
	if k.Project() != "proj" || k.Space() != "" || k.Kind() != "model" {
		t.Errorf("got project=%q space=%q kind=%q", k.Project(), k.Space(), k.Kind())
	}
}

func TestHangulKrefValid(t *testing.T) {
	uri := "kref://CognitiveMemory/Skills/mg-char-이지수.skill"
	if !IsValidKref(uri) {
		t.Fatalf("expected %q to be valid", uri)
	}
	k := Kref(uri)
	if k.ItemName() != "mg-char-이지수.skill" {
		t.Errorf("item_name = %q", k.ItemName())
	}
	if k.Kind() != "skill" {
		t.Errorf("kind = %q", k.Kind())
	}
}

func TestHangulPathSegments(t *testing.T) {
	uri := "kref://프로젝트/공간/항목.kind"
	if !IsValidKref(uri) {
		t.Fatalf("expected %q to be valid", uri)
	}
	if Kref(uri).Project() != "프로젝트" {
		t.Errorf("project = %q", Kref(uri).Project())
	}
}

func TestRejectsUnsafe(t *testing.T) {
	unsafe := []string{
		"kref://project/../item.skill",
		"kref://project/space bad/item.skill",
		"kref://project/space$/item.skill",
		"kref://project/space\x00/item.skill",
		"project/space/item.kind", // missing scheme
	}
	for _, uri := range unsafe {
		if err := ValidateKref(uri); err == nil {
			t.Errorf("expected %q to be rejected", uri)
		}
		if IsValidKref(uri) {
			t.Errorf("IsValidKref(%q) = true, want false", uri)
		}
	}
}

func TestEdgeTypeValidation(t *testing.T) {
	if !IsValidEdgeType(EdgeDependsOn) {
		t.Error("DEPENDS_ON should be valid")
	}
	if ValidateEdgeType("CUSTOM_REL") != nil {
		t.Error("CUSTOM_REL should be valid")
	}
	for _, bad := range []string{"depends_on", "1BAD", ""} {
		if ValidateEdgeType(bad) == nil {
			t.Errorf("expected %q to be rejected", bad)
		}
	}
}

func TestNewKrefRejectsInvalid(t *testing.T) {
	if _, err := NewKref("not-a-kref"); err == nil {
		t.Error("expected error for invalid kref")
	}
}
