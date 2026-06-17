// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';
import '../models/paged_list.dart';

/// Space API mixin for managing hierarchical containers.
///
/// Spaces form the folder structure within a project. They can contain
/// other spaces (subspaces) and items, allowing you to organize assets
/// in a meaningful hierarchy.
///
/// ```dart
/// // Create a space
/// final space = await client.createSpace('/my-project', 'characters');
///
/// // Get a space
/// final space = await client.getSpace('/my-project/characters');
///
/// // List child spaces
/// final children = await client.getChildSpaces('/my-project');
///
/// // Update metadata
/// await client.updateSpaceMetadata(
///   'kref:///my-project/characters',
///   {'status': 'active'},
/// );
/// ```
mixin SpaceApi on KumihoClientBase {
  /// Creates a new space within a project or parent space.
  ///
  /// [parentPath] is the path where the space will be created
  /// (e.g., '/project-name' or '/project-name/parent-space').
  /// [spaceName] is the name of the new space.
  /// [existsError] controls whether to throw an error if the space
  /// already exists (default: `false`).
  Future<SpaceResponse> createSpace(
    String parentPath,
    String spaceName, {
    bool existsError = false,
  }) async {
    final request = CreateSpaceRequest()
      ..parentPath = parentPath
      ..spaceName = spaceName
      ..existsError = existsError;
    return stub.createSpace(request, options: callOptions);
  }

  /// Gets a space by its path or kref.
  ///
  /// [pathOrKref] can be either a path (e.g., '/project/space')
  /// or a kref URI (e.g., 'kref:///project/space').
  Future<SpaceResponse> getSpace(String pathOrKref) async {
    final request = GetSpaceRequest()..pathOrKref = pathOrKref;
    return stub.getSpace(request, options: callOptions);
  }

  /// Lists child spaces under a parent path.
  ///
  /// [parentPath] is the path to list children from.
  /// Use an empty string to list root-level spaces.
  /// Set [recursive] to `true` to include all nested spaces.
  /// [pageSize] and [cursor] enable pagination; when either is supplied the
  /// result is a [PagedList] exposing `nextCursor` and `totalCount`.
  Future<List<SpaceResponse>> getChildSpaces(
    String parentPath, {
    bool recursive = false,
    int? pageSize,
    String? cursor,
  }) async {
    final request = GetChildSpacesRequest()
      ..parentPath = parentPath
      ..recursive = recursive;

    if (pageSize != null || cursor != null) {
      request.pagination = PaginationRequest()
        ..pageSize = pageSize ?? 100
        ..cursor = cursor ?? '';
    }

    final response = await stub.getChildSpaces(request, options: callOptions);

    if (response.hasPagination()) {
      return PagedList(
        response.spaces,
        nextCursor: response.pagination.nextCursor,
        totalCount: response.pagination.totalCount,
      );
    }
    return response.spaces;
  }

  /// Deletes a space.
  ///
  /// By default, deletion fails if the space contains items.
  /// Set [force] to `true` to delete even if the space has contents.
  ///
  /// **Warning**: Force deletion removes all items within the space.
  Future<StatusResponse> deleteSpace(
    String path, {
    bool force = false,
  }) async {
    final request = DeleteSpaceRequest()
      ..path = path
      ..force = force;
    return stub.deleteSpace(request, options: callOptions);
  }

  /// Updates metadata for a space.
  ///
  /// [kref] is the space's kref URI.
  /// [metadata] is a map of key-value pairs to set or update.
  /// Existing keys are overwritten; new keys are added.
  Future<SpaceResponse> updateSpaceMetadata(
    String kref,
    Map<String, String> metadata,
  ) async {
    final request = UpdateMetadataRequest()
      ..kref = Kref(uri: kref)
      ..metadata.addAll(metadata);
    return stub.updateSpaceMetadata(request, options: callOptions);
  }
}
