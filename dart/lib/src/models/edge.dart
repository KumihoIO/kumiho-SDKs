// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Edge model for Kumiho asset management.
///
/// This module provides the [Edge] class, which represents a relationship
/// between two revisions.
library;

import '../generated/kumiho.pb.dart' as pb;
import '../kref.dart';
import 'base.dart';

/// A relationship between two revisions in the Kumiho system.
///
/// Edges track dependencies, derivations, and references between revisions.
/// They form a directed graph that can be traversed to understand asset
/// relationships and impact analysis. The Dart SDK exposes edges as a
/// lightweight model object so dependency graph tooling can be built
/// without importing generated protobuf types.
///
/// ```dart
/// // Create an edge
/// final edge = await revision.createEdge(texture, EdgeType.dependsOn);
///
/// // Query edges
/// final edges = await revision.getEdges();
/// for (final edge in edges) {
///   print('${edge.sourceKref.uri} ${edge.edgeType} ${edge.targetKref.uri}');
/// }
/// ```
class Edge extends KumihoObject {
  /// Creates an [Edge] from a protobuf response.
  Edge(pb.Edge response, dynamic client) : super(client) {
    sourceKref = Kref(response.sourceKref.uri);
    targetKref = Kref(response.targetKref.uri);
    edgeType = response.edgeType;
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    author = response.author;
    metadata = Map<String, String>.from(response.metadata);
    username = response.username;
  }

  /// Reference to the source revision.
  late final Kref sourceKref;

  /// Reference to the target revision.
  late final Kref targetKref;

  /// The type of relationship (e.g., "DEPENDS_ON", "DERIVED_FROM").
  late final String edgeType;

  /// ISO timestamp when the edge was created.
  late final String? createdAt;

  /// The user ID who created the edge.
  late final String author;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// Display name of the creator.
  late final String username;

  /// Deletes this edge.
  ///
  /// This removes the relationship between [sourceKref] and [targetKref]
  /// for the stored [edgeType]. Metadata captured on the edge is also
  /// removed.
  ///
  /// ```dart
  /// await edge.delete();
  /// ```
  Future<void> delete() async {
    await client.deleteEdge(sourceKref.uri, targetKref.uri, edgeType);
  }

  @override
  String toString() =>
      "Edge(${sourceKref.uri} -[$edgeType]-> ${targetKref.uri})";
}
