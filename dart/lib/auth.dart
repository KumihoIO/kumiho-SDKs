// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Authentication utilities for Kumiho SDK.
///
/// This library provides authentication support for the Kumiho Dart SDK,
/// including:
///
/// - Token loading from environment variables
/// - Token loading from `~/.kumiho/kumiho_authentication.json` (kumiho-cli)
/// - Auto-refresh of expired tokens (opt-in)
///
/// ## Token Loading Priority
///
/// 1. `KUMIHO_AUTH_TOKEN` environment variable
/// 2. Firebase ID token from credentials file
/// 3. Control Plane token (if `KUMIHO_USE_CONTROL_PLANE_TOKEN=true`)
///
/// ## Auto-Refresh
///
/// Set `KUMIHO_ENABLE_AUTO_REFRESH=true` to enable automatic token refresh
/// when credentials expire. The SDK will use the stored refresh token to
/// obtain new ID tokens.
///
/// ## Environment Variables
///
/// | Variable | Description |
/// |----------|-------------|
/// | `KUMIHO_AUTH_TOKEN` | Primary auth token (overrides file) |
/// | `KUMIHO_FIREBASE_ID_TOKEN` | Firebase-specific token |
/// | `KUMIHO_CONFIG_DIR` | Custom config directory |
/// | `KUMIHO_USE_CONTROL_PLANE_TOKEN` | Prefer CP token (true/false) |
/// | `KUMIHO_ENABLE_AUTO_REFRESH` | Enable token auto-refresh (true/false) |
/// | `KUMIHO_AUTH_TOKEN_GRACE_SECONDS` | Grace period before expiry (default: 300) |
/// | `KUMIHO_FIREBASE_API_KEY` | Custom Firebase API key |
/// | `KUMIHO_CONTROL_PLANE_URL` | Custom Control Plane base URL (preferred) |
/// | `KUMIHO_CONTROL_PLANE_API_URL` | Custom CP base URL (legacy) |
///
/// ## Usage
///
/// ```dart
/// import 'package:kumiho/auth.dart';
///
/// // Simple token loading
/// final token = loadBearerToken();
///
/// // Token with source info
/// final result = loadBearerTokenWithSource();
/// print('Token from: ${result.source}');
///
/// // Auto-refresh credentials
/// final creds = await ensureValidCredentials();
/// if (creds != null) {
///   print('Token valid: ${creds.isValid}');
/// }
/// ```
library;

export 'src/auth/token_loader.dart'
    show
        AuthEnvVars,
        AuthDefaults,
        KumihoCredentials,
        TokenLoadResult,
        getConfigDir,
        getCredentialsFile,
        loadCredentials,
        saveCredentials,
        loadBearerToken,
        loadFirebaseToken,
        loadBearerTokenWithSource;

export 'src/auth/token_refresh.dart'
    show
        TokenRefreshError,
        TokenRefreshResult,
        refreshFirebaseToken,
        exchangeForControlPlaneToken,
        autoRefreshCredentials;
