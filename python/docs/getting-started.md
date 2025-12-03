# Getting Started

This guide will help you get started with the Kumiho Python SDK.

## Installation

Install the Kumiho SDK using pip:

```bash
pip install kumiho
```

For development, install with the optional dev dependencies:

```bash
pip install kumiho[dev]
```

## Authentication

Before using the SDK, you need to authenticate with Kumiho Cloud.

### Using the CLI

The easiest way to authenticate is using the built-in CLI:

```bash
kumiho-auth login
```

This will:
1. Prompt for your Kumiho Cloud email and password
2. Cache your credentials in `~/.kumiho/kumiho_authentication.json`
3. Automatically exchange for a Control Plane JWT

### Programmatic Authentication

You can also authenticate programmatically if you have a Firebase ID token:

```python
import kumiho

# Connect with explicit token
kumiho.connect(id_token="your-firebase-id-token")
```

Or use environment variables:

```bash
export KUMIHO_AUTH_TOKEN="your-control-plane-jwt"
```

```python
import kumiho

# SDK reads from environment automatically
kumiho.connect()
```

## Basic Concepts

### Projects

Projects are the top-level containers for organizing your assets:

```python
import kumiho

kumiho.connect()

# Create a new project
project = kumiho.create_project(
    name="my-project",
    description="My VFX Project"
)

# Get an existing project
project = kumiho.get_project("kref://my-project")
```

### Spaces

Spaces organize assets within a project (e.g., by type, department, or episode):

```python
# Create a space
space = project.create_space("characters")

# List spaces in a project
spaces = project.get_spaces()
```

### Items

Items represent individual assets with their metadata:

```python
# Create an item in a space
item = space.create_item(
    item_name="hero",
    kind="model"
)

# Or create directly from a project with a path
item = project.create_item(
    item_name="hero",
    kind="model",
    parent_path="/my-project/characters"
)

# Get an item from a space
item = space.get_item("hero", "model")

# Or get from a project with a path
item = project.get_item("hero", "model", parent_path="/my-project/characters")

# Get an item by Kref
item = kumiho.get_item("kref://my-project/characters/hero.model")
```

### Revisions

Revisions track changes to items over time:

```python
# Create a new revision with metadata
revision = item.create_revision(
    metadata={
        "artist": "jane",
        "notes": "Updated rigging for better deformation"
    }
)

# Get a specific revision
revision = kumiho.get_revision("kref://my-project/characters/hero.model?v=2")

# Update metadata later
revision.set_metadata({"render_engine": "arnold"})
```

### Artifacts

Artifacts are file references attached to a revision. Files stay on your local storage—Kumiho only tracks the location:

```python
# Add a file artifact
artifact = revision.create_artifact(
    name="hero_model.fbx",
    location="smb://server/projects/hero/hero_model.fbx"
)

# Add metadata to the artifact
artifact.set_metadata({
    "size": "1024000",
    "checksum": "sha256:abc123...",
    "format": "fbx"
})

# Get a specific artifact
artifact = kumiho.get_artifact(
    "kref://my-project/characters/hero.model?v=1&r=hero_model.fbx"
)
```

### Edges

Edges track relationships between assets for lineage:

```python
import kumiho

# Get the target revision first
texture = kumiho.get_revision("kref://my-project/textures/hero_skin.texture?v=1")

# Create a dependency edge with optional metadata
edge = revision.create_edge(
    target_revision=texture,
    edge_type=kumiho.DEPENDS_ON,
    metadata={"usage": "skin material"}
)

# Get outgoing edges
edges = revision.get_edges()

# Get incoming edges (what depends on this revision)
dependents = revision.get_edges(direction=kumiho.INCOMING)
```

### Bundles

Bundles group related items together with an audit trail of membership changes:

```python
# Create a bundle in a project or space
bundle = project.create_bundle("release-bundle")
# Or: bundle = space.create_bundle("character-bundle")

# Add items to the bundle
hero_model = space.get_item("hero", "model")
hero_rig = space.get_item("hero", "rig")
bundle.add_member(hero_model)
bundle.add_member(hero_rig)

# Get a bundle by name
bundle = project.get_bundle("release-bundle")
# Or: bundle = space.get_bundle("character-bundle")
# Or by kref: bundle = kumiho.get_bundle("kref://my-project/assets/release-bundle.bundle")

# List bundle members
members = bundle.get_members()
for member in members:
    print(f"  {member.item_kref}")

# View membership change history
history = bundle.get_revision_history()
```

## Kref URIs

Kumiho uses a URI scheme called "Kref" to reference assets:

```
kref://project/space/item.kind?v=N&r=artifact_name
```

Components:
- `project`: Project name
- `space`: Space name within the project
- `item`: Item name
- `kind`: Item kind (model, texture, animation, etc.)
- `v=N`: Revision number (optional)
- `r=artifact_name`: Artifact name (optional)

Examples:
```
kref://my-project                              # Project
kref://my-project/characters                   # Space
kref://my-project/characters/hero.model        # Item (latest revision)
kref://my-project/characters/hero.model?v=2    # Specific revision
kref://my-project/characters/hero.model?v=2&r=model  # Specific artifact
```

## Error Handling

The SDK raises specific exceptions for different error conditions:

```python
from kumiho import KumihoError

try:
    project = kumiho.get_project("kref://non-existent")
except KumihoError as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Use context managers**: The SDK manages connections automatically, but
   you can use `kumiho.connect()` explicitly for long-running scripts.

2. **Batch operations**: When creating many assets, consider using
   transactions or batch APIs (coming soon).

3. **Store file metadata**: Always include checksums and sizes for artifacts
   to enable integrity verification.

4. **Use meaningful names**: Project, space, and item names become part
   of Kref URIs, so use URL-safe, descriptive names.

5. **Track lineage**: Use edges to track dependencies between assets for
   full provenance.

## AI Assistant Integration (MCP)

The Kumiho SDK includes a Model Context Protocol (MCP) server that lets AI
assistants like GitHub Copilot and Claude interact with your Kumiho assets
directly.

### Quick Setup

1. Install with MCP support:
   ```bash
   pip install kumiho[mcp]
   ```

2. Authenticate:
   ```bash
   kumiho-auth login
   ```

3. Add to VS Code settings.json:
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

Once configured, you can ask your AI assistant questions like:
- "List all my Kumiho projects"
- "What assets depend on the hero model?"
- "Create a new revision for kref://film-2024/characters/hero.model"

For full documentation, see the [MCP Integration Guide](mcp.md).

## Next Steps

- Read the [Concepts](concepts.md) guide for deeper understanding
- Learn about [MCP Integration](mcp.md) for AI assistant support
- Explore the [API Reference](api/kumiho.rst) for all available methods
- Check out [Examples](https://github.com/kumihoclouds/kumiho-python/tree/main/examples)
