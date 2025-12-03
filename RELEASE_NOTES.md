# Kumiho Python SDK - Release Notes

## v0.3.0 (December 2025) - Initial Public Release 🎉

We're excited to announce the first public release of the **Kumiho Python SDK** — the official Python client for [Kumiho Cloud](https://kumiho.io), a graph-native creative and AI asset management platform.

### ✨ Highlights

- **First PyPI Release**: Install with `pip install kumiho`
- **Graph-Native Asset Management**: Built on Neo4j for powerful relationship tracking
- **MCP Server Integration**: AI assistant support for GitHub Copilot, Claude, Cursor, and more
- **Full Type Safety**: Complete type hints for IDE autocomplete and static analysis

### 🚀 Features

#### Core SDK
- **Project Management**: Create, list, and manage projects with multi-tenant support
- **Space Hierarchy**: Organize assets in hierarchical folder structures
- **Item Versioning**: Semantic versioning for creative assets with full revision history
- **Artifact Tracking**: Reference files on your local/NAS/on-prem storage (BYO Storage philosophy)
- **Kref URIs**: Universal URI-based addressing for any Kumiho entity
  ```
  kref://project/space/item.kind?r=revision&a=artifact
  ```

#### Graph Traversal & Lineage
- **Dependency Tracking**: Track what assets depend on each other
- **Impact Analysis**: Understand downstream effects of changes
- **Path Finding**: Find shortest paths between revisions
- **Edge Types**: `DEPENDS_ON`, `DERIVED_FROM`, `REFERENCED`, `CONTAINS`, `CREATED_FROM`

#### AI Lineage Tracking
- Track AI model training data provenance
- GenAI image/video output lineage
- Full dependency graphs for AI-generated assets

#### Event Streaming
- Real-time notifications for asset changes
- Routing key and kref glob filtering
- Tier-based capabilities (persistence, cursor-based resume)

#### Bundles
- Aggregate items into versioned collections
- Full audit trail with history tracking

#### Authentication
- Firebase authentication integration
- Built-in CLI: `kumiho-auth login`
- Automatic token refresh
- Credential caching at `~/.kumiho/`

#### MCP Server (Model Context Protocol)
- 39 tools for AI assistant integration
- Read, create, update, and delete operations
- Graph traversal capabilities
- Install with `pip install kumiho[mcp]`
- Run with `kumiho-mcp`

### 📦 Installation

```bash
# Standard installation
pip install kumiho

# With MCP server support
pip install kumiho[mcp]

# For development
pip install kumiho[dev]
```

### 🔧 Quick Start

```python
import kumiho

# Authenticate and configure
kumiho.auto_configure_from_discovery()

# Create a project
project = kumiho.create_project("my-vfx-project", "VFX assets for 2025 film")

# Create hierarchy
space = project.create_space("characters")
item = space.create_item("hero", "model")

# Create revision with metadata
revision = item.create_revision(metadata={"artist": "jane", "software": "maya-2024"})

# Attach file artifacts
revision.create_artifact("hero_model.fbx", "smb://studio-nas/projects/film/hero_model.fbx")

# Tag for approval workflow
revision.tag("approved")
```

### 📋 Requirements

- Python 3.10+
- gRPC and Protocol Buffers
- Firebase authentication (via `kumiho-auth` CLI)

### 🌐 Supported Platforms

- Windows
- macOS
- Linux

### 📚 Documentation

- **Full Documentation**: [docs.kumiho.io/python](https://docs.kumiho.io/python)
- **API Reference**: [docs.kumiho.io/python/api](https://docs.kumiho.io/python/api)
- **GitHub Repository**: [github.com/kumihoclouds/kumiho-python](https://github.com/kumihoclouds/kumiho-python)

### 🔗 Related SDKs

- [Kumiho C++ SDK](https://docs.kumiho.io/cpp)
- [Kumiho Dart SDK](https://docs.kumiho.io/dart)
- [Kumiho FastAPI](https://docs.kumiho.io/fastapi)

### 📄 License

Apache License 2.0

### 🙏 Acknowledgments

Thank you to the VFX and creative technology community for feedback and inspiration in building a graph-native asset management solution.

---

**Full Changelog**: https://github.com/kumihoclouds/kumiho-python/commits/v0.3.0
