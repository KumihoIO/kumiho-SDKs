//! The [`Revision`] domain object — a specific iteration of an item.

use crate::client::Client;
use crate::edge::{Edge, EdgeDirection, ImpactedRevision, RevisionPath, TraversalResult};
use crate::error::Result;
use crate::kref::Kref;
use crate::models::artifact::Artifact;
use crate::models::item::Item;
use crate::models::project::Project;
use crate::models::space::Space;
use crate::pb;
use std::collections::HashMap;

/// A specific, immutable iteration of an item.
///
/// `tags` is a snapshot captured when the revision was fetched; call
/// [`Revision::refresh`] to re-read server-managed tags (e.g. `latest`).
#[derive(Clone)]
pub struct Revision {
    /// Unique reference for this revision.
    pub kref: Kref,
    /// Reference to the parent item.
    pub item_kref: Kref,
    /// Revision number (1-based).
    pub number: i32,
    /// Whether this is currently the latest revision.
    pub latest: bool,
    /// Tags snapshot.
    pub tags: Vec<String>,
    /// Custom metadata.
    pub metadata: HashMap<String, String>,
    /// ISO-8601 creation timestamp, if set.
    pub created_at: Option<String>,
    /// Creator user id.
    pub author: String,
    /// Whether the revision is deprecated.
    pub deprecated: bool,
    /// Whether the revision is published.
    pub published: bool,
    /// Creator display name.
    pub username: String,
    /// Default artifact name, if set.
    pub default_artifact: Option<String>,
    pub(crate) client: Client,
}

impl Revision {
    pub(crate) fn from_pb(pb: pb::RevisionResponse, client: Client) -> Self {
        Revision {
            kref: Kref::from_pb(&pb.kref.unwrap_or_default()),
            item_kref: Kref::from_pb(&pb.item_kref.unwrap_or_default()),
            number: pb.number,
            latest: pb.latest,
            tags: pb.tags,
            metadata: pb.metadata,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            author: pb.author,
            deprecated: pb.deprecated,
            published: pb.published,
            username: pb.username,
            default_artifact: pb.default_artifact.filter(|s| !s.is_empty()),
            client,
        }
    }

    /// Create an artifact on this revision.
    pub async fn create_artifact(&self, name: &str, location: &str, metadata: Option<HashMap<String, String>>) -> Result<Artifact> {
        self.client.create_artifact(&self.kref, name, location, metadata).await
    }

    /// Merge metadata into this revision.
    pub async fn set_metadata(&self, metadata: HashMap<String, String>) -> Result<Revision> {
        self.client.update_revision_metadata(&self.kref, metadata).await
    }

    /// Set a single metadata attribute.
    pub async fn set_attribute(&self, key: &str, value: &str) -> Result<bool> {
        self.client.set_attribute(&self.kref, key, value).await
    }

    /// Get a single metadata attribute.
    pub async fn get_attribute(&self, key: &str) -> Result<Option<String>> {
        self.client.get_attribute(&self.kref, key).await
    }

    /// Delete a single metadata attribute.
    pub async fn delete_attribute(&self, key: &str) -> Result<bool> {
        self.client.delete_attribute(&self.kref, key).await
    }

    /// Whether this revision currently has `tag` (server call).
    pub async fn has_tag(&self, tag: &str) -> Result<bool> {
        self.client.has_tag(&self.kref, tag).await
    }

    /// Apply a tag.
    pub async fn tag(&self, tag: &str) -> Result<()> {
        self.client.tag_revision(&self.kref, tag).await
    }

    /// Remove a tag.
    pub async fn untag(&self, tag: &str) -> Result<()> {
        self.client.untag_revision(&self.kref, tag).await
    }

    /// Whether this revision was ever tagged with `tag`.
    pub async fn was_tagged(&self, tag: &str) -> Result<bool> {
        self.client.was_tagged(&self.kref, tag).await
    }

    /// Get an artifact by name.
    pub async fn get_artifact(&self, name: &str) -> Result<Artifact> {
        self.client.get_artifact(&self.kref, name).await
    }

    /// Get all artifacts.
    pub async fn get_artifacts(&self) -> Result<Vec<Artifact>> {
        self.client.get_artifacts(&self.kref).await
    }

    /// Get the file locations of all artifacts.
    pub async fn get_locations(&self) -> Result<Vec<String>> {
        Ok(self.get_artifacts().await?.into_iter().map(|a| a.location).collect())
    }

    /// Get the parent item.
    pub async fn get_item(&self) -> Result<Item> {
        self.client.get_item_by_kref(self.item_kref.uri()).await
    }

    /// Get the containing space.
    pub async fn get_space(&self) -> Result<Space> {
        let space = self.item_kref.space();
        let path = if space.is_empty() {
            format!("/{}", self.item_kref.project())
        } else {
            format!("/{}/{}", self.item_kref.project(), space)
        };
        self.client.get_space(&path).await
    }

    /// Get the containing project.
    pub async fn get_project(&self) -> Result<Project> {
        self.get_space().await?.get_project().await
    }

    /// Re-read this revision from the server (returns a fresh copy).
    pub async fn refresh(&self) -> Result<Revision> {
        self.client.get_revision(self.kref.uri()).await
    }

    /// Set the default artifact (used when resolving without `&a=`).
    pub async fn set_default_artifact(&self, artifact_name: &str) -> Result<()> {
        self.client.set_default_artifact(&self.kref, artifact_name).await
    }

    /// Delete this revision.
    pub async fn delete(&self, force: bool) -> Result<()> {
        self.client.delete_revision(&self.kref, force).await
    }

    /// Deprecate/restore this revision.
    pub async fn set_deprecated(&self, status: bool) -> Result<()> {
        self.client.set_deprecated(&self.kref, status).await
    }

    /// Create an edge from this revision to `target`.
    pub async fn create_edge(&self, target: &Revision, edge_type: &str, metadata: Option<HashMap<String, String>>) -> Result<Edge> {
        self.client.create_edge(self, target, edge_type, metadata).await
    }

    /// Get edges for this revision.
    pub async fn get_edges(&self, edge_type_filter: Option<&str>, direction: EdgeDirection) -> Result<Vec<Edge>> {
        self.client.get_edges(&self.kref, edge_type_filter.unwrap_or(""), direction).await
    }

    /// Delete an edge from this revision to `target`.
    pub async fn delete_edge(&self, target: &Revision, edge_type: &str) -> Result<()> {
        self.client.delete_edge(&self.kref, &target.kref, edge_type).await
    }

    /// All transitive dependencies (outgoing edges).
    pub async fn get_all_dependencies(&self, edge_type_filter: Option<Vec<String>>, max_depth: i32, limit: i32) -> Result<TraversalResult> {
        self.client.traverse_edges(&self.kref, EdgeDirection::Outgoing, edge_type_filter, max_depth, limit, false).await
    }

    /// All transitive dependents (incoming edges).
    pub async fn get_all_dependents(&self, edge_type_filter: Option<Vec<String>>, max_depth: i32, limit: i32) -> Result<TraversalResult> {
        self.client.traverse_edges(&self.kref, EdgeDirection::Incoming, edge_type_filter, max_depth, limit, false).await
    }

    /// Shortest path from this revision to `target`, if one exists.
    pub async fn find_path_to(&self, target: &Revision, edge_type_filter: Option<Vec<String>>, max_depth: i32) -> Result<Option<RevisionPath>> {
        let result = self
            .client
            .find_shortest_path(&self.kref, &target.kref, edge_type_filter, max_depth, false)
            .await?;
        Ok(result.first_path().cloned())
    }

    /// Revisions impacted by changes to this revision.
    pub async fn analyze_impact(&self, edge_type_filter: Option<Vec<String>>, max_depth: i32, limit: i32) -> Result<Vec<ImpactedRevision>> {
        self.client.analyze_impact(&self.kref, edge_type_filter, max_depth, limit).await
    }
}

impl std::fmt::Debug for Revision {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Revision(number={}, kref={})", self.number, self.kref)
    }
}
