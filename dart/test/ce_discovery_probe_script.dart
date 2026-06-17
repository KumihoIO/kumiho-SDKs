// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds
//
// Helper script invoked as a subprocess by ce_discovery_test.dart so that
// environment-variable driven candidate resolution can be exercised (Dart's
// Platform.environment is read-only within a single process).
//
// It calls resolveLocalCeEndpoint with a stub http.Client (no real network)
// and prints one of:
//   ERROR:<message>   — a CeDiscoveryError was thrown
//   RESULT:<target>   — the resolved target
//   RESULT:null       — no candidate matched

import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:kumiho/discovery.dart';

/// A stub client that always reports a healthy self-hosted CE server.
class _AlwaysCe extends http.BaseClient {
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final body = Uint8List.fromList(
      '{"deployment_mode":"self_hosted_ce"}'.codeUnits,
    );
    return http.StreamedResponse(Stream.value(body), 200);
  }
}

Future<void> main() async {
  try {
    final target = await resolveLocalCeEndpoint(httpClient: _AlwaysCe());
    print('RESULT:${target ?? 'null'}');
  } on CeDiscoveryError catch (e) {
    print('ERROR:${e.message}');
  }
}
