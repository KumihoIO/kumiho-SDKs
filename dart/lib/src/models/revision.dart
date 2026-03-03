// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Revision model for Kumiho asset management.
///
/// This module provides the [Revision] class, which represents a specific
/// iteration of an item.
library;

import '../generated/kumiho.pb.dart' as pb;
import '../kref.dart';
import 'base.dart';
import 'artifact.dart';
import 'edge.dart';

/// A specific iteration of an item in the Kumiho system.
///
/// Revisions are immutable snapshots of an item at a point in time. Each
/// revision can have multiple artifacts (file references), tags for
/// categorization, and edges to other revisions for dependency tracking.
/// The class presents these capabilities through first-class Dart models so
/// the API surface remains stable even if the underlying protobuf schema
/// evolves.
///
/// ```dart
/// final revision = await kumiho.getRevision('kref://project/models/hero.model?r=1');
///
/// // Add artifacts
/// await revision.createArtifact('mesh', '/assets/hero.fbx');
/// await revision.createArtifact('textures', '/assets/hero_tex.zip');
///
/// // Tag the revision
/// await revision.tag('approved');
///
/// // Create edges to dependencies
/// final texture = await kumiho.getRevision('kref://project/tex/skin.texture?r=3');
/// await revision.createEdge(texture, EdgeType.dependsOn);
/// ```
class Revision extends KumihoObject {
  /// Creates a [Revision] from a protobuf response.
  Revision(pb.RevisionResponse response, dynamic client) : super(client) {
    kref = Kref(response.kref.uri);
    itemKref = Kref(response.itemKref.uri);
    number = response.number;
    latest = response.latest;
    _tags = List<String>.from(response.tags);
    metadata = Map<String, String>.from(response.metadata);
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    author = response.author;
    deprecated = response.deprecated;
    published = response.published;
    username = response.username;
    defaultArtifact = response.defaultArtifact.isEmpty ? null : response.defaultArtifact;
  }

  /// The unique reference URI for this revision.
  late final Kref kref;

  /// Reference to the parent item.
  late final Kref itemKref;

  /// The revision number (1-based).
  late final int number;

  /// Whether this is currently the latest revision.
  late final bool latest;

  /// Internal tag storage.
  late final List<String> _tags;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// ISO timestamp when the revision was created.
  late final String? createdAt;

  /// The user ID who created the revision.
  late final String author;

  /// Whether the revision is deprecated.
  late final bool deprecated;

  /// Whether the revision is published.
  late final bool published;

  /// Display name of the creator.
  late final String username;

  /// Name of the default artifact.
  late final String? defaultArtifact;

  /// Gets the tags for this revision.
  List<String> get tags => List.unmodifiable(_tags);

  /// Creates a new artifact for this revision.
  ///
  /// Returns the high-level [Artifact] wrapper so callers can continue
  /// working in the model layer. Use [metadata] to attach attributes during
  /// creation (for example, format or render engine information).
  ///
  /// ```dart
  /// final mesh = await revision.createArtifact('mesh', '/assets/hero.fbx');
  /// final tex = await revision.createArtifact('textures', '/assets/hero_tex.zip',
  ///   metadata: {'format': 'png', 'resolution': '4k'},
  /// );
  /// ```
  Future<Artifact> createArtifact(
    String name,
    String location, {
    Map<String, String>? metadata,
  }) async {
    final response = await client.createArtifact(
      kref.uri,
      name,
      location,
      metadata: metadata,
    );
    return Artifact(response, client);
  }

  /// Gets an artifact by name.
  ///
  /// Resolves the artifact kref by combining [kref] and the name, then
  /// returns the model wrapper.
  ///
  /// ```dart
  /// final mesh = await revision.getArtifact('mesh');
  /// ```
  Future<Artifact> getArtifact(String name) async {
    final artifactKref = kref.withArtifact(name);
    final response = await client.getArtifact(artifactKref.uri);
    return Artifact(response, client);
  }

  /// Gets all artifacts for this revision.
  ///
  /// ```dart
  /// final artifacts = await revision.getArtifacts();
  /// for (final artifact in artifacts) {
  ///   print('${artifact.name}: ${artifact.location}');
  /// }
  /// ```
  Future<List<Artifact>> getArtifacts() async {
    final artifacts = await client.getArtifacts(kref.uri);
    return artifacts.map<Artifact>((a) => Artifact(a, client)).toList();
  }

  /// Sets the default artifact for this revision.
  ///
  /// The default artifact is used when resolving the revision without
  /// specifying an artifact name.
  ///
  /// ```dart
  /// await revision.setDefaultArtifact('mesh');
  /// ```
  Future<void> setDefaultArtifact(String artifactName) async {
    await client.setDefaultArtifact(kref.uri, artifactName);
  }

  /// Tags this revision with the given tag.
  ///
  /// ```dart
  /// await revision.tag('approved');
  /// await revision.tag('ready-for-lighting');
  /// ```
  Future<void> tag(String tag) async {
    await client.tagRevision(kref.uri, tag);
    if (!_tags.contains(tag)) {
      _tags.add(tag);
    }
  }

  /// Removes a tag from this revision.
  ///
  /// ```dart
  /// await revision.untag('wip');
  /// ```
  Future<void> untag(String tag) async {
    await client.untagRevision(kref.uri, tag);
    _tags.remove(tag);
  }

  /// Checks if this revision has a specific tag.
  ///
  /// ```dart
  /// if (await revision.hasTag('approved')) {
  ///   print('Revision is approved!');
  /// }
  /// ```
  Future<bool> hasTag(String tag) async {
    return client.hasTag(kref.uri, tag);
  }

  /// Checks if this revision has ever had a specific tag.
  ///
  /// ```dart
  /// if (await revision.wasTagged('reviewed')) {
  ///   print('Revision was reviewed at some point');
  /// }
  /// ```
  Future<bool> wasTagged(String tag) async {
    return client.wasTagged(kref.uri, tag);
  }

  /// Creates an edge from this revision to another revision.
  ///
  /// ```dart
  /// final texture = await kumiho.getRevision('kref://project/tex/skin.texture?r=2');
  /// await revision.createEdge(texture, EdgeType.dependsOn);
  /// ```
  Future<void> createEdge(
    Revision target,
    String edgeType, {
    Map<String, String>? metadata,
  }) async {
    await client.createEdge(
      kref.uri,
      target.kref.uri,
      edgeType,
      metadata: metadata,
    );
  }

  /// Creates an edge from this revision to a target kref.
  ///
  /// ```dart
  /// await revision.createEdgeTo('kref://project/tex/skin.texture?r=2', EdgeType.dependsOn);
  /// ```
  Future<void> createEdgeTo(
    String targetKref,
    String edgeType, {
    Map<String, String>? metadata,
  }) async {
    await client.createEdge(
      kref.uri,
      targetKref,
      edgeType,
      metadata: metadata,
    );
  }

  /// Gets all edges from this revision.
  ///
  /// [edgeTypeFilter] filters by edge type (empty for all types).
  /// [direction] specifies which edges to return:
  ///   - EDGE_DIRECTION_OUTGOING: edges where this revision is the source
  ///   - EDGE_DIRECTION_INCOMING: edges where this revision is the target
  ///   - EDGE_DIRECTION_BOTH: both directions
  ///
  /// ```dart
  /// final edges = await revision.getEdges();
  /// for (final edge in edges) {
  ///   print('${edge.edgeType} -> ${edge.targetKref.uri}');
  /// }
  /// ```
  Future<List<Edge>> getEdges({
    String? edgeTypeFilter,
    pb.EdgeDirection? direction,
  }) async {
    final response = await client.getEdges(
      kref.uri,
      edgeTypeFilter: edgeTypeFilter,
      direction: direction,
    );
    return response.edges.map<Edge>((e) => Edge(e, client)).toList();
  }

  /// Traverses edges starting from this revision.
  ///
  /// ```dart
  /// final results = await revision.traverseEdges(
  ///   direction: 'outgoing',
  ///   edgeTypes: [EdgeType.dependsOn],
  ///   maxDepth: 3,
  /// );
  /// ```
  Future<List<Kref>> traverseEdges({
    String direction = 'outgoing',
    List<String>? edgeTypes,
    int maxDepth = 10,
  }) async {
    final response = await client.traverseEdges(
      kref.uri,
      direction: direction,
      edgeTypes: edgeTypes,
      maxDepth: maxDepth,
    );
    return response.revisionKrefs.map((k) => Kref(k.uri)).toList();
  }

  /// Analyzes the impact of changes to this revision.
  ///
  /// Returns all revisions that would be affected by changes to this
  /// revision. The response is the protobuf DTO because it contains
  /// structured counts and graph paths, but the method signature keeps the
  /// model-centric calling pattern consistent.
  ///
  /// ```dart
  /// final impact = await revision.analyzeImpact(maxDepth: 5);
  /// print('${impact.totalImpacted} revisions would be affected');
  /// ```
  Future<pb.ImpactAnalysisResponse> analyzeImpact({
    List<String>? edgeTypes,
    int maxDepth = 10,
  }) async {
    return client.analyzeImpact(
      kref.uri,
      edgeTypes: edgeTypes,
      maxDepth: maxDepth,
    );
  }

  /// Gets the parent item of this revision.
  ///
  /// ```dart
  /// final parentItem = await revision.item;
  /// ```
  Future<dynamic> get item async {
    return client.getItemByKref(itemKref.uri);
  }

  /// Gets the parent item of this revision.
  ///
  /// @deprecated Use [item] getter instead.
  ///
  /// ```dart
  /// final item = await revision.getItem();
  /// ```
  Future<dynamic> getItem() async {
    final response = await client.getItemByKref(itemKref.uri);
    // Note: We return the raw response here to avoid circular imports.
    // The caller can wrap it in an Item if needed.
    return response;
  }

  /// Sets metadata for this revision.
  ///
  /// ```dart
  /// await revision.setMetadata({'notes': 'Updated mesh', 'artist': 'john'});
  /// ```
  Future<void> setMetadata(Map<String, String> metadata) async {
    for (final entry in metadata.entries) {
      await client.setAttribute(kref.uri, entry.key, entry.value);
    }
  }

  @override
  String toString() => "Revision(kref: '${kref.uri}', number: $number)";
}
