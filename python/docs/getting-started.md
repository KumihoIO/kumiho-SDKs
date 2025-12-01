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

### Groups

Groups organize assets within a project (e.g., by type, department, or episode):

```python
# Create a group
group = project.create_group("characters")

# List groups in a project
groups = project.get_groups()
```

### Products

Products represent individual assets with their metadata:

```python
# Create a product
product = group.create_product(
    product_name="hero",
    product_type="model"
)

# Get a product by Kref
product = kumiho.get_product("kref://my-project/characters/hero.model")
```

### Versions

Versions track changes to products over time:

```python
# Create a new version with metadata
version = product.create_version(
    metadata={
        "artist": "jane",
        "notes": "Updated rigging for better deformation"
    }
)

# Get a specific version
version = kumiho.get_version("kref://my-project/characters/hero.model?v=2")

# Update metadata later
version.set_metadata({"render_engine": "arnold"})
```

### Resources

Resources are file references attached to a version. Files stay on your local storage—Kumiho only tracks the location:

```python
# Add a file resource
resource = version.create_resource(
    name="hero_model.fbx",
    location="smb://server/projects/hero/hero_model.fbx"
)

# Add metadata to the resource
resource.set_metadata({
    "size": "1024000",
    "checksum": "sha256:abc123...",
    "format": "fbx"
})

# Get a specific resource
resource = kumiho.get_resource(
    "kref://my-project/characters/hero.model?v=1&r=hero_model.fbx"
)
```

### Links

Links track relationships between assets for lineage:

```python
import kumiho

# Get the target version first
texture = kumiho.get_version("kref://my-project/textures/hero_skin.texture?v=1")

# Create a dependency link with optional metadata
link = version.create_link(
    target_version=texture,
    link_type=kumiho.DEPENDS_ON,
    metadata={"usage": "skin material"}
)
)

# Get outgoing links
links = version.get_links()

# Get incoming links (what depends on this version)
dependents = version.get_links(direction=kumiho.INCOMING)
```

## Kref URIs

Kumiho uses a URI scheme called "Kref" to reference assets:

```
kref://project/group/product.type?v=N&r=resource_name
```

Components:
- `project`: Project name
- `group`: Group name within the project
- `product`: Product name
- `type`: Product type (model, texture, animation, etc.)
- `v=N`: Version number (optional)
- `r=resource_name`: Resource name (optional)

Examples:
```
kref://my-project                              # Project
kref://my-project/characters                   # Group
kref://my-project/characters/hero.model        # Product (latest version)
kref://my-project/characters/hero.model?v=2    # Specific version
kref://my-project/characters/hero.model?v=2&r=model.fbx  # Specific resource
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

3. **Store file metadata**: Always include checksums and sizes for resources
   to enable integrity verification.

4. **Use meaningful names**: Project, group, and product names become part
   of Kref URIs, so use URL-safe, descriptive names.

5. **Track lineage**: Use links to track dependencies between assets for
   full provenance.

## Next Steps

- Read the [Concepts](concepts.md) guide for deeper understanding
- Explore the [API Reference](api/kumiho.rst) for all available methods
- Check out [Examples](https://github.com/kumihoclouds/kumiho-python/tree/main/examples)
