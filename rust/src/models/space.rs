//! The [`Space`] domain object — a hierarchical container for items.

use crate::client::{Client, Page};
use crate::error::{Error, Result};
use crate::models::bundle::Bundle;
use crate::models::item::Item;
use crate::models::project::Project;
use crate::pb;
use std::collections::HashMap;

/// A hierarchical folder within a project.
#[derive(Clone)]
pub struct Space {
    /// Full path (e.g. `/project/assets`).
    pub path: String,
    /// Last path component.
    pub name: String,
    /// `"root"` for project-level, `"sub"` for nested.
    pub space_type: String,
    /// ISO-8601 creation timestamp, if set.
    pub created_at: Option<String>,
    /// Creator user id.
    pub author: String,
    /// Custom metadata.
    pub metadata: HashMap<String, String>,
    /// Creator display name.
    pub username: String,
    client: Client,
}

impl Space {
    pub(crate) fn from_pb(pb: pb::SpaceResponse, client: Client) -> Self {
        Space {
            path: pb.path,
            name: pb.name,
            space_type: pb.r#type,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            author: pb.author,
            metadata: pb.metadata,
            username: pb.username,
            client,
        }
    }

    /// Create a subspace.
    pub async fn create_space(&self, name: &str) -> Result<Space> {
        self.client.create_space(&self.path, name).await
    }

    /// Get a subspace by name.
    pub async fn get_space(&self, name: &str) -> Result<Space> {
        let path = format!("{}/{}", self.path.trim_end_matches('/'), name);
        self.client.get_space(&path).await
    }

    /// List child spaces.
    pub async fn get_spaces(
        &self,
        recursive: bool,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<Space>> {
        self.client
            .get_child_spaces(&self.path, recursive, page_size, cursor)
            .await
    }

    /// Create an item in this space.
    pub async fn create_item(&self, item_name: &str, kind: &str) -> Result<Item> {
        self.client
            .create_item(&self.path, item_name, kind, None)
            .await
    }

    /// Create a bundle in this space.
    pub async fn create_bundle(
        &self,
        bundle_name: &str,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Bundle> {
        self.client
            .create_bundle(&self.path, bundle_name, metadata)
            .await
    }

    /// List items in this space.
    pub async fn get_items(
        &self,
        item_name_filter: &str,
        kind_filter: &str,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<Item>> {
        self.client
            .get_items(
                &self.path,
                item_name_filter,
                kind_filter,
                page_size,
                cursor,
                false,
            )
            .await
    }

    /// Get an item by name + kind.
    pub async fn get_item(&self, item_name: &str, kind: &str) -> Result<Item> {
        self.client.get_item(&self.path, item_name, kind).await
    }

    /// Get a bundle by name.
    pub async fn get_bundle(&self, bundle_name: &str) -> Result<Bundle> {
        let uri = format!(
            "kref://{}/{}.bundle",
            self.path.trim_start_matches('/'),
            bundle_name
        );
        self.client.get_bundle_by_kref(&uri).await
    }

    /// Replace/merge this space's metadata.
    ///
    /// Spaces are addressed by raw path (not a `kref://` URI), so this bypasses
    /// kref validation, matching the Python SDK.
    pub async fn set_metadata(&self, metadata: HashMap<String, String>) -> Result<Space> {
        let kref = crate::Kref::unchecked(self.path.clone());
        self.client.update_space_metadata(&kref, metadata).await
    }

    /// Set a single metadata attribute.
    pub async fn set_attribute(&self, key: &str, value: &str) -> Result<bool> {
        let kref = crate::Kref::unchecked(self.path.clone());
        self.client.set_attribute(&kref, key, value).await
    }

    /// Get a single metadata attribute.
    pub async fn get_attribute(&self, key: &str) -> Result<Option<String>> {
        let kref = crate::Kref::unchecked(self.path.clone());
        self.client.get_attribute(&kref, key).await
    }

    /// Delete a single metadata attribute.
    pub async fn delete_attribute(&self, key: &str) -> Result<bool> {
        let kref = crate::Kref::unchecked(self.path.clone());
        self.client.delete_attribute(&kref, key).await
    }

    /// Delete this space (force=true to delete a non-empty space).
    pub async fn delete(&self, force: bool) -> Result<()> {
        self.client.delete_space(&self.path, force).await
    }

    /// Get the parent space, or `None` if this is a project-level root.
    pub async fn get_parent_space(&self) -> Result<Option<Space>> {
        if self.path == "/" {
            return Ok(None);
        }
        let parts: Vec<&str> = self.path.split('/').filter(|s| !s.is_empty()).collect();
        if parts.len() <= 1 {
            return Ok(None);
        }
        let parent_path = format!("/{}", parts[..parts.len() - 1].join("/"));
        Ok(Some(self.client.get_space(&parent_path).await?))
    }

    /// Get the owning project.
    pub async fn get_project(&self) -> Result<Project> {
        let project_name = self
            .path
            .split('/')
            .find(|s| !s.is_empty())
            .ok_or_else(|| Error::InvalidArgument("root space has no project".into()))?;
        self.client
            .get_project(project_name)
            .await?
            .ok_or_else(|| Error::InvalidArgument(format!("project '{project_name}' not found")))
    }
}

impl std::fmt::Debug for Space {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Space(path={:?})", self.path)
    }
}
