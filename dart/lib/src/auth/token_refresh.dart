// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Token refresh utilities for Kumiho authentication.
///
/// This module provides functions to refresh Firebase ID tokens using
/// the stored refresh token from the credentials file.
///
/// Auto-refresh is opt-in via `KUMIHO_ENABLE_AUTO_REFRESH=true`.
library;

import 'dart:convert';
import 'dart:io' show Platform;
import 'package:http/http.dart' as http;

import 'token_loader.dart';

/// Exception thrown when token refresh fails.
class TokenRefreshError implements Exception {
  /// Creates a token refresh error.
  const TokenRefreshError(this.message);

  /// Error message.
  final String message;

  @override
  String toString() => 'TokenRefreshError: $message';
}

/// Result of a token refresh operation.
class TokenRefreshResult {
  /// Creates a token refresh result.
  const TokenRefreshResult({
    required this.idToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  /// The new Firebase ID token.
  final String idToken;

  /// The new refresh token (may be the same as before).
  final String refreshToken;

  /// Token validity duration in seconds.
  final int expiresIn;
}

/// Refreshes a Firebase ID token using a refresh token.
///
/// [apiKey] is the Firebase API key.
/// [refreshToken] is the stored refresh token.
///
/// Throws [TokenRefreshError] if the refresh fails.
Future<TokenRefreshResult> refreshFirebaseToken(
  String apiKey,
  String refreshToken,
) async {
  final url = Uri.parse(
    'https://securetoken.googleapis.com/v1/token?key=$apiKey',
  );

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: {
      'grant_type': 'refresh_token',
      'refresh_token': refreshToken,
    },
  );

  if (response.statusCode != 200) {
    throw TokenRefreshError(
      'Firebase token refresh failed: ${response.statusCode} ${response.body}',
    );
  }

  final data = jsonDecode(response.body) as Map<String, dynamic>;
  return TokenRefreshResult(
    idToken: data['id_token'] as String,
    refreshToken: data['refresh_token'] as String,
    expiresIn: int.tryParse(data['expires_in']?.toString() ?? '3600') ?? 3600,
  );
}

/// Exchanges a Firebase ID token for a Control Plane JWT.
///
/// [firebaseToken] is the Firebase ID token.
/// [controlPlaneUrl] is the Control Plane API URL (optional).
///
/// Returns `null` if the exchange fails (non-critical).
Future<({String token, int expiresAt})?> exchangeForControlPlaneToken(
  String firebaseToken, {
  String? controlPlaneUrl,
}) async {
  final baseUrl = controlPlaneUrl ?? getControlPlaneUrl();
  final url = Uri.parse('$baseUrl/api/control-plane/token');

  try {
    final response = await http.post(
      url,
      headers: {'Authorization': 'Bearer $firebaseToken'},
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      return null;
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return (
      token: data['token'] as String,
      expiresAt: (data['expires_at'] as num).toInt(),
    );
  } catch (_) {
    // CP exchange failure is non-critical
    return null;
  }
}

/// Auto-refreshes credentials if they're expired and auto-refresh is enabled.
///
/// Returns the refreshed credentials, or the original if refresh wasn't needed
/// or auto-refresh is disabled.
///
/// Set `KUMIHO_ENABLE_AUTO_REFRESH=true` to enable auto-refresh.
Future<KumihoCredentials?> autoRefreshCredentials(
  KumihoCredentials? credentials, {
  bool forceRefresh = false,
}) async {
  if (credentials == null) return null;

  // Check if auto-refresh is enabled
  final autoRefreshEnabled = _envFlag(AuthEnvVars.enableAutoRefresh);
  if (!autoRefreshEnabled && !forceRefresh) {
    return credentials;
  }

  // Check if token needs refresh
  if (credentials.isValid && !forceRefresh) {
    // ID token is still valid, but check CP token
    if (!credentials.isCpValid && credentials.idToken.isNotEmpty) {
      // Try to refresh CP token only
      final cpResult = await exchangeForControlPlaneToken(credentials.idToken);
      if (cpResult != null) {
        final updated = credentials.copyWith(
          controlPlaneToken: cpResult.token,
          cpExpiresAt: cpResult.expiresAt,
        );
        saveCredentials(updated);
        return updated;
      }
    }
    return credentials;
  }

  // Need to refresh ID token
  if (credentials.refreshToken.isEmpty) {
    return credentials; // Can't refresh without refresh token
  }

  try {
    final apiKey = credentials.apiKey.isNotEmpty
        ? credentials.apiKey
        : AuthDefaults.firebaseApiKey;

    final result = await refreshFirebaseToken(apiKey, credentials.refreshToken);
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;

    var updated = credentials.copyWith(
      idToken: result.idToken,
      refreshToken: result.refreshToken,
      expiresAt: now + result.expiresIn,
    );

    // Also refresh CP token
    final cpResult = await exchangeForControlPlaneToken(result.idToken);
    if (cpResult != null) {
      updated = updated.copyWith(
        controlPlaneToken: cpResult.token,
        cpExpiresAt: cpResult.expiresAt,
      );
    }

    saveCredentials(updated);
    return updated;
  } catch (e) {
    // Refresh failed, return original credentials
    return credentials;
  }
}

/// Checks if an environment variable flag is set to true.
bool _envFlag(String name) {
  final value = Platform.environment[name];
  if (value == null) return false;
  return ['1', 'true', 'yes'].contains(value.trim().toLowerCase());
}
