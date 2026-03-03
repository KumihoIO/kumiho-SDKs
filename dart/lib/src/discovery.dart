// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Control-plane discovery utilities.
///
/// This module mirrors the Python/C++ SDK bootstrap flow:
/// - Call Control Plane discovery: POST `/api/discovery/tenant`
/// - Resolve the correct data-plane endpoint for the current user/tenant
/// - Return a ready-to-use [KumihoClient] configured with tenant routing.
library;

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../kumiho.dart' show KumihoClient;
import 'auth/token_loader.dart';
import 'auth/token_refresh.dart';

const String _defaultCacheKey = '__default__';

/// Environment variables used by discovery.
class DiscoveryEnvVars {
  DiscoveryEnvVars._();

  /// Overrides the discovery cache file path.
  static const String cacheFile = 'KUMIHO_DISCOVERY_CACHE_FILE';
}

/// A parsed discovery result.
class DiscoveryRecord {
  DiscoveryRecord({
    required this.tenantId,
    required this.serverUrl,
    required this.expiresAt,
  });

  final String tenantId;
  final Uri serverUrl;
  final DateTime expiresAt;

  bool get isExpired => DateTime.now().toUtc().isAfter(expiresAt);
}

File getDefaultDiscoveryCacheFile() {
  final env = Platform.environment[DiscoveryEnvVars.cacheFile];
  if (env != null && env.trim().isNotEmpty) {
    return File(env.trim());
  }
  return File('${getConfigDir().path}/discovery-cache.json');
}

Uri _buildDiscoveryUrl(String controlPlaneUrl) {
  final base = controlPlaneUrl.endsWith('/')
      ? controlPlaneUrl.substring(0, controlPlaneUrl.length - 1)
      : controlPlaneUrl;
  if (base.contains('/api/discovery/tenant')) {
    return Uri.parse(base);
  }
  return Uri.parse('$base/api/discovery/tenant');
}

DiscoveryRecord _parseDiscoveryRecord(Object decoded) {
  if (decoded is! Map<String, dynamic>) {
    throw const FormatException('Discovery response must be a JSON object');
  }

  final tenantId = (decoded['tenant_id'] as String?)?.trim() ?? '';
  if (tenantId.isEmpty) {
    throw const FormatException('Discovery response missing tenant_id');
  }

  final region = decoded['region'];
  String? serverUrlText;
  if (region is Map<String, dynamic>) {
    serverUrlText = region['server_url'] as String?;
  }
  serverUrlText ??= decoded['server_url'] as String?;

  final serverUrl = Uri.tryParse((serverUrlText ?? '').trim());
  if (serverUrl == null || serverUrl.host.isEmpty) {
    throw const FormatException('Discovery response missing region.server_url');
  }

  final cacheControl = decoded['cache_control'];
  if (cacheControl is! Map<String, dynamic>) {
    throw const FormatException('Discovery response missing cache_control');
  }

  final expiresAtText = cacheControl['expires_at'] as String?;
  if (expiresAtText == null || expiresAtText.trim().isEmpty) {
    throw const FormatException('Discovery response missing cache_control.expires_at');
  }

  // DateTime.parse supports ISO8601 with Z and timezone offsets.
  final expiresAt = DateTime.parse(expiresAtText).toUtc();

  return DiscoveryRecord(
    tenantId: tenantId,
    serverUrl: serverUrl,
    expiresAt: expiresAt,
  );
}

DiscoveryRecord? _loadFromCache(File cacheFile, String cacheKey) {
  if (!cacheFile.existsSync()) return null;

  try {
    final text = cacheFile.readAsStringSync();
    final decoded = jsonDecode(text);
    if (decoded is! Map<String, dynamic>) return null;

    final entry = decoded[cacheKey];
    if (entry == null) return null;

    final record = _parseDiscoveryRecord(entry);
    if (record.isExpired) return null;

    return record;
  } catch (_) {
    return null;
  }
}

void _storeToCache(File cacheFile, String cacheKey, Object jsonRecord) {
  cacheFile.parent.createSync(recursive: true);

  // Keep the cache format simple and compatible with other SDKs:
  // { "<cacheKey>": { ...discovery payload... } }
  final payload = <String, Object>{cacheKey: jsonRecord};
  final tmp = File('${cacheFile.path}.tmp');
  tmp.writeAsStringSync(const JsonEncoder.withIndent('  ').convert(payload));

  if (cacheFile.existsSync()) {
    cacheFile.deleteSync();
  }
  tmp.renameSync(cacheFile.path);
}

/// Resolves discovery info via Control Plane.
///
/// If [forceRefresh] is false, a non-expired cached result is used.
Future<DiscoveryRecord> discoverTenant({
  String? controlPlaneUrl,
  String? firebaseToken,
  String? tenantHint,
  bool forceRefresh = false,
  Duration timeout = const Duration(seconds: 10),
  File? cacheFile,
}) async {
  final cpUrl = (controlPlaneUrl == null || controlPlaneUrl.trim().isEmpty)
      ? getControlPlaneUrl()
      : controlPlaneUrl.trim();

  KumihoCredentials? credentials;
  String? token;

  if (firebaseToken != null && firebaseToken.trim().isNotEmpty) {
    token = firebaseToken.trim();
  } else {
    // Prefer explicit env var for discovery.
    final envToken = Platform.environment[AuthEnvVars.firebaseToken];
    if (envToken != null && envToken.trim().isNotEmpty) {
      token = envToken.trim();
    } else {
      // Fall back to cached credentials, optionally auto-refreshing.
      credentials = loadCredentials();
      final refreshed = await autoRefreshCredentials(credentials);
      credentials = refreshed ?? credentials;
      token = credentials?.idToken;
    }
  }

  if (token == null || token.trim().isEmpty) {
    throw ArgumentError(
      'A Firebase ID token is required for discovery. '
      'Set KUMIHO_FIREBASE_ID_TOKEN or login via kumiho-cli '
      '(~/.kumiho/kumiho_authentication.json).',
    );
  }

  final file = cacheFile ?? getDefaultDiscoveryCacheFile();
  final key = (tenantHint == null || tenantHint.trim().isEmpty)
      ? _defaultCacheKey
      : tenantHint.trim();

  if (!forceRefresh) {
    final cached = _loadFromCache(file, key);
    if (cached != null) return cached;
  }

  final url = _buildDiscoveryUrl(cpUrl);
  final body = <String, Object>{
    if (tenantHint != null && tenantHint.trim().isNotEmpty)
      'tenant_hint': tenantHint.trim(),
  };

  Future<http.Response> postWithToken(String bearer) {
    return http
        .post(
          url,
          headers: {
            'Authorization': 'Bearer $bearer',
            'Content-Type': 'application/json',
          },
          body: jsonEncode(body),
        )
        .timeout(timeout);
  }

  var response = await postWithToken(token);

  // If the cached token is expired/invalid, retry once after forcing refresh.
  if (response.statusCode == 401 &&
      firebaseToken == null &&
      (Platform.environment[AuthEnvVars.firebaseToken]?.trim().isEmpty ?? true) &&
      credentials != null &&
      credentials.refreshToken.isNotEmpty) {
    final bodyText = response.body;
    if (bodyText.contains('invalid_id_token')) {
      final refreshed = await autoRefreshCredentials(credentials, forceRefresh: true);
      if (refreshed != null && refreshed.idToken.isNotEmpty && refreshed.idToken != token) {
        token = refreshed.idToken;
        response = await postWithToken(token);
      }
    }
  }

  if (response.statusCode >= 400) {
    final snippet = response.body.length > 200
        ? response.body.substring(0, 200)
        : response.body;
    throw HttpException(
      'Discovery endpoint returned ${response.statusCode}: $snippet',
      uri: url,
    );
  }

  final decoded = jsonDecode(response.body);
  final record = _parseDiscoveryRecord(decoded);

  // Cache the raw JSON payload so we can re-parse it later.
  if (decoded is Map<String, dynamic>) {
    _storeToCache(file, key, decoded);
  }

  return record;
}

/// Creates a gRPC [KumihoClient] using Control Plane discovery.
///
/// - Uses discovery to find the correct data-plane endpoint.
/// - Sets `tenantId` so the base client injects `x-tenant-id`.
/// - If [token] is omitted, the client falls back to the standard token loader.
Future<KumihoClient> clientFromDiscovery({
  String? token,
  String? tenantHint,
  String? controlPlaneUrl,
  bool forceRefresh = false,
}) async {
  final record = await discoverTenant(
    controlPlaneUrl: controlPlaneUrl,
    tenantHint: tenantHint,
    forceRefresh: forceRefresh,
  );

  final uri = record.serverUrl;
  final secure = uri.scheme.toLowerCase() == 'https';
  final port = uri.hasPort ? uri.port : (secure ? 443 : 80);

  return KumihoClient(
    host: uri.host,
    port: port,
    secure: secure,
    token: token,
    tenantId: record.tenantId,
  );
}
