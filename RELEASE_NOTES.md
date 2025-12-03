# Kumiho Python SDK - Release Notes

## kumiho 0.4.0 (December 2024) - Package Restructuring 📦

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

## kumiho-cli 1.0.0 (December 2024) - Initial Release 🎉

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

### v0.3.0 (November 2024)

- Initial development release
- Integrated authentication CLI
- MCP server support
- Graph traversal features

---

**Repository**: https://github.com/kumihoclouds/kumiho-python  
**Issues**: https://github.com/kumihoclouds/kumiho-python/issues
