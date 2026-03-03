// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Token loading utilities for Kumiho authentication.
///
/// This module provides functions to load authentication tokens from:
/// - Environment variables
/// - Cached credentials file (`~/.kumiho/kumiho_authentication.json`)
///
/// The token loading priority is:
/// 1. `KUMIHO_AUTH_TOKEN` environment variable
/// 2. Firebase ID token from credentials file
/// 3. Control Plane token from credentials file (if `KUMIHO_USE_CONTROL_PLANE_TOKEN=true`)
library;

import 'dart:convert';
import 'dart:io';

/// Environment variable names for authentication.
class AuthEnvVars {
  AuthEnvVars._();

  /// Primary auth token environment variable.
  static const String authToken = 'KUMIHO_AUTH_TOKEN';

  /// Firebase-specific token environment variable.
  static const String firebaseToken = 'KUMIHO_FIREBASE_ID_TOKEN';

  /// Custom config directory override.
  static const String configDir = 'KUMIHO_CONFIG_DIR';

  /// Flag to prefer Control Plane token over Firebase token.
  static const String useControlPlaneToken = 'KUMIHO_USE_CONTROL_PLANE_TOKEN';

  /// Token grace period in seconds before expiry.
  static const String tokenGraceSeconds = 'KUMIHO_AUTH_TOKEN_GRACE_SECONDS';

  /// Enable auto-refresh of tokens (opt-in).
  static const String enableAutoRefresh = 'KUMIHO_ENABLE_AUTO_REFRESH';

  /// Firebase API key for token refresh.
  static const String firebaseApiKey = 'KUMIHO_FIREBASE_API_KEY';

  /// Control Plane API URL.
  static const String controlPlaneApiUrl = 'KUMIHO_CONTROL_PLANE_API_URL';

  /// Control Plane base URL.
  ///
  /// This is the preferred env var name (parity with Python/C++).
  static const String controlPlaneUrl = 'KUMIHO_CONTROL_PLANE_URL';
}

/// Default values for authentication.
class AuthDefaults {
  AuthDefaults._();

  /// Default grace period before token expiry (5 minutes).
  static const int tokenGraceSeconds = 300;

  /// Default Firebase API key.
  static const String firebaseApiKey = 'AIzaSyBFAo7Nv48xAvbN18rL-3W41Dqheporh8E';

  /// Default Control Plane API URL.
  static const String controlPlaneApiUrl = 'https://control.kumiho.cloud';

  /// Credentials filename.
  static const String credentialsFilename = 'kumiho_authentication.json';
}

/// Resolves the Control Plane base URL.
///
/// Priority:
/// 1) `KUMIHO_CONTROL_PLANE_URL`
/// 2) `KUMIHO_CONTROL_PLANE_API_URL` (legacy)
/// 3) [AuthDefaults.controlPlaneApiUrl]
String getControlPlaneUrl() {
  final preferred = Platform.environment[AuthEnvVars.controlPlaneUrl];
  if (preferred != null && preferred.trim().isNotEmpty) {
    return preferred.trim();
  }

  final legacy = Platform.environment[AuthEnvVars.controlPlaneApiUrl];
  if (legacy != null && legacy.trim().isNotEmpty) {
    return legacy.trim();
  }

  return AuthDefaults.controlPlaneApiUrl;
}

/// Cached credentials from the kumiho-cli authentication.
class KumihoCredentials {
  /// Creates credentials from JSON data.
  KumihoCredentials({
    required this.apiKey,
    required this.email,
    required this.refreshToken,
    required this.idToken,
    required this.expiresAt,
    this.projectId,
    this.controlPlaneToken,
    this.cpExpiresAt,
  });

  /// Creates credentials from a JSON map.
  factory KumihoCredentials.fromJson(Map<String, dynamic> json) {
    return KumihoCredentials(
      apiKey: json['api_key'] as String? ?? '',
      email: json['email'] as String? ?? '',
      refreshToken: json['refresh_token'] as String? ?? '',
      idToken: json['id_token'] as String? ?? '',
      expiresAt: (json['expires_at'] as num?)?.toInt() ?? 0,
      projectId: json['project_id'] as String?,
      controlPlaneToken: json['control_plane_token'] as String?,
      cpExpiresAt: (json['cp_expires_at'] as num?)?.toInt(),
    );
  }

  /// Firebase API key.
  final String apiKey;

  /// User email.
  final String email;

  /// Refresh token for obtaining new ID tokens.
  final String refreshToken;

  /// Firebase ID token.
  final String idToken;

  /// Unix timestamp when the ID token expires.
  final int expiresAt;

  /// Optional project ID.
  final String? projectId;

  /// Control Plane JWT token.
  final String? controlPlaneToken;

  /// Unix timestamp when the CP token expires.
  final int? cpExpiresAt;

  /// Converts to JSON map.
  Map<String, dynamic> toJson() => {
        'api_key': apiKey,
        'email': email,
        'refresh_token': refreshToken,
        'id_token': idToken,
        'expires_at': expiresAt,
        'project_id': projectId,
        'control_plane_token': controlPlaneToken,
        'cp_expires_at': cpExpiresAt,
      };

  /// Checks if the ID token is still valid.
  bool get isValid {
    if (idToken.isEmpty) return false;
    final graceSeconds = _getGraceSeconds();
    final remaining = expiresAt - _currentTimestamp();
    return remaining > graceSeconds;
  }

  /// Checks if the Control Plane token is still valid.
  bool get isCpValid {
    if (controlPlaneToken == null || controlPlaneToken!.isEmpty) return false;
    if (cpExpiresAt == null) return false;
    final graceSeconds = _getGraceSeconds();
    final remaining = cpExpiresAt! - _currentTimestamp();
    return remaining > graceSeconds;
  }

  /// Creates a copy with updated fields.
  KumihoCredentials copyWith({
    String? apiKey,
    String? email,
    String? refreshToken,
    String? idToken,
    int? expiresAt,
    String? projectId,
    String? controlPlaneToken,
    int? cpExpiresAt,
  }) {
    return KumihoCredentials(
      apiKey: apiKey ?? this.apiKey,
      email: email ?? this.email,
      refreshToken: refreshToken ?? this.refreshToken,
      idToken: idToken ?? this.idToken,
      expiresAt: expiresAt ?? this.expiresAt,
      projectId: projectId ?? this.projectId,
      controlPlaneToken: controlPlaneToken ?? this.controlPlaneToken,
      cpExpiresAt: cpExpiresAt ?? this.cpExpiresAt,
    );
  }

  static int _currentTimestamp() =>
      DateTime.now().millisecondsSinceEpoch ~/ 1000;

  static int _getGraceSeconds() {
    final env = Platform.environment[AuthEnvVars.tokenGraceSeconds];
    if (env != null) {
      return int.tryParse(env) ?? AuthDefaults.tokenGraceSeconds;
    }
    return AuthDefaults.tokenGraceSeconds;
  }
}

/// Gets the Kumiho configuration directory.
///
/// Returns the path specified by `KUMIHO_CONFIG_DIR` if set,
/// otherwise returns `~/.kumiho`.
Directory getConfigDir() {
  final envDir = Platform.environment[AuthEnvVars.configDir];
  if (envDir != null && envDir.isNotEmpty) {
    return Directory(envDir);
  }
  final home = Platform.environment['HOME'] ??
      Platform.environment['USERPROFILE'] ??
      '.';
  return Directory('$home/.kumiho');
}

/// Gets the path to the credentials file.
File getCredentialsFile() {
  return File('${getConfigDir().path}/${AuthDefaults.credentialsFilename}');
}

/// Checks if the credential file has secure permissions (Unix only).
///
/// Returns `true` if permissions are secure or on Windows.
/// Logs a warning if permissions allow group/world access.
bool _checkCredentialPermissions(File file) {
  if (Platform.isWindows) {
    return true; // Skip check on Windows
  }
  try {
    final stat = file.statSync();
    // On Unix, check if group or world has any permissions
    // mode bits: rwxrwxrwx -> owner/group/world
    // We want to ensure bits 0-5 (group and world) are all zero
    final mode = stat.mode;
    final groupWorldBits = mode & 0x3F; // Last 6 bits: group (3) + world (3)
    if (groupWorldBits != 0) {
      stderr.writeln(
        'Warning: Credential file ${file.path} has insecure permissions '
        '(mode: ${mode.toRadixString(8)}). Other users may be able to read '
        'your credentials. Run: chmod 600 ${file.path}',
      );
      return false;
    }
    return true;
  } catch (_) {
    return true; // Ignore errors checking permissions
  }
}

/// Reads cached credentials from the credentials file.
///
/// Returns `null` if the file doesn't exist or is invalid.
/// Warns if the file has insecure permissions on Unix systems.
KumihoCredentials? loadCredentials() {
  final file = getCredentialsFile();
  if (!file.existsSync()) {
    return null;
  }
  
  // Security: Check file permissions before reading
  _checkCredentialPermissions(file);
  
  try {
    final content = file.readAsStringSync();
    final json = jsonDecode(content) as Map<String, dynamic>;
    return KumihoCredentials.fromJson(json);
  } catch (_) {
    return null;
  }
}

/// Saves credentials to the credentials file.
void saveCredentials(KumihoCredentials credentials) {
  final file = getCredentialsFile();
  file.parent.createSync(recursive: true);
  file.writeAsStringSync(
    const JsonEncoder.withIndent('  ').convert(credentials.toJson()),
  );
  // Set file permissions to 600 (owner read/write only) on Unix
  if (!Platform.isWindows) {
    Process.runSync('chmod', ['600', file.path]);
  }
}

/// Checks if an environment variable flag is set to true.
bool _envFlag(String name) {
  final value = Platform.environment[name];
  if (value == null) return false;
  return ['1', 'true', 'yes'].contains(value.trim().toLowerCase());
}

/// Normalizes a string value (trims and returns null if empty).
String? _normalize(String? value) {
  if (value == null) return null;
  final trimmed = value.trim();
  return trimmed.isEmpty ? null : trimmed;
}

/// Exception thrown when a token has invalid format.
class InvalidTokenFormatException implements Exception {
  /// Creates an invalid token format exception.
  const InvalidTokenFormatException(this.message, this.source);
  
  /// The error message.
  final String message;
  
  /// The source of the invalid token.
  final String source;
  
  @override
  String toString() => 'InvalidTokenFormatException: $message (source: $source)';
}

/// Validates that a token has valid JWT structure (3 base64 parts).
/// 
/// Returns the validated token, or null if token was null/empty.
/// Throws [InvalidTokenFormatException] if the token is malformed.
String? validateTokenFormat(String? token, {String source = 'token'}) {
  if (token == null || token.trim().isEmpty) {
    return null;
  }
  
  final trimmed = token.trim();
  final parts = trimmed.split('.');
  
  if (parts.length != 3) {
    throw InvalidTokenFormatException(
      'Expected JWT with 3 parts (header.payload.signature), '
      'but got ${parts.length} part(s). '
      'Did you accidentally use an API key instead of a JWT token? '
      'Use "kumiho-cli login" to obtain a valid token.',
      source,
    );
  }
  
  // Basic check that each part is non-empty
  for (var i = 0; i < parts.length; i++) {
    if (parts[i].isEmpty) {
      throw InvalidTokenFormatException(
        'JWT part ${i + 1} is empty. The token may be corrupted or incomplete.',
        source,
      );
    }
  }
  
  return trimmed;
}

/// Loads the bearer token for gRPC calls.
///
/// Token loading priority:
/// 1. `KUMIHO_AUTH_TOKEN` environment variable
/// 2. Firebase ID token from credentials file
/// 3. Control Plane token from credentials file (if `KUMIHO_USE_CONTROL_PLANE_TOKEN=true`)
///
/// Returns `null` if no token is available.
/// Throws [InvalidTokenFormatException] if a token is found but has invalid format.
String? loadBearerToken() {
  // 1. Check environment variable first
  final envToken = _normalize(Platform.environment[AuthEnvVars.authToken]);
  if (envToken != null) {
    return validateTokenFormat(envToken, source: 'KUMIHO_AUTH_TOKEN');
  }

  // 2. Load from credentials file
  final credentials = loadCredentials();
  if (credentials == null) {
    return null;
  }

  // 3. Check preference for Control Plane token
  final preferCp = _envFlag(AuthEnvVars.useControlPlaneToken);
  if (preferCp && credentials.controlPlaneToken != null) {
    return validateTokenFormat(
      credentials.controlPlaneToken,
      source: 'control_plane_token',
    );
  }

  // 4. Prefer Firebase token
  if (credentials.idToken.isNotEmpty) {
    return validateTokenFormat(credentials.idToken, source: 'id_token');
  }

  // 5. Fallback to Control Plane token
  if (credentials.controlPlaneToken != null) {
    return validateTokenFormat(
      credentials.controlPlaneToken,
      source: 'control_plane_token',
    );
  }

  return null;
}

/// Loads the Firebase ID token for control-plane interactions.
///
/// Checks `KUMIHO_FIREBASE_ID_TOKEN` env var first, then credentials file.
String? loadFirebaseToken() {
  final envToken = _normalize(Platform.environment[AuthEnvVars.firebaseToken]);
  if (envToken != null) {
    return envToken;
  }

  final credentials = loadCredentials();
  return credentials?.idToken.isEmpty == false ? credentials!.idToken : null;
}

/// Result of loading a token with metadata.
class TokenLoadResult {
  /// Creates a token load result.
  const TokenLoadResult(this.token, this.source);

  /// The loaded token, or null if not available.
  final String? token;

  /// Description of where the token was loaded from.
  final String? source;

  /// Whether a token was loaded.
  bool get hasToken => token != null && token!.isNotEmpty;
}

/// Loads the bearer token with source information.
///
/// Returns a [TokenLoadResult] containing the token and its source.
TokenLoadResult loadBearerTokenWithSource() {
  // 1. Check environment variable
  final envToken = _normalize(Platform.environment[AuthEnvVars.authToken]);
  if (envToken != null) {
    return TokenLoadResult(envToken, 'KUMIHO_AUTH_TOKEN env var');
  }

  // 2. Load from credentials file
  final credentials = loadCredentials();
  if (credentials == null) {
    return const TokenLoadResult(null, null);
  }

  // 3. Check preference for Control Plane token
  final preferCp = _envFlag(AuthEnvVars.useControlPlaneToken);
  if (preferCp && credentials.controlPlaneToken != null) {
    return TokenLoadResult(
      credentials.controlPlaneToken,
      'Control Plane token from credentials file',
    );
  }

  // 4. Prefer Firebase token
  if (credentials.idToken.isNotEmpty) {
    return TokenLoadResult(
      credentials.idToken,
      'Firebase ID token from credentials file',
    );
  }

  // 5. Fallback to Control Plane token
  if (credentials.controlPlaneToken != null) {
    return TokenLoadResult(
      credentials.controlPlaneToken,
      'Control Plane token from credentials file',
    );
  }

  return const TokenLoadResult(null, null);
}
