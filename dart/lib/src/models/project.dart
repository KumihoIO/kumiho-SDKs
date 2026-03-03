// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Project model for Kumiho asset management.
///
/// This module provides the [Project] class, which represents the top-level
/// container for organizing assets in Kumiho.
library;

import '../generated/kumiho.pb.dart' as pb;
import 'base.dart';
import 'space.dart';
import 'item.dart';
import 'bundle.dart';
import 'paged_list.dart';

/// A Kumiho project—the top-level container for assets.
///
/// Projects are the root of the Kumiho hierarchy. Each project has its own
/// namespace for spaces and items, and manages access control and settings
/// independently. The [Project] class exposes ergonomic helpers for creating
/// and listing model-layer entities without exposing the protobuf surfaces
/// that back the gRPC transport.
///
/// ```dart
/// final project = await kumiho.getProject('my-project');
///
/// // Create spaces
/// final assets = await project.createSpace('assets');
/// final shots = await project.createSpace('shots');
///
/// // Create items
/// final hero = await project.createItem('hero', 'model');
///
/// // List all spaces
/// await for (final space in project.getSpaces(recursive: true)) {
///   print(space.path);
/// }
/// ```
class Project extends KumihoObject {
  /// Creates a [Project] from a protobuf response.
  Project(pb.ProjectResponse response, dynamic client) : super(client) {
    projectId = response.projectId;
    name = response.name;
    description = response.description;
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    updatedAt = response.updatedAt.isEmpty ? null : response.updatedAt;
    deprecated = response.deprecated;
    allowPublic = response.allowPublic;
  }

  /// The unique identifier for this project.
  late final String projectId;

  /// The URL-safe name of the project (e.g., "film-2024").
  late final String name;

  /// Human-readable description of the project.
  late final String description;

  /// ISO timestamp when the project was created.
  late final String? createdAt;

  /// ISO timestamp of the last update.
  late final String? updatedAt;

  /// Whether the project is deprecated (soft-deleted).
  late final bool deprecated;

  /// Whether anonymous read access is enabled.
  late final bool allowPublic;

  /// Creates a space within this project.
  ///
  /// ```dart
  /// final chars = await project.createSpace('characters');
  /// final heroes = await project.createSpace('heroes', parentPath: '/$projectName/characters');
  /// ```
  Future<Space> createSpace(String spaceName, {String? parentPath}) async {
    final baseParent = parentPath ?? '/$name';
    final response = await client.createSpace(baseParent, spaceName);
    return Space(response, client);
  }

  /// Creates a new item within this project.
  ///
  /// ```dart
  /// final hero = await project.createItem('hero', 'model');
  /// final texture = await project.createItem('skin', 'texture', parentPath: '/project/textures');
  /// ```
  Future<Item> createItem(
    String itemName,
    String kind, {
    String? parentPath,
  }) async {
    final baseParent = parentPath ?? '/$name';
    final response = await client.createItem(baseParent, itemName, kind);
    return Item(response, client);
  }

  /// Searches for items within this project.
  ///
  /// ```dart
  /// final items = await project.getItems(kindFilter: 'model');
  /// ```
  Future<PagedList<Item>> getItems({
    String? kindFilter,
    String? nameFilter,
    int? pageSize,
    String? cursor,
    bool includeDeprecated = false,
  }) async {
    final items = await client.itemSearch(
      name,
      nameFilter ?? '',
      kindFilter ?? '',
      pageSize: pageSize,
      cursor: cursor,
      includeDeprecated: includeDeprecated,
    );
    
    return PagedList(
      items.map<Item>((i) => Item(i, client)).toList(),
      nextCursor: items.nextCursor,
      totalCount: items.totalCount,
    );
  }

  /// Creates a new bundle within this project.
  ///
  /// Bundles are special items that aggregate other items.
  ///
  /// ```dart
  /// final release = await project.createBundle('release-v1');
  /// await release.addMember(hero.kref);
  /// ```
  Future<Bundle> createBundle(
    String bundleName, {
    String? parentPath,
    Map<String, String>? metadata,
  }) async {
    final baseParent = parentPath ?? '/$name';
    final response = await client.createBundle(baseParent, bundleName, metadata: metadata);
    return Bundle(response, client);
  }

  /// Gets a space by path relative to this project.
  ///
  /// ```dart
  /// final chars = await project.getSpace('characters');
  /// final heroes = await project.getSpace('characters/heroes');
  /// ```
  Future<Space> getSpace(String relativePath) async {
    final fullPath = '/$name/$relativePath';
    final response = await client.getSpace(fullPath);
    return Space(response, client);
  }

  /// Gets all child spaces of this project.
  ///
  /// If [recursive] is true, traverses the entire space tree depth-first
  /// and returns every space as a high-level [Space] model. This keeps the
  /// caller insulated from the raw gRPC paging responses.
  ///
  /// ```dart
  /// final spaces = await project.getSpaces();
  /// for (final space in spaces) {
  ///   print(space.path);
  /// }
  /// ```
  Future<List<Space>> getSpaces({bool recursive = false}) async {
    final spaceResponses = await client.getChildSpaces('/$name');
    final spaces = spaceResponses.map<Space>((s) => Space(s, client)).toList();

    if (recursive && spaces.isNotEmpty) {
      final allSpaces = <Space>[...spaces];
      for (final space in spaces) {
        final children = await space.getChildSpaces(recursive: true);
        allSpaces.addAll(children);
      }
      return allSpaces;
    }

    return spaces;
  }

  /// Updates the project description.
  ///
  /// ```dart
  /// await project.update(description: 'Updated description');
  /// ```
  Future<Project> update({String? description}) async {
    final response = await client.updateProject(name, description: description);
    return Project(response, client);
  }

  /// Soft-deletes (deprecates) or hard-deletes this project.
  ///
  /// ```dart
  /// await project.delete();        // Soft delete
  /// await project.delete(force: true);  // Hard delete
  /// ```
  Future<void> delete({bool force = false}) async {
    await client.deleteProject(name, force: force);
  }

  /// Sets the public access mode for this project.
  ///
  /// ```dart
  /// await project.setPublic(true);  // Enable public access
  /// ```
  Future<Project> setPublic(bool allowPublic) async {
    final response = await client.updateProject(name, allowPublic: allowPublic);
    return Project(response, client);
  }

  /// Alias for [setPublic] using the allow_public terminology.
  ///
  /// This exists because assigning `project.allowPublic = true` is not possible
  /// (the field is immutable) and callers often look for an explicit
  /// `setAllowPublic(...)` method.
  Future<Project> setAllowPublic(bool allowPublic) => setPublic(allowPublic);

  @override
  String toString() => "Project(name: '$name', id: '$projectId')";
}
