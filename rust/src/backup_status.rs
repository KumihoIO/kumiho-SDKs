//! The read-only backup observation from the connected native database.

use crate::{Error, Result};

pub mod pb {
    tonic::include_proto!("kumiho.backup.v1");
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BackupState {
    Unconfigured,
    Preparing,
    Healthy,
    Delayed,
    Unavailable,
}

/// The latest observation published by the database's archive runner.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BackupStatus {
    pub state: BackupState,
    /// The last successful checkpoint observed by the archive runner.
    pub last_checkpoint_ms: Option<u64>,
    /// Unix milliseconds at publication, which may be old when status is unavailable.
    pub observed_at_ms: Option<u64>,
}

pub(crate) fn read(response: pb::GetBackupStatusResponse) -> Result<BackupStatus> {
    let invalid = || Error::Rpc(tonic::Status::data_loss("invalid backup status response"));
    let state = match pb::BackupState::try_from(response.state).map_err(|_| invalid())? {
        pb::BackupState::Unspecified => return Err(invalid()),
        pb::BackupState::Unconfigured => BackupState::Unconfigured,
        pb::BackupState::Preparing => BackupState::Preparing,
        pb::BackupState::Healthy => BackupState::Healthy,
        pb::BackupState::Delayed => BackupState::Delayed,
        pb::BackupState::Unavailable => BackupState::Unavailable,
    };
    let observed_at_ms = response.observed_at_ms;
    let last_checkpoint_ms = response.last_checkpoint_ms;
    const MAX_TIMESTAMP_MS: u64 = 8_640_000_000_000_000;
    let timestamps_valid = observed_at_ms.map_or(true, |ms| (1..=MAX_TIMESTAMP_MS).contains(&ms))
        && last_checkpoint_ms.map_or(true, |ms| {
            ms > 0 && observed_at_ms.is_some_and(|seen| ms <= seen)
        });
    let shape_valid = match state {
        BackupState::Unconfigured => observed_at_ms.is_none() && last_checkpoint_ms.is_none(),
        BackupState::Unavailable => last_checkpoint_ms.is_none(),
        _ => observed_at_ms.is_some(),
    };
    if !timestamps_valid || !shape_valid {
        return Err(invalid());
    }
    Ok(BackupStatus {
        state,
        last_checkpoint_ms,
        observed_at_ms,
    })
}
