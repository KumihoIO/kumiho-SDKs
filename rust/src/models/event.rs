//! Real-time [`Event`]s and tier [`EventCapabilities`].

use crate::kref::Kref;
use crate::pb;
use std::collections::HashMap;

/// A real-time notification from the server.
#[derive(Debug, Clone)]
pub struct Event {
    /// Event type, e.g. `revision.created` (filterable with wildcards).
    pub routing_key: String,
    /// Reference to the affected object.
    pub kref: Kref,
    /// ISO-8601 timestamp, if set.
    pub timestamp: Option<String>,
    /// User id that triggered the event.
    pub author: String,
    /// Event-specific details (e.g. the tag name for `revision.tagged`).
    pub details: HashMap<String, String>,
    /// Opaque cursor for resumable streaming, if provided.
    pub cursor: Option<String>,
}

impl Event {
    pub(crate) fn from_pb(pb: pb::Event) -> Self {
        Event {
            routing_key: pb.routing_key,
            kref: Kref::from_pb(&pb.kref.unwrap_or_default()),
            timestamp: (!pb.timestamp.is_empty()).then_some(pb.timestamp),
            author: pb.author,
            details: pb.details,
            cursor: (!pb.cursor.is_empty()).then_some(pb.cursor),
        }
    }
}

/// Event-streaming capabilities for the current tenant tier.
#[derive(Debug, Clone)]
pub struct EventCapabilities {
    /// Whether past events can be replayed.
    pub supports_replay: bool,
    /// Whether cursor-based resume is supported.
    pub supports_cursor: bool,
    /// Whether consumer groups are supported (Enterprise).
    pub supports_consumer_groups: bool,
    /// Max retention in hours (0 = none, -1 = unlimited).
    pub max_retention_hours: i64,
    /// Max events buffered (0 = none, -1 = unlimited).
    pub max_buffer_size: i64,
    /// Tier name (free, creator, studio, enterprise).
    pub tier: String,
}
