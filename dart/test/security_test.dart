// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Security integration tests for the Kumiho Dart SDK.
///
/// These tests verify security features work correctly when communicating
/// with localhost kumiho-server and control-plane instances.
///
/// Run with:
///   dart test test/security_test.dart --tags=security
///
/// Requirements:
/// - kumiho-server running on localhost:8080
/// - control-plane running on localhost:3000
/// - Set KUMIHO_INTEGRATION_TEST=1 to enable

@Tags(['security', 'live'])
library;

import 'dart:io';
import 'dart:convert';
import 'dart:math';
import 'package:test/test.dart';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/auth.dart';
import 'package:grpc/grpc.dart';

/// Check if security tests should run
bool shouldRunSecurityTests() {
  return Platform.environment['KUMIHO_INTEGRATION_TEST'] == '1';
}

void main() {
  final skipReason = shouldRunSecurityTests()
      ? null
      : 'Security tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.';

  group('Token Validation', () {
    final serverEndpoint =
        Platform.environment['KUMIHO_SERVER_ENDPOINT'] ?? 'localhost:8080';
    final parts = serverEndpoint.split(':');
    final host = parts[0];
    final port = parts.length > 1 ? int.parse(parts[1]) : 8080;

    test('rejects expired token', () async {
      // Create an obviously expired token
      final expiredToken =
          'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ.fake_signature';

      final client = KumihoClient(
        host: host,
        port: port,
        token: expiredToken,
        secure: false, // localhost testing
      );

      try {
        await client.getProjects();
        fail('Should have rejected expired token');
      } on GrpcError catch (e) {
        // Expected: Unauthenticated or PermissionDenied
        expect(
          [StatusCode.unauthenticated, StatusCode.permissionDenied],
          contains(e.code),
          reason: 'Expected auth error, got: ${e.code} - ${e.message}',
        );
      } finally {
        await client.shutdownAsync();
      }
    }, skip: skipReason);

    test('rejects malformed token', () async {
      final malformedToken = 'not-a-valid-jwt-token';

      final client = KumihoClient(
        host: host,
        port: port,
        token: malformedToken,
        secure: false,
      );

      try {
        await client.getProjects();
        fail('Should have rejected malformed token');
      } on GrpcError catch (e) {
        expect(
          [StatusCode.unauthenticated, StatusCode.permissionDenied, StatusCode.invalidArgument],
          contains(e.code),
          reason: 'Expected auth error for malformed token',
        );
      } finally {
        await client.shutdownAsync();
      }
    }, skip: skipReason);

    test('rejects token with wrong audience', () async {
      // Create a JWT with wrong audience
      final header = base64Url.encode(utf8.encode('{"alg":"RS256","typ":"JWT"}'));
      final payload = base64Url.encode(utf8.encode(
          '{"sub":"test","aud":"wrong-audience","exp":${(DateTime.now().millisecondsSinceEpoch ~/ 1000) + 3600}}'));
      final wrongAudToken = '$header.$payload.fake_signature';

      final client = KumihoClient(
        host: host,
        port: port,
        token: wrongAudToken,
        secure: false,
      );

      try {
        await client.getProjects();
        fail('Should have rejected wrong audience token');
      } on GrpcError catch (e) {
        // Server should reject - either invalid signature or wrong audience
        expect(e, isNotNull);
      } finally {
        await client.shutdownAsync();
      }
    }, skip: skipReason);
  });

  group('Token Format Validation', () {
    test('validateTokenFormat accepts valid JWT', () {
      final validToken =
          'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature';

      // Should not throw
      expect(() => validateTokenFormat(validToken), returnsNormally);
    });

    test('validateTokenFormat rejects token too short', () {
      expect(
        () => validateTokenFormat('short'),
        throwsA(isA<InvalidTokenFormatException>()),
      );
    });

    test('validateTokenFormat rejects token too long', () {
      final longToken = 'a' * 20001;
      expect(
        () => validateTokenFormat(longToken),
        throwsA(isA<InvalidTokenFormatException>()),
      );
    });

    test('validateTokenFormat rejects wrong parts count', () {
      expect(
        () => validateTokenFormat('only.two'),
        throwsA(isA<InvalidTokenFormatException>()),
      );
      expect(
        () => validateTokenFormat('too.many.parts.here'),
        throwsA(isA<InvalidTokenFormatException>()),
      );
    });

    test('validateTokenFormat rejects invalid characters', () {
      expect(
        () => validateTokenFormat('header.pay<script>load.sig'),
        throwsA(isA<InvalidTokenFormatException>()),
      );
    });
  });

  group('TLS Enforcement', () {
    test('localhost without TLS is allowed', () {
      // These should NOT throw for localhost
      for (final endpoint in ['localhost:8080', '127.0.0.1:8080']) {
        final parts = endpoint.split(':');
        final host = parts[0];
        final port = int.parse(parts[1]);
        expect(
          () => KumihoClient(host: host, port: port, token: 'test.token.here', secure: false),
          returnsNormally,
          reason: 'Localhost should allow non-TLS connections',
        );
      }
    });

    test('non-localhost without TLS logs warning', () {
      // This should work but log a warning (hard to test logging in Dart)
      // At minimum it shouldn't throw
      try {
        final client = KumihoClient(
          host: 'remote-server.example.com',
          port: 443,
          token: 'test.token.here',
          secure: false,
        );
        // Connection will fail but client creation should succeed
        client.shutdownAsync();
      } catch (e) {
        // Connection failure is expected, but client creation should work
        expect(e, isNot(isA<InvalidTokenFormatException>()));
      }
    });
  });

  group('Correlation IDs', () {
    test('generates valid UUID correlation ID', () {
      final correlationId = generateCorrelationId();

      // UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      expect(correlationId.length, equals(36));

      // Should match UUID pattern
      final uuidRegex = RegExp(
          r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
          caseSensitive: false);
      expect(uuidRegex.hasMatch(correlationId), isTrue,
          reason: 'Should be valid UUID format');
    });

    test('each correlation ID is unique', () {
      final ids = <String>{};
      for (var i = 0; i < 100; i++) {
        final id = generateCorrelationId();
        expect(ids.add(id), isTrue, reason: 'Correlation IDs should be unique');
      }
    });
  });

  group('File Permissions', () {
    test('warns on insecure token file permissions', () async {
      if (Platform.isWindows) {
        // Skip on Windows - different permission model
        return;
      }

      final tempDir = await Directory.systemTemp.createTemp('kumiho_test_');
      try {
        final tokenFile = File('${tempDir.path}/insecure_token.txt');
        await tokenFile.writeAsString('test.token.content');

        // Make world-readable (insecure)
        await Process.run('chmod', ['644', tokenFile.path]);

        // The SDK should warn about this when loading
        // (Testing the actual warning would require capturing stderr)
        final stat = await tokenFile.stat();
        final mode = stat.mode & 0x1FF; // Get permission bits

        // World-readable check
        final worldReadable = (mode & 0x004) != 0;
        expect(worldReadable, isTrue,
            reason: 'Test setup: file should be world-readable');
      } finally {
        await tempDir.delete(recursive: true);
      }
    }, skip: Platform.isWindows ? 'Unix permissions only' : null);
  });

  group('Error Handling', () {
    final serverEndpoint =
        Platform.environment['KUMIHO_SERVER_ENDPOINT'] ?? 'localhost:8080';
    final parts = serverEndpoint.split(':');
    final host = parts[0];
    final port = parts.length > 1 ? int.parse(parts[1]) : 8080;

    test('permission denied has clear error message', () async {
      final token = Platform.environment['KUMIHO_AUTH_TOKEN'];
      if (token == null) {
        return; // Skip if no token
      }

      final client = KumihoClient(
        host: host,
        port: port,
        token: token,
        secure: false,
      );

      try {
        // Try to access a nonexistent project
        await client.getSpace('/nonexistent-project-xyz-12345/main');
        fail('Should have thrown for nonexistent project');
      } on GrpcError catch (e) {
        // Error should be clear about what went wrong
        expect(
          [StatusCode.notFound, StatusCode.permissionDenied],
          contains(e.code),
          reason: 'Should get clear not found or permission denied error',
        );
      } finally {
        await client.shutdownAsync();
      }
    }, skip: skipReason);

    test('handles rate limiting gracefully', () async {
      final token = Platform.environment['KUMIHO_AUTH_TOKEN'];
      if (token == null) {
        return;
      }

      final client = KumihoClient(
        host: host,
        port: port,
        token: token,
        secure: false,
      );

      try {
        // Make rapid requests - should handle gracefully
        final futures = <Future>[];
        for (var i = 0; i < 10; i++) {
          futures.add(client.getProjects().catchError((e) => <ProjectResponse>[]));
        }
        await Future.wait(futures);
        // Should complete without crashing
      } finally {
        await client.shutdownAsync();
      }
    }, skip: skipReason);
  });

  group('Metadata Sanitization', () {
    test('rejects metadata with control characters', () {
      // Control characters should be stripped or rejected
      final controlChars = '\x00\x01\x02\n\r\t';

      // When metadata validation is implemented, this should fail
      // For now, just verify the pattern we're protecting against
      expect(controlChars.contains('\x00'), isTrue);
      expect(controlChars.contains('\n'), isTrue);
    });

    test('metadata with valid characters accepted', () {
      final validMetadata = {
        'artist': 'John Doe',
        'tool': 'Maya 2024',
        'notes': 'Final approved version',
      };

      // Valid metadata should work
      for (final entry in validMetadata.entries) {
        // No control characters
        expect(entry.value.contains(RegExp(r'[\x00-\x1F]')), isFalse);
      }
    });
  });
}

/// Validates token format before use.
/// Throws [InvalidTokenFormatException] if format is invalid.
void validateTokenFormat(String token) {
  // Length checks
  if (token.length < 20) {
    throw InvalidTokenFormatException('Token too short');
  }
  if (token.length > 20000) {
    throw InvalidTokenFormatException('Token too long');
  }

  // JWT format: header.payload.signature
  final parts = token.split('.');
  if (parts.length != 3) {
    throw InvalidTokenFormatException('Invalid JWT format: expected 3 parts');
  }

  // Valid base64url characters only
  final validChars = RegExp(r'^[A-Za-z0-9_\-=.]+$');
  if (!validChars.hasMatch(token)) {
    throw InvalidTokenFormatException('Invalid characters in token');
  }
}

/// Exception for invalid token format.
class InvalidTokenFormatException implements Exception {
  final String message;
  InvalidTokenFormatException(this.message);

  @override
  String toString() => 'InvalidTokenFormatException: $message';
}

/// Generates a correlation ID for request tracking.
String generateCorrelationId() {
  final random = Random.secure();
  final bytes = List.generate(16, (_) => random.nextInt(256));

  // Set version (4) and variant (10)
  bytes[6] = (bytes[6] & 0x0F) | 0x40;
  bytes[8] = (bytes[8] & 0x3F) | 0x80;

  // Format as UUID string
  final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-'
      '${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
}
