// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Self-hosted Community Edition (CE) local discovery.
///
/// This module mirrors the Python SDK's CE bootstrap flow:
/// - Resolve a loopback gRPC target from `KUMIHO_LOCAL_SERVER_ENDPOINT` /
///   `KUMIHO_LOCAL_SERVER_PORT`, falling back to `127.0.0.1:9190`.
/// - Probe `http://<target>/api/_live` and accept the target only when the
///   server reports `deployment_mode == "self_hosted_ce"`.
/// - Build a tokenless [KumihoClient] for that endpoint, or return `null` when
///   no local CE server is present.
///
/// The loopback-only normalisation is a hard security invariant: a non-loopback
/// host is rejected outright so the implicit CE auto-probe can never be steered
/// at a remote address.
library;

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../kumiho.dart' show KumihoClient;

/// Environment variables used by local CE discovery.
///
/// The names and the default port are a cross-component contract shared with
/// the server (`kumiho-server` CE deployment defaults) and the installer
/// scripts. Do not change them.
class CeDiscoveryEnvVars {
  CeDiscoveryEnvVars._();

  /// Explicit loopback endpoint override (e.g. `127.0.0.1:9190`).
  static const String endpoint = 'KUMIHO_LOCAL_SERVER_ENDPOINT';

  /// Loopback port override (host is forced to `127.0.0.1`).
  static const String port = 'KUMIHO_LOCAL_SERVER_PORT';

  /// Probe timeout override, in seconds (parsed as a float).
  static const String timeoutSeconds = 'KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS';
}

/// Self-hosted CE default loopback port.
///
/// Must match the server's CE default and the installer scripts.
const int kDefaultLocalCePort = 9190;

/// Default loopback gRPC target for a self-hosted CE server.
const String kDefaultLocalCeTarget = '127.0.0.1:$kDefaultLocalCePort';

/// Raised when a CE environment variable is malformed.
class CeDiscoveryError implements Exception {
  /// Creates a new [CeDiscoveryError] with the given [message].
  const CeDiscoveryError(this.message);

  /// The error message.
  final String message;

  @override
  String toString() => 'CeDiscoveryError: $message';
}

/// Resolves a loopback CE gRPC target when a local server advertises CE mode.
///
/// Returns the first probe-passing loopback target, or `null` when no local CE
/// server responds. Candidate resolution order:
/// 1. `KUMIHO_LOCAL_SERVER_ENDPOINT` (loopback host required)
/// 2. `KUMIHO_LOCAL_SERVER_PORT` (host forced to `127.0.0.1`)
/// 3. The default `127.0.0.1:9190`
///
/// When [timeout] is omitted it is read from
/// `KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS` (min 50ms, default 500ms).
///
/// Throws [CeDiscoveryError] when an environment variable is malformed (for
/// example a non-numeric port, or a non-loopback endpoint host).
Future<String?> resolveLocalCeEndpoint({
  Duration? timeout,
  http.Client? httpClient,
}) async {
  final probeTimeout = timeout ?? _localCeTimeout();
  for (final target in _localCeCandidates()) {
    final ok = await _probeLocalCeCandidate(
      target,
      timeout: probeTimeout,
      httpClient: httpClient,
    );
    if (ok) {
      return target;
    }
  }
  return null;
}

/// Creates a tokenless [KumihoClient] for a loopback self-hosted CE server.
///
/// Returns `null` (does not throw) when no local CE server is present. The
/// returned client never loads an auth token, never runs discovery, and never
/// auto-logs-in — it is strictly the loopback CE path.
Future<KumihoClient?> clientFromLocalCe({
  Duration? timeout,
  http.Client? httpClient,
}) async {
  final target = await resolveLocalCeEndpoint(
    timeout: timeout,
    httpClient: httpClient,
  );
  if (target == null) {
    return null;
  }

  final (host, port) = _splitTarget(target);
  return KumihoClient(
    host: host,
    port: port,
    secure: false,
    autoLoadToken: false,
  );
}

Duration _localCeTimeout() {
  final raw = Platform.environment[CeDiscoveryEnvVars.timeoutSeconds];
  if (raw == null || raw.trim().isEmpty) {
    return const Duration(milliseconds: 500);
  }
  final seconds = double.tryParse(raw.trim());
  if (seconds == null || !seconds.isFinite) {
    return const Duration(milliseconds: 500);
  }
  // Clamp to a sane range: min 50ms (avoid a zero/negative probe timeout) and
  // max 1h (guard against a huge value overflowing the microsecond conversion).
  final clamped = seconds.clamp(0.05, 3600.0);
  return Duration(microseconds: (clamped * 1000000).round());
}

List<String> _localCeCandidates() {
  final endpoint = Platform.environment[CeDiscoveryEnvVars.endpoint];
  if (endpoint != null && endpoint.trim().isNotEmpty) {
    return [_normaliseLocalCeTarget(endpoint)];
  }

  final port = Platform.environment[CeDiscoveryEnvVars.port];
  if (port != null && port.trim().isNotEmpty) {
    final trimmed = port.trim();
    final parsed = int.tryParse(trimmed);
    if (parsed == null || !_isAllDigits(trimmed)) {
      throw CeDiscoveryError(
        '${CeDiscoveryEnvVars.port} must be a numeric loopback port',
      );
    }
    if (parsed < 1 || parsed > 65535) {
      throw CeDiscoveryError(
        '${CeDiscoveryEnvVars.port} must be between 1 and 65535',
      );
    }
    return ['127.0.0.1:$parsed'];
  }

  return [kDefaultLocalCeTarget];
}

bool _isAllDigits(String value) {
  if (value.isEmpty) return false;
  for (var i = 0; i < value.length; i++) {
    final c = value.codeUnitAt(i);
    if (c < 0x30 || c > 0x39) return false;
  }
  return true;
}

/// Normalises (and validates) an explicit endpoint env value to `host:port`.
///
/// Enforces the loopback-only security invariant using a real IP parser rather
/// than a regex.
String _normaliseLocalCeTarget(String raw) {
  final text = raw.trim();
  final uri = Uri.parse(text.contains('://') ? text : '//$text');

  final host = uri.host;
  if (host.isEmpty) {
    throw CeDiscoveryError(
      '${CeDiscoveryEnvVars.endpoint} must include a loopback host',
    );
  }
  if (!_isLoopbackHost(host)) {
    throw CeDiscoveryError(
      '${CeDiscoveryEnvVars.endpoint} must point to localhost, 127.0.0.1, '
      'or ::1',
    );
  }

  final port = uri.hasPort ? uri.port : kDefaultLocalCePort;
  if (port <= 0 || port > 65535) {
    throw CeDiscoveryError(
      '${CeDiscoveryEnvVars.endpoint} port must be between 1 and 65535',
    );
  }

  return '${_formatHostForTarget(host)}:$port';
}

bool _isLoopbackHost(String host) {
  if (host.toLowerCase() == 'localhost') {
    return true;
  }
  final addr = InternetAddress.tryParse(host);
  if (addr == null) {
    return false;
  }
  return addr.isLoopback;
}

String _formatHostForTarget(String host) {
  // IPv6 literals must be bracketed in a host:port target.
  if (host.contains(':') && !host.startsWith('[')) {
    return '[$host]';
  }
  return host;
}

/// Probes `http://<target>/api/_live` and returns true only when the response
/// is healthy (status < 400) and reports `deployment_mode == "self_hosted_ce"`.
///
/// Uses an HTTP client, not the gRPC channel. Any exception, timeout, non-JSON
/// body, or mismatched deployment mode yields `false`.
Future<bool> _probeLocalCeCandidate(
  String target, {
  required Duration timeout,
  http.Client? httpClient,
}) async {
  final url = Uri.parse('http://$target/api/_live');
  final client = httpClient ?? http.Client();
  final ownsClient = httpClient == null;
  try {
    final response = await client.get(url).timeout(timeout);
    if (response.statusCode >= 400) {
      return false;
    }
    final Object? body;
    try {
      body = jsonDecode(response.body);
    } catch (_) {
      return false;
    }
    if (body is! Map) {
      return false;
    }
    return body['deployment_mode'] == 'self_hosted_ce';
  } catch (_) {
    return false;
  } finally {
    if (ownsClient) {
      client.close();
    }
  }
}

(String, int) _splitTarget(String target) {
  // IPv6 bracketed form: [::1]:9190
  if (target.startsWith('[')) {
    final close = target.indexOf(']');
    final host = target.substring(1, close);
    final rest = target.substring(close + 1);
    final port = rest.startsWith(':')
        ? int.parse(rest.substring(1))
        : kDefaultLocalCePort;
    return (host, port);
  }
  final colon = target.lastIndexOf(':');
  if (colon < 0) {
    return (target, kDefaultLocalCePort);
  }
  final host = target.substring(0, colon);
  final port = int.parse(target.substring(colon + 1));
  return (host, port);
}
