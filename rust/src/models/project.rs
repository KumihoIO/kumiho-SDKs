//! The [`Project`] domain object — top-level container for assets.

use crate::client::{Client, Page};
use crate::error::Result;
use crate::models::bundle::Bundle;
use crate::models::item::Item;
use crate::models::space::Space;
use crate::pb;
use std::collections::HashMap;

/// A Kumiho project: the root namespace for spaces and items.
#[derive(Clone)]
pub struct Project {
    /// Unique project id.
    pub project_id: String,
    /// URL-safe project name.
    pub name: String,
    /// Human-readable description.
    pub description: String,
    /// ISO-8601 creation timestamp, if set.
    pub created_at: Option<String>,
    /// ISO-8601 last-update timestamp, if set.
    pub updated_at: Option<String>,
    /// Whether the project is deprecated (soft-deleted).
    pub deprecated: bool,
    /// Whether anonymous read access is enabled.
    pub allow_public: bool,
    client: Client,
}

impl Project {
    pub(crate) fn from_pb(pb: pb::ProjectResponse, client: Client) -> Self {
        Project {
            project_id: pb.project_id,
            name: pb.name,
            description: pb.description,
            created_at: (!pb.created_at.is_empty()).then_some(pb.created_at),
            updated_at: (!pb.updated_at.is_empty()).then_some(pb.updated_at),
            deprecated: pb.deprecated,
            allow_public: pb.allow_public,
            client,
        }
    }

    fn base_parent(&self, parent_path: Option<&str>) -> String {
        parent_path.map(String::from).unwrap_or_else(|| format!("/{}", self.name))
    }

    /// Create a space (defaults to the project root).
    pub async fn create_space(&self, name: &str, parent_path: Option<&str>) -> Result<Space> {
        self.client.create_space(&self.base_parent(parent_path), name).await
    }

    /// Create an item (defaults to the project root).
    pub async fn create_item(
        &self,
        item_name: &str,
        kind: &str,
        parent_path: Option<&str>,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Item> {
        self.client.create_item(&self.base_parent(parent_path), item_name, kind, metadata).await
    }

    /// Create a bundle (defaults to the project root).
    pub async fn create_bundle(
        &self,
        bundle_name: &str,
        parent_path: Option<&str>,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Bundle> {
        self.client.create_bundle(&self.base_parent(parent_path), bundle_name, metadata).await
    }

    /// Get an item by name + kind (defaults to the project root).
    pub async fn get_item(&self, item_name: &str, kind: &str, parent_path: Option<&str>) -> Result<Item> {
        let base = self.base_parent(parent_path);
        let uri = format!("kref://{}/{}.{}", base.trim_matches('/'), item_name, kind);
        self.client.get_item_by_kref(&uri).await
    }

    /// Get a bundle by name (defaults to the project root).
    pub async fn get_bundle(&self, bundle_name: &str, parent_path: Option<&str>) -> Result<Bundle> {
        let base = self.base_parent(parent_path);
        let uri = format!("kref://{}/{}.bundle", base.trim_matches('/'), bundle_name);
        self.client.get_bundle_by_kref(&uri).await
    }

    /// Get a space by relative name or absolute `/path`.
    pub async fn get_space(&self, name: &str, parent_path: Option<&str>) -> Result<Space> {
        let path = if name.starts_with('/') {
            name.to_string()
        } else {
            format!("{}/{}", self.base_parent(parent_path).trim_end_matches('/'), name)
        };
        self.client.get_space(&path).await
    }

    /// List spaces in this project.
    pub async fn get_spaces(
        &self,
        parent_path: Option<&str>,
        recursive: bool,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<Space>> {
        self.client.get_child_spaces(&self.base_parent(parent_path), recursive, page_size, cursor).await
    }

    /// Search items within this project.
    pub async fn get_items(
        &self,
        name_filter: &str,
        kind_filter: &str,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<Item>> {
        self.client.item_search(&self.name, name_filter, kind_filter, page_size, cursor, false).await
    }

    /// Delete (force=true) or deprecate this project.
    pub async fn delete(&self, force: bool) -> Result<()> {
        self.client.delete_project(&self.project_id, force).await
    }

    /// Enable/disable anonymous read access.
    pub async fn set_public(&self, public: bool) -> Result<Project> {
        self.client.update_project(&self.project_id, Some(public), None).await
    }

    /// Update description and/or public flag.
    pub async fn update(&self, description: Option<String>, allow_public: Option<bool>) -> Result<Project> {
        self.client.update_project(&self.project_id, allow_public, description).await
    }
}

impl std::fmt::Debug for Project {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Project(id={:?}, name={:?})", self.project_id, self.name)
    }
}
