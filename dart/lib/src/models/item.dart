// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Item model for Kumiho asset management.
///
/// This module provides the [Item] class, which represents a versioned
/// asset in the Kumiho system.
library;

import '../generated/kumiho.pb.dart' as pb;
import '../kref.dart';
import 'base.dart';
import 'revision.dart';

/// A versioned asset in the Kumiho system.
///
/// Items represent assets that can have multiple revisions, such as 3D models,
/// textures, workflows, or any other type of creative content. They are the
/// main entry-point for client tools: each API in this class returns a
/// high-level model object rather than the protobuf response so dartdoc can
/// generate user-facing documentation without exposing transport details.
///
/// ```dart
/// final item = await kumiho.getItem('kref://my-project/models/hero.model');
///
/// // Create a new revision
/// final v1 = await item.createRevision(metadata: {'artist': 'john'});
///
/// // Add artifacts to the revision
/// await v1.createArtifact('mesh', '/assets/hero_v1.fbx');
///
/// // Tag the revision
/// await v1.tag('approved');
///
/// // Get all revisions
/// for (final revision in await item.getRevisions()) {
///   print('v${revision.number}: ${revision.tags}');
/// }
/// ```
class Item extends KumihoObject {
  /// Creates an [Item] from a protobuf response.
  Item(pb.ItemResponse response, dynamic client) : super(client) {
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

  /// The unique reference URI for this item.
  late final Kref kref;

  /// The full name including kind (e.g., "hero.model").
  late final String name;

  /// The base name of the item (e.g., "hero").
  late final String itemName;

  /// The kind of item (e.g., "model", "texture").
  late final String kind;

  /// ISO timestamp when the item was created.
  late final String? createdAt;

  /// The user ID who created the item.
  late final String author;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// Whether the item is deprecated.
  late final bool deprecated;

  /// Display name of the creator.
  late final String username;

  /// Gets the project name from the kref.
  String get projectName => kref.project;

  /// Gets the space path from the kref.
  String get spacePath => kref.space;

  /// Gets the parent space of this item.
  ///
  /// Returns the [Space] model for the kref path. The returned object is
  /// the high-level wrapper, not the protobuf payload.
  ///
  /// ```dart
  /// final parentSpace = await item.space;
  /// ```
  Future<dynamic> get space async {
    final path = '/${kref.project}${spacePath.isEmpty ? '' : '/$spacePath'}';
    return client.getSpace(path);
  }

  /// Creates a new revision of this item.
  ///
  /// ```dart
  /// final v1 = await item.createRevision(metadata: {'notes': 'Initial'});
  /// ```
  Future<Revision> createRevision({Map<String, String>? metadata}) async {
    final response = await client.createRevision(kref.uri, metadata: metadata);
    return Revision(response, client);
  }

  /// Gets a specific revision by number.
  ///
  /// ```dart
  /// final v1 = await item.getRevision(1);
  /// ```
  Future<Revision> getRevision(int number) async {
    final revKref = kref.withRevision(number);
    final response = await client.getRevision(revKref.uri);
    return Revision(response, client);
  }

  /// Gets the latest revision of this item.
  ///
  /// Returns `null` if no revisions exist. The helper swallows the
  /// "not found" response from the control plane and surfaces a
  /// nullable [Revision] wrapper instead of throwing.
  ///
  /// ```dart
  /// final latest = await item.getLatestRevision();
  /// if (latest != null) {
  ///   print('Latest: v${latest.number}');
  /// }
  /// ```
  Future<Revision?> getLatestRevision() async {
    try {
      final response = await client.getLatestRevision(kref.uri);
      return Revision(response, client);
    } catch (e) {
      // No revisions found
      return null;
    }
  }

  /// Gets all revisions of this item.
  ///
  /// ```dart
  /// final revisions = await item.getRevisions();
  /// for (final rev in revisions) {
  ///   print('v${rev.number}');
  /// }
  /// ```
  Future<List<Revision>> getRevisions() async {
    final revisions = await client.getRevisions(kref.uri);
    return revisions.map<Revision>((r) => Revision(r, client)).toList();
  }

  /// Gets a revision by tag.
  ///
  /// ```dart
  /// final approved = await item.getRevisionByTag('approved');
  /// ```
  Future<Revision?> getRevisionByTag(String tag) async {
    final revisions = await getRevisions();
    for (final rev in revisions) {
      if (rev.tags.contains(tag)) {
        return rev;
      }
    }
    return null;
  }

  /// Sets metadata for this item.
  ///
  /// ```dart
  /// await item.setMetadata({'status': 'final', 'priority': 'high'});
  /// ```
  Future<void> setMetadata(Map<String, String> metadata) async {
    for (final entry in metadata.entries) {
      await client.setAttribute(kref.uri, entry.key, entry.value);
    }
  }

  /// Sets the deprecated status of this item.
  ///
  /// ```dart
  /// await item.setDeprecated(true);
  /// ```
  Future<void> setDeprecated(bool deprecated) async {
    await client.setDeprecated(kref.uri, deprecated);
  }

  /// Deletes this item.
  ///
  /// ```dart
  /// await item.delete();
  /// ```
  Future<void> delete() async {
    await client.deleteItem(kref.uri);
  }

  @override
  String toString() => "Item(kref: '${kref.uri}', name: '$name')";
}
