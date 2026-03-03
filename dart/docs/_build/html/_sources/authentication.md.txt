# Authentication

This guide covers authentication methods for the Kumiho Dart SDK.

## Overview

Kumiho Cloud uses **Firebase Authentication** for identity management. The authentication flow works as follows:

1. User authenticates with Firebase via email/password
2. Firebase issues an ID token
3. SDK exchanges the token with Kumiho Control Plane
4. Control Plane returns tenant info and a region-scoped JWT
5. SDK connects to the appropriate regional server

## Token Sources

Kumiho authenticates with a Bearer token attached to every gRPC call. The client loads the token in the following order:

1. A token provided directly to `KumihoClient` via the `token` argument
2. The `KUMIHO_AUTH_TOKEN` environment variable
3. Credentials cached by `kumiho-auth login` at `~/.kumiho/kumiho_authentication.json`

You can disable automatic loading by setting `autoLoadToken: false` when constructing `KumihoClientBase`.

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

```dart
// SDK automatically uses cached credentials
final client = KumihoClient(
  host: 'api.kumiho.io',
  port: 443,
);
```

### Refreshing Tokens

To manually refresh an expired token:

```bash
kumiho-auth refresh
```

## Programmatic Authentication

### With Explicit Token

If you have a Control Plane JWT (e.g., from a web app or mobile app):

```dart
final client = KumihoClient(
  host: 'api.kumiho.io',
  port: 443,
  token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVC...',
);
```

### With Environment Variables

For CI/CD pipelines and containerized deployments:

```bash
export KUMIHO_AUTH_TOKEN="your-control-plane-jwt"
```

```dart
// SDK reads from environment automatically
final client = KumihoClient(
  host: 'api.kumiho.io',
  port: 443,
);
```

## Environment Variables

The SDK recognizes several environment variables for authentication behavior:

| Variable | Description |
|----------|-------------|
| `KUMIHO_AUTH_TOKEN` | Primary token, overrides anything stored in the credentials file |
| `KUMIHO_ENABLE_AUTO_REFRESH` | When `true`, refreshes expiring tokens using cached credentials |
| `KUMIHO_USE_CONTROL_PLANE_TOKEN` | Prefer the control-plane token if present in cached credentials |
| `KUMIHO_AUTH_TOKEN_GRACE_SECONDS` | Grace period before expiry that triggers refresh (default `300`) |

## Token Refresh

Automatic refresh is opt-in via `KUMIHO_ENABLE_AUTO_REFRESH`. When enabled, the client:

1. Loads cached credentials from `~/.kumiho/kumiho_authentication.json`
2. Monitors token expiration
3. Refreshes tokens when they approach expiry (within grace period)
4. Updates the Bearer token used in subsequent requests

You can also force a refresh attempt regardless of expiry state:

```dart
await client.forceRefreshToken();
```

## Manual Token Updates

Set `client.token` at runtime to replace the active Bearer token. This is useful when:

- Rotating tokens in long-lived applications
- Swapping between user sessions
- Implementing custom token refresh logic

```dart
// Update token at runtime
client.token = 'new-jwt-token';
```

## Flutter Authentication

For Flutter applications, you might want to integrate with Firebase Auth directly:

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:kumiho/kumiho.dart';

Future<KumihoClient> createAuthenticatedClient() async {
  // Get Firebase ID token
  final user = FirebaseAuth.instance.currentUser;
  final idToken = await user?.getIdToken();
  
  if (idToken == null) {
    throw Exception('User not authenticated');
  }
  
  // Exchange for Kumiho Control Plane JWT
  // (Implement your exchange logic here)
  final controlPlaneJwt = await exchangeToken(idToken);
  
  return KumihoClient(
    host: 'api.kumiho.io',
    port: 443,
    token: controlPlaneJwt,
  );
}
```

## Error Handling

Authentication errors surface as `GrpcError` instances. Common scenarios:

```dart
try {
  await client.getProjects();
} on GrpcError catch (e) {
  if (e.code == StatusCode.unauthenticated) {
    // Token is invalid or expired
    await client.forceRefreshToken();
  } else if (e.code == StatusCode.permissionDenied) {
    // Token lacks required permissions
    print('Access denied: ${e.message}');
  }
}
```

## Security Best Practices

1. **Never commit tokens**: Use environment variables or secure credential storage
2. **Use short-lived tokens**: Enable auto-refresh for production deployments
3. **Secure storage**: On mobile/desktop, use platform-specific secure storage
4. **Rotate tokens regularly**: For service accounts, implement token rotation
