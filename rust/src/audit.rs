//! Bounded, persisted native change audit. Unsupported servers return their original RPC error.
//! Cursors, attribution, coverage and absent historical request ids remain server-owned.
pub mod pb {
    tonic::include_proto!("kumiho.audit.v1");
}
pub use pb::{AuditPrincipal, ChangeAuditEntry, ChangeAuditPage, ListChangesRequest};
