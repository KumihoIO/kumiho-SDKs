//! Exact tenant aggregates from the connected native database: every number equals one snapshot
//! of the tenant, and the server refuses instead of answering with a partial number. Unsupported
//! servers return their original RPC error.
pub mod pb {
    tonic::include_proto!("kumiho.db.insight.v1");
}
pub use pb::{
    ActivityCount, AggregateBasis, ArtifactCoverage, GetTenantAggregatesRequest, Granularity,
    KindCount, ProjectAggregate, RecentRevision, TenantAggregates,
};

/// The server refuses an answer over 4 MiB; the margin covers the frame.
pub(crate) const MAX_RESPONSE_BYTES: usize = 4 * 1024 * 1024 + 1024;
