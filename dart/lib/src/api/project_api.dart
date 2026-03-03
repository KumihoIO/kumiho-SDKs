// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

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
  /// Throws a gRPC error if the project already exists or
  /// the project limit has been reached.
  Future<ProjectResponse> createProject(
    String name, {
    String? description,
  }) async {
    final request = CreateProjectRequest()
      ..name = name
      ..description = description ?? '';
    return stub.createProject(request, options: callOptions);
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

  /// Deletes or deprecates a project.
  ///
  /// By default, this performs a soft delete (deprecation).
  /// Set [force] to `true` to permanently delete the project
  /// and all its contents.
  ///
  /// **Warning**: Force deletion is irreversible.
  Future<StatusResponse> deleteProject(
    String projectId, {
    bool force = false,
  }) async {
    final request = DeleteProjectRequest()
      ..projectId = projectId
      ..force = force;
    return stub.deleteProject(request, options: callOptions);
  }
}
