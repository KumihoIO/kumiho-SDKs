# Kumiho Python SDK

[![PyPI version](https://img.shields.io/pypi/v/kumiho.svg)](https://pypi.org/project/kumiho/)
[![Python versions](https://img.shields.io/pypi/pyversions/kumiho.svg)](https://pypi.org/project/kumiho/)
[![Documentation](https://img.shields.io/badge/docs-kumiho.io-blue)](https://docs.kumiho.io/python/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [Kumiho Cloud](https://kumiho.io) — a graph-native creative and AI asset management platform.

## Installation

```bash
pip install kumiho
```

With MCP server support (for AI assistants):

```bash
pip install kumiho[mcp]
```

## Quick Start

```bash
# Authenticate
kumiho-auth login
```

```python
import kumiho

kumiho.auto_configure_from_discovery()

# Create project and assets
project = kumiho.create_project("my-project", "My VFX project")
space = project.create_space("characters")
item = space.create_item("hero", "model")
revision = item.create_revision(metadata={"artist": "jane"})
revision.tag("approved")
```

## Documentation

📖 **[Full Documentation](./python/README.md)** — Detailed SDK guide with examples

- [Getting Started](https://docs.kumiho.io/python/getting-started.html)
- [Core Concepts](https://docs.kumiho.io/python/concepts.html)
- [API Reference](https://docs.kumiho.io/python/api/kumiho.html)
- [MCP Server](https://docs.kumiho.io/python/mcp.html)

## Links

- **Website**: [kumiho.io](https://kumiho.io)
- **Docs**: [docs.kumiho.io](https://docs.kumiho.io)
- **PyPI**: [pypi.org/project/kumiho](https://pypi.org/project/kumiho)

## License

MIT — See [LICENSE](LICENSE) for details

