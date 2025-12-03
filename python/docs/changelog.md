# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-12-03

### Added
- **Event streaming cursor support**: `Event.cursor` attribute for resumable streaming
- **EventCapabilities API**: `get_event_capabilities()` to query tier-based streaming features
- **New event_stream() parameters**:
  - `cursor`: Resume from last position (Creator+ tiers, Coming Soon)
  - `consumer_group`: Load-balanced consumption (Enterprise tier, Coming Soon)
  - `from_beginning`: Replay entire buffer (Creator+ tiers, Coming Soon)
- Tier capability documentation with Coming Soon markers

### Changed
- Updated event streaming documentation with tier matrix
- Event object now includes `cursor` attribute (None for Free tier)

### Notes
- Creator tier and above streaming features are planned but not yet deployed
- Free tier provides real-time streaming without persistence

## [0.3.0] - 2024-XX-XX

### Added
- Comprehensive Google-style docstrings for all public APIs
- Sphinx documentation with ReadTheDocs theme
- `get_artifact()` top-level function for fetching artifacts by Kref
- `get_artifact_by_kref()` method in Client class
- Type hints throughout the codebase

### Changed
- Updated `pyproject.toml` with full PyPI metadata
- Improved error messages with more context

### Fixed
- Kref parsing for artifact URIs with special characters

## [0.2.0] - 2024-XX-XX

### Added
- Event streaming support with `stream_events()`
- Link traversal for lineage tracking
- Batch operations for multiple artifacts

### Changed
- Switched to context-variable-based client management
- Improved connection pooling for gRPC channels

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Core entity classes: Project, Space, Item, Revision, Artifact, Edge
- Kref URI parsing and generation
- Discovery-based authentication
- CLI authentication tool (`kumiho-auth`)
