// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Artifact API mixin for managing file references.
///
/// Artifacts are the leaf nodes of the Kumiho hierarchy. They point to
/// actual files on local disk, network storage, or cloud URIs. Kumiho
/// tracks the path and metadata but does not upload or modify the files.
///
/// The artifact's kref includes both revision and artifact name:
/// `kref://project/space/item.kind?r=1&a=artifact_name`
///
/// ```dart
/// // Create an artifact
/// final artifact = await client.createArtifact(
///   'kref://project/models/hero.model?r=1',
///   'mesh',
///   '/assets/hero.fbx',
/// );
///
/// // Get artifacts for a revision
/// final artifacts = await client.getArtifacts(
///   'kref://project/models/hero.model?r=1',
/// );
///
/// // Find artifacts by location
/// final related = await client.getArtifactsByLocation('/assets/hero.fbx');
/// ```
mixin ArtifactApi on KumihoClientBase {
  /// Creates a new artifact for a revision.
  ///
  /// [revisionKref] is the revision's kref URI (must include ?r=N).
  /// [name] is the artifact name (e.g., 'mesh', 'textures').
  /// [location] is the file path or URI where the artifact is stored.
  /// [metadata] is optional key-value metadata for the artifact.
  /// [existsError] controls whether to throw if artifact exists (default: `true`).
  Future<ArtifactResponse> createArtifact(
    String revisionKref,
    String name,
    String location, {
    Map<String, String>? metadata,
    bool existsError = true,
  }) async {
    final request = CreateArtifactRequest()
      ..revisionKref = Kref(uri: revisionKref)
      ..name = name
      ..location = location
      ..existsError = existsError;
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    return stub.createArtifact(request, options: callOptions);
  }

  /// Gets a specific artifact by name.
  ///
  /// [revisionKref] is the revision's kref URI.
  /// [name] is the artifact name.
  Future<ArtifactResponse> getArtifact(
    String revisionKref,
    String name,
  ) async {
    final request = GetArtifactRequest()
      ..revisionKref = Kref(uri: revisionKref)
      ..name = name;
    return stub.getArtifact(request, options: callOptions);
  }

  /// Lists all artifacts for a revision.
  ///
  /// [revisionKref] is the revision's kref URI.
  Future<List<ArtifactResponse>> getArtifacts(String revisionKref) async {
    final request = GetArtifactsRequest()..revisionKref = Kref(uri: revisionKref);
    final response = await stub.getArtifacts(request, options: callOptions);
    return response.artifacts;
  }

  /// Finds artifacts by their file location.
  ///
  /// [location] is the file path or URI to search for.
  /// Returns all artifacts pointing to this location across all revisions.
  Future<List<ArtifactResponse>> getArtifactsByLocation(String location) async {
    final request = GetArtifactsByLocationRequest()..location = location;
    final response = await stub.getArtifactsByLocation(
      request,
      options: callOptions,
    );
    return response.artifacts;
  }

  /// Deletes an artifact.
  ///
  /// [kref] is the artifact's full kref URI (including ?r=N&a=name).
  /// Set [force] to `true` to force deletion.
  Future<StatusResponse> deleteArtifact(
    String kref, {
    bool force = false,
  }) async {
    final request = DeleteArtifactRequest()
      ..kref = Kref(uri: kref)
      ..force = force;
    return stub.deleteArtifact(request, options: callOptions);
  }

  /// Updates metadata for an artifact.
  ///
  /// [kref] is the artifact's kref URI.
  /// [metadata] is a map of key-value pairs to set or update.
  Future<ArtifactResponse> updateArtifactMetadata(
    String kref,
    Map<String, String> metadata,
  ) async {
    final request = UpdateMetadataRequest()
      ..kref = Kref(uri: kref)
      ..metadata.addAll(metadata);
    return stub.updateArtifactMetadata(request, options: callOptions);
  }
}
