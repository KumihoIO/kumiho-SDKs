// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Unit tests for Kumiho Dart SDK API operations.
///
/// These tests verify the API interface and data structures without
/// requiring a live Kumiho server connection.
library;

import 'package:test/test.dart';
import 'package:kumiho/kumiho.dart';
import 'mock_helpers.dart';

void main() {
  group('Project API', () {
    test('mockProjectResponse has expected fields', () {
      final response = mockProjectResponse();

      expect(response.name, equals('demo'));
      expect(response.description, equals(''));
    });

    test('mockProjectResponse accepts custom values', () {
      final response = mockProjectResponse(
        name: 'custom-project',
        description: 'Custom description',
      );

      expect(response.name, equals('custom-project'));
      expect(response.description, equals('Custom description'));
    });

    test('mockGetProjectsResponse returns multiple projects', () {
      final projects = [
        mockProjectResponse(name: 'project-0'),
        mockProjectResponse(name: 'project-1'),
        mockProjectResponse(name: 'project-2'),
      ];
      final response = mockGetProjectsResponse(projects: projects);

      expect(response.projects.length, equals(3));
      expect(response.projects[0].name, equals('project-0'));
      expect(response.projects[1].name, equals('project-1'));
      expect(response.projects[2].name, equals('project-2'));
    });

    test('Project.setAllowPublic calls updateProject', () async {
      final calls = <Map<String, Object?>>[];

      final fakeClient = _FakeProjectClient((projectId, {allowPublic, description}) {
        calls.add({
          'projectId': projectId,
          'allowPublic': allowPublic,
          'description': description,
        });
        return mockProjectResponse(projectId: projectId, name: 'demo', allowPublic: allowPublic ?? false);
      });

      final project = Project(mockProjectResponse(projectId: 'p1', name: 'demo', allowPublic: false), fakeClient);
      final updated = await project.setAllowPublic(true);

      expect(updated.allowPublic, isTrue);
      expect(calls.length, equals(1));
      expect(calls.single['projectId'], equals('demo'));
      expect(calls.single['allowPublic'], equals(true));
    });
  });

  group('Space API', () {
    test('mockSpaceResponse has expected fields', () {
      final response = mockSpaceResponse(path: 'test-project/test-space');

      expect(response.name, equals('test-space'));
      expect(response.path, equals('test-project/test-space'));
    });

    test('mockSpaceResponse accepts custom values', () {
      final response = mockSpaceResponse(
        name: 'characters',
        path: 'film-2024/characters',
      );

      expect(response.name, equals('characters'));
      expect(response.path, equals('film-2024/characters'));
    });
  });

  group('Item API', () {
    test('mockItemResponse has expected fields', () {
      final response = mockItemResponse(
        krefUri: 'kref://project/space/hero.model',
        name: 'hero.model',
        itemName: 'hero',
        kind: 'model',
      );

      expect(response.itemName, equals('hero'));
      expect(response.kind, equals('model'));
    });

    test('mockItemResponse accepts custom values', () {
      final response = mockItemResponse(
        krefUri: 'kref://project/space/villain.texture',
        name: 'villain.texture',
        itemName: 'villain',
        kind: 'texture',
      );

      expect(response.itemName, equals('villain'));
      expect(response.kind, equals('texture'));
    });

    test('mockGetItemsResponse returns multiple items', () {
      final items = [
        mockItemResponse(
          krefUri: 'kref://p/s/item-0.model',
          name: 'item-0.model',
          itemName: 'item-0',
          kind: 'model',
        ),
        mockItemResponse(
          krefUri: 'kref://p/s/item-1.model',
          name: 'item-1.model',
          itemName: 'item-1',
          kind: 'model',
        ),
      ];
      final response = mockGetItemsResponse(items: items);

      expect(response.items.length, equals(2));
      expect(response.items[0].itemName, equals('item-0'));
      expect(response.items[1].itemName, equals('item-1'));
    });
  });

  group('Revision API', () {
    test('mockRevisionResponse has expected fields', () {
      final response = mockRevisionResponse(
        krefUri: 'kref://project/space/item.model?r=1',
        itemKrefUri: 'kref://project/space/item.model',
      );

      expect(response.number, equals(1));
      expect(response.author, equals('test_author'));
    });

    test('mockRevisionResponse accepts custom values', () {
      final response = mockRevisionResponse(
        krefUri: 'kref://project/space/item.model?r=5',
        itemKrefUri: 'kref://project/space/item.model',
        number: 5,
        author: 'john.doe',
      );

      expect(response.number, equals(5));
      expect(response.author, equals('john.doe'));
    });
  });

  group('Artifact API', () {
    test('mockArtifactResponse has expected fields', () {
      final response = mockArtifactResponse(
        krefUri: 'kref://project/space/item.model?r=1&a=mesh',
        revisionKrefUri: 'kref://project/space/item.model?r=1',
        location: '/assets/hero/mesh.fbx',
      );

      expect(response.name, equals('mesh'));
      expect(response.location, equals('/assets/hero/mesh.fbx'));
    });

    test('mockArtifactResponse accepts custom values', () {
      final response = mockArtifactResponse(
        krefUri: 'kref://project/space/item.model?r=1&a=textures',
        revisionKrefUri: 'kref://project/space/item.model?r=1',
        location: 'smb://server/textures/hero_diffuse.png',
        name: 'textures',
      );

      expect(response.name, equals('textures'));
      expect(response.location, equals('smb://server/textures/hero_diffuse.png'));
    });
  });

  group('Edge API', () {
    test('EdgeType constants are defined', () {
      expect(EdgeType.dependsOn, equals('DEPENDS_ON'));
      expect(EdgeType.derivedFrom, equals('DERIVED_FROM'));
      expect(EdgeType.referenced, equals('REFERENCED'));
      expect(EdgeType.contains, equals('CONTAINS'));
      expect(EdgeType.createdFrom, equals('CREATED_FROM'));
    });

    test('mockEdge creates valid edge', () {
      final edge = mockEdge(
        sourceKrefUri: 'kref://project/space/a.model?r=1',
        targetKrefUri: 'kref://project/space/b.texture?r=1',
        edgeType: EdgeType.dependsOn,
      );

      expect(edge.sourceKref.uri, equals('kref://project/space/a.model?r=1'));
      expect(edge.targetKref.uri, equals('kref://project/space/b.texture?r=1'));
      expect(edge.edgeType, equals('DEPENDS_ON'));
    });
  });

  group('Kref integration', () {
    test('mockPbKref creates valid protobuf Kref', () {
      final kref = mockPbKref('kref://test-project/test-space/test-item.model');

      expect(kref.uri, equals('kref://test-project/test-space/test-item.model'));
    });

    test('Kref class parsing from mock uri', () {
      final krefUri = 'kref://project/space/item.model?r=3';
      final dartKref = Kref(krefUri);

      expect(dartKref.project, equals('project'));
      expect(dartKref.space, equals('space'));
      expect(dartKref.itemName, equals('item'));
      expect(dartKref.kind, equals('model'));
      expect(dartKref.revision, equals(3));
    });

    test('get item from revision kref', () {
      // Simulate test_get_item_from_revision_kref from Python tests
      final revisionKref = Kref('kref://project/models/hero.model?r=5');
      final itemKref = revisionKref.itemKref;

      expect(itemKref.uri, equals('kref://project/models/hero.model'));
      expect(itemKref.revision, isNull);
    });

    test('extract revision kref from artifact kref', () {
      final artifactKref = Kref('kref://project/models/hero.model?r=2&a=mesh');
      final revisionKref = artifactKref.revisionKref;

      expect(revisionKref?.uri, equals('kref://project/models/hero.model?r=2'));
      expect(revisionKref?.artifactName, isNull);
    });
  });

  group('Status response', () {
    test('mockStatusResponse indicates success', () {
      final response = mockStatusResponse();

      expect(response.success, isTrue);
    });

    test('mockStatusResponse can indicate failure', () {
      final response = mockStatusResponse(success: false);

      expect(response.success, isFalse);
    });
  });

  group('Tenant API', () {
    test('mockTenantUsageResponse has expected fields', () {
      final response = mockTenantUsageResponse();

      expect(response.nodeCount, equals(Int64(100)));
      expect(response.nodeLimit, equals(Int64(10000)));
      expect(response.tenantId, equals('tenant-1'));
    });

    test('mockTenantUsageResponse accepts custom values', () {
      final response = mockTenantUsageResponse(
        nodeCount: 500,
        nodeLimit: 50000,
        tenantId: 'my-tenant',
      );

      expect(response.nodeCount, equals(Int64(500)));
      expect(response.nodeLimit, equals(Int64(50000)));
      expect(response.tenantId, equals('my-tenant'));
    });
  });

  group('Pagination', () {
    test('mockGetItemsResponse supports pagination fields', () {
      final items = [
        mockItemResponse(
            krefUri: 'kref://p1/s1/i1',
            name: 'i1',
            itemName: 'i1',
            kind: 'model'),
        mockItemResponse(
            krefUri: 'kref://p1/s1/i2',
            name: 'i2',
            itemName: 'i2',
            kind: 'model'),
      ];
      final response = mockGetItemsResponse(
        items: items,
        nextCursor: 'cursor_123',
        totalCount: 10,
      );

      expect(response.items.length, equals(2));
      expect(response.pagination.nextCursor, equals('cursor_123'));
      expect(response.pagination.totalCount, equals(10));
    });

    test('PagedList behaves like a list and has metadata', () {
      final items = ['a', 'b', 'c'];
      final pagedList = PagedList(items, nextCursor: 'next_page', totalCount: 100);

      expect(pagedList.length, equals(3));
      expect(pagedList[0], equals('a'));
      expect(pagedList.nextCursor, equals('next_page'));
      expect(pagedList.totalCount, equals(100));
      
      // Verify list methods work
      expect(pagedList.contains('b'), isTrue);
      expect(pagedList.map((e) => e.toUpperCase()).toList(), equals(['A', 'B', 'C']));
    });
  });
}

class _FakeProjectClient {
  _FakeProjectClient(this._updateProject);

  final ProjectResponse Function(
    String projectId, {
    bool? allowPublic,
    String? description,
  }) _updateProject;

  Future<ProjectResponse> updateProject(
    String projectId, {
    bool? allowPublic,
    String? description,
  }) async {
    return _updateProject(projectId, allowPublic: allowPublic, description: description);
  }
}
