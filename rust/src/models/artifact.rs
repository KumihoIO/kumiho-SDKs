//! The [`Artifact`] domain object — a file reference within a revision.

use crate::client::Client;
use crate::error::Result;
use crate::kref::Kref;
use crate::models::item::Item;
use crate::models::project::Project;
use crate::models::revision::Revision;
use crate::models::space::Space;
use crate::pb;
use std::collections::HashMap;

/// A file reference (path/URI) within a revision. Kumiho tracks the location,
/// never the bytes ("BYO storage").
#[derive(Clone)]
pub struct Artifact {
    /// Unique reference for this artifact.
    pub kref: Kref,
    /// File path or URI.
    pub location: String,
    /// Parent revision reference.
    pub revision_kref: Kref,
    /// Parent item reference, if provided by the server.
    pub item_kref: Option<Kref>,
    /// ISO-8601 creation timestamp, if set.
    pub created_at: Option<String>,
    /// Creator user id.
    pub author: String,
    /// Custom metadata.
    pub metadata: HashMap<String, String>,
    /// Whether the artifact is deprecated.
    pub deprecated: bool,
    /// Creator display name.
    pub username: String,
    client: Client,
}

impl Artifact {
    pub(crate) fn from_pb(pb: pb::ArtifactResponse, client: Client) -> Self {
        let item_kref = pb
            .item_kref
            .as_ref()
            .and_then(|k| (!k.uri.is_empty()).then(|| Kref::from_pb(k)));
        Artifact {
            kref: Kref::from_pb(&pb.kref.unwrap_or_default()),
            location: pb.location,
            revision_kref: Kref::from_pb(&pb.revision_kref.unwrap_or_default()),
            item_kref,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            author: pb.author,
            metadata: pb.metadata,
            deprecated: pb.deprecated,
            username: pb.username,
            client,
        }
    }

    /// The artifact name (from the kref's `&a=`).
    pub fn name(&self) -> String {
        self.kref.artifact_name().unwrap_or_default()
    }

    /// Merge metadata into this artifact.
    pub async fn set_metadata(&self, metadata: HashMap<String, String>) -> Result<Artifact> {
        self.client
            .update_artifact_metadata(&self.kref, metadata)
            .await
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

    /// Delete this artifact.
    pub async fn delete(&self, force: bool) -> Result<()> {
        self.client.delete_artifact(&self.kref, force).await
    }

    /// Deprecate/restore this artifact.
    pub async fn set_deprecated(&self, status: bool) -> Result<()> {
        self.client.set_deprecated(&self.kref, status).await
    }

    /// Make this artifact the default for its revision.
    pub async fn set_default(&self) -> Result<()> {
        self.client
            .set_default_artifact(&self.revision_kref, &self.name())
            .await
    }

    /// Get the parent revision.
    pub async fn get_revision(&self) -> Result<Revision> {
        self.client.get_revision(self.revision_kref.uri()).await
    }

    /// Get the owning item.
    pub async fn get_item(&self) -> Result<Item> {
        match &self.item_kref {
            Some(k) => self.client.get_item_by_kref(k.uri()).await,
            None => self.get_revision().await?.get_item().await,
        }
    }

    /// Get the containing space.
    pub async fn get_space(&self) -> Result<Space> {
        self.get_item().await?.get_space().await
    }

    /// Get the containing project.
    pub async fn get_project(&self) -> Result<Project> {
        self.get_space().await?.get_project().await
    }
}

impl std::fmt::Debug for Artifact {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Artifact(kref={})", self.kref)
    }
}
