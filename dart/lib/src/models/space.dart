// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Space model for Kumiho asset management.
///
/// This module provides the [Space] class, which represents hierarchical
/// containers for organizing items within a project.
library;

import '../generated/kumiho.pb.dart' as pb;
import 'base.dart';
import 'item.dart';
import 'bundle.dart';
import 'paged_list.dart';

/// A hierarchical container for organizing items in Kumiho.
///
/// Spaces form the folder structure within a project. They can contain
/// other spaces (subspaces) and items, allowing you to organize assets
/// in a meaningful hierarchy. The SDK exposes navigation helpers here so
/// callers can traverse the project tree without importing any of the
/// generated protobuf code.
///
/// ```dart
/// final assets = await project.createSpace('assets');
/// final models = await assets.createSpace('models');
/// final textures = await assets.createSpace('textures');
///
/// // Create items
/// final chair = await models.createItem('chair', 'model');
///
/// // Navigate hierarchy
/// final parent = await models.getParentSpace();  // Returns assets
/// ```
class Space extends KumihoObject {
  /// Creates a [Space] from a protobuf response.
  Space(pb.SpaceResponse response, dynamic client) : super(client) {
    path = response.path;
    name = response.name;
    type = response.type;
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    author = response.author;
    metadata = Map<String, String>.from(response.metadata);
    username = response.username;
  }

  /// The full path of the space (e.g., "/project/assets").
  late final String path;

  /// The name of this space (last component of path).
  late final String name;

  /// The type of space ("root" for project-level, "sub" for nested).
  late final String type;

  /// ISO timestamp when the space was created.
  late final String? createdAt;

  /// The user ID who created the space.
  late final String author;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// Display name of the creator.
  late final String username;

  /// Gets the project name from the path.
  String get projectName {
    final parts = path.split('/').where((s) => s.isNotEmpty).toList();
    return parts.isNotEmpty ? parts.first : '';
  }

  /// Gets the kref for this space.
  String get kref => 'kref://$projectName$path'.replaceFirst('kref:///', 'kref://');

  /// Gets the parent project of this space.
  ///
  /// ```dart
  /// final proj = await space.project;
  /// ```
  Future<dynamic> get project async {
    final projectList = await client.getProjects();
    final pb = projectList.firstWhere(
      (p) => p.name == projectName,
      orElse: () => throw KumihoError('Project not found: $projectName'),
    );
    // Return raw response; caller can wrap in Project if needed
    return pb;
  }

  /// Creates a new subspace within this space.
  ///
  /// Returns the high-level [Space] wrapper for the newly-created node.
  ///
  /// ```dart
  /// final models = await assets.createSpace('models');
  /// ```
  Future<Space> createSpace(String spaceName) async {
    final response = await client.createSpace(path, spaceName);
    return Space(response, client);
  }

  /// Creates a new item within this space.
  ///
  /// ```dart
  /// final hero = await models.createItem('hero', 'model');
  /// ```
  Future<Item> createItem(
    String itemName,
    String kind,
  ) async {
    final response = await client.createItem(path, itemName, kind);
    return Item(response, client);
  }

  /// Creates a new bundle within this space.
  ///
  /// ```dart
  /// final characterBundle = await characters.createBundle('main-chars');
  /// ```
  Future<Bundle> createBundle(
    String bundleName, {
    Map<String, String>? metadata,
  }) async {
    final response = await client.createBundle(path, bundleName, metadata: metadata);
    return Bundle(response, client);
  }

  /// Gets an item by name and kind from this space.
  ///
  /// ```dart
  /// final hero = await models.getItem('hero', 'model');
  /// ```
  Future<Item> getItem(String itemName, String kind) async {
    final krefUri = 'kref://$path/$itemName.$kind'.replaceFirst('kref:///', 'kref://');
    final response = await client.getItemByKref(krefUri);
    return Item(response, client);
  }

  /// Gets all items in this space.
  ///
  /// The optional [kindFilter] and [nameFilter] mirror the server-side
  /// filtering semantics and still return the model-layer [Item] wrappers.
  ///
  /// ```dart
  /// final items = await models.getItems();
  /// final textures = await assets.getItems(kindFilter: 'texture');
  /// ```
  Future<PagedList<Item>> getItems({
    String? kindFilter,
    String? nameFilter,
    int? pageSize,
    String? cursor,
    bool includeDeprecated = false,
  }) async {
    final items = await client.getItems(
      path,
      kindFilter: kindFilter,
      nameFilter: nameFilter,
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

  /// Gets all child spaces of this space.
  ///
  /// When [recursive] is true, traverses the space tree depth-first to
  /// return every descendant as a [Space] model. This mirrors
  /// [Project.getSpaces] to keep navigation consistent.
  ///
  /// ```dart
  /// final children = await assets.getChildSpaces();
  /// ```
  Future<List<Space>> getChildSpaces({bool recursive = false}) async {
    final spaceResponses = await client.getChildSpaces(path);
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

  /// Gets the parent space of this space.
  ///
  /// Returns `null` if this is a root-level space (directly under project).
  /// Use [parent] to get either the parent Space or Project.
  ///
  /// ```dart
  /// final parentSpace = await heroes.getParentSpace();
  /// if (parentSpace != null) {
  ///   print('Parent space: ${parentSpace.path}');
  /// }
  /// ```
  Future<Space?> getParentSpace() async {
    final parts = path.split('/').where((s) => s.isNotEmpty).toList();
    // If only 1 part (project name), this is root level - no parent space
    if (parts.length <= 1) return null;
    // If 2 parts (project/space), parent is project - no parent space
    if (parts.length == 2) return null;

    final parentPath = '/${parts.sublist(0, parts.length - 1).join('/')}';
    try {
      final response = await client.getSpace(parentPath);
      return Space(response, client);
    } catch (_) {
      return null;
    }
  }

  /// Gets the parent of this space.
  ///
  /// Returns the parent [Space] if this is a nested space, or the parent
  /// [Project] if this is a root-level space (directly under project).
  ///
  /// ```dart
  /// final parent = await space.parent;
  /// if (parent is Space) {
  ///   print('Parent space: ${parent.path}');
  /// } else if (parent is Project) {
  ///   print('Parent project: ${parent.name}');
  /// }
  /// ```
  Future<dynamic> get parent async {
    final parts = path.split('/').where((s) => s.isNotEmpty).toList();

    // Root-level space (e.g., /project/space) - parent is the project
    if (parts.length <= 2) {
      return project;
    }

    // Nested space - parent is another space
    final parentPath = '/${parts.sublist(0, parts.length - 1).join('/')}';
    try {
      final response = await client.getSpace(parentPath);
      return Space(response, client);
    } catch (_) {
      // Fallback to project if space lookup fails
      return project;
    }
  }

  /// Updates metadata for this space.
  ///
  /// The attributes are stored on the space path and immediately available
  /// to other callers.
  ///
  /// ```dart
  /// await space.updateMetadata({'status': 'active'});
  /// ```
  Future<void> updateMetadata(Map<String, String> metadata) async {
    await client.updateSpaceMetadata(path, metadata);
  }

  /// Deletes this space.
  ///
  /// If [force] is true, deletes even if the space contains items.
  ///
  /// ```dart
  /// await space.delete();
  /// await space.delete(force: true);  // Delete even if not empty
  /// ```
  Future<void> delete({bool force = false}) async {
    await client.deleteSpace(path, force: force);
  }

  @override
  String toString() => "Space(path: '$path')";
}
