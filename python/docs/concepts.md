# Core Concepts

This guide explains the core concepts of Kumiho Cloud and how they relate to the Python SDK.

## Graph-Native Architecture

Kumiho Cloud is built on a **graph database (Neo4j)**, which means relationships between assets are first-class citizens. Unlike traditional file-based systems, Kumiho tracks:

- **Dependencies**: What assets does this asset depend on?
- **Lineage**: What was this asset created from?
- **Usage**: Where is this asset used?

```
┌───────────────────────────────────────────────────────┐
│                         PROJECT                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │                        GROUP                    │  │
│  │  ┌─────────┐      ┌─────────┐     ┌─────────┐   │  │
│  │  │ PRODUCT │────▶│ PRODUCT │────▶│ PRODUCT │   │  │
│  │  └────┬────┘      └────┬────┘     └────┬────┘   │  │
│  │       │                │               │        │  │
│  │  ┌────▼────┐      ┌────▼────┐     ┌────▼────┐   │  │
│  │  │ VERSION │      │ VERSION │     │ VERSION │   │  │
│  │  │   v1    │      │   v1    │     │   v1    │   │  │
│  │  └────┬────┘      └────┬────┘     └────┬────┘   │  │
│  │       │                │               │        │  │
│  │  ┌────▼────┐      ┌────▼────┐     ┌────▼────┐   │  │
│  │  │RESOURCE │      │RESOURCE │     │RESOURCE │   │  │
│  │  └─────────┘      └─────────┘     └─────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

## Entity Hierarchy

### Project

A **Project** is the top-level container representing a production, show, or workspace. Each project is isolated within a tenant's graph database.

```python
project = kumiho.create_project(
    name="sci-fi-short",
    description="Sci-fi short film VFX assets"
)
```

**Key attributes:**
- `name`: URL-safe identifier (used in Kref URIs)
- `description`: Human-readable description
- `kref`: Reference URI (`kref://sci-fi-short`)

### Group

A **Group** organizes assets within a project. Common groupings include:
- By type: `characters`, `environments`, `props`
- By episode: `ep01`, `ep02`
- By department: `modeling`, `animation`, `lighting`

```python
group = project.create_group("characters")
```

**Key attributes:**
- `name`: URL-safe identifier
- `path`: Full path in the hierarchy (e.g., `/sci-fi-short/characters`)
- `metadata`: Custom key-value metadata

### Product

A **Product** represents a single creative asset or AI artifact. Products have a type that indicates what kind of asset they are.

```python
product = group.create_product(
    product_name="hero-robot",
    product_type="model"
)
```

**Common product types:**
- `model`: 3D models
- `texture`: Textures and materials
- `animation`: Animation data
- `rig`: Character rigs
- `composite`: Compositing setups
- `ai_model`: Trained AI models
- `dataset`: Training datasets
- `prompt`: AI prompts

**Key attributes:**
- `name`: URL-safe identifier
- `product_type`: Category of the asset
- `kref`: Reference URI (`kref://sci-fi-short/characters/hero-robot.model`)

### Version

A **Version** represents a specific iteration of a product. Versions are immutable once published.

```python
# Simple version creation
version = product.create_version()

# Version with metadata
version = product.create_version(
    metadata={
        "artist": "jane",
        "render_engine": "arnold",
        "notes": "Added facial rigging for dialogue"
    }
)
```

**Key attributes:**
- `number`: Auto-incrementing version number
- `metadata`: Custom key-value metadata
- `kref`: Reference URI (`kref://sci-fi-short/characters/hero-robot.model?v=3`)
- `tags`: List of tags (e.g., "latest", "published", "approved")

### Resource

A **Resource** is a file reference attached to a version. Resources store metadata about files without uploading the actual data—files stay on your local/NAS storage.

```python
resource = version.create_resource(
    name="hero_robot_v3.fbx",
    location="smb://studio-nas/projects/scifi/hero_robot_v3.fbx"
)

# Add metadata after creation
resource.set_metadata({
    "size": "52428800",
    "checksum": "sha256:a1b2c3...",
    "format": "fbx"
})
```

**Key attributes:**
- `name`: Resource identifier within the version
- `location`: URI pointing to the actual file
- `metadata`: Custom key-value metadata

### Link

A **Link** represents a relationship between versions. Links enable lineage tracking.

```python
import kumiho

# Get the target version
texture = kumiho.get_version("kref://sci-fi-short/textures/metal.texture?v=2")

# Create link with optional metadata
link = version.create_link(
    target_version=texture,
    link_type=kumiho.DEPENDS_ON,
    metadata={"usage": "body material"}
)
```

**Link types:**
- `kumiho.DEPENDS_ON`: This version depends on the target
- `kumiho.DERIVED_FROM`: This version was derived from the target
- `kumiho.REFERENCED`: This version references the target
- `kumiho.CONTAINS`: This version contains the target

## Metadata

All node types support custom metadata as key-value string pairs. Metadata can be set during creation (where supported) or updated afterward.

### Setting Metadata

```python
# During version creation
version = product.create_version(metadata={
    "artist": "jane",
    "render_engine": "arnold",
    "frame_range": "1-100"
})

# During link creation
link = version.create_link(
    target_version=texture,
    link_type=kumiho.DEPENDS_ON,
    metadata={"channel": "diffuse"}
)

# Update metadata after creation (all node types)
group.set_metadata({"department": "modeling"})
product.set_metadata({"status": "approved"})
version.set_metadata({"published_by": "supervisor"})
resource.set_metadata({"checksum": "sha256:..."})
```

### Common Metadata Patterns

| Node Type | Common Keys |
|-----------|-------------|
| Group | `department`, `supervisor`, `deadline` |
| Product | `status`, `priority`, `assigned_to` |
| Version | `artist`, `render_engine`, `notes`, `software_version` |
| Resource | `size`, `checksum`, `format`, `resolution` |
| Link | `usage`, `channel`, `relationship_notes` |

## Kref URI Scheme

Kumiho uses **Kref URIs** as universal identifiers for all entities:

```
kref://project/group/product.type?v=version&r=resource
```

| URI | Resolves To |
|-----|-------------|
| `kref://my-project` | Project |
| `kref://my-project/chars` | Group |
| `kref://my-project/chars/hero.model` | Product (latest version) |
| `kref://my-project/chars/hero.model?v=2` | Specific version |
| `kref://my-project/chars/hero.model?v=2&r=mesh.fbx` | Specific resource |

## BYO Storage Philosophy

Kumiho follows a **"Bring Your Own Storage"** philosophy:

1. **Files stay local**: Original files remain on your NAS, local disk, or on-prem storage
2. **Metadata in cloud**: Only paths, hashes, and relationships are stored in the cloud
3. **No vendor lock-in**: You can always access your files directly

```python
# Resource location is just a URI - files aren't uploaded
resource = version.create_resource(
    name="hero.fbx",
    resource_type="file",
    location="file:///mnt/studio/projects/hero.fbx"  # File stays here
)
```

**Supported URI schemes:**
- `file://`: Local filesystem
- `smb://`: Windows/Samba shares
- `nfs://`: NFS mounts
- `s3://`: Amazon S3 (for hybrid setups)
- `gs://`: Google Cloud Storage (for hybrid setups)

## Multi-Tenant Architecture

Kumiho Cloud is a multi-tenant SaaS:

- **Tenant**: A studio or organization with their own isolated data
- **Region**: Geographic location of the data (e.g., `us-central`, `eu-west`)
- **Control Plane**: Global service for authentication and routing
- **Data Plane**: Regional servers with Neo4j databases

The SDK handles tenant resolution automatically:

```python
# SDK automatically routes to the correct region
kumiho.connect()  # Uses cached credentials and tenant info
```

## Event Streaming

Kumiho supports real-time event streaming for reactive workflows:

```python
# Stream events from a project
for event in project.stream_events():
    if event.event_type == "version.created":
        print(f"New version: {event.payload}")
```

**Event types:**
- `version.created`: New version was published
- `link.created`: New relationship was created
- `resource.added`: Resource was added to a version

## Next Steps

- Try the [Getting Started](getting-started.md) tutorial
- Explore the [API Reference](api/kumiho.rst)
- Learn about [Authentication](authentication.md)
