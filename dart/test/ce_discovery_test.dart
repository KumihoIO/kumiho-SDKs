// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'dart:io';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:kumiho/discovery.dart';
import 'package:test/test.dart';

/// A stub [http.Client] that returns a canned response for any request,
/// so the CE liveness probe can be exercised without a real network.
class _StubClient extends http.BaseClient {
  _StubClient(this.statusCode, this.body);

  final int statusCode;
  final String body;

  Uri? lastRequestUrl;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    lastRequestUrl = request.url;
    final bytes = Uint8List.fromList(body.codeUnits);
    return http.StreamedResponse(Stream.value(bytes), statusCode);
  }
}

/// A stub that always throws (simulates connection refused / timeout).
class _FailingClient extends http.BaseClient {
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) {
    throw const SocketException('connection refused');
  }
}

void main() {
  group('resolveLocalCeEndpoint (default loopback candidate)', () {
    test('accepts a loopback server reporting self_hosted_ce', () async {
      final stub = _StubClient(200, '{"deployment_mode":"self_hosted_ce"}');

      final target = await resolveLocalCeEndpoint(httpClient: stub);

      expect(target, equals(kDefaultLocalCeTarget));
      expect(target, equals('127.0.0.1:9190'));
      // Liveness probe uses HTTP GET /api/_live, not the gRPC channel.
      expect(stub.lastRequestUrl?.path, equals('/api/_live'));
      expect(stub.lastRequestUrl?.scheme, equals('http'));
    });

    test('rejects when deployment_mode is not self_hosted_ce', () async {
      final stub = _StubClient(200, '{"deployment_mode":"cloud"}');

      final target = await resolveLocalCeEndpoint(httpClient: stub);

      expect(target, isNull);
    });

    test('rejects when deployment_mode is missing', () async {
      final stub = _StubClient(200, '{"status":"ok"}');

      final target = await resolveLocalCeEndpoint(httpClient: stub);

      expect(target, isNull);
    });

    test('rejects on non-2xx/3xx status', () async {
      final stub = _StubClient(503, '{"deployment_mode":"self_hosted_ce"}');

      final target = await resolveLocalCeEndpoint(httpClient: stub);

      expect(target, isNull);
    });

    test('rejects on non-JSON body', () async {
      final stub = _StubClient(200, 'not json at all');

      final target = await resolveLocalCeEndpoint(httpClient: stub);

      expect(target, isNull);
    });

    test('rejects when the probe throws (no server listening)', () async {
      final target = await resolveLocalCeEndpoint(httpClient: _FailingClient());

      expect(target, isNull);
    });
  });

  group('clientFromLocalCe', () {
    test('returns null when no CE server responds', () async {
      final client = await clientFromLocalCe(httpClient: _FailingClient());

      expect(client, isNull);
    });

    test('returns a tokenless client when a CE server is present', () async {
      final stub = _StubClient(200, '{"deployment_mode":"self_hosted_ce"}');

      final client = await clientFromLocalCe(httpClient: stub);

      expect(client, isNotNull);
      // Tokenless: no auth token loaded for the loopback CE path.
      expect(client!.token, isNull);
      await client.shutdownAsync();
    });
  });

  group('loopback-only normalisation (env-driven, subprocess)', () {
    // Platform.environment is read-only within a process, so candidate
    // resolution from env vars is exercised in a child Dart process.
    final dart = Platform.resolvedExecutable;
    final script = 'test/ce_discovery_probe_script.dart';

    Future<ProcessResult> runProbe(Map<String, String> env) {
      return Process.run(
        dart,
        ['run', script],
        environment: env,
        workingDirectory: Directory.current.path,
      );
    }

    test('accepts an explicit loopback endpoint (127.0.0.1)', () async {
      final result =
          await runProbe({'KUMIHO_LOCAL_SERVER_ENDPOINT': '127.0.0.1:7777'});

      expect(result.exitCode, equals(0), reason: result.stderr.toString());
      expect(result.stdout.toString().trim(), equals('RESULT:127.0.0.1:7777'));
    });

    test('accepts localhost and ::1 loopback hosts', () async {
      final localhost =
          await runProbe({'KUMIHO_LOCAL_SERVER_ENDPOINT': 'localhost:8200'});
      expect(localhost.stdout.toString().trim(), equals('RESULT:localhost:8200'));

      final ipv6 =
          await runProbe({'KUMIHO_LOCAL_SERVER_ENDPOINT': '[::1]:8300'});
      expect(ipv6.stdout.toString().trim(), equals('RESULT:[::1]:8300'));
    });

    test('rejects a non-loopback endpoint host', () async {
      final result =
          await runProbe({'KUMIHO_LOCAL_SERVER_ENDPOINT': '8.8.8.8:9190'});

      expect(result.exitCode, equals(0), reason: result.stderr.toString());
      final out = result.stdout.toString().trim();
      expect(out, startsWith('ERROR:'));
      expect(out, contains('localhost'));
    });

    test('rejects a public hostname endpoint', () async {
      final result = await runProbe(
          {'KUMIHO_LOCAL_SERVER_ENDPOINT': 'evil.example.com:9190'});

      final out = result.stdout.toString().trim();
      expect(out, startsWith('ERROR:'));
    });

    test('port env forces 127.0.0.1 and accepts a numeric port', () async {
      final result = await runProbe({'KUMIHO_LOCAL_SERVER_PORT': '12345'});

      expect(result.stdout.toString().trim(), equals('RESULT:127.0.0.1:12345'));
    });

    test('non-numeric port env is an error', () async {
      final result = await runProbe({'KUMIHO_LOCAL_SERVER_PORT': 'abc'});

      final out = result.stdout.toString().trim();
      expect(out, startsWith('ERROR:'));
      expect(out, contains('numeric'));
    });

    test('out-of-range port env (0) is an error', () async {
      final result = await runProbe({'KUMIHO_LOCAL_SERVER_PORT': '0'});

      final out = result.stdout.toString().trim();
      expect(out, startsWith('ERROR:'));
      expect(out, contains('between 1 and 65535'));
    });

    test('out-of-range port env (>65535) is an error', () async {
      final result = await runProbe({'KUMIHO_LOCAL_SERVER_PORT': '99999'});

      final out = result.stdout.toString().trim();
      expect(out, startsWith('ERROR:'));
      expect(out, contains('between 1 and 65535'));
    });

    test('a non-finite timeout env falls back to the default (no crash)',
        () async {
      final result = await runProbe({
        'KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS': 'NaN',
      });

      // The stub server always reports CE, so resolution must succeed with the
      // default candidate rather than throwing on NaN.round().
      expect(result.exitCode, equals(0), reason: result.stderr.toString());
      expect(result.stdout.toString().trim(), equals('RESULT:127.0.0.1:9190'));
    });
  });
}
