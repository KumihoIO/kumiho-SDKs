//! Kref parsing & validation tests — mirror the Python gold-standard suite,
//! including Unicode (Hangul) acceptance and unsafe-character rejection.

use kumiho::{is_valid_kref, validate_kref, EdgeType, Kref};

#[test]
fn parses_full_artifact_kref() {
    let k = Kref::new("kref://film-2024/characters/hero.model?r=3&a=mesh").unwrap();
    assert_eq!(k.project(), "film-2024");
    assert_eq!(k.space(), "characters");
    assert_eq!(k.item_name(), "hero.model");
    assert_eq!(k.kind(), "model");
    assert_eq!(k.revision(), 3);
    assert_eq!(k.artifact_name().as_deref(), Some("mesh"));
}

#[test]
fn nested_space_and_default_revision() {
    let k = Kref::new("kref://proj/models/characters/hero.model").unwrap();
    assert_eq!(k.space(), "models/characters");
    assert_eq!(k.revision(), 1); // default
    assert_eq!(k.artifact_name(), None);
}

#[test]
fn no_space_item_at_project_root() {
    let k = Kref::new("kref://proj/hero.model").unwrap();
    assert_eq!(k.project(), "proj");
    assert_eq!(k.space(), "");
    assert_eq!(k.item_name(), "hero.model");
    assert_eq!(k.kind(), "model");
}

#[test]
fn hangul_kref_is_valid() {
    let uri = "kref://CognitiveMemory/Skills/mg-char-이지수.skill";
    assert!(is_valid_kref(uri));
    validate_kref(uri).unwrap();
    let k = Kref::new(uri).unwrap();
    assert_eq!(k.item_name(), "mg-char-이지수.skill");
    assert_eq!(k.kind(), "skill");
}

#[test]
fn hangul_path_segments_are_valid() {
    let uri = "kref://프로젝트/공간/항목.kind";
    assert!(is_valid_kref(uri));
    assert_eq!(Kref::new(uri).unwrap().project(), "프로젝트");
}

#[test]
fn unicode_class_parity_with_python() {
    // \p{No} (e.g. ½ U+00BD) is a valid segment char, matching Python's \w (\p{N}).
    assert!(is_valid_kref("kref://proj/space/item\u{00BD}.kind"));
    // Connector punctuation other than '_' (e.g. ‿ U+203F) must be rejected,
    // matching Python which allows only letters, numbers and underscore.
    assert!(!is_valid_kref("kref://proj/space/a\u{203F}b.kind"));
}

#[test]
fn rejects_unsafe_characters() {
    let unsafe_uris = [
        "kref://project/../item.skill",      // path traversal
        "kref://project/space bad/item.skill", // space char
        "kref://project/space$/item.skill",  // disallowed symbol
        "kref://project/space\u{0}/item.skill", // NUL control char
    ];
    for uri in unsafe_uris {
        assert!(validate_kref(uri).is_err(), "should reject: {uri:?}");
        assert!(!is_valid_kref(uri));
    }
}

#[test]
fn rejects_missing_scheme() {
    assert!(Kref::new("project/space/item.kind").is_err());
}

#[test]
fn display_and_equality() {
    let k = Kref::new("kref://p/s/i.kind").unwrap();
    assert_eq!(k.to_string(), "kref://p/s/i.kind");
    assert_eq!(&*k, "kref://p/s/i.kind");
    assert!(k == *"kref://p/s/i.kind");
}

#[test]
fn unchecked_allows_raw_paths() {
    // Spaces are addressed by raw path; unchecked must not validate.
    let k = Kref::unchecked("/project/space");
    assert_eq!(k.uri(), "/project/space");
}

#[test]
fn edge_type_validation() {
    use kumiho::{is_valid_edge_type, validate_edge_type};
    assert!(is_valid_edge_type(EdgeType::DEPENDS_ON));
    assert!(validate_edge_type("CUSTOM_REL").is_ok());
    assert!(validate_edge_type("depends_on").is_err()); // lowercase
    assert!(validate_edge_type("1BAD").is_err()); // starts with digit
    assert!(validate_edge_type("").is_err());
}
