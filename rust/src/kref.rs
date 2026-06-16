//! Kumiho Reference (Kref) — a URI uniquely identifying any Kumiho object.
//!
//! Format: `kref://project/space/item.kind?r=REVISION&a=ARTIFACT`
//!
//! The validation rules here mirror the Python gold standard exactly so that
//! all SDKs accept and reject the same set of URIs.

use crate::pb;
use once_cell::sync::Lazy;
use regex::Regex;
use std::fmt;

/// Raised when a kref URI is malformed or contains a malicious pattern.
#[derive(Debug, Clone, thiserror::Error)]
#[error("{0}")]
pub struct KrefValidationError(pub String);

// Path segments may contain Unicode letters/numbers plus underscore, dots and
// hyphens. Python's `re` `\w` matches exactly `[\p{L}\p{N}_]`; the regex crate's
// `\w` differs (it also matches combining marks `\p{M}` and connector punctuation
// `\p{Pc}`, and uses `\p{Nd}` so it excludes other-numbers `\p{No}`), so we spell
// the class out to match the Python gold standard. Artifact ids stay ASCII because
// they are server-generated opaque identifiers. Path traversal (`..`) and control
// characters are rejected by explicit checks, not by this pattern.
static KREF_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"^kref://(/[\p{L}\p{N}_][\p{L}\p{N}_.\-]*(/[\p{L}\p{N}_][\p{L}\p{N}_.\-]*)*|[\p{L}\p{N}_][\p{L}\p{N}_.\-]*(/[\p{L}\p{N}_][\p{L}\p{N}_.\-]*)*)(\?r=\d+(&a=[a-zA-Z0-9._\-]+)?)?$",
    )
    .expect("kref regex is valid")
});

/// Validate a kref URI for security and correctness.
///
/// Checks the `kref://` scheme, rejects path traversal (`..`) and control
/// characters, and enforces the path/query grammar.
pub fn validate_kref(uri: &str) -> Result<(), KrefValidationError> {
    if uri.contains("..") {
        return Err(KrefValidationError(format!(
            "Invalid kref URI '{uri}': path traversal (..) not allowed"
        )));
    }
    if uri.chars().any(|c| (c as u32) < 32 || c == '\u{7f}') {
        return Err(KrefValidationError(format!(
            "Invalid kref URI '{uri}': control characters not allowed"
        )));
    }
    if !KREF_PATTERN.is_match(uri) {
        return Err(KrefValidationError(format!(
            "Invalid kref URI '{uri}': must be format kref://project/space/item.kind"
        )));
    }
    Ok(())
}

/// Returns `true` if `uri` is a valid kref, without allocating an error.
pub fn is_valid_kref(uri: &str) -> bool {
    validate_kref(uri).is_ok()
}

/// A validated Kumiho reference.
///
/// `Kref` is a thin wrapper around a `String`; it derefs to `str` and displays
/// as the underlying URI, so it can be used anywhere a string is expected.
#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct Kref(String);

impl Kref {
    /// Parse and validate a kref URI.
    pub fn new(uri: impl Into<String>) -> Result<Self, KrefValidationError> {
        let uri = uri.into();
        validate_kref(&uri)?;
        Ok(Kref(uri))
    }

    /// Wrap a string as a kref **without** validation.
    ///
    /// Use only for trusted, server-returned values (the server may emit krefs
    /// whose shape predates current client validation, e.g. Unicode ids).
    pub fn unchecked(uri: impl Into<String>) -> Self {
        Kref(uri.into())
    }

    /// Build a [`Kref`] from a protobuf `Kref` message (trusted, unvalidated).
    pub fn from_pb(pb: &pb::Kref) -> Self {
        Kref(pb.uri.clone())
    }

    /// Convert into a protobuf `Kref` message for gRPC requests.
    pub fn to_pb(&self) -> pb::Kref {
        pb::Kref { uri: self.0.clone() }
    }

    /// The full URI string.
    pub fn uri(&self) -> &str {
        &self.0
    }

    /// The path component (after `kref://`, before any `?` query).
    pub fn path(&self) -> &str {
        let after = self.0.split_once("://").map(|x| x.1).unwrap_or(&self.0);
        after.split('?').next().unwrap_or(after)
    }

    /// The project name (first path segment).
    pub fn project(&self) -> &str {
        let p = self.path();
        p.split_once('/').map(|x| x.0).unwrap_or(p)
    }

    /// The space path (segments between project and item), or `""` if none.
    pub fn space(&self) -> String {
        let p = self.path();
        let parts: Vec<&str> = p.split('/').collect();
        if parts.len() <= 2 {
            return String::new();
        }
        parts[1..parts.len() - 1].join("/")
    }

    /// The item name including kind (e.g. `hero.model`), or `""` if none.
    pub fn item_name(&self) -> &str {
        let p = self.path();
        match p.rsplit_once('/') {
            Some((_, last)) => last,
            None => "",
        }
    }

    /// The item kind (after the first `.` in the item name), or `""`.
    pub fn kind(&self) -> &str {
        let name = self.item_name();
        name.split_once('.').map(|x| x.1).unwrap_or("")
    }

    /// The revision number from `?r=`, defaulting to `1`.
    pub fn revision(&self) -> i32 {
        self.0
            .split_once("?r=")
            .and_then(|(_, rest)| {
                let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
                digits.parse().ok()
            })
            .unwrap_or(1)
    }

    /// The artifact name from `&a=`, if present.
    pub fn artifact_name(&self) -> Option<String> {
        self.0.split_once("&a=").map(|(_, rest)| {
            rest.chars().take_while(|&c| c != '&').collect()
        })
    }
}

impl fmt::Display for Kref {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::ops::Deref for Kref {
    type Target = str;
    fn deref(&self) -> &str {
        &self.0
    }
}

impl std::str::FromStr for Kref {
    type Err = KrefValidationError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Kref::new(s)
    }
}

impl From<Kref> for String {
    fn from(k: Kref) -> String {
        k.0
    }
}

impl PartialEq<str> for Kref {
    fn eq(&self, other: &str) -> bool {
        self.0 == other
    }
}
