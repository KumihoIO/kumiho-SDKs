# Authentication

This guide covers authentication methods for the Kumiho Python SDK.

## Overview

Kumiho Cloud uses **Firebase Authentication** for identity management. The authentication flow works as follows:

1. User authenticates with Firebase via email/password
2. Firebase issues an ID token
3. SDK exchanges the token with Kumiho Control Plane
4. Control Plane returns tenant info and a region-scoped JWT
5. SDK connects to the appropriate regional server

## CLI Authentication

The simplest way to authenticate is using the CLI:

```bash
kumiho-auth login
```

This prompts for your Kumiho Cloud email and password in the terminal. After successful login, credentials are cached in `~/.kumiho/kumiho_authentication.json`.

### Cached Credentials

The cached credentials include:
- Firebase refresh token (for automatic token renewal)
- Control Plane JWT (region-scoped access token)
- Token expiration times

```python
# SDK automatically uses cached credentials
import kumiho

kumiho.connect()  # Uses ~/.kumiho/kumiho_authentication.json
```

### Refreshing Tokens

To manually refresh an expired token:

```bash
kumiho-auth refresh
```

## Programmatic Authentication

### With Firebase ID Token

If you have a Firebase ID token (e.g., from a web app or mobile app):

```python
import kumiho

kumiho.connect(id_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVC...")
```

### With Environment Variables

For CI/CD pipelines and containerized deployments:

```bash
export KUMIHO_AUTH_TOKEN="your-control-plane-jwt"
# Or for Firebase token:
export KUMIHO_AUTH_TOKEN_FILE="/path/to/token-file"
```

```python
import kumiho

# SDK reads from environment automatically
kumiho.connect()
```

## Future Authentication Methods

The following authentication methods are planned but not yet implemented:

- **Browser-based OAuth flow**: Opening kumiho.io login page
- **Firebase popup authentication**: Google, GitHub, Microsoft SSO
- **Service account authentication**: For automated pipelines

## Discovery Flow

The SDK uses a discovery-based approach to find the correct regional server:

```python
from kumiho.discovery import discover_tenant

# Discover tenant configuration
config = discover_tenant(id_token)
print(f"Region: {config.region}")
print(f"Server: {config.server_url}")
```

### Discovery Response

The discovery endpoint returns:
- `tenant_id`: Your organization's tenant ID
- `tenant_name`: Human-readable tenant name
- `region`: Geographic region (e.g., `us-central`)
- `server_url`: Regional server endpoint

## Token Refresh

Tokens are automatically refreshed when they expire:

```python
import kumiho

# SDK handles token refresh automatically
kumiho.connect()

# Long-running operations work seamlessly
for project in kumiho.get_projects():
    # Token refreshed if needed
    process(project)
```

## Multiple Tenants

If you belong to multiple tenants, you can switch between them:

```python
import kumiho

# Connect to default tenant
kumiho.connect()

# Switch to a different tenant
kumiho.connect(tenant_id="other-tenant-id")
```

## Environment Variables

The SDK supports the following environment variables:

| Variable | Description |
|----------|-------------|
| `KUMIHO_AUTH_TOKEN` | Pre-authenticated token (Control Plane JWT or Firebase ID token) |
| `KUMIHO_AUTH_TOKEN_FILE` | Path to file containing the auth token |
| `KUMIHO_CONTROL_PLANE_API_URL` | Control Plane URL (default: `https://control.kumiho.cloud`) |
| `KUMIHO_CONFIG_DIR` | Custom config directory (default: `~/.kumiho`) |
| `KUMIHO_FIREBASE_API_KEY` | Firebase API key (for custom deployments) |

```python
import kumiho

# SDK reads from environment
kumiho.connect()
```

## Security Best Practices

1. **Never commit credentials**: Add `~/.kumiho/` to `.gitignore`
2. **Use short-lived tokens**: ID tokens expire after 1 hour
3. **Use environment variables in CI/CD**: Don't hardcode tokens
4. **Rotate credentials regularly**: Re-authenticate periodically

## Troubleshooting

### Token Expired

```
KumihoError: Token expired
```

Re-authenticate using the CLI:
```bash
kumiho-auth login
```

Or refresh the existing token:
```bash
kumiho-auth refresh
```

### Invalid Tenant

```
KumihoError: Tenant not found
```

Verify your tenant membership in the Kumiho Cloud dashboard at https://kumiho.io.

### Connection Failed

```
KumihoError: Failed to connect to regional server
```

1. Check your network connection
2. Verify the server URL is correct
3. Check the status page at https://status.kumiho.cloud

## Next Steps

- Learn about [Core Concepts](concepts.md)
- Explore the [API Reference](api/kumiho.rst)
- See [Getting Started](getting-started.md) for a complete tutorial
