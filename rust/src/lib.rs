//! # Kumiho Rust SDK
//!
//! Async Rust client for [Kumiho Cloud](https://kumiho.io) — a graph-native
//! creative & AI asset-management system. Kumiho tracks revisions,
//! relationships, and lineage without uploading your files ("BYO storage").
//!
//! This SDK mirrors the Python gold-standard SDK: a low-level [`Client`] that
//! wraps every gRPC method, plus fluent domain types ([`Project`], [`Space`],
//! [`Item`], [`Revision`], [`Artifact`], [`Edge`], [`Bundle`]).
//!
//! ## Quick start
//!
//! ```no_run
//! use kumiho::{Client, EdgeType};
//!
//! # async fn run() -> kumiho::Result<()> {
//! // Connect (auto-discovery from ~/.kumiho credentials, or explicit endpoint).
//! let client = Client::connect("https://us-central.kumiho.cloud").await?;
//!
//! let project = client.create_project("my-vfx-project", "VFX assets").await?;
//! let space = project.create_space("characters", None).await?;
//! let item = space.create_item("hero", "model").await?;
//!
//! let revision = item.create_revision(None, 0).await?;
//! revision.create_artifact("mesh", "/assets/hero.fbx", None).await?;
//! revision.tag("approved").await?;
//! # Ok(())
//! # }
//! ```
//!
//! ## Krefs
//!
//! A [`Kref`] is a URI uniquely identifying any object:
//! `kref://project/space/item.kind?r=REVISION&a=ARTIFACT`.

#![forbid(unsafe_code)]
// gRPC error types (tonic::Status / transport::Error) are intentionally large;
// boxing every Result would hurt ergonomics for little gain.
#![allow(clippy::result_large_err)]

/// Generated protobuf + gRPC types (`package kumiho`).
pub mod pb {
    #![allow(clippy::all)]
    #![allow(missing_docs)]
    tonic::include_proto!("kumiho");
}

mod client;
mod discovery;
mod edge;
mod error;
mod kref;
mod models;
mod token_loader;

pub use client::{Client, ClientBuilder, ScoredRevision, SearchResult};
pub use discovery::{DiscoveryError, DiscoveryRecord};
pub use edge::{
    is_valid_edge_type, validate_edge_type, Edge, EdgeDirection, EdgeType, EdgeTypeValidationError,
    ImpactedRevision, PathStep, RevisionPath, ShortestPathResult, TraversalResult,
};
pub use error::{Error, Result};
pub use kref::{is_valid_kref, validate_kref, Kref, KrefValidationError};
pub use models::artifact::Artifact;
pub use models::bundle::{Bundle, BundleMember, BundleRevisionHistory, RESERVED_KINDS};
pub use models::event::{Event, EventCapabilities};
pub use models::item::Item;
pub use models::project::Project;
pub use models::revision::Revision;
pub use models::space::Space;

/// Standard tag pointing at the newest revision of an item.
pub const LATEST_TAG: &str = "latest";
/// Standard tag marking a published / released revision.
pub const PUBLISHED_TAG: &str = "published";
