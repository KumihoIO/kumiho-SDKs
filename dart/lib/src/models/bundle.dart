// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Bundle model for Kumiho asset management.
///
/// This module provides the [Bundle] class, which represents a special item
/// that aggregates other items.
library;

import '../generated/kumiho.pb.dart' as pb;
import '../kref.dart';
import 'base.dart';
import 'item.dart';
import 'revision.dart';

/// A bundle that aggregates multiple items in the Kumiho system.
///
/// Bundles are special items (kind="bundle") that can contain references
/// to other items. They provide a way to group related assets together
/// and maintain an audit trail of membership changes. Bundles are
/// first-class model objects—they expose rich helper methods without
/// requiring the consumer to touch protobuf-generated stubs.
///
/// Practical scenarios include:
/// - Packaging the set of approved assets for a release.
/// - Tracking episodic or level-based deliveries without duplicating the
///   underlying items.
/// - Capturing metadata on the membership relationship (e.g., role,
///   variant, platform) for downstream automation.
///
/// ```dart
/// final bundle = await project.createBundle('release-v1');
///
/// // Add items to the bundle
/// await bundle.addMember(hero.kref);
/// await bundle.addMember(texture.kref);
///
/// // Get bundle members
/// final members = await bundle.getMembers();
/// for (final member in members) {
///   print(member.itemKref.uri);
/// }
///
/// // Get membership history
/// final history = await bundle.getMembershipHistory();
/// ```
class Bundle extends KumihoObject {
  /// Creates a [Bundle] from a protobuf ItemResponse.
  Bundle(pb.ItemResponse response, dynamic client) : super(client) {
    kref = Kref(response.kref.uri);
    name = response.name;
    itemName = response.itemName;
    kind = response.kind;
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    author = response.author;
    metadata = Map<String, String>.from(response.metadata);
    deprecated = response.deprecated;
    username = response.username;
  }

  /// The unique reference URI for this bundle.
  late final Kref kref;

  /// The full name including kind (e.g., "release-v1.bundle").
  late final String name;

  /// The base name of the bundle (e.g., "release-v1").
  late final String itemName;

  /// The kind of item (always "bundle").
  late final String kind;

  /// ISO timestamp when the bundle was created.
  late final String? createdAt;

  /// The user ID who created the bundle.
  late final String author;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// Whether the bundle is deprecated.
  late final bool deprecated;

  /// Display name of the creator.
  late final String username;

  /// Gets the project name from the kref.
  String get project => kref.project;

  /// Gets the space path from the kref.
  String get space => kref.space;

  /// Adds a member to this bundle.
  ///
  /// The optional [metadata] map is attached to the new bundle revision and
  /// can later be inspected via [getMembershipHistory].
  ///
  /// Returns the [pb.AddBundleMemberResponse] (success/message/newRevision),
  /// mirroring the Python SDK's `Bundle.add_member`.
  ///
  /// ```dart
  /// final response = await bundle.addMember(hero.kref, metadata: {'role': 'hero'});
  /// ```
  Future<pb.AddBundleMemberResponse> addMember(Kref memberKref,
      {Map<String, String>? metadata}) async {
    return client.addBundleMember(kref.uri, memberKref.uri, metadata: metadata);
  }

  /// Adds an item to this bundle.
  ///
  /// ```dart
  /// await bundle.addItem(hero);
  /// ```
  Future<pb.AddBundleMemberResponse> addItem(Item item,
      {Map<String, String>? metadata}) async {
    return addMember(item.kref, metadata: metadata);
  }

  /// Removes a member from this bundle.
  ///
  /// The optional [metadata] map is attached to the new bundle revision and
  /// can later be inspected via [getMembershipHistory].
  ///
  /// Returns the [pb.RemoveBundleMemberResponse] (success/message/newRevision),
  /// mirroring the Python SDK's `Bundle.remove_member`.
  ///
  /// ```dart
  /// await bundle.removeMember(hero.kref);
  /// ```
  Future<pb.RemoveBundleMemberResponse> removeMember(Kref memberKref,
      {Map<String, String>? metadata}) async {
    return client.removeBundleMember(kref.uri, memberKref.uri,
        metadata: metadata);
  }

  /// Removes an item from this bundle.
  ///
  /// ```dart
  /// await bundle.removeItem(hero);
  /// ```
  Future<pb.RemoveBundleMemberResponse> removeItem(Item item,
      {Map<String, String>? metadata}) async {
    return removeMember(item.kref, metadata: metadata);
  }

  /// Gets all current members of this bundle.
  ///
  /// Returns the rich [pb.BundleMember] entries (item kref plus audit fields:
  /// addedAt, addedBy, addedByUsername, addedInRevision), mirroring the Python
  /// SDK's `Bundle.get_members`.
  ///
  /// [revisionNumber] optionally queries membership at a specific bundle
  /// revision; if omitted, returns the current (latest) membership.
  ///
  /// ```dart
  /// final members = await bundle.getMembers();
  /// for (final member in members) {
  ///   print(member.itemKref.uri);
  /// }
  /// ```
  Future<List<pb.BundleMember>> getMembers({int? revisionNumber}) async {
    final response = await client.getBundleMembers(kref.uri,
        revisionNumber: revisionNumber);
    return response.members.toList();
  }

  /// Gets the full membership history of this bundle.
  ///
  /// Returns the complete chronological history of membership changes
  /// (additions and removals), including the metadata captured at each
  /// change. Useful for audits and debugging automation.
  ///
  /// Mirrors the Python SDK's `Bundle.get_history()`: the GetBundleHistory
  /// RPC returns the entire audit trail for the bundle and has no per-member
  /// filter.
  ///
  /// ```dart
  /// final history = await bundle.getMembershipHistory();
  /// ```
  Future<pb.GetBundleHistoryResponse> getMembershipHistory() async {
    return client.getBundleHistory(kref.uri);
  }

  /// Creates a new revision of this bundle.
  ///
  /// The resulting [Revision] captures the current membership snapshot.
  ///
  /// ```dart
  /// final v1 = await bundle.createRevision(metadata: {'notes': 'Initial release'});
  /// ```
  Future<Revision> createRevision({Map<String, String>? metadata}) async {
    final response = await client.createRevision(kref.uri, metadata: metadata);
    return Revision(response, client);
  }

  /// Gets all revisions of this bundle.
  ///
  /// ```dart
  /// final revisions = await bundle.getRevisions();
  /// ```
  Future<List<Revision>> getRevisions() async {
    final responses = await client.getRevisions(kref.uri);
    return responses.map((r) => Revision(r, client)).toList();
  }

  /// Gets the latest revision of this bundle.
  ///
  /// Returns `null` if the bundle has no revisions, mirroring Python's
  /// `Item.get_latest_revision` (which `Bundle` inherits).
  ///
  /// ```dart
  /// final latest = await bundle.getLatestRevision();
  /// ```
  Future<Revision?> getLatestRevision() async {
    final response = await client.getLatestRevision(kref.uri);
    if (response == null) {
      return null;
    }
    return Revision(response, client);
  }

  @override
  String toString() => "Bundle(kref: '${kref.uri}', name: '$name')";
}
