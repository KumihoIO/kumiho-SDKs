# Kumiho Python SDK

[![PyPI version](https://badge.fury.io/py/kumiho.svg)](https://badge.fury.io/py/kumiho)
[![Python versions](https://img.shields.io/pypi/pyversions/kumiho.svg)](https://pypi.org/project/kumiho/)
[![Documentation Status](https://readthedocs.org/projects/kumiho/badge/?version=latest)](https://kumiho.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python SDK for [Kumiho Cloud](https://kumiho.cloud) — a graph-native creative and AI asset management platform.

## Features

- **Graph-Native Design**: Built on Neo4j for tracking asset relationships and lineage
- **Version Control**: Semantic versioning for creative assets with full history
- **AI Lineage Tracking**: Track AI model training data provenance and dependencies
- **BYO Storage**: Files stay on your local/NAS/on-prem storage — only metadata is managed
- **Multi-Tenant SaaS**: Secure, region-aware multi-tenant architecture
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

### Authentication

First, authenticate with Kumiho Cloud using the CLI:

```bash
kumiho-auth login
```

This opens a browser for Firebase authentication and caches your credentials.

### Basic Usage

```python
import kumiho

# Connect to Kumiho Cloud (uses cached credentials)
kumiho.connect()

# Create a new project
project = kumiho.create_project(
    name="my-vfx-project",
    description="My VFX Project for 2024 film"
)

# Create an asset group
group = project.create_group("characters")

# Create a product (asset)
product = group.create_product(
    product_name="hero",
    product_type="model"
)

# Create a version with resources
version = product.create_version(
    description="Initial model with rigging"
)

# Add a file resource (file stays on your storage)
resource = version.create_resource(
    name="hero_model.fbx",
    resource_type="file",
    location="file:///projects/hero/hero_model.fbx",
    size=52428800,
    checksum="sha256:abc123..."
)

# Track dependencies with links
link = version.create_link(
    target_kref="kref://my-vfx-project/textures/skin.texture?v=1",
    link_type="DEPENDS_ON"
)
```

### Kref URIs

Reference any asset using Kref URIs:

```python
# Get a product by Kref
product = kumiho.get_product("kref://my-project/characters/hero.model")

# Get a specific version
version = kumiho.get_version("kref://my-project/characters/hero.model?v=2")

# Get a specific resource
resource = kumiho.get_resource(
    "kref://my-project/characters/hero.model?v=2&r=hero_model.fbx"
)
```

### Event Streaming

Stream real-time events for reactive workflows:

```python
# Stream events from a project
for event in project.stream_events():
    if event.event_type == "version.created":
        print(f"New version: {event.kref}")
```

## Documentation

- **[Getting Started](https://kumiho.readthedocs.io/en/latest/getting-started.html)** — Installation and first steps
- **[Concepts](https://kumiho.readthedocs.io/en/latest/concepts.html)** — Core concepts and architecture
- **[API Reference](https://kumiho.readthedocs.io/en/latest/api/kumiho.html)** — Full API documentation

## Entity Hierarchy

```
Project
└── Group
    └── Product
        └── Version
            ├── Resource (files/data)
            └── Link (relationships)
```

## Kref URI Format

```
kref://project/group/product.type?v=version&r=resource
```

| URI | Resolves To |
|-----|-------------|
| `kref://my-project` | Project |
| `kref://my-project/chars` | Group |
| `kref://my-project/chars/hero.model` | Product (latest) |
| `kref://my-project/chars/hero.model?v=2` | Version |
| `kref://my-project/chars/hero.model?v=2&r=mesh.fbx` | Resource |

## Requirements

- Python 3.10+
- Kumiho Cloud account ([sign up](https://kumiho.cloud))

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://github.com/kumihoclouds/kumiho-python/blob/main/CONTRIBUTING.md) for guidelines.

## Links

- **Website**: [kumiho.cloud](https://kumiho.cloud)
- **Documentation**: [kumiho.readthedocs.io](https://kumiho.readthedocs.io)
- **GitHub**: [github.com/kumihoclouds/kumiho-python](https://github.com/kumihoclouds/kumiho-python)
- **PyPI**: [pypi.org/project/kumiho](https://pypi.org/project/kumiho)
