// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Standard edge types for Kumiho relationships.
///
/// These constants define the semantic meaning of relationships between
/// revisions. Use them when creating or querying edges.
///
/// ```dart
/// // Model depends on texture
/// await client.createEdge(
///   modelRevision.kref.uri,
///   textureRevision.kref.uri,
///   EdgeType.dependsOn,
/// );
///
/// // LOD derived from high-poly
/// await client.createEdge(
///   lodRevision.kref.uri,
///   highpolyRevision.kref.uri,
///   EdgeType.derivedFrom,
/// );
/// ```
class EdgeType {
  EdgeType._();

  /// Ownership or grouping relationship.
  static const String belongsTo = 'BELONGS_TO';

  /// Source was generated/created from target.
  static const String createdFrom = 'CREATED_FROM';

  /// Soft reference relationship.
  static const String referenced = 'REFERENCED';

  /// Source requires target to function.
  static const String dependsOn = 'DEPENDS_ON';

  /// Source was derived or modified from target.
  static const String derivedFrom = 'DERIVED_FROM';

  /// Source contains or includes target.
  static const String contains = 'CONTAINS';

  /// All valid edge type values.
  static const List<String> values = [
    belongsTo,
    createdFrom,
    referenced,
    dependsOn,
    derivedFrom,
    contains,
  ];

  /// Checks if a string is a valid edge type.
  static bool isValid(String edgeType) => values.contains(edgeType);
}

/// Edge API mixin for managing relationships between revisions.
///
/// Edges enable dependency tracking, lineage visualization, and impact
/// analysis. They are directed relationships between revisions.
///
/// ```dart
/// // Create a dependency edge
/// await client.createEdge(
///   'kref://project/models/hero.model?r=1',
///   'kref://project/textures/skin.texture?r=2',
///   EdgeType.dependsOn,
/// );
///
/// // Get all dependencies
/// final edges = await client.getEdges(
///   'kref://project/models/hero.model?r=1',
///   direction: EdgeDirection.OUTGOING,
/// );
///
/// // Impact analysis
/// final impact = await client.analyzeImpact(
///   'kref://project/textures/skin.texture?r=2',
/// );
/// ```
mixin EdgeApi on KumihoClientBase {
  /// Creates an edge between two revisions.
  ///
  /// [sourceKref] is the source revision's kref URI.
  /// [targetKref] is the target revision's kref URI.
  /// [edgeType] is the type of relationship (use [EdgeType] constants).
  /// [metadata] is optional key-value pairs to attach.
  /// [existsError] controls whether to throw if edge exists (default: `true`).
  Future<StatusResponse> createEdge(
    String sourceKref,
    String targetKref,
    String edgeType, {
    Map<String, String>? metadata,
    bool existsError = true,
  }) async {
    final request = CreateEdgeRequest()
      ..sourceRevisionKref = Kref(uri: sourceKref)
      ..targetRevisionKref = Kref(uri: targetKref)
      ..edgeType = edgeType
      ..existsError = existsError;
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    return stub.createEdge(request, options: callOptions);
  }

  /// Gets edges for a revision.
  ///
  /// [kref] is the revision's kref URI.
  /// [edgeTypeFilter] filters by edge type (empty for all types).
  /// [direction] specifies which edges to return:
  ///   - OUTGOING: edges where this revision is the source
  ///   - INCOMING: edges where this revision is the target
  ///   - BOTH: both directions
  Future<GetEdgesResponse> getEdges(
    String kref, {
    String? edgeTypeFilter,
    EdgeDirection? direction,
  }) async {
    final request = GetEdgesRequest()..kref = Kref(uri: kref);
    if (edgeTypeFilter != null && edgeTypeFilter.isNotEmpty) {
      request.edgeTypeFilter = edgeTypeFilter;
    }
    if (direction != null) {
      request.direction = direction;
    }
    return stub.getEdges(request, options: callOptions);
  }

  /// Deletes an edge between two revisions.
  ///
  /// All three parameters must match an existing edge exactly.
  Future<StatusResponse> deleteEdge(
    String sourceKref,
    String targetKref,
    String edgeType,
  ) async {
    final request = DeleteEdgeRequest()
      ..sourceKref = Kref(uri: sourceKref)
      ..targetKref = Kref(uri: targetKref)
      ..edgeType = edgeType;
    return stub.deleteEdge(request, options: callOptions);
  }

  /// Traverses edges to find all connected revisions.
  ///
  /// [originKref] is the starting revision.
  /// [direction] specifies traversal direction:
  ///   - OUTGOING: follow edges from source to target (find dependencies)
  ///   - INCOMING: follow edges from target to source (find dependents)
  /// [edgeTypeFilter] filters by edge types (empty for all).
  /// [maxDepth] limits traversal depth (default: 10).
  /// [limit] limits number of results (default: 100).
  /// [includePath] includes full path information in results.
  Future<TraverseEdgesResponse> traverseEdges(
    String originKref,
    EdgeDirection direction, {
    List<String>? edgeTypeFilter,
    int? maxDepth,
    int? limit,
    bool includePath = false,
  }) async {
    final request = TraverseEdgesRequest()
      ..originKref = Kref(uri: originKref)
      ..direction = direction
      ..includePath = includePath;
    if (edgeTypeFilter != null && edgeTypeFilter.isNotEmpty) {
      request.edgeTypeFilter.addAll(edgeTypeFilter);
    }
    if (maxDepth != null) {
      request.maxDepth = maxDepth;
    }
    if (limit != null) {
      request.limit = limit;
    }
    return stub.traverseEdges(request, options: callOptions);
  }

  /// Finds the shortest path between two revisions.
  ///
  /// [sourceKref] is the starting revision.
  /// [targetKref] is the destination revision.
  /// [edgeTypeFilter] filters by edge types (empty for all).
  /// [maxDepth] limits search depth (default: 10).
  /// [allShortest] returns all shortest paths instead of just one.
  Future<ShortestPathResponse> findShortestPath(
    String sourceKref,
    String targetKref, {
    List<String>? edgeTypeFilter,
    int? maxDepth,
    bool allShortest = false,
  }) async {
    final request = ShortestPathRequest()
      ..sourceKref = Kref(uri: sourceKref)
      ..targetKref = Kref(uri: targetKref)
      ..allShortest = allShortest;
    if (edgeTypeFilter != null && edgeTypeFilter.isNotEmpty) {
      request.edgeTypeFilter.addAll(edgeTypeFilter);
    }
    if (maxDepth != null) {
      request.maxDepth = maxDepth;
    }
    return stub.findShortestPath(request, options: callOptions);
  }

  /// Analyzes the impact of changes to a revision.
  ///
  /// Finds all revisions that depend on the given revision (transitively).
  /// Useful for understanding what would be affected by a change.
  ///
  /// [revisionKref] is the revision to analyze.
  /// [edgeTypeFilter] filters by edge types (usually [EdgeType.dependsOn]).
  /// [maxDepth] limits analysis depth (default: 10).
  /// [limit] limits number of results.
  Future<ImpactAnalysisResponse> analyzeImpact(
    String revisionKref, {
    List<String>? edgeTypeFilter,
    int? maxDepth,
    int? limit,
  }) async {
    final request = ImpactAnalysisRequest()..revisionKref = Kref(uri: revisionKref);
    if (edgeTypeFilter != null && edgeTypeFilter.isNotEmpty) {
      request.edgeTypeFilter.addAll(edgeTypeFilter);
    }
    if (maxDepth != null) {
      request.maxDepth = maxDepth;
    }
    if (limit != null) {
      request.limit = limit;
    }
    return stub.analyzeImpact(request, options: callOptions);
  }
}
