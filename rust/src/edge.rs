//! Edges (typed relationships between revisions) and graph-traversal results.

use crate::client::Client;
use crate::error::Result;
use crate::kref::Kref;
use crate::models::revision::Revision;
use crate::pb;
use once_cell::sync::Lazy;
use regex::Regex;

/// Raised when an edge type is malformed.
#[derive(Debug, Clone, thiserror::Error)]
#[error("{0}")]
pub struct EdgeTypeValidationError(pub String);

// Must match the Rust server's validation: uppercase start, 1-50 chars.
static EDGE_TYPE_PATTERN: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^[A-Z][A-Z0-9_]{0,49}$").expect("edge type regex is valid"));

/// Validate an edge type (uppercase, `[A-Z0-9_]`, 1-50 chars).
///
/// Returns the named [`EdgeTypeValidationError`] (mirroring `validate_kref` and
/// the Python/Go SDKs); it converts to [`crate::Error`] via `?`.
pub fn validate_edge_type(edge_type: &str) -> std::result::Result<(), EdgeTypeValidationError> {
    if EDGE_TYPE_PATTERN.is_match(edge_type) {
        Ok(())
    } else {
        Err(EdgeTypeValidationError(format!(
            "Invalid edge_type '{edge_type}'. Must start with an uppercase letter, contain only \
             uppercase letters, digits, underscores, and be 1-50 chars."
        )))
    }
}

/// Returns `true` if `edge_type` is valid.
pub fn is_valid_edge_type(edge_type: &str) -> bool {
    EDGE_TYPE_PATTERN.is_match(edge_type)
}

/// Standard, semantically-meaningful edge types.
///
/// All are UPPERCASE as required by the Neo4j-backed graph.
#[non_exhaustive]
pub struct EdgeType;

impl EdgeType {
    /// Ownership / grouping relationship.
    pub const BELONGS_TO: &'static str = "BELONGS_TO";
    /// Source was generated/created from target.
    pub const CREATED_FROM: &'static str = "CREATED_FROM";
    /// Soft reference relationship.
    pub const REFERENCED: &'static str = "REFERENCED";
    /// Source requires target to function.
    pub const DEPENDS_ON: &'static str = "DEPENDS_ON";
    /// Source was derived/modified from target.
    pub const DERIVED_FROM: &'static str = "DERIVED_FROM";
    /// Source contains/includes target.
    pub const CONTAINS: &'static str = "CONTAINS";
    /// Source replaces/supersedes target (belief revision).
    pub const SUPERSEDES: &'static str = "SUPERSEDES";
}

/// Direction for edge queries and traversals.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum EdgeDirection {
    /// Edges where the queried revision is the source.
    #[default]
    Outgoing,
    /// Edges where the queried revision is the target.
    Incoming,
    /// Edges in either direction.
    Both,
}

impl EdgeDirection {
    pub(crate) fn as_pb(self) -> i32 {
        match self {
            EdgeDirection::Outgoing => pb::EdgeDirection::Outgoing as i32,
            EdgeDirection::Incoming => pb::EdgeDirection::Incoming as i32,
            EdgeDirection::Both => pb::EdgeDirection::Both as i32,
        }
    }
}

/// A directed, typed relationship between two revisions.
#[derive(Clone)]
pub struct Edge {
    /// Source revision reference.
    pub source_kref: Kref,
    /// Target revision reference.
    pub target_kref: Kref,
    /// Relationship type (see [`EdgeType`]).
    pub edge_type: String,
    /// Edge metadata.
    pub metadata: std::collections::HashMap<String, String>,
    /// Creation timestamp (ISO-8601), if set.
    pub created_at: Option<String>,
    /// Author user id.
    pub author: String,
    /// Author display name.
    pub username: String,
    client: Client,
}

impl Edge {
    pub(crate) fn from_pb(pb: pb::Edge, client: Client) -> Self {
        Edge {
            source_kref: Kref::from_pb(&pb.source_kref.unwrap_or_default()),
            target_kref: Kref::from_pb(&pb.target_kref.unwrap_or_default()),
            edge_type: pb.edge_type,
            metadata: pb.metadata,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            author: pb.author,
            username: pb.username,
            client,
        }
    }

    /// Delete this edge.
    pub async fn delete(&self) -> Result<()> {
        self.client
            .delete_edge(&self.source_kref, &self.target_kref, &self.edge_type)
            .await
    }
}

impl std::fmt::Debug for Edge {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Edge({} -> {} type={})",
            self.source_kref, self.target_kref, self.edge_type
        )
    }
}

/// A single hop in a traversal path.
#[derive(Debug, Clone)]
pub struct PathStep {
    /// Revision reached at this step.
    pub revision_kref: Kref,
    /// Relationship type used to reach it.
    pub edge_type: String,
    /// Distance from the origin (0 = origin).
    pub depth: i32,
}

/// A complete path between two revisions.
#[derive(Debug, Clone, Default)]
pub struct RevisionPath {
    /// Ordered steps in the path.
    pub steps: Vec<PathStep>,
    /// Total length of the path.
    pub total_depth: i32,
}

/// A revision impacted by changes to another revision.
#[derive(Debug, Clone)]
pub struct ImpactedRevision {
    /// The impacted revision.
    pub revision_kref: Kref,
    /// The item that owns the impacted revision.
    pub item_kref: Option<Kref>,
    /// Hops away from the analyzed revision.
    pub impact_depth: i32,
    /// Edge types along the impact chain.
    pub impact_path_types: Vec<String>,
}

/// Result of a transitive edge traversal.
pub struct TraversalResult {
    /// Flat list of discovered revision references.
    pub revision_krefs: Vec<Kref>,
    /// Path details (populated when `include_path` was requested).
    pub paths: Vec<RevisionPath>,
    /// All traversed edges.
    pub edges: Vec<Edge>,
    /// Total number of discovered revisions.
    pub total_count: i32,
    /// True if results were limited by depth/limit.
    pub truncated: bool,
    client: Client,
}

impl TraversalResult {
    pub(crate) fn new(
        revision_krefs: Vec<Kref>,
        paths: Vec<RevisionPath>,
        edges: Vec<Edge>,
        total_count: i32,
        truncated: bool,
        client: Client,
    ) -> Self {
        TraversalResult {
            revision_krefs,
            paths,
            edges,
            total_count,
            truncated,
            client,
        }
    }

    /// Fetch full [`Revision`] objects for every discovered revision.
    pub async fn get_revisions(&self) -> Result<Vec<Revision>> {
        let mut out = Vec::with_capacity(self.revision_krefs.len());
        for kref in &self.revision_krefs {
            out.push(self.client.get_revision(kref.uri()).await?);
        }
        Ok(out)
    }
}

/// Result of a shortest-path query.
#[derive(Debug, Clone)]
pub struct ShortestPathResult {
    /// One or more shortest paths.
    pub paths: Vec<RevisionPath>,
    /// Whether any path exists.
    pub path_exists: bool,
    /// Length of the shortest path(s).
    pub path_length: i32,
}

impl ShortestPathResult {
    /// The first (or only) shortest path, if any.
    pub fn first_path(&self) -> Option<&RevisionPath> {
        self.paths.first()
    }
}
