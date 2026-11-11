//! The versioned, read-only project manifest from the native database.

use serde::{de::IgnoredAny, Deserialize};

use crate::{Error, Result};

pub mod pb {
    tonic::include_proto!("kumiho.export.v1");
}

pub(crate) const MAX_DOCUMENT_BYTES: usize = 8 * 1024 * 1024;

/// A complete UTF-8 project export, ready to save as a JSON file.
#[derive(Clone, PartialEq, Eq)]
pub struct ProjectExport {
    pub project: String,
    pub snapshot_sequence: u64,
    pub document: String,
}

impl std::fmt::Debug for ProjectExport {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ProjectExport")
            .field("snapshot_sequence", &self.snapshot_sequence)
            .field("document_bytes", &self.document.len())
            .finish_non_exhaustive()
    }
}

#[derive(Deserialize)]
struct Project {
    name: String,
}

#[derive(Deserialize)]
struct Manifest {
    schema_version: u32,
    snapshot_sequence: String,
    project: Project,
    #[serde(rename = "spaces")]
    _spaces: Vec<IgnoredAny>,
    #[serde(rename = "assets")]
    _assets: Vec<IgnoredAny>,
    #[serde(rename = "revisions")]
    _revisions: Vec<IgnoredAny>,
    #[serde(rename = "dependencies")]
    _dependencies: Vec<IgnoredAny>,
    #[serde(rename = "artifacts")]
    _artifacts: Vec<IgnoredAny>,
}

pub(crate) fn read(project: &str, response: pb::ExportProjectResponse) -> Result<ProjectExport> {
    let invalid = || Error::Rpc(tonic::Status::data_loss("invalid project export response"));
    if response.schema_version != 1
        || response.project != project
        || response.document.len() > MAX_DOCUMENT_BYTES
    {
        return Err(invalid());
    }
    let document = String::from_utf8(response.document).map_err(|_| invalid())?;
    let manifest: Manifest = serde_json::from_str(&document).map_err(|_| invalid())?;
    if manifest.schema_version != response.schema_version || manifest.project.name != project {
        return Err(invalid());
    }
    let snapshot_sequence = manifest.snapshot_sequence.parse().map_err(|_| invalid())?;
    Ok(ProjectExport {
        project: response.project,
        snapshot_sequence,
        document,
    })
}
