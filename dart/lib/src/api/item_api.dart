// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';
import '../models/paged_list.dart';

/// Item API mixin for managing versioned assets.
///
/// Items represent assets that can have multiple revisions, such as 3D models,
/// textures, workflows, or any other type of creative content. Each item
/// belongs to a space and is identified by a combination of name and kind.
///
/// The item's kref is a URI that uniquely identifies it:
/// `kref://project/space/item.kind`
///
/// ```dart
/// // Create an item
/// final item = await client.createItem('/my-project/characters', 'hero', 'model');
///
/// // Get an item by kref
/// final item = await client.getItemByKref('kref://my-project/characters/hero.model');
///
/// // Search for items
/// final models = await client.itemSearch('my-project', '', 'model');
///
/// // Deprecate an item
/// await client.setDeprecated(item.kref.uri, true);
/// ```
mixin ItemApi on KumihoClientBase {
  /// Creates a new item within a space.
  ///
  /// [parentPath] is the space path where the item will be created.
  /// [itemName] is the name of the item (e.g., 'hero').
  /// [kind] is the type of item (e.g., 'model', 'texture', 'workflow').
  /// [existsError] controls whether to throw an error if the item
  /// already exists (default: `true`).
  Future<ItemResponse> createItem(
    String parentPath,
    String itemName,
    String kind, {
    bool existsError = true,
  }) async {
    final request = CreateItemRequest()
      ..parentPath = parentPath
      ..itemName = itemName
      ..kind = kind
      ..existsError = existsError;
    return stub.createItem(request, options: callOptions);
  }

  /// Gets an item by its path components.
  ///
  /// [parentPath] is the space path containing the item.
  /// [itemName] is the item name.
  /// [kind] is the item kind.
  Future<ItemResponse> getItem(
    String parentPath,
    String itemName,
    String kind,
  ) async {
    final request = GetItemRequest()
      ..parentPath = parentPath
      ..itemName = itemName
      ..kind = kind;
    return stub.getItem(request, options: callOptions);
  }

  /// Gets an item by its kref URI.
  ///
  /// [kref] is the full kref URI (e.g., 'kref://project/space/item.kind').
  Future<ItemResponse> getItemByKref(String kref) async {
    // Parse the kref to extract components
    final sanitized = kref.startsWith('kref://')
        ? kref.substring('kref://'.length)
        : kref.startsWith('/')
            ? kref.substring(1)
            : kref;
    final pathPart = sanitized.split('?').first;
    final segments =
        pathPart.split('/').where((segment) => segment.isNotEmpty).toList();
    if (segments.isEmpty) {
      throw ArgumentError('Invalid item kref format: $kref');
    }

    final fullItemName = segments.removeLast();
    final dotIndex = fullItemName.lastIndexOf('.');
    if (dotIndex <= 0) {
      throw ArgumentError('Invalid item kref format - missing kind: $kref');
    }

    final itemName = fullItemName.substring(0, dotIndex);
    final kind = fullItemName.substring(dotIndex + 1);
    final parentPath = segments.isEmpty ? '/' : '/${segments.join('/')}';

    return getItem(parentPath, itemName, kind);
  }

  /// Lists items within a space with optional filtering.
  ///
  /// [parentPath] is the space path to list items from.
  /// [nameFilter] filters items by name pattern (supports wildcards).
  /// [kindFilter] filters items by kind.
  /// [pageSize] optional page size for pagination.
  /// [cursor] optional cursor for pagination.
  /// [includeDeprecated] whether to include deprecated items.
  Future<PagedList<ItemResponse>> getItems(
    String parentPath, {
    String? nameFilter,
    String? kindFilter,
    int? pageSize,
    String? cursor,
    bool includeDeprecated = false,
  }) async {
    final request = GetItemsRequest()
      ..parentPath = parentPath
      ..itemNameFilter = nameFilter ?? ''
      ..kindFilter = kindFilter ?? ''
      ..includeDeprecated = includeDeprecated;
      
    if (pageSize != null || cursor != null) {
      request.pagination = PaginationRequest()
        ..pageSize = pageSize ?? 100
        ..cursor = cursor ?? '';
    }

    final response = await stub.getItems(request, options: callOptions);
    
    return PagedList(
      response.items,
      nextCursor: response.hasPagination() ? response.pagination.nextCursor : null,
      totalCount: response.hasPagination() ? response.pagination.totalCount : null,
    );
  }

  /// Searches for items across the project.
  ///
  /// [contextFilter] filters by project or space path (supports wildcards).
  /// [nameFilter] filters by item name pattern.
  /// [kindFilter] filters by item kind.
  /// [pageSize] optional page size for pagination.
  /// [cursor] optional cursor for pagination.
  /// [includeDeprecated] whether to include deprecated items.
  Future<PagedList<ItemResponse>> itemSearch(
    String contextFilter,
    String nameFilter,
    String kindFilter, {
    int? pageSize,
    String? cursor,
    bool includeDeprecated = false,
  }) async {
    final request = ItemSearchRequest()
      ..contextFilter = contextFilter
      ..itemNameFilter = nameFilter
      ..kindFilter = kindFilter
      ..includeDeprecated = includeDeprecated;

    if (pageSize != null || cursor != null) {
      request.pagination = PaginationRequest()
        ..pageSize = pageSize ?? 100
        ..cursor = cursor ?? '';
    }

    final response = await stub.itemSearch(request, options: callOptions);
    
    return PagedList(
      response.items,
      nextCursor: response.hasPagination() ? response.pagination.nextCursor : null,
      totalCount: response.hasPagination() ? response.pagination.totalCount : null,
    );
  }

  /// Deletes an item.
  ///
  /// By default, deletion fails if the item has revisions.
  /// Set [force] to `true` to delete with all revisions.
  ///
  /// **Warning**: Force deletion removes all revisions and artifacts.
  Future<StatusResponse> deleteItem(
    String kref, {
    bool force = false,
  }) async {
    final request = DeleteItemRequest()
      ..kref = Kref(uri: kref)
      ..force = force;
    return stub.deleteItem(request, options: callOptions);
  }

  /// Updates metadata for an item.
  ///
  /// [kref] is the item's kref URI.
  /// [metadata] is a map of key-value pairs to set or update.
  Future<ItemResponse> updateItemMetadata(
    String kref,
    Map<String, String> metadata,
  ) async {
    final request = UpdateMetadataRequest()
      ..kref = Kref(uri: kref)
      ..metadata.addAll(metadata);
    return stub.updateItemMetadata(request, options: callOptions);
  }

  /// Sets the deprecated status of an item.
  ///
  /// Deprecated items are hidden from searches but not deleted.
  /// Set [deprecated] to `false` to restore an item.
  Future<StatusResponse> setDeprecated(
    String kref,
    bool deprecated,
  ) async {
    final request = SetDeprecatedRequest()
      ..kref = Kref(uri: kref)
      ..deprecated = deprecated;
    return stub.setDeprecated(request, options: callOptions);
  }
}
