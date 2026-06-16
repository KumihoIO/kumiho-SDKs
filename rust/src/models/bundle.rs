//! The [`Bundle`] domain object — a special item that aggregates other items.

use crate::client::Client;
use crate::error::{Error, Result};
use crate::kref::Kref;
use crate::models::item::Item;
use crate::models::revision::Revision;
use crate::pb;
use std::collections::HashMap;

/// Item kinds reserved by the system (cannot be created via `create_item`).
pub const RESERVED_KINDS: &[&str] = &["bundle"];

/// An item that is a member of a bundle.
#[derive(Debug, Clone)]
pub struct BundleMember {
    /// The member item's kref.
    pub item_kref: Kref,
    /// ISO-8601 timestamp the item was added.
    pub added_at: String,
    /// UUID of the user who added it.
    pub added_by: String,
    /// Display name of the user who added it.
    pub added_by_username: String,
    /// Bundle revision in which it was added.
    pub added_in_revision: i32,
}

/// One immutable entry in a bundle's membership-change history.
#[derive(Debug, Clone)]
pub struct BundleRevisionHistory {
    /// Bundle revision number for this change.
    pub revision_number: i32,
    /// `"CREATED"`, `"ADDED"`, or `"REMOVED"`.
    pub action: String,
    /// Item added/removed (`None` for the initial `CREATED`).
    pub member_item_kref: Option<Kref>,
    /// UUID of the user who made the change.
    pub author: String,
    /// Display name of the user who made the change.
    pub username: String,
    /// ISO-8601 timestamp of the change.
    pub created_at: String,
    /// Immutable metadata captured at change time.
    pub metadata: HashMap<String, String>,
}

/// A bundle: a reserved-kind item that groups other items with a full,
/// immutable audit trail of membership changes.
///
/// Derefs to its underlying [`Item`], so `bundle.kref`, `bundle.metadata`, etc.
/// are available directly.
#[derive(Clone, Debug)]
pub struct Bundle {
    item: Item,
}

impl Bundle {
    pub(crate) fn from_pb(pb: pb::ItemResponse, client: Client) -> Result<Self> {
        let item = Item::from_pb(pb, client);
        item.require_kind("bundle")?;
        Ok(Bundle { item })
    }

    /// Borrow the underlying [`Item`].
    pub fn as_item(&self) -> &Item {
        &self.item
    }

    /// Add an item to this bundle. Returns `(success, message, new_revision)`.
    pub async fn add_member(
        &self,
        member: &Item,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<(bool, String, Option<Revision>)> {
        if member.kref == self.item.kref {
            return Err(Error::InvalidArgument(
                "a bundle cannot contain itself".into(),
            ));
        }
        self.item
            .client
            .add_bundle_member(&self.item.kref, &member.kref, metadata)
            .await
    }

    /// Remove an item from this bundle. Returns `(success, message, new_revision)`.
    pub async fn remove_member(
        &self,
        member: &Item,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<(bool, String, Option<Revision>)> {
        self.item
            .client
            .remove_bundle_member(&self.item.kref, &member.kref, metadata)
            .await
    }

    /// Current members (or those at `revision_number`).
    pub async fn get_members(&self, revision_number: Option<i32>) -> Result<Vec<BundleMember>> {
        let (members, _, _) = self
            .item
            .client
            .get_bundle_members(&self.item.kref, revision_number)
            .await?;
        Ok(members)
    }

    /// The full, immutable membership-change history.
    pub async fn get_history(&self) -> Result<Vec<BundleRevisionHistory>> {
        self.item.client.get_bundle_history(&self.item.kref).await
    }
}

impl std::ops::Deref for Bundle {
    type Target = Item;
    fn deref(&self) -> &Item {
        &self.item
    }
}
