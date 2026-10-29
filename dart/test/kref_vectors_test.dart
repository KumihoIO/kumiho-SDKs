// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Verifies the Dart SDK against the shared kref conformance corpus
/// (`spec/kref/vectors.json`).
///
/// The Dart SDK already splits an item kref at its LAST `/` and its LAST `.`
/// ([ItemApi.getItemByKref]), so this is a verification, not a change: for every
/// kref today's Python SDK accepts, the `GetItem` request the client sends must
/// be the corpus's `sdk_fix_request`, and a leaf with no `.` where an item is
/// required must be refused before anything is sent.
///
/// The only difference is the legacy `kref:///s/x.k` spelling: Dart drops the
/// empty segment and sends `/s` where the corpus has `//s`. The kumiho-server
/// normalizes both to the same space path (`normalize_space_path`), so the test
/// compares parent paths after that normalization.
///
/// The corpus is read from the repository root, never copied.
library;

import 'dart:convert';
import 'dart:io';

import 'package:grpc/grpc.dart';
import 'package:kumiho/kumiho.dart';
import 'package:test/test.dart';

/// Answers `GetItem` and records the requests; every other RPC is unimplemented.
class _RecordingService extends KumihoServiceBase {
  final List<List<String>> requests = [];

  @override
  Future<ItemResponse> getItem(ServiceCall call, GetItemRequest request) async {
    requests.add([request.parentPath, request.itemName, request.kind]);
    return ItemResponse()
      ..itemName = request.itemName
      ..kind = request.kind;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) =>
      throw GrpcError.unimplemented('${invocation.memberName}');
}

/// kumiho-server `normalize_space_path`: `/` plus the path without leading or
/// trailing slashes.
String _normalize(String path) {
  final trimmed = path.trim().replaceAll(RegExp(r'^/+|/+$'), '');
  return trimmed.isEmpty ? '/' : '/$trimmed';
}

void main() {
  final vectorsFile = File('../spec/kref/vectors.json');
  final cases =
      (jsonDecode(vectorsFile.readAsStringSync()) as Map<String, dynamic>)['cases']
          as List<dynamic>;

  late Server server;
  late _RecordingService service;
  late KumihoClient client;

  setUp(() async {
    service = _RecordingService();
    server = Server.create(services: [service]);
    await server.serve(address: InternetAddress.loopbackIPv4, port: 0);
    client = KumihoClient(
      host: '127.0.0.1',
      port: server.port!,
      token: 'test-token',
      autoLoadToken: false,
    );
  });

  tearDown(() async {
    await client.channel.shutdown();
    await server.shutdown();
  });

  test('the corpus is the shared one', () {
    expect(cases.length, 133);
  });

  test('getItemByKref sends the corpus GetItem request for every accepted kref',
      () async {
    var sent = 0;
    for (final raw in cases) {
      final c = raw as Map<String, dynamic>;
      if (c['sdk_current_accepts'] != true) continue;
      final id = c['id'] as String;
      final input = c['input'] as String;
      final fixed =
          (c['sdk_fix_request'] as Map<String, dynamic>)['get_item_by_kref']
              as Map<String, dynamic>;
      service.requests.clear();

      if (fixed.containsKey('rpc')) {
        await client.getItemByKref(input);
        expect(service.requests.length, 1, reason: id);
        final got = service.requests.single;
        expect(_normalize(got[0]), _normalize(fixed['parent_path'] as String),
            reason: '$id parent_path');
        expect(got[1], fixed['item_name'], reason: '$id item_name');
        expect(got[2], fixed['kind'], reason: '$id kind');
        sent++;
      } else {
        // Refused before sending (decision 2 of 2026-10-29).
        await expectLater(
          client.getItemByKref(input),
          throwsA(isA<ArgumentError>()),
          reason: id,
        );
        expect(service.requests, isEmpty, reason: id);
      }
    }
    expect(sent, 51);
  });

  test('a leaf with no "." where an item is required is refused', () async {
    await expectLater(
        client.getItemByKref('kref://p/s.v1/x'), throwsA(isA<ArgumentError>()));
    expect(service.requests, isEmpty);
  });
  // kumiho-server rebuilds the key it matches as normalize_space_path(parent) +
  // "/" + name + "." + kind, and normalize_space_path trims whitespace and "/".
  // A server-returned item kref can hold a space segment that ends in whitespace
  // or an empty segment. [ItemApi.getItemByKref] has not changed since a7f155e:
  // it drops empty segments and sends every other segment as it is, so these
  // requests are byte-identical to the ones a7f155e sent.
  test('item krefs a server may return keep the request a7f155e sent', () async {
    const cases = <List<String>>[
      // kref, parent_path, item_name, kind
      ['kref://p/s /x.k', '/p/s ', 'x', 'k'],
      ['kref://p/s	/x.k', '/p/s	', 'x', 'k'],
      ['kref://p/s /x.k', '/p/s ', 'x', 'k'],
      ['kref://p/s　/x.k', '/p/s　', 'x', 'k'],
      ['kref://p//x.k', '/p', 'x', 'k'],
      ['kref://p/s//x.k', '/p/s', 'x', 'k'],
      ['kref://p /s/x.k', '/p /s', 'x', 'k'],
    ];
    for (final c in cases) {
      service.requests.clear();
      await client.getItemByKref(c[0]);
      expect(service.requests, [
        [c[1], c[2], c[3]],
      ], reason: c[0]);
    }
  });

  test('a huge revision does not break the lookup', () async {
    final huge = '1' * 5000;
    await client.getItemByKref('kref://p/s/x.k?r=$huge');
    expect(service.requests, [
      ['/p/s', 'x', 'k'],
    ]);
    // The Kref accessor reads the revision without throwing.
    expect(Kref('kref://p/s/x.k?r=$huge').revision, isNull);
  });
}
