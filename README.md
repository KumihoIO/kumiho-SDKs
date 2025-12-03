# Kumiho Python SDK

[![PyPI version](https://img.shields.io/pypi/v/kumiho.svg)](https://pypi.org/project/kumiho/)
[![Python versions](https://img.shields.io/pypi/pyversions/kumiho.svg)](https://pypi.org/project/kumiho/)
[![Documentation Status](https://readthedocs.org/projects/kumiho/badge/?version=latest)](https://docs.kumiho.io/python/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python SDK for [Kumiho Cloud](https://kumiho.io) — a graph-native creative and AI asset management platform for VFX, animation, and AI-driven workflows.

## Features

- **Graph-Native Design**: Built on Neo4j for tracking asset relationships and lineage
- **Revision Control**: Semantic versioning for creative assets with full history
- **AI Lineage Tracking**: Track AI model training data / GenAI image, video output provenance and dependencies
- **BYO Storage**: Files stay on your local/NAS/on-prem storage — only metadata is in the cloud
- **Multi-Tenant SaaS**: Secure, region-aware multi-tenant architecture
- **Event Streaming**: Real-time notifications for asset changes with tier-based capabilities
- **Graph Traversal**: Powerful dependency analysis and impact assessment
- **Type-Safe**: Full type hints for IDE autocomplete and static analysis

## Installation

```bash
pip install kumiho
```

For development:

```bash
pip install kumiho[dev]
```

## Quick Start

### 1. Authenticate

Run the built-in CLI to cache your Firebase credentials:

```bash
kumiho-auth login
```

This stores credentials at `~/.kumiho/kumiho_authentication.json` and automatically refreshes tokens when needed.

### 2. Connect and Use

```python
import kumiho

# Auto-configure from cached credentials and discovery
kumiho.auto_configure_from_discovery()

# Create a project
project = kumiho.create_project(
    name="my-vfx-project",
    description="VFX assets for 2025 film"
)

# Create a space (organizational container)
space = project.create_space("characters")

# Create an item (versioned asset)
item = space.create_item(
    item_name="hero",
    kind="model"
)

# Create a revision with metadata
revision = item.create_revision(
    metadata={
        "artist": "jane",
        "software": "maya-2024",
        "notes": "Initial model with base topology"
    }
)

# Attach file artifacts (files stay on your storage)
artifact = revision.create_artifact(
    name="hero_model.fbx",
    location="smb://studio-nas/projects/film/hero_model.fbx"
)

# Tag the revision
revision.tag("approved")
```

## Core Concepts

### Entity Hierarchy

```
Project
  └── Space (organizational container)
        └── Item (versioned asset)
              └── Revision (immutable snapshot)
                    └── Artifact (file reference)
```

### Kref URIs

Kumiho uses URI-based references to address any entity:

```
kref://project/space/item.kind?r=revision&a=artifact
```

Examples:
```python
# Reference an item (latest revision)
item = kumiho.get_item("kref://my-project/characters/hero.model")

# Reference a specific revision
revision = kumiho.get_revision("kref://my-project/characters/hero.model?r=3")

# Reference a specific artifact
artifact = kumiho.get_artifact("kref://my-project/characters/hero.model?r=3&a=mesh.fbx")

# Reference by tag
published = kumiho.get_revision("kref://my-project/characters/hero.model?t=published")
```

### Edges (Relationships)

Track dependencies and lineage between revisions:

```python
# Create a dependency edge
texture = kumiho.get_revision("kref://my-project/textures/skin.texture?r=2")
revision.create_edge(
    target_revision=texture,
    edge_type=kumiho.DEPENDS_ON,
    metadata={"usage": "skin material"}
)

# Query edges
outgoing = revision.get_edges(direction=kumiho.OUTGOING)
incoming = revision.get_edges(direction=kumiho.INCOMING)
```

### Graph Traversal

Analyze dependencies and impact:

```python
# Find all dependencies (what this revision uses)
deps = revision.get_all_dependencies(max_depth=5)
for kref in deps.revision_krefs:
    print(f"Depends on: {kref}")

# Find all dependents (what uses this revision)
dependents = revision.get_all_dependents(max_depth=5)

# Impact analysis (what would be affected by changes)
impact = revision.analyze_impact()
for impacted in impact:
    print(f"Would affect: {impacted.revision_kref} at depth {impacted.impact_depth}")

# Find shortest path between revisions
path = source.find_path_to(target)
```

### Bundles

Aggregate items into versioned collections:

```python
# Create a bundle
bundle = project.create_bundle("character-bundle")

# Add items
bundle.add_member(hero_model)
bundle.add_member(hero_rig)
bundle.add_member(hero_textures)

# Get members and history
members = bundle.get_members()
history = bundle.get_history()  # Full audit trail
```

### Event Streaming

React to changes in real-time:

```python
import kumiho

# Stream all events with filtering
for event in kumiho.event_stream(routing_key_filter="revision.*"):
    print(f"{event.action}: {event.kref}")

# Filter by kref pattern (glob syntax)
for event in kumiho.event_stream(kref_filter="kref://my-project/**/*.model"):
    print(f"Model changed: {event.kref}")
```

#### Tier-Based Streaming Capabilities

| Feature | Free | Creator | Studio | Enterprise |
|---------|------|---------|--------|------------|
| Real-time streaming | ✅ | ✅ | ✅ | ✅ |
| Routing key filters | ✅ | ✅ | ✅ | ✅ |
| Kref glob filters | ✅ | ✅ | ✅ | ✅ |
| Event persistence | ❌ | 1 hour | 24 hours | 30 days |
| Cursor-based resume | ❌ | ✅ | ✅ | ✅ |
| Consumer groups | ❌ | ❌ | ❌ | ✅ |

> **Note**: Creator tier and above features are **Coming Soon**. Currently only Free tier is available.

```python
# Check your tier's capabilities
caps = kumiho.get_event_capabilities()
print(f"Tier: {caps.tier}, Replay: {caps.supports_replay}")

# Resumable streaming (Creator+ tiers, Coming Soon)
for event in kumiho.event_stream(cursor=saved_cursor):
    process(event)
    save_cursor(event.cursor)  # Persist for recovery
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KUMIHO_SERVER_ENDPOINT` | No | gRPC endpoint. Defaults to `localhost:8080`. |
| `KUMIHO_AUTH_TOKEN` | For live calls | Firebase ID token (JWT). |
| `KUMIHO_AUTH_TOKEN_FILE` | No | Path to file containing the Firebase token. |
| `KUMIHO_CONTROL_PLANE_URL` | No | Control plane URL. Defaults to `https://kumiho.io`. |
| `KUMIHO_AUTO_CONFIGURE` | No | Set to `true` to auto-bootstrap on import. |
| `KUMIHO_DISCOVERY_CACHE_FILE` | No | Discovery cache path. Defaults to `~/.kumiho/discovery-cache.json`. |

## Multi-Tenant Usage

```python
# Use discovery to auto-configure for your tenant
kumiho.auto_configure_from_discovery()

# Or specify a tenant explicitly
kumiho.auto_configure_from_discovery(tenant_hint="my-studio")

# Switch between tenants using context managers
tenant_a = kumiho.connect(endpoint="tenant-a.kumiho.cloud:443")
tenant_b = kumiho.connect(endpoint="tenant-b.kumiho.cloud:443")

with kumiho.use_client(tenant_a):
    projects_a = kumiho.get_projects()

with kumiho.use_client(tenant_b):
    projects_b = kumiho.get_projects()
```

## MCP Server (Model Context Protocol)

Kumiho includes an MCP server that enables AI assistants (GitHub Copilot, Claude, Cursor, etc.) to interact with your asset graph.

### Installation

```bash
pip install kumiho[mcp]
```

### Running the MCP Server

```bash
# Ensure you're authenticated first
kumiho-auth login

# Start the MCP server
kumiho-mcp
```

### VS Code Configuration

Add to your VS Code `settings.json`:

```json
{
    "mcp": {
        "servers": {
            "kumiho": {
                "command": "kumiho-mcp"
            }
        }
    }
}
```

### Available Tools

The MCP server exposes 39 tools organized by category:

#### Read Operations

| Tool | Description |
|------|-------------|
| `kumiho_list_projects` | List all accessible projects |
| `kumiho_get_project` | Get project details by name |
| `kumiho_get_spaces` | Get spaces within a project |
| `kumiho_get_space` | Get a space by path |
| `kumiho_get_item` | Get an item by kref URI |
| `kumiho_search_items` | Search items with filters |
| `kumiho_get_item_revisions` | Get all revisions for an item |
| `kumiho_get_revision` | Get a revision by kref |
| `kumiho_get_revision_by_tag` | Get revision by tag (latest, published, etc.) |
| `kumiho_get_artifacts` | Get all artifacts for a revision |
| `kumiho_get_artifact` | Get a single artifact by kref |
| `kumiho_get_bundle` | Get a bundle by kref |
| `kumiho_resolve_kref` | Resolve kref to file location |
| `kumiho_get_artifacts_by_location` | Reverse lookup artifacts by file path |

#### Graph Traversal

| Tool | Description |
|------|-------------|
| `kumiho_get_dependencies` | Get what a revision depends on |
| `kumiho_get_dependents` | Get what depends on a revision |
| `kumiho_analyze_impact` | Analyze downstream impact of changes |
| `kumiho_find_path` | Find shortest path between revisions |
| `kumiho_get_edges` | Get edges (relationships) for a revision |

#### Create Operations

| Tool | Description |
|------|-------------|
| `kumiho_create_project` | Create a new project |
| `kumiho_create_space` | Create a space within a project |
| `kumiho_create_item` | Create an item within a space |
| `kumiho_create_revision` | Create a new revision for an item |
| `kumiho_create_artifact` | Create an artifact for a revision |
| `kumiho_create_bundle` | Create a bundle to group items |
| `kumiho_create_edge` | Create relationship between revisions |
| `kumiho_tag_revision` | Apply a tag to a revision |

#### Update Operations

| Tool | Description |
|------|-------------|
| `kumiho_untag_revision` | Remove a tag from a revision |
| `kumiho_set_metadata` | Set metadata on item or revision |
| `kumiho_deprecate_item` | Mark an item as deprecated |
| `kumiho_add_bundle_member` | Add an item to a bundle |
| `kumiho_remove_bundle_member` | Remove an item from a bundle |
| `kumiho_get_bundle_members` | List all items in a bundle |

#### Delete Operations

| Tool | Description |
|------|-------------|
| `kumiho_delete_project` | Delete a project |
| `kumiho_delete_space` | Delete a space |
| `kumiho_delete_item` | Delete an item |
| `kumiho_delete_revision` | Delete a revision |
| `kumiho_delete_artifact` | Delete an artifact |
| `kumiho_delete_edge` | Delete a relationship |

For full MCP documentation, see [MCP Server Integration](python/docs/mcp.md).

### Example AI Interactions

With the MCP server running, you can ask your AI assistant:

- "What are all the dependencies of this model?"
- "What would be impacted if I change this texture?"
- "Find all model assets in the characters space"
- "What's the path from this render to its source scene?"

## Running Tests

The test suite includes both unit tests (mocked) and integration tests (require live server):

```bash
cd kumiho-python
pytest
```

For live integration tests, ensure:
1. A running Rust server with Neo4j
2. Valid Firebase credentials (`kumiho-auth login`)

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=kumiho
```

## Documentation

- [Getting Started Guide](https://docs.kumiho.io/python/getting-started.html)
- [Core Concepts](https://docs.kumiho.io/python/concepts.html)
- [API Reference](https://docs.kumiho.io/python/api/kumiho.html)

## Requirements

- Python 3.10+
- Kumiho Cloud account ([sign up](https://kumiho.io))

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Links

- **Website**: [kumiho.io](https://kumiho.io)
- **Documentation**: [docs.kumiho.io](https://docs.kumiho.io)
- **GitHub**: [github.com/kumihoclouds/kumiho-python](https://github.com/kumihoclouds/kumiho-python)
- **PyPI**: [pypi.org/project/kumiho](https://pypi.org/project/kumiho)

