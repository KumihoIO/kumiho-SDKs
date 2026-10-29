//! The shared kref conformance corpus (`spec/kref/vectors.json`), case by case.
//!
//! The corpus is the single source: it is read from the repository root at run
//! time, never copied. Every one of its 133 cases goes through the structured
//! parser, [`kumiho::parse_kref`], and this file checks the kernel verdict, the
//! `error_class`, every field of the reading, the `GetItem` tuple, and that the
//! Kref accessors and the validator behave as before (decision 3 changes only
//! `Kref::kind()`).
//!
//! The requests the client sends for these cases are checked against the same
//! corpus in `tests/integration.rs`, which has the mock server.

use kumiho::{is_valid_kref, parse_kref, Kref};
use serde_json::Value;

fn cases() -> Vec<Value> {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("spec")
        .join("kref")
        .join("vectors.json");
    let text = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
    let doc: Value = serde_json::from_str(&text).expect("vectors.json parses");
    assert_eq!(doc["schema"], "kumiho-kref-vectors/1");
    doc["cases"].as_array().expect("cases").clone()
}

fn id(case: &Value) -> &str {
    case["id"].as_str().unwrap()
}

fn input(case: &Value) -> &str {
    case["input"].as_str().unwrap()
}

fn strings(value: &Value) -> Option<Vec<String>> {
    value
        .as_array()
        .map(|a| a.iter().map(|s| s.as_str().unwrap().to_string()).collect())
}

#[test]
fn corpus_is_the_shared_one() {
    let cases = cases();
    assert_eq!(cases.len(), 133);
    let mut ids: Vec<&str> = cases.iter().map(id).collect();
    ids.sort_unstable();
    ids.dedup();
    assert_eq!(ids.len(), 133, "case ids are unique");
}

#[test]
fn parse_matches_the_kernel_reading() {
    let mut failures = Vec::new();
    for case in cases() {
        let parts = parse_kref(input(&case));
        let mut check = |field: &str, got: String, want: String| {
            if got != want {
                failures.push(format!("{} {field}: got {got}, want {want}", id(&case)));
            }
        };
        check(
            "valid",
            format!("{}", parts.valid()),
            format!("{}", case["valid"]),
        );
        check(
            "error_class",
            format!("{:?}", parts.error_class.map(|c| c.as_str())),
            format!("{:?}", case["error_class"].as_str()),
        );
        check(
            "base",
            format!("{:?}", parts.base),
            format!("{:?}", case["base"].as_str()),
        );
        check(
            "shapes",
            format!(
                "{:?}",
                parts.shapes.iter().map(|s| s.as_str()).collect::<Vec<_>>()
            ),
            format!("{:?}", strings(&case["shapes"]).unwrap()),
        );
        check(
            "project",
            format!("{:?}", parts.project),
            format!("{:?}", case["project"].as_str()),
        );
        check(
            "space_path",
            format!("{:?}", parts.space_path),
            format!("{:?}", strings(&case["space_path"])),
        );
        check(
            "item_name",
            format!("{:?}", parts.item_name),
            format!("{:?}", case["item_name"].as_str()),
        );
        check(
            "kind",
            format!("{:?}", parts.kind),
            format!("{:?}", case["kind"].as_str()),
        );
        check(
            "is_project_root_item",
            format!("{:?}", parts.is_project_root_item),
            format!("{:?}", case["is_project_root_item"].as_bool()),
        );
        check(
            "revision",
            format!("{:?}", parts.revision),
            format!("{:?}", case["revision"].as_u64()),
        );
        check(
            "tag",
            format!("{:?}", parts.tag),
            format!("{:?}", case["tag"].as_str()),
        );
        check(
            "artifact",
            format!("{:?}", parts.artifact),
            format!("{:?}", case["artifact"].as_str()),
        );
    }
    assert!(
        failures.is_empty(),
        "{} mismatches:\n{}",
        failures.len(),
        failures.join("\n")
    );
}

#[test]
fn get_item_tuple_matches_the_grammar() {
    let mut checked = 0;
    for case in cases() {
        let want = &case["get_item_tuple"];
        if want.is_null() {
            continue;
        }
        let got = parse_kref(input(&case))
            .get_item_tuple()
            .unwrap_or_else(|e| panic!("{}: {e}", id(&case)));
        assert_eq!(
            got,
            (
                want["parent_path"].as_str().unwrap().to_string(),
                want["item_name"].as_str().unwrap().to_string(),
                want["kind"].as_str().unwrap().to_string(),
            ),
            "{}",
            id(&case)
        );
        checked += 1;
    }
    assert_eq!(checked, 55);
}

/// Cases where this crate's own validator (unchanged by the parser) differs
/// from Python's at `a7f155e`, which is what `sdk_current_accepts` records:
/// Rust's `\d` is the regex crate's Unicode `Nd` like Python's, but the segment
/// class is spelled out as `\p{L}\p{N}_`, so it matches Python except for the
/// ids below. The list is the baseline behavior of this crate, pinned so the
/// parser change cannot move it.
const VALIDATOR_DIFFERS_FROM_PYTHON: &[&str] = &[];

#[test]
fn validation_is_unchanged() {
    for case in cases() {
        let want = case["sdk_current_accepts"].as_bool().unwrap();
        let expected = if VALIDATOR_DIFFERS_FROM_PYTHON.contains(&id(&case)) {
            !want
        } else {
            want
        };
        assert_eq!(is_valid_kref(input(&case)), expected, "{}", id(&case));
        assert_eq!(Kref::new(input(&case)).is_ok(), expected, "{}", id(&case));
    }
}

#[test]
fn accessors_match_a7f155e_except_kind() {
    let mut checked = 0;
    for case in cases() {
        let Ok(kref) = Kref::new(input(&case)) else {
            continue;
        };
        let mut want = case["sdk_current_accessors"].clone();
        if let Some(changes) = case["sdk_fix_accessor_changes"].as_object() {
            for (name, change) in changes {
                assert_eq!(name, "get_kind", "{}: only get_kind may change", id(&case));
                want[name] = change["fix"].clone();
            }
        }
        assert_eq!(
            kref.path(),
            want["get_path"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        assert_eq!(
            kref.project(),
            want["get_project"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        assert_eq!(
            kref.space(),
            want["get_space"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        assert_eq!(
            kref.item_name(),
            want["get_item_name"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        assert_eq!(
            kref.kind(),
            want["get_kind"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        checked += 1;
    }
    assert_eq!(checked, 60, "the corpus has 60 krefs this SDK accepts");
}

#[test]
fn kind_splits_at_the_last_dot() {
    assert_eq!(Kref::new("kref://p/s/my.file.v2.k").unwrap().kind(), "k");
    assert_eq!(Kref::new("kref://p/s/x.tar.gz").unwrap().kind(), "gz");
    assert_eq!(Kref::new("kref://p/s/x").unwrap().kind(), "");
}

#[test]
fn error_class_displays_as_its_corpus_spelling() {
    let mut seen = std::collections::BTreeSet::new();
    for case in cases() {
        let Some(class) = parse_kref(input(&case)).error_class else {
            continue;
        };
        assert_eq!(
            class.to_string(),
            case["error_class"].as_str().unwrap(),
            "{}",
            id(&case)
        );
        assert_eq!(format!("{class}"), class.as_str());
        seen.insert(class.to_string());
    }
    assert_eq!(seen.len(), 11, "the corpus exercises every error class");
}

#[test]
fn a_revision_past_u64_is_refused_without_a_panic() {
    for digits in [20, 21, 4300, 4301, 100_000] {
        let uri = format!("kref://p/s/x.k?r={}", "9".repeat(digits));
        let parts = parse_kref(&uri);
        assert_eq!(
            parts.error_class.map(|c| c.as_str()),
            Some("revision_number"),
            "{digits} digits"
        );
        assert_eq!(parts.revision, None);
        // The request comes from the textual split alone.
        assert_eq!(
            parts.get_item_tuple().unwrap(),
            ("/p/s".to_string(), "x".to_string(), "k".to_string())
        );
    }
    assert_eq!(
        parse_kref("kref://p/s/x.k?r=18446744073709551615").revision,
        Some(u64::MAX)
    );
    assert_eq!(
        parse_kref("kref://p/s/x.k?r=18446744073709551616").revision,
        None
    );
}

#[test]
fn parse_kref_never_panics_on_odd_input() {
    let long_path = format!("kref://{}x.k", "a/".repeat(5000));
    let many_amps = format!("kref://p/s/x.k?{}", "&".repeat(3000));
    for uri in [
        "",
        "kref://",
        "\u{0}",
        "kref://p/s/x.k?r=",
        long_path.as_str(),
        many_amps.as_str(),
        "kref://\u{3000}\u{3000}",
    ] {
        let parts = parse_kref(uri);
        assert_eq!(parts.uri, uri);
        let _ = parts.get_item_tuple();
    }
}
