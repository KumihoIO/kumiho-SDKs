//! Error types for the Kumiho SDK.

/// Result alias used throughout the crate.
pub type Result<T> = std::result::Result<T, Error>;

/// All errors surfaced by the Kumiho SDK.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    /// A kref URI failed validation.
    #[error("invalid kref: {0}")]
    KrefValidation(String),

    /// An edge type failed validation.
    #[error("invalid edge type: {0}")]
    EdgeTypeValidation(String),

    /// `create_item` was called with a reserved item kind (e.g. "bundle");
    /// use `create_bundle` instead. Mirrors Python's `ReservedKindError`.
    #[error("item kind '{0}' is reserved; use create_bundle() instead")]
    ReservedKind(String),

    /// A caller-supplied argument was invalid (e.g. malformed kref shape).
    #[error("invalid argument: {0}")]
    InvalidArgument(String),

    /// The server returned a gRPC error status.
    #[error("grpc status: {0}")]
    Rpc(#[from] tonic::Status),

    /// The gRPC transport (channel/TLS) failed.
    #[error("transport: {0}")]
    Transport(#[from] tonic::transport::Error),

    /// Discovery / control-plane bootstrap failed.
    #[error("discovery: {0}")]
    Discovery(String),

    /// A local I/O error (credential/cache files).
    #[error("io: {0}")]
    Io(#[from] std::io::Error),

    /// Guardrails blocked project creation (e.g. max projects reached).
    #[error("project limit reached: {0}")]
    ProjectLimit(String),
}

impl Error {
    /// True when the underlying gRPC status was `NOT_FOUND`.
    pub fn is_not_found(&self) -> bool {
        matches!(self, Error::Rpc(s) if s.code() == tonic::Code::NotFound)
    }
}
