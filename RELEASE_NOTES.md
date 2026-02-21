# Kumiho Python SDK - Release Notes

## kumiho 0.9.6 (February 2026) - Belief Revision & Privacy Boundary 🛡️

This release closes the gap between the paper's formal model and the SDK's runtime behavior. Every change maps to a specific claim in *Graph-Native Cognitive Memory for AI Agents* (v16).

### ✨ New Features

**`SUPERSEDES` edge type** *(Paper §7.4, Definition 7.4)*:

- Exposed `kumiho.SUPERSEDES` as a first-class edge type constant.
- Completes the belief revision vocabulary: when a revision replaces another, the SDK can now express `(r_new, SUPERSEDES, r_old)` as required by Definition 7.4.
- Available in both the Python SDK (`kumiho.SUPERSEDES`) and Dream State's LLM relationship analysis.

```python
import kumiho

# Express that a new decision supersedes the prior one
new_rev.create_edge(old_rev, kumiho.SUPERSEDES)
```

### 🔒 Privacy & Security

**Credential rejection boundary** *(Paper §10.4.5)*:

- New `PIIRedactor.reject_credentials()` method blocks secrets from crossing the local→cloud boundary.
- The MCP `memory_store` tool now scans `user_text`, `assistant_text`, `summary`, and `title` fields before any cloud graph write.
- Detected patterns raise `CredentialDetectedError` with a clear message — the write is rejected, not silently redacted.
- Six credential pattern categories are detected:

| Pattern | Examples |
| --- | --- |
| AWS access keys | `AKIA...`, `ASIA...` |
| Bearer tokens | `Bearer eyJ...` |
| API keys | `sk-...`, `pk-...`, `rk-...` (20+ chars) |
| PEM private keys | `-----BEGIN RSA PRIVATE KEY-----` |
| GitHub tokens | `ghp_...`, `gho_...`, `ghs_...` |
| Generic secrets | `api_key="..."`, `password="..."` |

- The same gate is enforced in `MemoryManager.consolidate_session()` and `store_tool_execution()` — all write paths to the cloud graph are covered.

### 🧠 Dream State Consolidation *(Paper §9)*

**Configurable safety parameters**:

- `max_deprecation_ratio` (float, 0.1–0.9, default 0.5) — controls the circuit-breaker threshold per run. Previously hardcoded at 50%.
- `allow_published_deprecation` (bool, default `False`) — when enabled, the Dream State *can* deprecate published items, with a WARNING-level audit entry. Previously these were unconditionally protected.
- Both parameters are exposed via the `kumiho_memory_dream_state` MCP tool for agent-accessible tuning.

**`SUPERSEDES` in relationship analysis**:

- The Dream State LLM prompt now includes `SUPERSEDES` as a candidate relationship type alongside `DERIVED_FROM`, `REFERENCED`, and `DEPENDS_ON`.
- This enables automatic detection of supersession chains during offline consolidation.

### 🔧 Improvements

**Discovery User-Agent tracking**:

- Discovery HTTP requests now include `User-Agent: kumiho-python/{version}` for control-plane observability and debugging.

### 📦 Companion Release: kumiho-memory 0.2.0

This SDK release ships alongside `kumiho-memory` 0.2.0, which contains the runtime implementations referenced above:

- `kumiho_memory.privacy` module (`PIIRedactor`, `CredentialDetectedError`)
- Credential rejection gates in `MemoryManager`
- Configurable Dream State safety parameters
- Updated MCP tool schemas

### ✅ Paper Compliance Summary

| Paper Claim | Section | SDK Implementation | Status |
| --- | --- | --- | --- |
| Revision creates SUPERSEDES edge | §7.4, Def 7.4 | `kumiho.SUPERSEDES` edge type | ✅ |
| Secrets must not cross privacy boundary | §10.4.5 | `PIIRedactor.reject_credentials()` | ✅ |
| Dream State circuit breaker configurable | §9.3 | `max_deprecation_ratio` param | ✅ |
| Published protection override with audit | §9.3 | `allow_published_deprecation` param | ✅ |
| Dream State detects supersession | §9, §7.4 | SUPERSEDES in LLM assessment prompt | ✅ |

## kumiho 0.9.5 (February 2026) - API Token Bootstrap for Discovery 🔑

### ✨ New Behavior

**`auto_configure_from_discovery()` now supports API-token-first flows**:
- When `KUMIHO_AUTH_TOKEN` is explicitly set, the SDK now bootstraps discovery directly from that token.
- No cached `kumiho-auth login` credentials are required for this path.

### 🔧 Reliability Improvements

**Bootstrap and discovery token handling hardened**:
- Default-client bootstrap now prefers an explicit env token before attempting cached credential refresh.
- Discovery routing now supports control-plane JWT-first behavior with Firebase fallback when needed.

## kumiho 0.9.4 (February 2026) - Hybrid Search Mode + Kref Validation 🔍

### ✨ New Behavior

**MCP full-text search now reports search mode**:
- `kumiho_fulltext_search` responses now include `search_mode`.
- Reported values are `"fulltext"` or `"hybrid"` (when STUDIO+ vector-backed hybrid search is available).

### 🐛 Bug Fixes

**Kref validation accepts underscore-prefixed segments**:
- Updated Kref URI validation regex to allow `_` at the start of project/space path segments.
- Fixes false-negative validation for valid krefs containing underscore-prefixed segments.

### 📦 Proto Sync

- Synced generated protobufs to include `SearchResponse.search_mode`.

### ✅ Compatibility Notes

- `search_mode` in MCP search output depends on server support; it falls back to `"fulltext"` when unavailable.

## kumiho 0.9.2 (February 2026) - Batch Revision Fetch (Proto Sync) 📦

### ✨ New Features

- Added `batch_get_revisions` to fetch multiple revisions by revision krefs or item krefs + tag, with optional partial results.

## kumiho 0.9.1 (January 2026) - MCP Full-Text Search Tool 🔎

### ✨ New Features

**MCP full-text search tool**:
- Added `kumiho_fulltext_search` MCP tool for fuzzy search across items (Google-like search).
- Supports `context`, `kind`, and `include_deprecated` filters for scoping results.
- Optional deep search across revision tags/metadata and artifact names/metadata via `include_revision_metadata` and `include_artifact_metadata`.
- Results include relevance `score` and `matched_in`, with `limit` and `include_metadata` for output control.

## kumiho 0.9.0 (January 2026) - Full-Text Search 🔎

### ✨ New Features

**Full-text fuzzy search API**:
- Added `kumiho.search()` and `Client.search()` for Google-like fuzzy search across item names and kinds.
- Supports `context_filter`, `kind_filter`, and `min_score` to scope and tune relevance.
- Optional deep search across revision tags/metadata and artifact names/metadata via `include_revision_metadata` and `include_artifact_metadata`.
- Results include relevance score and `matched_in` source, with pagination via `page_size` and `cursor`.

### ✅ Compatibility Notes

- Requires a kumiho-server build that exposes the `Search` gRPC endpoint and full-text indexes.

## kumiho 0.8.6 (January 2026) - Kref Ergonomics for Artifacts 🔗

### ✨ New Behavior

**`get_artifact()` default artifact resolution**:
- `kumiho.get_artifact("kref://project/space/item.kind")` now resolves the *default artifact* on the latest revision.
- `kumiho.get_artifact("kref://project/space/item.kind?r=REV")` now resolves the *default artifact* on that specific revision.
- If no default artifact is set, the SDK raises a `ValueError` prompting the caller to supply an explicit `&a=name`.

### ✅ Compatibility Notes

- This workflow expects a `kumiho-server` that can return a revision when given an item kref (latest revision resolution).

## kumiho 0.8.5 (January 2026) - Revision Delete & System Tag Consistency 🏷️

### 🔧 Behavior Updates

**Server-authoritative `latest` on deletion**:
- Removed SDK-side logic that attempted to re-tag `latest` after deleting a revision.
- `Revision.delete(force=...)` now issues `DeleteRevision` and relies on the server to keep the system-managed `latest` tag consistent.

### 🧪 Tests

- Updated unit tests to assert the SDK does not call tag operations as part of revision deletion.

### ✅ Compatibility Notes

- For tag-based latest resolution (e.g. resolving with `tag="latest"`) after hard deletes, use with a `kumiho-server` version that re-points `latest` after deleting the latest-tagged revision.

## kumiho 0.8.4 (January 2026) - Item Metadata Fix & Packaging Cleanup 🧰

### 🐛 Bug Fixes

**Create Item with Metadata**:
- Fixed `AttributeError: to_pb` when calling `create_item(..., metadata=...)`.
- The SDK now correctly converts the returned protobuf Kref into a `kumiho.Kref` before calling `UpdateItemMetadata`.

### 📦 Packaging

**License & Distribution Metadata**:
- Updated README/package metadata to reflect MIT licensing.
- Ensured the wheel includes a license file.

## kumiho 0.8.3 (December 2025) - Authentication Resilience 🛡️

### 🐛 Bug Fixes

**Auto-refresh on JWKS Errors**:
- Fixed an issue where the client would fail with `UNAVAILABLE` status and "jwks fetch error" when the server rotated keys.
- The client now correctly identifies this specific error pattern and forces a token refresh, ensuring seamless connectivity during control plane updates.

## kumiho 0.8.2 (December 2025) - MCP Token Optimization 📉

### 🚀 Performance Improvements

**MCP Token Usage Reduction**:
- Optimized MCP tools to significantly reduce token consumption in LLM contexts.
- **New Tool**: `kumiho_get_provenance_summary` provides a lightweight summary of AI provenance (seed, model, prompt) without the full revision overhead.
- **Metadata Stripping**: `kumiho_search_items` and `kumiho_get_item_revisions` now default to `include_metadata=False`.
- Added `include_metadata` parameter to these tools for cases where full metadata is explicitly needed.
- Solves "Quota exceeded" errors when listing large directories or search results containing heavy ComfyUI workflows.

## kumiho 0.8.1 (December 2025) - MCP Multi-tenancy & Stability 🛠️

### 🐛 Bug Fixes

**MCP Context Propagation**:
- Fixed `EOF when reading a line` error in MCP tool handlers when running in non-interactive environments (like Cloud Run).
- Switched tool handlers to use `asyncio.to_thread` to ensure `contextvars` (like `kumiho.use_client`) are correctly propagated to the execution thread.
- This enables multi-tenant MCP support where tools are executed with the user's specific credentials.

**Non-interactive Bootstrapping**:
- Updated internal bootstrapping to default to `interactive=False`, preventing the SDK from attempting to prompt for credentials in server environments.

## kumiho 0.8.0 (December 2025) - Event Streaming Enhancements ⚡

### ✨ New Features

**Event Stream Timeouts**:
- Added `timeout` parameter to `event_stream()` and `Client.event_stream()`.
- Allows the gRPC stream to close gracefully after a specified duration.
- Essential for polling-based integrations (like n8n) and serverless environments.

```python
# Stream events for 30 seconds then stop
try:
    for event in kumiho.event_stream(routing_key_filter="revision.*", timeout=30):
        print(f"New revision: {event.kref}")
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        print("Polling window finished")
```

### 📦 API Changes

- `kumiho.event_stream()`: Added `timeout: Optional[float]` argument.
- `Client.event_stream()`: Added `timeout: Optional[float]` argument.

### 🛠️ Bug Fixes

- Fixed an issue where `event_stream` would hang indefinitely in certain network conditions.
- Improved cleanup of gRPC stream resources when the iterator is exhausted or timed out.

---

## kumiho 0.7.0 (December 2025) - Deprecation Support 🗑️

### ✨ New Features

**Deprecation Filtering**:
- Added `include_deprecated` parameter to `get_items()` and `item_search()` methods.
- Allows retrieving items that have been marked as deprecated (soft deleted/hidden).
- Default behavior remains to exclude deprecated items.

```python
# Search including deprecated items
items = client.item_search(
    context_filter="my-project",
    include_deprecated=True
)
```

### 📦 API Changes

- `Client.get_items()`: Added `include_deprecated` argument (default: `False`).
- `Client.item_search()`: Added `include_deprecated` argument (default: `False`).
- `Space.get_items()`: Added `include_deprecated` argument (default: `False`).
- Updated Protobuf definitions to match server version 0.7.0.

---

## kumiho 0.4.4 (December 2025) - Pagination & Search Improvements 🔍

### ✨ New Features

**Pagination Support**:
- Added pagination to item listing and search methods.
- New `PagedList` return type containing `next_cursor` and `total_count`.

```python
# Pagination in Project
page1 = project.get_items(page_size=10)
if page1.next_cursor:
    page2 = project.get_items(page_size=10, cursor=page1.next_cursor)
```

**Project Search**:
- Added `project.get_items()` method for searching items within a project context.
- Updated `project.get_items()` to support pagination.

### 📦 API Changes

- `Space.get_items()` now accepts `page_size` and `cursor`.
- `Project.get_items()` now accepts `page_size` and `cursor`.
- `Client.item_search()` and `Client.get_items()` now return `PagedList` when pagination is active.

---

## kumiho 0.4.3 (December 2025) - Stability & Performance 🚀

### ✨ New Features

- **Improved Connection Handling**: Better retry logic for transient network failures
- **Enhanced Error Messages**: More descriptive error messages for common failure scenarios

### 🐛 Bug Fixes

- Fixed race condition in concurrent revision creation
- Fixed memory leak in long-running sessions with many graph traversals
- Fixed edge case where `get_space()` returned incorrect path for root-level items

### 🔧 Improvements

- Reduced gRPC connection overhead by reusing channels
- Optimized batch operations for large artifact lists
- Improved type hints coverage across all public APIs

### 📦 Dependencies

- Updated `grpcio` to 1.60.0+
- Updated `protobuf` to 4.25.0+

---

## kumiho 0.4.2 (December 2025) - Item Properties & Kref Improvements 🎯

### ✨ New Features

**Item Class Properties**:
- `item.project` - Get the project name the item belongs to
- `item.space` - Get the space path the item belongs to

```python
import kumiho

# Get an item and access its project/space
item = kumiho.get_item("kref://my-project/models/characters/hero.model")
print(item.project)  # "my-project"
print(item.space)    # "models/characters"
print(item.kref)     # "kref://my-project/models/characters/hero.model"
```

**Kref Class Improvements**:
- `kref.get_project()` - Extract just the project name from a kref URI
- `kref.get_space()` - Now returns space path **without** the project prefix

```python
from kumiho import Kref

kref = Kref("kref://my-project/assets/textures/hero-diffuse.texture")
print(kref.get_project())  # "my-project"
print(kref.get_space())    # "assets/textures" (previously: "my-project/assets/textures")
```

### ⚠️ Breaking Changes

- **`Kref.get_space()` behavior changed**: Previously returned `project/space`, now returns just `space` without the project prefix. Use `kref.get_project()` to get the project separately.

### 📦 Updated Exports

`Item` class now has:
- `project` property → `str`
- `space` property → `str`

`Kref` class now has:
- `get_project()` method → `str`
- Updated `get_space()` method → `str` (space only, no project)

---

## kumiho 0.4.1 (December 2025) - Tenant Info & Bug Fixes 🔧

### ✨ New Features

**Tenant Information Functions**:
- `kumiho.get_tenant_info()` - Get full tenant info from discovery cache
- `kumiho.get_tenant_slug()` - Get URL-safe tenant identifier for project naming

```python
import kumiho

# Get full tenant info
info = kumiho.get_tenant_info()
print(info["tenant_id"])    # "22fac7c8-5daf-4ad6-9b7e-70606b1d0c92"
print(info["tenant_name"])  # "My Studio"
print(info["roles"])        # ["owner", "editor"]

# Get URL-safe slug for project naming
slug = kumiho.get_tenant_slug()  # "22fac7c8" (falls back to tenant_id prefix if name has special chars)
project_name = f"ComfyUI@{slug}"
```

### 🐛 Bug Fixes

- **Reduced Logging Verbosity**: Sensitive metadata no longer logged at INFO level
  - Changed gRPC interceptor logging from INFO to DEBUG
  - Metadata keys logged instead of full values

### 📦 New Exports

Added to `kumiho` module:
- `get_tenant_info(tenant_hint=None)` → `Dict` or `None`
- `get_tenant_slug(tenant_hint=None)` → `str` or `None`

---

## kumiho 0.4.0 (December 2025) - Package Restructuring 📦

### 🎯 Overview

This release restructures the Kumiho Python SDK into two separate PyPI packages for better modularity and independent versioning.

### 📦 Package Split

Starting with v0.4.0, Kumiho is distributed as **two separate packages**:

| Package | Version | Description | Install |
|---------|---------|-------------|---------|
| **kumiho** | 0.4.0 | Core SDK library | `pip install kumiho` |
| **kumiho-cli** | 1.0.0 | CLI tools & MCP server | `pip install kumiho-cli` |

### ⚠️ Breaking Changes

**Removed from `kumiho` package**:
- `kumiho-auth` CLI command (moved to `kumiho-cli` package)

**Migration**:
```bash
# Before (v0.3.0)
pip install kumiho
kumiho-auth login  # This worked

# After (v0.4.0)
pip install kumiho kumiho-cli
kumiho-cli login   # New command name

# Or install with CLI extra
pip install kumiho[cli]
kumiho-cli login
```

### ✨ What's New

- **Optional CLI Dependency**: Install `kumiho[cli]` to get both packages
- **Cleaner SDK**: Core SDK no longer includes CLI dependencies
- **Independent Versioning**: CLI tools can be updated without SDK changes

### 📦 Installation

```bash
# Core SDK only (for programmatic use)
pip install kumiho

# SDK + CLI tools (for interactive development)
pip install kumiho[cli]

# Or install separately
pip install kumiho kumiho-cli
```

### 🔧 Usage

**SDK (unchanged)**:
```python
import kumiho

# Auto-configure from cached credentials
kumiho.auto_configure_from_discovery()

# Create and manage assets
project = kumiho.create_project("my-project")
space = project.create_space("assets")
item = space.create_item("hero", "model")
```

**CLI (new package)**:
```bash
# Authentication
kumiho-cli login
kumiho-cli refresh
kumiho-cli whoami

# MCP Server (unchanged)
kumiho-mcp
```

### 📋 Requirements

- Python 3.10+
- `kumiho-cli` package for authentication (optional)

### 📚 Documentation

- **SDK Documentation**: [docs.kumiho.io/python](https://docs.kumiho.io/python)
- **CLI Documentation**: See `kumiho-cli` package README

### 🔗 Related Packages

- [kumiho-cli](https://pypi.org/project/kumiho-cli/) - CLI tools (v1.0.0)

---

## kumiho-cli 1.0.0 (December 2025) - Initial Release 🎉

### 🎯 Overview

First standalone release of Kumiho CLI tools, extracted from the main `kumiho` package for independent versioning and lighter dependencies.

### ✨ Features

**Authentication Commands**:
- `kumiho-cli login` - Interactive Firebase authentication
- `kumiho-cli refresh` - Refresh cached tokens
- `kumiho-cli whoami` - Display current user info

**MCP Server** (Model Context Protocol):
- `kumiho-mcp` - Start MCP server for AI assistants
- 39 tools for GitHub Copilot, Claude, Cursor integration
- Graph traversal and asset management capabilities

**Credential Management**:
- Secure storage in `~/.kumiho/kumiho_authentication.json`
- Automatic token refresh
- Firebase ID token + Control Plane JWT exchange
- Environment variable support

### 📦 Installation

```bash
# Standalone installation
pip install kumiho-cli

# Or with pipx (recommended for CLI tools)
pipx install kumiho-cli

# Or as part of kumiho SDK
pip install kumiho[cli]
```

### 🔧 Quick Start

```bash
# Login to Kumiho Cloud
kumiho-cli login

# Check authentication status
kumiho-cli whoami

# Refresh tokens
kumiho-cli refresh

# Start MCP server for AI assistants
kumiho-mcp
```

### 🌐 Cross-SDK Support

The `kumiho-cli` package provides authentication for **all Kumiho SDKs**:

**Python**:
```python
import kumiho
kumiho.auto_configure_from_discovery()  # Uses ~/.kumiho/ credentials
```

**C++**:
```cpp
auto client = kumiho::Client::createFromEnv();  // Reads ~/.kumiho/
```

**Dart**:
```dart
final client = await KumihoClient.fromEnv();  // Reads ~/.kumiho/
```

**FastAPI**:
```bash
export KUMIHO_TOKEN=$(kumiho-cli get-token)  # For deployment
```

### 📋 Requirements

- Python 3.8+ (lower requirement than SDK)
- `requests>=2.31.0` (lightweight dependencies)

### 🌐 Supported Platforms

- Windows
- macOS
- Linux

### � Security

- Credentials stored with `0600` permissions
- Supports environment variable overrides
- No credentials in code or version control

### 📚 Documentation

- **Full README**: [GitHub](https://github.com/kumihoclouds/kumiho-python/tree/main/kumiho-cli)
- **Environment Variables**: See README for `KUMIHO_*` variables

### 📄 License

Apache License 2.0

---

## Previous Releases

### v0.3.0 (November 2025)

- Initial development release
- Integrated authentication CLI
- MCP server support
- Graph traversal features

---

**Repository**: https://github.com/kumihoclouds/kumiho-python  
**Issues**: https://github.com/kumihoclouds/kumiho-python/issues
