// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Attribute API mixin for granular metadata operations.
///
/// Attributes allow setting, getting, and deleting individual metadata
/// keys without replacing the entire metadata map. This is useful for
/// atomic updates to specific metadata fields.
///
/// Works on any entity type (Space, Item, Revision, Artifact) identified
/// by its kref.
///
/// ```dart
/// // Set a single attribute
/// await client.setAttribute(
///   'kref://project/models/hero.model?r=1',
///   'status',
///   'approved',
/// );
///
/// // Get a single attribute
/// final attr = await client.getAttribute(
///   'kref://project/models/hero.model?r=1',
///   'status',
/// );
/// if (attr.exists) {
///   print('Status: ${attr.value}');
/// }
///
/// // Delete an attribute
/// await client.deleteAttribute(
///   'kref://project/models/hero.model?r=1',
///   'temp_flag',
/// );
/// ```
mixin AttributeApi on KumihoClientBase {
  /// Sets a single metadata attribute.
  ///
  /// [kref] is the entity's kref URI.
  /// [key] is the attribute key.
  /// [value] is the attribute value.
  ///
  /// This performs an upsert—creates the key if it doesn't exist,
  /// or updates it if it does.
  Future<StatusResponse> setAttribute(
    String kref,
    String key,
    String value,
  ) async {
    final request = SetAttributeRequest()
      ..kref = Kref(uri: kref)
      ..key = key
      ..value = value;
    return stub.setAttribute(request, options: callOptions);
  }

  /// Gets a single metadata attribute.
  ///
  /// [kref] is the entity's kref URI.
  /// [key] is the attribute key to retrieve.
  ///
  /// Returns a response with `exists: false` if the key is not found.
  Future<GetAttributeResponse> getAttribute(
    String kref,
    String key,
  ) async {
    final request = GetAttributeRequest()
      ..kref = Kref(uri: kref)
      ..key = key;
    return stub.getAttribute(request, options: callOptions);
  }

  /// Deletes a single metadata attribute.
  ///
  /// [kref] is the entity's kref URI.
  /// [key] is the attribute key to delete.
  ///
  /// No error is thrown if the key doesn't exist.
  Future<StatusResponse> deleteAttribute(
    String kref,
    String key,
  ) async {
    final request = DeleteAttributeRequest()
      ..kref = Kref(uri: kref)
      ..key = key;
    return stub.deleteAttribute(request, options: callOptions);
  }
}
