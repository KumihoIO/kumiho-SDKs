//! The [`Item`] domain object — a versioned asset.

use crate::client::Client;
use crate::error::{Error, Result};
use crate::kref::Kref;
use crate::models::project::Project;
use crate::models::revision::Revision;
use crate::models::space::Space;
use crate::pb;
use std::collections::HashMap;

/// A versioned asset (model, texture, workflow, …) identified by a [`Kref`].
#[derive(Clone)]
pub struct Item {
    /// Unique reference for this item.
    pub kref: Kref,
    /// Full name including kind (e.g. `hero.model`).
    pub name: String,
    /// Base name (e.g. `hero`).
    pub item_name: String,
    /// Item kind (e.g. `model`).
    pub kind: String,
    /// ISO-8601 creation timestamp, if set.
    pub created_at: Option<String>,
    /// Creator user id.
    pub author: String,
    /// Custom metadata.
    pub metadata: HashMap<String, String>,
    /// Whether the item is deprecated.
    pub deprecated: bool,
    /// Creator display name.
    pub username: String,
    pub(crate) client: Client,
}

impl Item {
    pub(crate) fn from_pb(pb: pb::ItemResponse, client: Client) -> Self {
        let kref = Kref::from_pb(&pb.kref.unwrap_or_default());
        Item {
            kref,
            name: pb.name,
            item_name: pb.item_name,
            kind: pb.kind,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            author: pb.author,
            metadata: pb.metadata,
            deprecated: pb.deprecated,
            username: pb.username,
            client,
        }
    }

    /// Project name this item belongs to.
    pub fn project(&self) -> &str {
        self.kref.project()
    }

    /// Space path this item belongs to.
    pub fn space(&self) -> String {
        self.kref.space()
    }

    /// Create a new revision (`number = 0` auto-increments).
    pub async fn create_revision(
        &self,
        metadata: Option<HashMap<String, String>>,
        number: i32,
    ) -> Result<Revision> {
        self.client
            .create_revision(&self.kref, metadata, number, "")
            .await
    }

    /// List all revisions.
    pub async fn get_revisions(&self) -> Result<Vec<Revision>> {
        self.client.get_revisions(&self.kref).await
    }

    /// Get a revision by number.
    pub async fn get_revision(&self, number: i32) -> Result<Revision> {
        self.client
            .get_revision(&format!("{}?r={}", self.kref.uri(), number))
            .await
    }

    /// Get the latest revision, or `None` if the item has none.
    ///
    /// Mirrors Python's `Item.get_latest_revision`: prefer the revision flagged
    /// `latest`, otherwise fall back to the highest-numbered revision.
    pub async fn get_latest_revision(&self) -> Result<Option<Revision>> {
        let revisions = self.get_revisions().await?;
        if let Some(latest) = revisions.iter().find(|r| r.latest) {
            return Ok(Some(latest.clone()));
        }
        Ok(revisions.into_iter().max_by_key(|r| r.number))
    }

    /// Get the revision currently carrying `tag`, or `None`.
    pub async fn get_revision_by_tag(&self, tag: &str) -> Result<Option<Revision>> {
        match self
            .client
            .resolve_kref(self.kref.uri(), Some(tag.to_string()), None)
            .await
        {
            Ok(r) => Ok(Some(r)),
            Err(e) if e.is_not_found() => Ok(None),
            Err(e) => Err(e),
        }
    }

    /// Get the revision that held `tag` (or latest) at `time`.
    ///
    /// `time` may be `YYYYMMDDHHMM` or an RFC3339 timestamp.
    pub async fn get_revision_by_time(
        &self,
        time: &str,
        tag: Option<&str>,
    ) -> Result<Option<Revision>> {
        let time_str = if time.contains('T') {
            time.to_string()
        } else if time.chars().count() >= 12 {
            // Index by char (like Python's time[0:4]) so a non-ASCII time string
            // can never split a multi-byte boundary and panic.
            let c: Vec<char> = time.chars().collect();
            format!(
                "{}-{}-{}T{}:{}:59+00:00",
                c[0..4].iter().collect::<String>(),
                c[4..6].iter().collect::<String>(),
                c[6..8].iter().collect::<String>(),
                c[8..10].iter().collect::<String>(),
                c[10..12].iter().collect::<String>(),
            )
        } else {
            time.to_string()
        };
        match self
            .client
            .resolve_kref(self.kref.uri(), tag.map(String::from), Some(time_str))
            .await
        {
            Ok(r) => Ok(Some(r)),
            Err(e) if e.is_not_found() => Ok(None),
            Err(e) => Err(e),
        }
    }

    /// Peek the next revision number.
    pub async fn peek_next_revision(&self) -> Result<i32> {
        self.client.peek_next_revision(&self.kref).await
    }

    /// Get the containing space.
    pub async fn get_space(&self) -> Result<Space> {
        self.client.get_space(&self.space_path()).await
    }

    /// Get the containing project.
    pub async fn get_project(&self) -> Result<Project> {
        self.get_space().await?.get_project().await
    }

    fn space_path(&self) -> String {
        let space = self.kref.space();
        if space.is_empty() {
            format!("/{}", self.kref.project())
        } else {
            format!("/{}/{}", self.kref.project(), space)
        }
    }

    /// Merge metadata into this item.
    pub async fn set_metadata(&self, metadata: HashMap<String, String>) -> Result<Item> {
        self.client.update_item_metadata(&self.kref, metadata).await
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

    /// Delete this item (force=true to delete with revisions).
    pub async fn delete(&self, force: bool) -> Result<()> {
        self.client.delete_item(&self.kref, force).await
    }

    /// Deprecate/restore this item.
    pub async fn set_deprecated(&self, status: bool) -> Result<()> {
        self.client.set_deprecated(&self.kref, status).await
    }
}

impl std::fmt::Debug for Item {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Item(kref={})", self.kref)
    }
}

// Used by Bundle to surface a "not a bundle" style guard if needed.
impl Item {
    pub(crate) fn require_kind(&self, expected: &str) -> Result<()> {
        if self.kind != expected {
            return Err(Error::InvalidArgument(format!(
                "expected kind '{expected}', got '{}'",
                self.kind
            )));
        }
        Ok(())
    }
}
