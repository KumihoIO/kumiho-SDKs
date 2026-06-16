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
import 'item.dart';
import 'space.dart';
import 'project.dart';

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
  ///
  /// Mutable so [setDeprecated] can keep the local model in sync with the
  /// server after a successful update.
  late bool deprecated;

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
  /// Existing keys are overwritten and new keys are added in a single RPC.
  /// Metadata is immediately available to other SDK callers and in the
  /// web console.
  ///
  /// ```dart
  /// await artifact.setMetadata({
  ///   'file_size': '125MB',
  ///   'format': 'FBX',
  /// });
  /// ```
  Future<void> setMetadata(Map<String, String> metadata) async {
    await client.updateArtifactMetadata(kref.uri, metadata);
  }

  /// Gets a metadata value by key.
  ///
  /// Returns `null` only when the attribute is not set. An attribute that
  /// exists with an empty-string value returns `''`, not `null`.
  ///
  /// ```dart
  /// final format = await artifact.getMetadataValue('format');
  /// ```
  Future<String?> getMetadataValue(String key) async {
    final response = await client.getAttribute(kref.uri, key);
    return response.exists ? response.value : null;
  }

  /// Sets the deprecated status of this artifact.
  ///
  /// Deprecated artifacts are hidden from default queries but remain
  /// accessible for historical reference.
  ///
  /// ```dart
  /// await artifact.setDeprecated(true);   // Hide from queries
  /// await artifact.setDeprecated(false);  // Restore visibility
  /// ```
  Future<void> setDeprecated(bool status) async {
    await client.setDeprecated(kref.uri, status);
    deprecated = status;
  }

  /// Deletes this artifact.
  ///
  /// If [force] is true, force deletion regardless of normal rules.
  ///
  /// ```dart
  /// await artifact.delete();
  /// ```
  Future<void> delete({bool force = false}) async {
    await client.deleteArtifact(kref.uri, force: force);
  }

  /// Gets the parent revision of this artifact.
  ///
  /// ```dart
  /// final revision = await artifact.getRevision();
  /// ```
  Future<dynamic> getRevision() async {
    return client.getRevision(revisionKref.uri);
  }

  /// Gets the parent item of this artifact as an [Item] model.
  ///
  /// ```dart
  /// final item = await artifact.getItem();
  /// ```
  Future<Item> getItem() async {
    final targetKref = itemKref ?? revisionKref.itemKref;
    final response = await client.getItemByKref(targetKref.uri);
    return Item(response, client);
  }

  /// Gets the space containing this artifact's item as a [Space] model.
  ///
  /// ```dart
  /// final space = await artifact.getSpace();
  /// print(space.path);
  /// ```
  Future<Space> getSpace() async {
    final item = await getItem();
    return item.getSpace();
  }

  /// Gets the project containing this artifact as a [Project] model.
  ///
  /// ```dart
  /// final project = await artifact.getProject();
  /// print(project.name);
  /// ```
  Future<Project> getProject() async {
    final item = await getItem();
    return item.getProject();
  }

  @override
  String toString() => "Artifact(kref: '${kref.uri}', location: '$location')";
}
