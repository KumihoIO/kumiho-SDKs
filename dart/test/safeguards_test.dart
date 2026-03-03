// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Safeguard tests for Kumiho Dart SDK.
///
/// These tests verify edge type validation and security constraints.
/// Matches the Python SDK's test_safeguards.py pattern.
library;

import 'package:test/test.dart';
import 'package:kumiho/kumiho.dart';
import 'mock_helpers.dart';

void main() {
  group('EdgeType validation', () {
    test('EdgeType constants match proto values', () {
      // Verify the edge type constants match what the server expects
      expect(EdgeType.dependsOn, equals('DEPENDS_ON'));
      expect(EdgeType.derivedFrom, equals('DERIVED_FROM'));
      expect(EdgeType.referenced, equals('REFERENCED'));
      expect(EdgeType.contains, equals('CONTAINS'));
      expect(EdgeType.createdFrom, equals('CREATED_FROM'));
    });

    test('EdgeType.values contains all types', () {
      expect(EdgeType.values, contains('DEPENDS_ON'));
      expect(EdgeType.values, contains('DERIVED_FROM'));
      expect(EdgeType.values, contains('REFERENCED'));
      expect(EdgeType.values, contains('CONTAINS'));
      expect(EdgeType.values, contains('CREATED_FROM'));
    });

    test('isValidEdgeType validates correctly', () {
      expect(EdgeType.isValid('DEPENDS_ON'), isTrue);
      expect(EdgeType.isValid('DERIVED_FROM'), isTrue);
      expect(EdgeType.isValid('REFERENCED'), isTrue);
      expect(EdgeType.isValid('CONTAINS'), isTrue);
      expect(EdgeType.isValid('CREATED_FROM'), isTrue);

      expect(EdgeType.isValid('INVALID_TYPE'), isFalse);
      expect(EdgeType.isValid('depends_on'), isFalse); // case sensitive
      expect(EdgeType.isValid(''), isFalse);
    });
  });

  group('Kref security validation', () {
    test('rejects path traversal attempts', () {
      expect(
        () => Kref('kref://project/../other/item.kind'),
        throwsA(isA<KrefValidationError>()),
      );
    });

    test('rejects null bytes', () {
      expect(
        () => Kref('kref://project/space/item\x00.kind'),
        throwsA(isA<KrefValidationError>()),
      );
    });

    test('rejects other control characters', () {
      expect(
        () => Kref('kref://project/space/item\x1f.kind'),
        throwsA(isA<KrefValidationError>()),
      );
    });

    test('rejects invalid scheme', () {
      expect(
        () => Kref('http://project/space/item.kind'),
        throwsA(isA<KrefValidationError>()),
      );
    });

    test('accepts valid nested paths', () {
      expect(
        () => Kref('kref://project/a/b/c/d/item.kind'),
        returnsNormally,
      );
    });

    test('accepts valid revision and artifact refs', () {
      expect(
        () => Kref('kref://project/space/item.kind?r=1'),
        returnsNormally,
      );
      expect(
        () => Kref('kref://project/space/item.kind?r=1&a=mesh'),
        returnsNormally,
      );
    });
  });

  group('Mock response integrity', () {
    test('mockEdge preserves edge type', () {
      final edge = mockEdge(
        sourceKrefUri: 'kref://p/s/a.m?r=1',
        targetKrefUri: 'kref://p/s/b.t?r=1',
        edgeType: EdgeType.dependsOn,
      );

      expect(edge.edgeType, equals(EdgeType.dependsOn));
      expect(EdgeType.isValid(edge.edgeType), isTrue);
    });

    test('mockRevisionResponse preserves tags', () {
      final response = mockRevisionResponse(
        krefUri: 'kref://p/s/i.m?r=1',
        itemKrefUri: 'kref://p/s/i.m',
        tags: ['published', 'approved', 'latest'],
      );

      expect(response.tags, containsAll(['published', 'approved', 'latest']));
    });

    test('mockItemResponse preserves metadata', () {
      final response = mockItemResponse(
        krefUri: 'kref://p/s/hero.model',
        name: 'hero.model',
        itemName: 'hero',
        kind: 'model',
        metadata: {'author': 'john', 'version': '1.0'},
      );

      expect(response.metadata['author'], equals('john'));
      expect(response.metadata['version'], equals('1.0'));
    });
  });

  group('Tenant isolation', () {
    test('TenantUsageResponse tracks limits', () {
      final usage = mockTenantUsageResponse(
        nodeCount: 9500,
        nodeLimit: 10000,
        tenantId: 'tenant-abc',
      );

      expect(usage.nodeCount, equals(Int64(9500)));
      expect(usage.nodeLimit, equals(Int64(10000)));
      expect(usage.tenantId, equals('tenant-abc'));

      // Check usage percentage calculation
      final usagePercent = usage.nodeCount.toDouble() / usage.nodeLimit.toDouble() * 100;
      expect(usagePercent, equals(95.0));
    });
  });

  group('Impact analysis', () {
    test('ImpactAnalysisResponse handles truncation', () {
      final response = mockImpactAnalysisResponse(
        totalImpacted: 150,
        truncated: true,
      );

      expect(response.totalImpacted, equals(150));
      expect(response.truncated, isTrue);
    });

    test('ImpactAnalysisResponse non-truncated', () {
      final response = mockImpactAnalysisResponse(
        totalImpacted: 50,
        truncated: false,
      );

      expect(response.totalImpacted, equals(50));
      expect(response.truncated, isFalse);
    });
  });
}
