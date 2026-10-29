//! The structured kref parser.
//!
//! [`parse_kref`] reads a kref once, with the grammar in `spec/kref/README.md`
//! that kumiho-db and every Kumiho SDK share, and returns a [`KrefParts`]. It
//! is the only place a kref string is cut into pieces for an item lookup: the
//! `GetItem` request comes from [`KrefParts::get_item_tuple`], and
//! [`crate::Kref::item_name`] and [`crate::Kref::kind`] read the same split.
//!
//! The parser never fails. A string the kumiho-db kernel refuses comes back
//! with [`KrefParts::error_class`] set and no reading. Whether a string is
//! *accepted* is a separate question, answered by [`crate::validate_kref`] and
//! not changed here: a kref the kernel refuses but this SDK accepts (`?r=0`, a
//! 33rd segment, the legacy `kref:///space` spelling) is still sent, and the
//! backend decides.

use crate::error::Error;
use once_cell::sync::Lazy;
use regex::Regex;

const SCHEME: &str = "kref://";
/// Longest base (scheme and query not counted), in UTF-8 bytes.
pub const MAX_KREF_BYTES: usize = 1024;
/// Most `/`-separated segments in a base.
pub const MAX_KREF_SEGMENTS: usize = 32;
/// Longest tag selector, in UTF-8 bytes.
pub const MAX_TAG_BYTES: usize = 1024;
/// Longest artifact selector, in bytes.
pub const MAX_ARTIFACT_NAME_BYTES: usize = 256;

// `\w` of the regex crate is the kernel's word class: Alphabetic | Mark |
// Decimal_Number | Connector_Punctuation | Join_Control.
static SEGMENT: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^\w[\w.\-]*$").expect("segment regex is valid"));

/// Why the kernel refuses a kref, in the order it checks.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KrefErrorClass {
    /// Not `kref://` (the scheme is case-sensitive).
    Scheme,
    /// A `#` or `%` outside a tag selector.
    FragmentOrPercent,
    /// A `#`, `%` or `&` inside a tag selector.
    TagReservedChar,
    /// The base breaks a path rule.
    Path,
    /// A query pair that is not `key=value`.
    QueryPair,
    /// A query key other than `r`, `t`, `a`.
    UnknownKey,
    /// A query key given twice.
    DuplicateKey,
    /// Both `r` and `t`.
    RAndT,
    /// An `r` that is not a positive u64 (or `latest`).
    RevisionNumber,
    /// A `t` that is not a valid tag.
    Tag,
    /// An `a` without `r`/`t`, or not a valid artifact name.
    Artifact,
}

impl KrefErrorClass {
    /// The corpus spelling, for example `"revision_number"`.
    pub fn as_str(self) -> &'static str {
        match self {
            KrefErrorClass::Scheme => "scheme",
            KrefErrorClass::FragmentOrPercent => "fragment_or_percent",
            KrefErrorClass::TagReservedChar => "tag_reserved_char",
            KrefErrorClass::Path => "path",
            KrefErrorClass::QueryPair => "query_pair",
            KrefErrorClass::UnknownKey => "unknown_key",
            KrefErrorClass::DuplicateKey => "duplicate_key",
            KrefErrorClass::RAndT => "r_and_t",
            KrefErrorClass::RevisionNumber => "revision_number",
            KrefErrorClass::Tag => "tag",
            KrefErrorClass::Artifact => "artifact",
        }
    }
}

/// A namespace a base can satisfy, in the order the kernel parser and the
/// resolver try them.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KrefShape {
    /// An item directly under the project: exactly two segments.
    RootItem,
    /// An item in a space: three or more segments.
    Item,
    /// A space: two or more segments.
    Space,
    /// A project: one segment.
    Project,
}

impl KrefShape {
    /// The corpus spelling, for example `"root_item"`.
    pub fn as_str(self) -> &'static str {
        match self {
            KrefShape::RootItem => "root_item",
            KrefShape::Item => "item",
            KrefShape::Space => "space",
            KrefShape::Project => "project",
        }
    }
}

/// A kref read once: the kernel's reading plus the textual split.
///
/// The kernel's reading (`error_class`, `base`, `shapes` and the fields below)
/// follows `spec/kref/README.md`. A kref the kernel refuses has `error_class`
/// set and no reading: `base` and every field are `None` and `shapes` is empty.
///
/// `item_name`, `kind` and `is_project_root_item` describe the *first* shape
/// the base satisfies; `item_name` and `kind` are `None` when that shape is a
/// space or a project.
///
/// The textual split (`path`, `parent`, `leaf`, `leaf_name`, `leaf_kind`) does
/// not depend on the kernel's verdict. [`KrefParts::get_item_tuple`] uses it,
/// so a kref this SDK passes through to the backend still yields its request.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct KrefParts {
    /// The string that was parsed.
    pub uri: String,
    /// Why the kernel refuses it, or `None` when it accepts.
    pub error_class: Option<KrefErrorClass>,
    /// The text between `kref://` and the first `?`.
    pub base: Option<String>,
    /// Every namespace the base satisfies, in resolver order.
    pub shapes: Vec<KrefShape>,
    /// The first segment.
    pub project: Option<String>,
    /// The spaces between the project and the item (or all of them for a space).
    pub space_path: Option<Vec<String>>,
    /// The item name: the leaf up to its last `.`.
    pub item_name: Option<String>,
    /// The kind: the leaf after its last `.`.
    pub kind: Option<String>,
    /// Whether the item sits directly under the project.
    pub is_project_root_item: Option<bool>,
    /// The revision number from `r=`.
    pub revision: Option<u64>,
    /// The tag from `t=` (`r=latest` reads as the tag `latest`).
    pub tag: Option<String>,
    /// The artifact name from `a=`.
    pub artifact: Option<String>,
    /// The text after the first `://` and before the first `?`.
    pub path: String,
    /// Everything before the last `/` of `path`.
    pub parent: Option<String>,
    /// Everything after the last `/` of `path`.
    pub leaf: Option<String>,
    /// The leaf up to its last `.`.
    pub leaf_name: Option<String>,
    /// The leaf after its last `.`.
    pub leaf_kind: Option<String>,
}

impl KrefParts {
    /// Whether the kumiho-db kernel accepts this kref.
    pub fn valid(&self) -> bool {
        self.error_class.is_none()
    }

    /// The `GetItem` request `(parent_path, item_name, kind)` for this kref.
    ///
    /// The parent path is `/` plus everything before the LAST `/` of the path,
    /// so it holds the project and every nested space. The leaf after it is
    /// split at its LAST `.`: item names may contain dots, kinds never do. The
    /// query is dropped.
    ///
    /// This is the one split used for every item lookup. It depends on the text
    /// only, never on the kernel's verdict.
    ///
    /// # Errors
    ///
    /// [`Error::InvalidArgument`] if the path has no `/` or its leaf has no
    /// `.`. A leaf without a dot (`kref://p/s.v1/x`) names a space, not an item.
    pub fn get_item_tuple(&self) -> Result<(String, String, String), Error> {
        let (Some(parent), Some(leaf)) = (&self.parent, &self.leaf) else {
            return Err(Error::InvalidArgument(format!(
                "invalid item kref: {}",
                self.uri
            )));
        };
        let (Some(name), Some(kind)) = (&self.leaf_name, &self.leaf_kind) else {
            return Err(Error::InvalidArgument(format!(
                "invalid item name.kind: {leaf}"
            )));
        };
        Ok((format!("/{parent}"), name.clone(), kind.clone()))
    }
}

/// The purely textual split of a kref: no grammar is applied.
pub(crate) struct Lexical<'a> {
    pub(crate) path: &'a str,
    pub(crate) parent: Option<&'a str>,
    pub(crate) leaf: Option<&'a str>,
    pub(crate) leaf_name: Option<&'a str>,
    pub(crate) leaf_kind: Option<&'a str>,
}

/// Split `uri` at the first `://`, the first `?`, the last `/` and the last `.`.
///
/// This is the one place a kref is cut into parent path, item name and kind. It
/// never fails: `leaf_name`/`leaf_kind` are `None` when the leaf has no `.`, and
/// `parent`/`leaf` are `None` when the path has no `/`.
pub(crate) fn lexical(uri: &str) -> Lexical<'_> {
    let after = uri.split_once("://").map(|x| x.1).unwrap_or(uri);
    let path = after.split('?').next().unwrap_or(after);
    let (parent, leaf) = match path.rsplit_once('/') {
        Some((parent, leaf)) => (Some(parent), Some(leaf)),
        None => (None, None),
    };
    // Item names may contain dots; kinds never do.
    let (leaf_name, leaf_kind) = match leaf.and_then(|l| l.rsplit_once('.')) {
        Some((name, kind)) => (Some(name), Some(kind)),
        None => (None, None),
    };
    Lexical {
        path,
        parent,
        leaf,
        leaf_name,
        leaf_kind,
    }
}

/// Parse `uri` once into a [`KrefParts`].
///
/// Never fails: a string the kernel refuses comes back with
/// [`KrefParts::error_class`] set.
///
/// ```
/// let parts = kumiho::parse_kref("kref://p/a/b/my.file.k?r=2");
/// assert_eq!(
///     parts.get_item_tuple().unwrap(),
///     ("/p/a/b".to_string(), "my.file".to_string(), "k".to_string())
/// );
/// assert_eq!(parts.revision, Some(2));
/// ```
pub fn parse_kref(uri: &str) -> KrefParts {
    let lex = lexical(uri);
    let mut parts = KrefParts {
        uri: uri.to_string(),
        error_class: None,
        base: None,
        shapes: Vec::new(),
        project: None,
        space_path: None,
        item_name: None,
        kind: None,
        is_project_root_item: None,
        revision: None,
        tag: None,
        artifact: None,
        path: lex.path.to_string(),
        parent: lex.parent.map(str::to_string),
        leaf: lex.leaf.map(str::to_string),
        leaf_name: lex.leaf_name.map(str::to_string),
        leaf_kind: lex.leaf_kind.map(str::to_string),
    };
    match read(uri) {
        Ok(reading) => {
            parts.base = Some(reading.base);
            parts.shapes = reading.shapes;
            parts.project = Some(reading.project);
            parts.space_path = Some(reading.space_path);
            parts.item_name = reading.item_name;
            parts.kind = reading.kind;
            parts.is_project_root_item = Some(reading.is_project_root_item);
            parts.revision = reading.revision;
            parts.tag = reading.tag;
            parts.artifact = reading.artifact;
        }
        Err(class) => parts.error_class = Some(class),
    }
    parts
}

struct Reading {
    base: String,
    shapes: Vec<KrefShape>,
    project: String,
    space_path: Vec<String>,
    item_name: Option<String>,
    kind: Option<String>,
    is_project_root_item: bool,
    revision: Option<u64>,
    tag: Option<String>,
    artifact: Option<String>,
}

/// The kernel's verdict and reading of `uri`.
fn read(uri: &str) -> Result<Reading, KrefErrorClass> {
    let Some(rest) = uri.strip_prefix(SCHEME) else {
        return Err(KrefErrorClass::Scheme);
    };
    let (base, query) = match rest.split_once('?') {
        Some((base, query)) => (base, Some(query)),
        None => (rest, None),
    };
    if rest.contains('#') || rest.contains('%') {
        let in_tag = query.is_some_and(|q| {
            q.split('&').any(|pair| {
                pair.strip_prefix("t=")
                    .is_some_and(|v| v.contains('#') || v.contains('%'))
            })
        });
        return Err(if in_tag {
            KrefErrorClass::TagReservedChar
        } else {
            KrefErrorClass::FragmentOrPercent
        });
    }
    let shapes = path_shapes(base);
    if shapes.is_empty() {
        return Err(KrefErrorClass::Path);
    }
    let (revision, tag, artifact) = match query {
        Some(query) => read_query(query)?,
        None => (None, None, None),
    };

    let segments: Vec<&str> = base.split('/').collect();
    let mut reading = Reading {
        base: base.to_string(),
        shapes: shapes.clone(),
        project: segments[0].to_string(),
        space_path: Vec::new(),
        item_name: None,
        kind: None,
        is_project_root_item: false,
        revision,
        tag,
        artifact,
    };
    match shapes[0] {
        KrefShape::RootItem | KrefShape::Item => {
            let (name, kind) = segments[segments.len() - 1]
                .rsplit_once('.')
                .expect("an item shape has a '.' in its leaf");
            reading.space_path = segments[1..segments.len() - 1]
                .iter()
                .map(|s| s.to_string())
                .collect();
            reading.item_name = Some(name.to_string());
            reading.kind = Some(kind.to_string());
            reading.is_project_root_item = shapes[0] == KrefShape::RootItem;
        }
        KrefShape::Space => {
            reading.space_path = segments[1..].iter().map(|s| s.to_string()).collect();
        }
        KrefShape::Project => {}
    }
    Ok(reading)
}

fn has_control(text: &str) -> bool {
    text.chars().any(char::is_control)
}

/// Every namespace whose path rule `base` satisfies, in resolver order.
fn path_shapes(base: &str) -> Vec<KrefShape> {
    if base.is_empty() || base.len() > MAX_KREF_BYTES || base.contains("..") || has_control(base) {
        return Vec::new();
    }
    let segments: Vec<&str> = base.split('/').collect();
    if segments.len() > MAX_KREF_SEGMENTS || !segments.iter().all(|s| SEGMENT.is_match(s)) {
        return Vec::new();
    }
    let names_an_item = segments[segments.len() - 1]
        .rsplit_once('.')
        .is_some_and(|(name, kind)| !name.is_empty() && !kind.is_empty());
    let count = segments.len();
    let mut shapes = Vec::new();
    if count == 2 && names_an_item {
        shapes.push(KrefShape::RootItem);
    }
    if count >= 3 && names_an_item {
        shapes.push(KrefShape::Item);
    }
    if count >= 2 {
        shapes.push(KrefShape::Space);
    }
    if count == 1 {
        shapes.push(KrefShape::Project);
    }
    shapes
}

fn valid_tag(text: &str) -> bool {
    !text.is_empty()
        && text.len() <= MAX_TAG_BYTES
        && !text.contains('"')
        && !text.contains('\\')
        && !has_control(text)
}

fn valid_artifact_name(text: &str) -> bool {
    !text.is_empty()
        && text.len() <= MAX_ARTIFACT_NAME_BYTES
        && text
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'.' | b'_' | b'-'))
}

/// A revision number: ASCII digits, no leading zero, 1..=u64::MAX.
fn read_revision(text: &str) -> Option<u64> {
    if text.is_empty() || !text.bytes().all(|b| b.is_ascii_digit()) || text.starts_with('0') {
        return None;
    }
    text.parse::<u64>().ok().filter(|n| *n >= 1)
}

type Selectors = (Option<u64>, Option<String>, Option<String>);

/// The `r`, `t` and `a` selectors of the text after `?`.
fn read_query(query: &str) -> Result<Selectors, KrefErrorClass> {
    let (mut r, mut t, mut a): (Option<&str>, Option<&str>, Option<&str>) = (None, None, None);
    for pair in query.split('&') {
        let Some((key, value)) = pair.split_once('=') else {
            // A tag holding '&' leaves a pair without '=' behind.
            return Err(if t.is_some() {
                KrefErrorClass::TagReservedChar
            } else {
                KrefErrorClass::QueryPair
            });
        };
        let slot = match key {
            "r" => &mut r,
            "t" => &mut t,
            "a" => &mut a,
            _ => return Err(KrefErrorClass::UnknownKey),
        };
        if slot.is_some() {
            return Err(KrefErrorClass::DuplicateKey);
        }
        *slot = Some(value);
    }
    if r.is_some() && t.is_some() {
        return Err(KrefErrorClass::RAndT);
    }
    let mut revision = None;
    let mut tag = None;
    if r == Some("latest") {
        tag = Some("latest".to_string());
    } else if let Some(r) = r {
        revision = Some(read_revision(r).ok_or(KrefErrorClass::RevisionNumber)?);
    } else if let Some(t) = t {
        if !valid_tag(t) {
            return Err(KrefErrorClass::Tag);
        }
        tag = Some(t.to_string());
    }
    let mut artifact = None;
    if let Some(a) = a {
        if (revision.is_none() && tag.is_none()) || !valid_artifact_name(a) {
            return Err(KrefErrorClass::Artifact);
        }
        artifact = Some(a.to_string());
    }
    Ok((revision, tag, artifact))
}
