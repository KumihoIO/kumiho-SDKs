// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Bundle API mixin for managing item collections.
///
/// Bundles are special items that aggregate other items. They provide a way
/// to group related items together and maintain an audit trail of membership
/// changes through revision history.
///
/// The "bundle" kind is reserved and cannot be created manually via createItem.
///
/// ```dart
/// // Create a bundle
/// final bundle = await client.createBundle(
///   '/my-project/shots',
///   'shot-001-assets',
///   metadata: {'shot': '001'},
/// );
///
/// // Add items to bundle
/// await client.addBundleMember(
///   bundle.kref.uri,
///   'kref://my-project/models/hero.model',
/// );
///
/// // Get current members
/// final members = await client.getBundleMembers(bundle.kref.uri);
///
/// // Get membership history
/// final history = await client.getBundleHistory(bundle.kref.uri);
/// ```
mixin BundleApi on KumihoClientBase {
  /// Creates a new bundle item.
  ///
  /// [parentPath] is the space path where the bundle will be created.
  /// [bundleName] is the name of the bundle.
  /// [metadata] is optional key-value pairs to attach.
  ///
  /// Returns an ItemResponse with kind='bundle'.
  Future<ItemResponse> createBundle(
    String parentPath,
    String bundleName, {
    Map<String, String>? metadata,
  }) async {
    final request = CreateBundleRequest()
      ..parentPath = parentPath
      ..bundleName = bundleName;
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    return stub.createBundle(request, options: callOptions);
  }

  /// Adds an item as a member of a bundle.
  ///
  /// [bundleKref] is the bundle's kref URI.
  /// [memberItemKref] is the item's kref URI to add.
  /// [metadata] is optional audit metadata for this operation.
  ///
  /// This creates a new bundle revision tracking the addition.
  Future<AddBundleMemberResponse> addBundleMember(
    String bundleKref,
    String memberItemKref, {
    Map<String, String>? metadata,
  }) async {
    final request = AddBundleMemberRequest()
      ..bundleKref = Kref(uri: bundleKref)
      ..memberItemKref = Kref(uri: memberItemKref);
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    return stub.addBundleMember(request, options: callOptions);
  }

  /// Removes an item from a bundle.
  ///
  /// [bundleKref] is the bundle's kref URI.
  /// [memberItemKref] is the item's kref URI to remove.
  /// [metadata] is optional audit metadata for this operation.
  ///
  /// This creates a new bundle revision tracking the removal.
  Future<RemoveBundleMemberResponse> removeBundleMember(
    String bundleKref,
    String memberItemKref, {
    Map<String, String>? metadata,
  }) async {
    final request = RemoveBundleMemberRequest()
      ..bundleKref = Kref(uri: bundleKref)
      ..memberItemKref = Kref(uri: memberItemKref);
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    return stub.removeBundleMember(request, options: callOptions);
  }

  /// Gets the current members of a bundle.
  ///
  /// [bundleKref] is the bundle's kref URI.
  /// [revisionNumber] is optional; if provided, gets members at that revision.
  /// If not provided, returns current (latest) membership.
  Future<GetBundleMembersResponse> getBundleMembers(
    String bundleKref, {
    int? revisionNumber,
  }) async {
    final request = GetBundleMembersRequest()..bundleKref = Kref(uri: bundleKref);
    if (revisionNumber != null) {
      request.revisionNumber = revisionNumber;
    }
    return stub.getBundleMembers(request, options: callOptions);
  }

  /// Gets the membership history of a bundle.
  ///
  /// Returns a chronological list of all membership changes (additions
  /// and removals) with audit information.
  Future<GetBundleHistoryResponse> getBundleHistory(String bundleKref) async {
    final request = GetBundleHistoryRequest()..bundleKref = Kref(uri: bundleKref);
    return stub.getBundleHistory(request, options: callOptions);
  }
}
