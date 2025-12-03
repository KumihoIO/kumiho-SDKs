# kumiho-cli

Command-line tools for Kumiho Cloud asset management system.

[![PyPI version](https://badge.fury.io/py/kumiho-cli.svg)](https://pypi.org/project/kumiho-cli/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

`kumiho-cli` provides command-line utilities for authenticating with Kumiho Cloud and managing credentials. It's used by all Kumiho SDKs (Python, C++, Dart, FastAPI) to provide a unified authentication experience.

## Installation

```bash
pip install kumiho-cli
```

Or install with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install kumiho-cli
```

## Quick Start

### Login

Authenticate with your Kumiho Cloud credentials:

```bash
kumiho-cli login
```

This will:
1. Prompt for your Kumiho Cloud email and password
2. Obtain authentication tokens from Firebase
3. Exchange for a Control Plane JWT
4. Store credentials securely in `~/.kumiho/kumiho_authentication.json`

### Refresh Token

Refresh your authentication token:

```bash
kumiho-cli refresh
```

### Check Status

View your current authentication status:

```bash
kumiho-cli whoami
```

## Credential Storage

Credentials are stored in:
- **Location**: `~/.kumiho/kumiho_authentication.json`
- **Permissions**: `0600` (read/write for owner only)
- **Format**: JSON with Firebase ID token, refresh token, and Control Plane JWT

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KUMIHO_CONFIG_DIR` | Override config directory | `~/.kumiho` |
| `KUMIHO_FIREBASE_API_KEY` | Firebase API key | (built-in) |
| `KUMIHO_FIREBASE_PROJECT_ID` | Firebase project ID | (optional) |
| `KUMIHO_CONTROL_PLANE_API_URL` | Control plane URL | `https://kumiho.io` |
| `KUMIHO_AUTH_TOKEN_GRACE_SECONDS` | Token refresh grace period | `300` |

## Usage with SDKs

### Python SDK

```bash
# Install kumiho with CLI tools
pip install kumiho[cli]

# Or install separately
pip install kumiho kumiho-cli
```

```python
import kumiho

# Automatically uses credentials from kumiho-cli
kumiho.auto_configure_from_discovery()
projects = kumiho.get_projects()
```

### C++ SDK

```bash
# One-time setup
pip install kumiho-cli
kumiho-cli login
```

```cpp
#include <kumiho/kumiho.hpp>

// Automatically loads tokens from ~/.kumiho/
auto client = kumiho::Client::createFromEnv();
```

## Commands

### `login`

Interactive login with email and password.

```bash
kumiho-cli login [--api-key KEY] [--project-id ID]
```

**Options:**
- `--api-key`: Override Firebase API key (default: uses built-in key)
- `--project-id`: Specify Firebase project ID (optional)

### `refresh`

Refresh the cached authentication token.

```bash
kumiho-cli refresh
```

### `whoami`

Display current user information.

```bash
kumiho-cli whoami
```

## Security Best Practices

1. **Never commit credentials**: Add `~/.kumiho/` to your `.gitignore`
2. **Use environment variables in CI/CD**: Set `KUMIHO_AUTH_TOKEN` instead of storing files
3. **Rotate tokens regularly**: Use `kumiho-cli refresh` to get fresh tokens
4. **Protect credential files**: The CLI automatically sets `0600` permissions

## CI/CD Integration

For automated environments (GitHub Actions, Jenkins, etc.):

```bash
# Option 1: Use environment variable
export KUMIHO_AUTH_TOKEN="your-token-here"

# Option 2: Non-interactive login (if supported by your CI)
echo "password" | kumiho-cli login --email user@example.com
```

## Development

### Install from source

```bash
git clone https://github.com/kumihoclouds/kumiho-python.git
cd kumiho-python/kumiho-cli
pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/
```

## Troubleshooting

### "No cached credentials found"

Run `kumiho-cli login` to authenticate.

### "Token expired"

Run `kumiho-cli refresh` to get a fresh token.

### "Permission denied" on credential file

```bash
chmod 600 ~/.kumiho/kumiho_authentication.json
```

## Links

- [Kumiho Cloud](https://kumiho.io)
- [Documentation](https://docs.kumiho.io)
- [Python SDK](https://github.com/kumihoclouds/kumiho-python)
- [Issue Tracker](https://github.com/kumihoclouds/kumiho-python/issues)

## License

Apache License 2.0 - see [LICENSE](../LICENSE) for details.
