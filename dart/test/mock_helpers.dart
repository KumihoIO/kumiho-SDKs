// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Mock helpers for Kumiho Dart tests.
///
/// This abstracts away the direct usage of protobuf messages in test files,
/// matching the Python SDK's mock_helpers.py pattern.
library;

import 'package:fixnum/fixnum.dart';
// Import protobuf directly to get the protobuf Kref message
import 'package:kumiho/src/generated/kumiho.pb.dart' as pb;
// Import the main library for other exports
import 'package:kumiho/kumiho.dart';

export 'package:fixnum/fixnum.dart' show Int64;
// Re-export Kref from kref.dart for tests that need our Dart Kref class
export 'package:kumiho/src/kref.dart' show Kref, KrefValidationError, isValidKref;

/// Creates a mock ProjectResponse.
ProjectResponse mockProjectResponse({
  String projectId = 'p1',
  String name = 'demo',
  String description = '',
  String createdAt = 'now',
  String updatedAt = 'now',
  bool deprecated = false,
  bool allowPublic = false,
}) {
  return ProjectResponse()
    ..projectId = projectId
    ..name = name
    ..description = description
    ..createdAt = createdAt
    ..updatedAt = updatedAt
    ..deprecated = deprecated
    ..allowPublic = allowPublic;
}

/// Creates a mock GetProjectsResponse.
GetProjectsResponse mockGetProjectsResponse({
  List<ProjectResponse>? projects,
}) {
  return GetProjectsResponse()..projects.addAll(projects ?? []);
}

/// Creates a mock StatusResponse.
StatusResponse mockStatusResponse({
  bool success = true,
  String message = 'ok',
}) {
  return StatusResponse()
    ..success = success
    ..message = message;
}

/// Creates a mock SpaceResponse.
SpaceResponse mockSpaceResponse({
  required String path,
  String name = '',
  String type = 'sub',
  String createdAt = 'now',
  String author = 'test_author',
  String username = 'test_user',
  Map<String, String>? metadata,
}) {
  final response = SpaceResponse()
    ..path = path
    ..name = name.isEmpty ? path.split('/').last : name
    ..type = type
    ..createdAt = createdAt
    ..author = author
    ..username = username;
  if (metadata != null) {
    response.metadata.addAll(metadata);
  }
  return response;
}

/// Creates a mock protobuf Kref message.
pb.Kref mockPbKref(String uri) {
  return pb.Kref()..uri = uri;
}

/// Creates a mock RevisionResponse.
RevisionResponse mockRevisionResponse({
  required String krefUri,
  required String itemKrefUri,
  int number = 1,
  bool latest = true,
  List<String>? tags,
  Map<String, String>? metadata,
  String author = 'test_author',
  String username = 'test_user',
  bool deprecated = false,
  bool published = false,
  String? defaultArtifact,
}) {
  final response = RevisionResponse()
    ..kref = mockPbKref(krefUri)
    ..itemKref = mockPbKref(itemKrefUri)
    ..number = number
    ..latest = latest
    ..author = author
    ..username = username
    ..deprecated = deprecated
    ..published = published;
  if (tags != null) {
    response.tags.addAll(tags);
  }
  if (metadata != null) {
    response.metadata.addAll(metadata);
  }
  if (defaultArtifact != null) {
    response.defaultArtifact = defaultArtifact;
  }
  return response;
}

/// Creates a mock ItemResponse.
ItemResponse mockItemResponse({
  required String krefUri,
  required String name,
  required String itemName,
  required String kind,
  String author = 'test_author',
  String username = 'test_user',
  bool deprecated = false,
  Map<String, String>? metadata,
}) {
  final response = ItemResponse()
    ..kref = mockPbKref(krefUri)
    ..name = name
    ..itemName = itemName
    ..kind = kind
    ..author = author
    ..username = username
    ..deprecated = deprecated;
  if (metadata != null) {
    response.metadata.addAll(metadata);
  }
  return response;
}

/// Creates a mock GetItemsResponse.
GetItemsResponse mockGetItemsResponse({
  List<ItemResponse>? items,
  String nextCursor = '',
  int totalCount = 0,
}) {
  final pagination = PaginationResponse()
    ..nextCursor = nextCursor
    ..totalCount = totalCount
    ..hasMore = nextCursor.isNotEmpty;

  return GetItemsResponse()
    ..items.addAll(items ?? [])
    ..pagination = pagination;
}

/// Creates a mock ArtifactResponse.
ArtifactResponse mockArtifactResponse({
  required String krefUri,
  required String location,
  required String revisionKrefUri,
  String? itemKrefUri,
  String name = 'mesh',
  String author = 'test_author',
  String username = 'test_user',
  bool deprecated = false,
  Map<String, String>? metadata,
}) {
  final response = ArtifactResponse()
    ..kref = mockPbKref(krefUri)
    ..location = location
    ..revisionKref = mockPbKref(revisionKrefUri)
    ..name = name
    ..author = author
    ..username = username
    ..deprecated = deprecated;
  if (itemKrefUri != null) {
    response.itemKref = mockPbKref(itemKrefUri);
  }
  if (metadata != null) {
    response.metadata.addAll(metadata);
  }
  return response;
}

/// Creates a mock GetArtifactsResponse.
GetArtifactsResponse mockGetArtifactsResponse({
  List<ArtifactResponse>? artifacts,
}) {
  return GetArtifactsResponse()..artifacts.addAll(artifacts ?? []);
}

/// Creates a mock GetRevisionsResponse.
GetRevisionsResponse mockGetRevisionsResponse({
  List<RevisionResponse>? revisions,
}) {
  return GetRevisionsResponse()..revisions.addAll(revisions ?? []);
}

/// Creates a mock GetChildSpacesResponse.
GetChildSpacesResponse mockGetChildSpacesResponse({
  List<SpaceResponse>? spaces,
}) {
  return GetChildSpacesResponse()..spaces.addAll(spaces ?? []);
}

/// Creates a mock protobuf Edge.
pb.Edge mockEdge({
  required String sourceKrefUri,
  required String targetKrefUri,
  required String edgeType,
  String createdAt = 'now',
  String author = 'test_author',
  String username = 'test_user',
  Map<String, String>? metadata,
}) {
  final edge = pb.Edge()
    ..sourceKref = mockPbKref(sourceKrefUri)
    ..targetKref = mockPbKref(targetKrefUri)
    ..edgeType = edgeType
    ..createdAt = createdAt
    ..author = author
    ..username = username;
  if (metadata != null) {
    edge.metadata.addAll(metadata);
  }
  return edge;
}

/// Creates a mock GetEdgesResponse.
GetEdgesResponse mockGetEdgesResponse({
  List<pb.Edge>? edges,
  List<pb.Kref>? revisionKrefs,
}) {
  final response = GetEdgesResponse();
  if (edges != null) {
    response.edges.addAll(edges);
  }
  if (revisionKrefs != null) {
    response.revisionKrefs.addAll(revisionKrefs);
  }
  return response;
}

/// Creates a mock TenantUsageResponse.
TenantUsageResponse mockTenantUsageResponse({
  int nodeCount = 100,
  int nodeLimit = 10000,
  String tenantId = 'tenant-1',
}) {
  return TenantUsageResponse()
    ..nodeCount = Int64(nodeCount)
    ..nodeLimit = Int64(nodeLimit)
    ..tenantId = tenantId;
}

/// Creates a mock ImpactAnalysisResponse.
ImpactAnalysisResponse mockImpactAnalysisResponse({
  List<ImpactedRevision>? impactedRevisions,
  int totalImpacted = 0,
  bool truncated = false,
}) {
  final response = ImpactAnalysisResponse()
    ..totalImpacted = totalImpacted
    ..truncated = truncated;
  if (impactedRevisions != null) {
    response.impactedRevisions.addAll(impactedRevisions);
  }
  return response;
}
