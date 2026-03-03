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
///   print(member.uri);
/// }
///
/// // Get membership history
/// final history = await bundle.getMembershipHistory(hero.kref);
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
  /// The optional [metadata] map is attached to the membership edge and
  /// can later be inspected via [getMembershipHistory].
  ///
  /// ```dart
  /// await bundle.addMember(hero.kref, metadata: {'role': 'hero'});
  /// ```
  Future<void> addMember(Kref memberKref, {Map<String, String>? metadata}) async {
    await client.addBundleMember(kref.uri, memberKref.uri, metadata: metadata);
  }

  /// Adds an item to this bundle.
  ///
  /// ```dart
  /// await bundle.addItem(hero);
  /// ```
  Future<void> addItem(Item item, {Map<String, String>? metadata}) async {
    await addMember(item.kref, metadata: metadata);
  }

  /// Removes a member from this bundle.
  ///
  /// ```dart
  /// await bundle.removeMember(hero.kref);
  /// ```
  Future<void> removeMember(Kref memberKref) async {
    await client.removeBundleMember(kref.uri, memberKref.uri);
  }

  /// Removes an item from this bundle.
  ///
  /// ```dart
  /// await bundle.removeItem(hero);
  /// ```
  Future<void> removeItem(Item item) async {
    await removeMember(item.kref);
  }

  /// Gets all current members of this bundle.
  ///
  /// Returns the krefs of the linked items, allowing callers to lazily
  /// hydrate the items only when needed.
  ///
  /// ```dart
  /// final members = await bundle.getMembers();
  /// for (final member in members) {
  ///   print(member.uri);
  /// }
  /// ```
  Future<List<Kref>> getMembers() async {
    final response = await client.getBundleMembers(kref.uri);
    return response.memberKrefs.map((k) => Kref(k.uri)).toList();
  }

  /// Gets the membership history for a specific member.
  ///
  /// Returns the history of when the member was added/removed from this
  /// bundle, including the metadata captured at each change. This is
  /// useful for audits and debugging automation.
  ///
  /// ```dart
  /// final history = await bundle.getMembershipHistory(hero.kref);
  /// ```
  Future<pb.GetBundleHistoryResponse> getMembershipHistory(Kref memberKref) async {
    return client.getBundleHistory(kref.uri, memberKref.uri);
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
    final response = await client.getRevisions(kref.uri);
    return response.revisions.map((r) => Revision(r, client)).toList();
  }

  /// Gets the latest revision of this bundle.
  ///
  /// ```dart
  /// final latest = await bundle.getLatestRevision();
  /// ```
  Future<Revision> getLatestRevision() async {
    final response = await client.getLatestRevision(kref.uri);
    return Revision(response, client);
  }

  @override
  String toString() => "Bundle(kref: '${kref.uri}', name: '$name')";
}
