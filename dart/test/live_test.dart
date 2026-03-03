// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Integration tests for the Kumiho Dart SDK.
///
/// These tests require a running Kumiho server and valid authentication token.
///
/// Run with:
///   dart test test/live_test.dart --tags=live
///
/// Authentication is loaded automatically from:
/// 1. KUMIHO_AUTH_TOKEN environment variable
/// 2. ~/.kumiho/kumiho_authentication.json (from kumiho-cli login)

@Tags(['live'])
library;

import 'dart:io';
import 'package:test/test.dart';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/auth.dart';
import 'package:kumiho/src/discovery.dart';

/// Check if live integration tests should run.
bool shouldRunLiveTests() {
  return Platform.environment['KUMIHO_INTEGRATION_TEST'] == '1';
}

/// Generates a unique name with a prefix for test isolation.
String uniqueName(String prefix) {
  final timestamp = DateTime.now().millisecondsSinceEpoch;
  final random = timestamp.toRadixString(36).substring(0, 8);
  return '${prefix}_$random';
}

/// Test fixture for cleanup after tests.
class TestCleanup {
  final KumihoClient client;
  final List<dynamic> _objects = [];

  TestCleanup(this.client);

  void track(dynamic obj) {
    _objects.add(obj);
  }

  Future<void> cleanup() async {
    print('\nCleaning up ${_objects.length} objects...');
    // Reverse order: artifacts -> revisions -> items -> spaces -> projects
    for (final obj in _objects.reversed) {
      try {
        final type = obj.runtimeType.toString();
        if (obj is Project) {
          print('Deleting Project: ${obj.name}');
          await client.deleteProject(obj.name, force: true);
        } else if (obj is Space) {
          print('Deleting Space: ${obj.path}');
          await client.deleteSpace(obj.path, force: true);
        } else if (obj is Item) {
          print('Deleting Item: ${obj.kref.uri}');
          await client.deleteItem(obj.kref.uri, force: true);
        } else if (obj is Revision) {
          print('Deleting Revision: ${obj.kref.uri}');
          await client.deleteRevision(obj.kref.uri, force: true);
        } else if (obj is Artifact) {
          print('Deleting Artifact: ${obj.kref.uri}');
          await client.deleteArtifact(obj.kref.uri, force: true);
        }
        print('Successfully deleted $type');
      } catch (e) {
        print('Warning: Failed to cleanup ${obj.runtimeType}: $e');
      }
    }
    _objects.clear();
  }
}

void main() {
  final skipReason = shouldRunLiveTests()
      ? null
      : 'Live tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.';

  KumihoClient? client;
  TestCleanup? cleanup;

  setUpAll(() async {
    if (skipReason != null) return;

    // Use the auth module to load token automatically
    // Priority: env var -> credentials file
    final token = await loadBearerToken();
    if (token == null) {
      throw StateError(
        'Live tests require authentication. Either:\n'
        '  1. Set KUMIHO_AUTH_TOKEN environment variable\n'
        '  2. Run `kumiho-cli login` to cache credentials\n'
        '\nRun: dart test test/live_test.dart --tags=live',
      );
    }

    // Production-style flow: discover the correct data-plane via Control Plane.
    // Uses:
    // - Firebase ID token from ~/.kumiho/kumiho_authentication.json
    // - Control plane URL from env / credentials defaults
    // - server_url returned by /api/discovery/tenant
    client = await clientFromDiscovery(
      token: token,
      forceRefresh: true,
    );
  });

  setUp(() {
    final active = client;
    if (active == null) return;
    cleanup = TestCleanup(active);
  });

  tearDown(() async {
    final active = cleanup;
    if (active == null) return;
    await active.cleanup();
  });

  tearDownAll(() async {
    if (skipReason != null) return;
    final active = client;
    if (active == null) return;
    await active.shutdownAsync();
  });

  group('Full Creation Workflow', () {
    test('creates project, space, item, revision, and artifact', () async {
      final projectName = uniqueName('smoke_test_project');
      final spaceName = 'assets';
      final assetName = uniqueName('smoke_test_asset');

      // Create project
      final project = await client.newProject(projectName);
      cleanup.track(project);
      expect(project.name, equals(projectName));

      // Create space
      final space = await project.createSpace(spaceName);
      cleanup.track(space);
      expect(space.path, equals('/$projectName/$spaceName'));

      // Create item
      final item = await space.createItem(assetName, 'model');
      cleanup.track(item);
      expect(item.kref.uri, equals('kref://$projectName/$spaceName/$assetName.model'));

      // Create revision
      final revision = await item.createRevision();
      cleanup.track(revision);
      expect(revision.kref.uri, endsWith('?r=1'));

      // Create artifact
      final artifact = await revision.createArtifact('data', '/path/to/smoke_test.dat');
      cleanup.track(artifact);
      expect(artifact.kref.uri, endsWith('&a=data'));
      expect(artifact.location, equals('/path/to/smoke_test.dat'));
    });
  }, skip: skipReason);

  group('Artifact Operations', () {
    test('get_artifacts_by_location returns time-sorted list', () async {
      final projectName = uniqueName('loc_test_project');
      final assetName = uniqueName('loc_test_asset');
      final sharedLocation = '/mnt/data/test_data/${uniqueName('file')}.vdb';

      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);
      final item = await space.createItem(assetName, 'model');
      cleanup.track(item);

      final v1 = await item.createRevision();
      cleanup.track(v1);
      await Future.delayed(Duration(milliseconds: 100));
      final v2 = await item.createRevision();
      cleanup.track(v2);

      final res1 = await v1.createArtifact('model_data', sharedLocation);
      cleanup.track(res1);
      final res2 = await v2.createArtifact('model_data', sharedLocation);
      cleanup.track(res2);

      final foundArtifacts = await client.getArtifactsByLocation(sharedLocation);

      expect(foundArtifacts.length, greaterThanOrEqualTo(2));
      // Most recent artifact should be first
      final newest = foundArtifacts[0];
      expect(newest.kref.uri, equals(res2.kref.uri));
    });
  }, skip: skipReason);

  group('Edge Workflow', () {
    test('creates and retrieves edges between revisions', () async {
      final projectName = uniqueName('edge_proj');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);

      final modelItem = await space.createItem('character_model', 'model');
      cleanup.track(modelItem);
      final textureItem = await space.createItem('character_textures', 'texture');
      cleanup.track(textureItem);

      final modelV1 = await modelItem.createRevision();
      cleanup.track(modelV1);
      final textureV1 = await textureItem.createRevision();
      cleanup.track(textureV1);

      // Create edge: texture depends on model
      await textureV1.createEdgeTo(modelV1.kref.uri, EdgeType.dependsOn);

      // Retrieve and verify
      final sourceEdges = await textureV1.getEdges();
      expect(sourceEdges.length, greaterThanOrEqualTo(1));
      expect(sourceEdges[0].sourceKref.uri, equals(textureV1.kref.uri));
      expect(sourceEdges[0].targetKref.uri, equals(modelV1.kref.uri));
      expect(sourceEdges[0].edgeType, equals(EdgeType.dependsOn));
    });
  }, skip: skipReason);

  group('Revision Operations', () {
    test('peek_next_revision works correctly', () async {
      final projectName = uniqueName('peek_test_project');
      final assetName = uniqueName('peek_test_asset');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);
      final item = await space.createItem(assetName, 'rig');
      cleanup.track(item);

      // First peek should return 1
      final next1 = await client.peekNextRevision(item.kref.uri);
      expect(next1, equals(1));

      final v1 = await item.createRevision();
      cleanup.track(v1);
      expect(v1.number, equals(1));

      // After v1, should return 2
      final next2 = await client.peekNextRevision(item.kref.uri);
      expect(next2, equals(2));

      final v2 = await item.createRevision();
      cleanup.track(v2);
      expect(v2.number, equals(2));

      // After v2, should return 3
      final next3 = await client.peekNextRevision(item.kref.uri);
      expect(next3, equals(3));
    });

    test('get_latest_revision returns correct revision', () async {
      final projectName = uniqueName('latest_test_project');
      final assetName = uniqueName('latest_test_asset');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);
      final item = await space.createItem(assetName, 'rig');
      cleanup.track(item);

      // No revisions yet
      final noLatest = await item.getLatestRevision();
      expect(noLatest, isNull);

      // Create first revision
      final v1 = await item.createRevision();
      cleanup.track(v1);
      expect(v1.number, equals(1));

      final latest1 = await item.getLatestRevision();
      expect(latest1, isNotNull);
      expect(latest1!.number, equals(1));

      // Create second revision
      final v2 = await item.createRevision();
      cleanup.track(v2);
      expect(v2.number, equals(2));

      final latest2 = await item.getLatestRevision();
      expect(latest2, isNotNull);
      expect(latest2!.number, equals(2));
    });

    test('delete_latest_revision preserves latest resolution', () async {
      final projectName = uniqueName('delete_latest_project');
      final assetName = uniqueName('delete_latest_asset');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);
      final item = await space.createItem(assetName, 'rig');
      cleanup.track(item);

      final v1 = await item.createRevision();
      cleanup.track(v1);
      final v2 = await item.createRevision();

      // Delete the revision that currently holds the server-managed 'latest' tag.
      await client.deleteRevision(v2.kref.uri, force: true);

      // 'latest' should now resolve to v1.
      final resolved = await client.resolveKref(item.kref.uri, tag: 'latest');
      expect(resolved.number, equals(1));

      final latest = await item.getLatestRevision();
      expect(latest, isNotNull);
      expect(latest!.number, equals(1));
    });
  }, skip: skipReason);

  group('Tagging Workflow', () {
    test('full lifecycle of tagging a revision', () async {
      final project = await client.newProject(uniqueName('tag_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem('fx', 'cache');
      cleanup.track(item);
      final v1 = await item.createRevision();
      cleanup.track(v1);

      // Initial state: no tags
      final hasApproved = await client.hasTag(v1.kref.uri, 'approved');
      expect(hasApproved, isFalse);

      // Tag the revision
      await v1.tag('approved');
      final hasApprovedAfter = await client.hasTag(v1.kref.uri, 'approved');
      expect(hasApprovedAfter, isTrue);

      final wasTagged = await client.wasTagged(v1.kref.uri, 'approved');
      expect(wasTagged, isTrue);

      // Untag the revision
      await v1.untag('approved');
      final hasApprovedRemoved = await client.hasTag(v1.kref.uri, 'approved');
      expect(hasApprovedRemoved, isFalse);

      // was_tagged should still be true (historical check)
      final wasTaggedAfter = await client.wasTagged(v1.kref.uri, 'approved');
      expect(wasTaggedAfter, isTrue);
    });

    test('published tag can be moved before deleting a revision', () async {
      final project = await client.newProject(uniqueName('published_move_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem('hero', 'rig');
      cleanup.track(item);

      final v1 = await item.createRevision();
      cleanup.track(v1);
      final v2 = await item.createRevision();

      // Publish v2.
      await v2.tag('published');
      expect(await client.hasTag(v2.kref.uri, 'published'), isTrue);

      // Move published back to v1 (server enforces single active published tag).
      await v1.tag('published');
      expect(await client.hasTag(v1.kref.uri, 'published'), isTrue);
      expect(await client.hasTag(v2.kref.uri, 'published'), isFalse);

      // Now v2 is not published anymore and can be deleted.
      await client.deleteRevision(v2.kref.uri, force: true);
    });
  }, skip: skipReason);

  group('Metadata Operations', () {
    test('setting and updating metadata on all object types', () async {
      final project = await client.newProject(uniqueName('meta_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem(uniqueName('asset'), 'model');
      cleanup.track(item);
      final revision = await item.createRevision();
      cleanup.track(revision);
      final artifact = await revision.createArtifact('geo', '/path/to/file.abc');
      cleanup.track(artifact);

      // Update metadata (space uses path, others use kref)
      await client.updateSpaceMetadata(space.path, {'status': 'active'});
      await client.updateItemMetadata(item.kref.uri, {'pipeline_step': 'modeling'});
      await client.updateRevisionMetadata(revision.kref.uri, {'approved_by': 'lead'});
      await client.updateArtifactMetadata(artifact.kref.uri, {'format': 'alembic'});

      // Verify metadata was set (re-fetch objects)
      final updatedSpace = await client.getSpace(space.path);
      final updatedItem = await client.getItemByKref(item.kref.uri);
      final updatedRevision = await client.getRevision(revision.kref.uri);
      final updatedArtifact = await client.getArtifact(revision.kref.uri, artifact.name);

      expect(updatedSpace.metadata['status'], equals('active'));
      expect(updatedItem.metadata['pipeline_step'], equals('modeling'));
      expect(updatedRevision.metadata['approved_by'], equals('lead'));
      expect(updatedArtifact.metadata['format'], equals('alembic'));
    });
  }, skip: skipReason);

  group('Deprecation and Deletion', () {
    test('item deprecation workflow', () async {
      final project = await client.newProject(uniqueName('dep_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem('char', 'rig');
      cleanup.track(item);

      // Initial state
      expect(item.deprecated, isFalse);

      // Deprecate the item
      await item.setDeprecated(true);

      // Verify deprecation
      final reloaded = await client.getItem(space.path, 'char', 'rig');
      expect(reloaded.deprecated, isTrue);

      // Un-deprecate
      await client.setDeprecated(item.kref.uri, false);
      final reloaded2 = await client.getItem(space.path, 'char', 'rig');
      expect(reloaded2.deprecated, isFalse);
    });
  }, skip: skipReason);

  group('Navigation and Traversal', () {
    test('Janus parity: deprecation, default artifact, traversal', () async {
      final projectName = uniqueName('janus_proj');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);
      final item = await space.createItem('asset', 'model');
      cleanup.track(item);
      final revision = await item.createRevision();
      cleanup.track(revision);
      final artifact = await revision.createArtifact('main', '/path/to/file');
      cleanup.track(artifact);

      // 1. Deprecation
      expect(item.deprecated, isFalse);
      await item.setDeprecated(true);
      final itemReloaded = await client.getItem(space.path, 'asset', 'model');
      expect(itemReloaded.deprecated, isTrue);
      await item.setDeprecated(false);

      // 2. Default Artifact
      await revision.setDefaultArtifact(artifact.name);
      final revReloaded = await client.getRevision(revision.kref.uri);
      print('DEBUG: artifact.name="${artifact.name}"');
      print('DEBUG: revReloaded.defaultArtifact="${revReloaded.defaultArtifact}"');
      print('DEBUG: revReloaded.hasDefaultArtifact()=${revReloaded.hasDefaultArtifact()}');
      print('DEBUG: revReloaded.name="${revReloaded.name}"');
      print('DEBUG: revReloaded.username="${revReloaded.username}"');
      print('DEBUG: revReloaded.hasName()=${revReloaded.hasName()}');
      print('DEBUG: revReloaded raw response type=${revReloaded.runtimeType}');
      expect(revReloaded.defaultArtifact, equals(artifact.name));

      // 3. Traversal - From Artifact
      final artRevision = await artifact.revision;
      expect(artRevision.kref.uri, equals(revision.kref.uri));

      // 4. Traversal - From Revision
      final revItem = await revision.item;
      expect(revItem.kref.uri, equals(item.kref.uri));

      // 5. Traversal - From Item
      final itemSpace = await item.space;
      expect(itemSpace.path, equals(space.path));

      // 6. Traversal - From Space
      final spaceProject = await space.project;
      expect(spaceProject.name, equals(project.name));
    });
  }, skip: skipReason);

  group('Edge Direction', () {
    test('edges with different directions', () async {
      final project = await client.newProject(uniqueName('edge_dir_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem('asset', 'model');
      cleanup.track(item);
      final v1 = await item.createRevision();
      cleanup.track(v1);
      final v2 = await item.createRevision();
      cleanup.track(v2);

      // Create edge: v1 -> v2 (CREATED_FROM)
      await v1.createEdgeTo(v2.kref.uri, EdgeType.createdFrom);

      // Test Outgoing (from v1's perspective)
      final outgoing = await v1.getEdges(direction: EdgeDirection.OUTGOING);
      expect(outgoing.length, greaterThan(0));
      expect(outgoing[0].sourceKref.uri, equals(v1.kref.uri));
      expect(outgoing[0].targetKref.uri, equals(v2.kref.uri));

      // Test Incoming (from v2's perspective)
      final incoming = await v2.getEdges(direction: EdgeDirection.INCOMING);
      expect(incoming.length, greaterThan(0));
      expect(incoming[0].sourceKref.uri, equals(v1.kref.uri));
      expect(incoming[0].targetKref.uri, equals(v2.kref.uri));

      // Test Both
      final bothV1 = await v1.getEdges(direction: EdgeDirection.BOTH);
      expect(bothV1.length, greaterThan(0));
    });
  }, skip: skipReason);

  group('Item Search', () {
    test('search items with context and kind filter', () async {
      final projectName = uniqueName('search_proj');
      final project = await client.newProject(projectName);
      cleanup.track(project);
      final space = await project.createSpace(projectName);
      cleanup.track(space);

      final modelItem = await space.createItem('hero', 'model');
      cleanup.track(modelItem);
      final textureItem = await space.createItem('hero_tex', 'texture');
      cleanup.track(textureItem);

      // Search for models only
      final models = await client.searchItems(
        contextFilter: projectName,
        kindFilter: 'model',
      );

      expect(models.length, greaterThanOrEqualTo(1));
      expect(models.any((i) => i.itemName == 'hero'), isTrue);

      // Search for all items in project
      final allItems = await client.searchItems(contextFilter: projectName);
      expect(allItems.length, greaterThanOrEqualTo(2));
    });
  }, skip: skipReason);

  group('Published Revision Immutability', () {
    test('published revision and artifacts are immutable', () async {
      final project = await client.newProject(uniqueName('immutable_proj'));
      cleanup.track(project);
      final space = await project.createSpace(project.name);
      cleanup.track(space);
      final item = await space.createItem('shot', 'comp');
      cleanup.track(item);
      final v1 = await item.createRevision();
      cleanup.track(v1);
      final artifact = await v1.createArtifact('main', '/path/to/exr_seq');
      cleanup.track(artifact);

      // Tag as published
      await v1.tag('published');
      final v1Reloaded = await client.getRevision(v1.kref.uri);
      expect(v1Reloaded.published, isTrue);

      // Test immutability rules - these should fail
      await expectLater(
        client.updateRevisionMetadata(v1.kref.uri, {'new_key': 'new_val'}),
        throwsA(anything),
      );

      await expectLater(
        client.updateArtifactMetadata(artifact.kref.uri, {'new_key': 'new_val'}),
        throwsA(anything),
      );

      await expectLater(
        v1.untag('published'),
        throwsA(anything),
      );

      await expectLater(
        v1.createArtifact('mask', '/path/to/mask.png'),
        throwsA(anything),
      );
    }, skip: 'Immutability rules may vary by server configuration');
  }, skip: skipReason);
}
