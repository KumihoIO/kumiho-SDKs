// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Artifact model for Kumiho asset management.
///
/// This module provides the [Artifact] class, which represents a file
/// reference within a revision.
library;

import '../generated/kumiho.pb.dart' as pb;
import '../kref.dart';
import 'base.dart';

/// A file reference within a revision in the Kumiho system.
///
/// Artifacts are the leaf nodes of the Kumiho hierarchy. They point to
/// actual files on local disk, network storage, or cloud URIs. Kumiho
/// tracks the path and metadata but does not upload or modify the files.
/// Instead, the SDK keeps the revision graph, attributes, and default
/// selection in sync with the control plane so downstream tools can
/// resolve the correct asset without pulling in protobuf stubs.
///
/// Typical uses include:
/// - Referencing published geometry, textures, caches, or documents.
/// - Promoting one artifact to the default for a revision so callers can
///   omit the name when resolving a kref.
/// - Attaching rich metadata (format, scale, pipeline stages) that can be
///   inspected from automation without needing the raw gRPC response.
///
/// ```dart
/// final revision = await kumiho.getRevision('kref://project/models/hero.model?r=1');
///
/// // Create artifacts
/// final mesh = await revision.createArtifact('mesh', '/assets/hero.fbx');
/// final rig = await revision.createArtifact('rig', '/assets/hero_rig.fbx');
/// final textures = await revision.createArtifact('textures', 'smb://server/tex/hero/');
///
/// // Set metadata
/// await mesh.setMetadata({
///   'triangles': '2.5M',
///   'format': 'FBX 2020',
///   'units': 'centimeters',
/// });
///
/// // Set as default artifact
/// await mesh.setDefault();
/// ```
class Artifact extends KumihoObject {
  /// Creates an [Artifact] from a protobuf response.
  Artifact(pb.ArtifactResponse response, dynamic client) : super(client) {
    kref = Kref(response.kref.uri);
    name = response.name;
    location = response.location;
    revisionKref = Kref(response.revisionKref.uri);
    itemKref = response.hasItemKref() ? Kref(response.itemKref.uri) : null;
    createdAt = response.createdAt.isEmpty ? null : response.createdAt;
    author = response.author;
    metadata = Map<String, String>.from(response.metadata);
    deprecated = response.deprecated;
    username = response.username;
  }

  /// The unique reference URI for this artifact.
  late final Kref kref;

  /// The name of the artifact (e.g., "mesh", "textures").
  late final String name;

  /// The file path or URI where the artifact is stored.
  late final String location;

  /// Reference to the parent revision.
  late final Kref revisionKref;

  /// Reference to the parent item.
  late final Kref? itemKref;

  /// ISO timestamp when the artifact was created.
  late final String? createdAt;

  /// The user ID who created the artifact.
  late final String author;

  /// Custom metadata key-value pairs.
  late final Map<String, String> metadata;

  /// Whether the artifact is deprecated.
  late final bool deprecated;

  /// Display name of the creator.
  late final String username;

  /// Gets the parent revision of this artifact.
  ///
  /// This is a convenience wrapper around [KumihoClient.getRevision] that
  /// returns the high-level [Revision] model rather than the protobuf
  /// payload.
  ///
  /// ```dart
  /// final rev = await artifact.revision;
  /// ```
  Future<dynamic> get revision async {
    return client.getRevision(revisionKref.uri);
  }

  /// Sets this artifact as the default for its revision.
  ///
  /// The default artifact is returned when a revision kref is resolved
  /// without an explicit artifact name.
  ///
  /// ```dart
  /// await mesh.setDefault();
  /// ```
  Future<void> setDefault() async {
    await client.setDefaultArtifact(revisionKref.uri, name);
  }

  /// Sets metadata for this artifact.
  ///
  /// Each key/value is stored as an attribute on the artifact kref.
  /// Metadata is immediately available to other SDK callers and in the
  /// web console. Existing keys are overwritten; to remove a key, set its
  /// value to an empty string.
  ///
  /// ```dart
  /// await artifact.setMetadata({
  ///   'file_size': '125MB',
  ///   'format': 'FBX',
  /// });
  /// ```
  Future<void> setMetadata(Map<String, String> metadata) async {
    for (final entry in metadata.entries) {
      await client.setAttribute(kref.uri, entry.key, entry.value);
    }
  }

  /// Gets a metadata value by key.
  ///
  /// Returns `null` when the attribute is not set.
  ///
  /// ```dart
  /// final format = await artifact.getMetadataValue('format');
  /// ```
  Future<String?> getMetadataValue(String key) async {
    final response = await client.getAttribute(kref.uri, key);
    return response.value.isEmpty ? null : response.value;
  }

  /// Deletes this artifact.
  ///
  /// ```dart
  /// await artifact.delete();
  /// ```
  Future<void> delete() async {
    await client.deleteArtifact(kref.uri);
  }

  /// Gets the parent revision of this artifact.
  ///
  /// ```dart
  /// final revision = await artifact.getRevision();
  /// ```
  Future<dynamic> getRevision() async {
    return client.getRevision(revisionKref.uri);
  }

  /// Gets the parent item of this artifact.
  ///
  /// ```dart
  /// final item = await artifact.getItem();
  /// ```
  Future<dynamic> getItem() async {
    final targetKref = itemKref ?? revisionKref.itemKref;
    return client.getItemByKref(targetKref.uri);
  }

  @override
  String toString() => "Artifact(kref: '${kref.uri}', location: '$location')";
}
