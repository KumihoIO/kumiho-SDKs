// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'package:grpc/grpc.dart' show GrpcError, StatusCode;

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';
import '../models/base.dart' show ProjectLimitError;

/// Project API mixin for managing Kumiho projects.
///
/// Projects are the top-level containers for all assets and spaces
/// in the Kumiho system.
///
/// ```dart
/// // Create a project
/// final project = await client.createProject(
///   'my-vfx-project',
///   description: 'VFX assets for commercial',
/// );
///
/// // List all projects
/// final projects = await client.getProjects();
///
/// // Update project settings
/// await client.updateProject(
///   project.projectId,
///   allowPublic: true,
/// );
///
/// // Delete (deprecate) a project
/// await client.deleteProject(project.projectId);
/// ```
mixin ProjectApi on KumihoClientBase {
  /// Creates a new project.
  ///
  /// [name] must be URL-safe (alphanumeric with hyphens).
  /// [description] is an optional human-readable description.
  ///
  /// Throws a gRPC error if the project already exists.
  ///
  /// Throws a [ProjectLimitError] if the server returns `RESOURCE_EXHAUSTED`
  /// (for example, when the project limit has been reached).
  Future<ProjectResponse> createProject(
    String name, {
    String? description,
  }) async {
    final request =
        CreateProjectRequest()
          ..name = name
          ..description = description ?? '';
    try {
      return await stub.createProject(request, options: callOptions);
    } on GrpcError catch (e) {
      if (e.code == StatusCode.resourceExhausted) {
        throw ProjectLimitError(e.message ?? 'Project limit reached');
      }
      rethrow;
    }
  }

  /// Lists all projects accessible to the current user.
  ///
  /// Returns a list of [ProjectResponse] objects containing
  /// project metadata and settings.
  Future<List<ProjectResponse>> getProjects() async {
    final request = GetProjectsRequest();
    final response = await stub.getProjects(request, options: callOptions);
    return response.projects;
  }

  /// Updates a project's settings.
  ///
  /// [projectId] is the unique identifier for the project.
  /// [allowPublic] controls whether anonymous read access is enabled.
  /// [description] updates the project description.
  ///
  /// Only provided values are updated; omitted values remain unchanged.
  Future<ProjectResponse> updateProject(
    String projectId, {
    bool? allowPublic,
    String? description,
  }) async {
    final request = UpdateProjectRequest()..projectId = projectId;
    if (allowPublic != null) {
      request.allowPublic = allowPublic;
    }
    if (description != null) {
      request.description = description;
    }
    return stub.updateProject(request, options: callOptions);
  }

  /// Forwards the legacy delete/deprecate request to the connected server.
  /// New servers require [hardDeleteProject] for permanent deletion, while
  /// older servers can continue to honor `force: true`.
  Future<StatusResponse> deleteProject(
    String projectId, {
    bool force = false,
  }) async {
    final request =
        DeleteProjectRequest()
          ..projectId = projectId
          ..force = force;
    return stub.deleteProject(request, options: callOptions);
  }

  Future<ProjectDeletionImpactResponse> analyzeProjectDeletion(
    String projectId,
  ) {
    return stub.analyzeProjectDeletion(
      ProjectDeletionImpactRequest()..projectId = projectId,
      options: callOptions,
    );
  }

  Future<StatusResponse> hardDeleteProject(
    ProjectDeletionImpactResponse impact, {
    bool confirmed = false,
  }) {
    if (!confirmed ||
        impact.projectId.isEmpty ||
        impact.impactSnapshotId.isEmpty ||
        impact.impactSnapshotHash.isEmpty) {
      throw ArgumentError(
        'hard-delete requires a server impact snapshot and confirmed=true',
      );
    }
    final request =
        HardDeleteProjectRequest()
          ..projectId = impact.projectId
          ..impactSnapshotId = impact.impactSnapshotId
          ..impactSnapshotHash = impact.impactSnapshotHash
          ..confirmed = confirmed;
    return stub.hardDeleteProject(request, options: callOptions);
  }

  Future<ProjectDeletionGuardResponse> registerProjectDeletionGuard(
    String projectId,
    String guardId,
    String resourceKref, {
    required List<String> allowedOperations,
    List<String> allowedMetadataKeys = const [],
  }) {
    final request =
        RegisterProjectDeletionGuardRequest()
          ..projectId = projectId
          ..guardId = guardId
          ..resourceKref = resourceKref
          ..allowedOperations.addAll(allowedOperations)
          ..allowedMetadataKeys.addAll(allowedMetadataKeys);
    return stub.registerProjectDeletionGuard(request, options: callOptions);
  }

  Future<StatusResponse> resolveProjectDeletionGuard(
    String projectId,
    String guardId,
  ) {
    return stub.resolveProjectDeletionGuard(
      ResolveProjectDeletionGuardRequest()
        ..projectId = projectId
        ..guardId = guardId,
      options: callOptions,
    );
  }

  Future<StatusResponse> resolveProjectReference(
    String projectId,
    String insideRevisionKref,
    String outsideRevisionKref,
    String edgeType,
    String action, {
    String replacementRevisionKref = '',
  }) {
    return stub.resolveProjectReference(
      ResolveProjectReferenceRequest()
        ..projectId = projectId
        ..insideRevisionKref = insideRevisionKref
        ..outsideRevisionKref = outsideRevisionKref
        ..edgeType = edgeType
        ..action = action
        ..replacementRevisionKref = replacementRevisionKref,
      options: callOptions,
    );
  }
}
