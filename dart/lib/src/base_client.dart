// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'dart:io';
import 'package:grpc/grpc.dart';
import 'package:grpc/grpc_connection_interface.dart';

import 'generated/kumiho.pbgrpc.dart';
import 'auth/token_loader.dart';
import 'auth/token_refresh.dart';

/// Shared gRPC channel and stub wiring for the Kumiho clients.
///
/// This base class handles connection management, authentication,
/// and provides the gRPC stub for making service calls.
///
/// ## Authentication
///
/// The client supports multiple authentication methods:
///
/// 1. **Explicit token**: Pass `token` parameter to constructor
/// 2. **Environment variable**: Set `KUMIHO_AUTH_TOKEN`
/// 3. **Credentials file**: Use `kumiho-cli login` to cache credentials
///
/// ## Auto-Refresh
///
/// Set `KUMIHO_ENABLE_AUTO_REFRESH=true` to enable automatic token refresh
/// when credentials expire. The SDK will use the stored refresh token.
abstract class KumihoClientBase {
  /// Creates a new Kumiho client base.
  ///
  /// Either provide an existing [clientChannel], or specify [host] and [port]
  /// to create a new channel.
  ///
  /// Use [token] to provide a Bearer token for authentication.
  /// Use [tenantId] to specify the tenant for anonymous public access.
  /// Set [secure] to `true` to use TLS (required for production).
  /// Set [autoLoadToken] to `true` (default) to load token from env/file.
  KumihoClientBase({
    ClientChannelBase? clientChannel,
    String? host,
    int? port,
    String? token,
    String? tenantId,
    ChannelOptions? options,
    bool secure = false,
    bool autoLoadToken = true,
  })  : _tenantId = tenantId,
        assert(
          clientChannel != null || (host != null && port != null),
          'Provide either an existing channel or host/port pair.',
        ),
        _ownsChannel = clientChannel == null {
    // Initialize token
    if (token != null) {
      _token = token;
      _tokenSource = 'constructor';
    } else if (autoLoadToken) {
      final result = loadBearerTokenWithSource();
      _token = result.token;
      _tokenSource = result.source;
    }

    // Initialize channel
    if (clientChannel != null) {
      channel = clientChannel;
    } else {
      // Security: Warn if connecting to non-localhost without TLS
      final isLocalhost = host!.toLowerCase() == 'localhost' ||
          host == '127.0.0.1' ||
          host == '::1';
      final requireTls = _envFlag('KUMIHO_REQUIRE_TLS');
      if (!isLocalhost && !secure) {
        if (requireTls) {
          throw ArgumentError(
            'TLS is required but connecting to $host without TLS. '
            'Set secure: true or use KUMIHO_SERVER_USE_TLS=true.',
          );
        }
        stderr.writeln(
          'Warning: Connecting to $host without TLS. Credentials may be '
          'transmitted in plaintext. Set secure: true for production.',
        );
      }
      channel = ClientChannel(
        host,
        port: port!,
        options: options ??
            ChannelOptions(
              credentials: secure
                  ? const ChannelCredentials.secure()
                  : const ChannelCredentials.insecure(),
            ),
      );
    }
    stub = KumihoServiceClient(channel);
  }

  /// Underlying gRPC channel.
  late final ClientChannelBase channel;

  /// Generated service stub for issuing RPCs.
  late final KumihoServiceClient stub;

  final bool _ownsChannel;

  /// Bearer token for authentication.
  String? _token;

  /// Source of the current token.
  String? _tokenSource;

  /// Tenant ID for anonymous public access.
  final String? _tenantId;

  /// Cached credentials for refresh.
  KumihoCredentials? _credentials;

  /// Get the current authentication token.
  String? get token => _token;

  /// Get the tenant ID for anonymous access.
  String? get tenantId => _tenantId;

  /// Get the source of the current token (for debugging).
  String? get tokenSource => _tokenSource;

  /// Update the authentication token.
  ///
  /// This will be used for all subsequent RPC calls.
  set token(String? value) {
    _token = value;
    _tokenSource = value != null ? 'manual' : null;
  }

  /// Creates [CallOptions] with authentication metadata and correlation ID.
  ///
  /// Call this to get options with the Bearer token and correlation ID injected.
  /// A unique correlation ID is generated per call for end-to-end tracing.
  CallOptions get callOptions {
    final correlationId = _generateCorrelationId();
    final metadata = <String, String>{
      'x-correlation-id': correlationId,
    };
    
    if (_token != null && _token!.isNotEmpty) {
      metadata['authorization'] = 'Bearer $_token';
    }
    
    // Add tenant ID for anonymous public access
    if (_tenantId != null && _tenantId!.isNotEmpty) {
      metadata['x-tenant-id'] = _tenantId!;
    }
    
    return CallOptions(metadata: metadata);
  }
  
  /// Generates a unique correlation ID for request tracing.
  static String _generateCorrelationId() {
    // Use current timestamp + random suffix for uniqueness
    final timestamp = DateTime.now().millisecondsSinceEpoch.toRadixString(16);
    final random = (DateTime.now().microsecond * 1000 + 
                   DateTime.now().millisecond).toRadixString(16).padLeft(4, '0');
    return 'kumiho-$timestamp$random';
  }

  /// Merges default call options with custom options.
  ///
  /// Use this when you need to add custom metadata or timeout
  /// while preserving authentication.
  CallOptions mergeOptions(CallOptions? custom) {
    final base = callOptions;
    if (custom == null) return base;
    return base.mergedWith(custom);
  }

  /// Refreshes the authentication token if needed.
  ///
  /// This method checks if the current token is expired and refreshes it
  /// if auto-refresh is enabled (`KUMIHO_ENABLE_AUTO_REFRESH=true`).
  ///
  /// Returns `true` if a refresh occurred, `false` otherwise.
  Future<bool> refreshTokenIfNeeded() async {
    // Check if auto-refresh is enabled
    final autoRefresh = _envFlag(AuthEnvVars.enableAutoRefresh);
    if (!autoRefresh) return false;

    // Load current credentials
    _credentials ??= loadCredentials();
    if (_credentials == null) return false;

    // Check if refresh is needed
    if (_credentials!.isValid) return false;

    // Perform refresh
    final refreshed = await autoRefreshCredentials(_credentials!, forceRefresh: true);
    if (refreshed != null && refreshed != _credentials) {
      _credentials = refreshed;
      _token = _envFlag(AuthEnvVars.useControlPlaneToken)
          ? refreshed.controlPlaneToken ?? refreshed.idToken
          : refreshed.idToken;
      _tokenSource = 'auto-refreshed';
      return true;
    }

    return false;
  }

  /// Force refresh the authentication token.
  ///
  /// This method forces a token refresh regardless of expiry status.
  /// Requires credentials with a valid refresh token.
  ///
  /// Throws [TokenRefreshError] if refresh fails.
  Future<void> forceRefreshToken() async {
    _credentials ??= loadCredentials();
    if (_credentials == null) {
      throw const TokenRefreshError('No credentials available for refresh');
    }
    if (_credentials!.refreshToken.isEmpty) {
      throw const TokenRefreshError('No refresh token available');
    }

    final refreshed = await autoRefreshCredentials(_credentials!, forceRefresh: true);
    if (refreshed != null) {
      _credentials = refreshed;
      _token = _envFlag(AuthEnvVars.useControlPlaneToken)
          ? refreshed.controlPlaneToken ?? refreshed.idToken
          : refreshed.idToken;
      _tokenSource = 'force-refreshed';
    } else {
      throw const TokenRefreshError('Token refresh failed');
    }
  }

  /// Shut down the channel if it was created by this client.
  ///
  /// Matches the original Flutter client's fire-and-forget behaviour.
  /// Call [shutdownAsync] if you need to await the channel closing.
  void shutdown() {
    if (_ownsChannel) {
      // Fire-and-forget to preserve compatibility with existing callers.
      channel.shutdown();
    }
  }

  /// Awaitable variant for callers that need to ensure the channel is closed.
  Future<void> shutdownAsync() async {
    if (_ownsChannel) {
      await channel.shutdown();
    }
  }

  /// Checks if an environment variable flag is set to true.
  static bool _envFlag(String name) {
    final value = Platform.environment[name];
    if (value == null) return false;
    return ['1', 'true', 'yes'].contains(value.trim().toLowerCase());
  }
}
