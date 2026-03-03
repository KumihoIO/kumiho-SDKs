// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Revision API mixin for managing item versions.
///
/// Revisions are immutable snapshots of an item at a point in time. Each
/// revision can have multiple artifacts (file references), tags for
/// categorization, and edges to other revisions for dependency tracking.
///
/// The revision's kref includes the revision number:
/// `kref://project/space/item.kind?r=1`
///
/// ```dart
/// // Create a revision
/// final revision = await client.createRevision(
///   item.kref.uri,
///   metadata: {'artist': 'john'},
/// );
///
/// // Tag a revision
/// await client.tagRevision(revision.kref.uri, 'approved');
///
/// // Resolve a kref with tag
/// final approved = await client.resolveKref(
///   'kref://project/space/hero.model',
///   tag: 'approved',
/// );
/// ```
mixin RevisionApi on KumihoClientBase {
  /// Creates a new revision for an item.
  ///
  /// [itemKref] is the item's kref URI.
  /// [metadata] is optional key-value pairs to attach.
  /// [number] is optional; if not provided, uses the next available number.
  /// [existsError] controls whether to throw if revision exists (default: `true`).
  Future<RevisionResponse> createRevision(
    String itemKref, {
    Map<String, String>? metadata,
    int? number,
    bool existsError = true,
  }) async {
    final request = CreateRevisionRequest()
      ..itemKref = Kref(uri: itemKref)
      ..existsError = existsError;
    if (metadata != null) {
      request.metadata.addAll(metadata);
    }
    if (number != null && number > 0) {
      request.number = number;
    }
    return stub.createRevision(request, options: callOptions);
  }

  /// Gets a revision by its kref URI.
  ///
  /// [kref] must include the revision number (e.g., '?r=1').
  Future<RevisionResponse> getRevision(String kref) async {
    final request = KrefRequest()..kref = Kref(uri: kref);
    final response = await stub.getRevision(request, options: callOptions);
    // Debug: print the raw response
    print('DEBUG getRevision response:');
    print('  name: "${response.name}"');
    print('  username: "${response.username}"');
    print('  defaultArtifact: "${response.defaultArtifact}"');
    print('  hasDefaultArtifact(): ${response.hasDefaultArtifact()}');
    return response;
  }

  /// Lists all revisions for an item.
  ///
  /// [itemKref] is the item's kref URI.
  /// Returns revisions ordered by number (newest first by default).
  Future<List<RevisionResponse>> getRevisions(String itemKref) async {
    final request = GetRevisionsRequest()..itemKref = Kref(uri: itemKref);
    final response = await stub.getRevisions(request, options: callOptions);
    return response.revisions;
  }

  /// Resolves a kref to a specific revision.
  ///
  /// [kref] is the item kref (can include revision).
  /// [tag] resolves to the revision with this tag.
  /// [time] resolves to the revision at this timestamp (YYYYMMDDHHMM format).
  ///
  /// If neither tag nor time is provided, resolves to the latest revision.
  Future<RevisionResponse> resolveKref(
    String kref, {
    String? tag,
    String? time,
  }) async {
    final request = ResolveKrefRequest()..kref = kref;
    if (tag != null && tag.isNotEmpty) {
      request.tag = tag;
    }
    if (time != null && time.isNotEmpty) {
      request.time = time;
    }
    return stub.resolveKref(request, options: callOptions);
  }

  /// Resolves a kref to a file location.
  ///
  /// Returns the location of the default artifact for the resolved revision.
  Future<ResolveLocationResponse> resolveLocation(
    String kref, {
    String? tag,
    String? time,
  }) async {
    final request = ResolveLocationRequest()..kref = kref;
    if (tag != null && tag.isNotEmpty) {
      request.tag = tag;
    }
    if (time != null && time.isNotEmpty) {
      request.time = time;
    }
    return stub.resolveLocation(request, options: callOptions);
  }

  /// Gets the latest revision for an item.
  ///
  /// Convenience method that resolves to the revision with the 'latest' tag.
  Future<RevisionResponse> getLatestRevision(String itemKref) async {
    final revisions = await getRevisions(itemKref);
    if (revisions.isEmpty) {
      throw Exception('No revisions found');
    }
    return revisions.firstWhere(
      (revision) => revision.latest,
      orElse: () => revisions.first,
    );
  }

  /// Peeks at the next revision number without creating it.
  ///
  /// [itemKref] is the item's kref URI.
  /// Returns the number that would be assigned to the next revision.
  Future<int> peekNextRevision(String itemKref) async {
    final request = PeekNextRevisionRequest()..itemKref = Kref(uri: itemKref);
    final response = await stub.peekNextRevision(request, options: callOptions);
    return response.number;
  }

  /// Deletes a revision.
  ///
  /// By default, deletion fails if the revision has artifacts or edges.
  /// Set [force] to `true` to delete with all contents.
  ///
  /// **Warning**: Force deletion removes all artifacts and edges.
  Future<StatusResponse> deleteRevision(
    String kref, {
    bool force = false,
  }) async {
    final request = DeleteRevisionRequest()
      ..kref = Kref(uri: kref)
      ..force = force;
    return stub.deleteRevision(request, options: callOptions);
  }

  /// Updates metadata for a revision.
  ///
  /// [kref] is the revision's kref URI.
  /// [metadata] is a map of key-value pairs to set or update.
  Future<RevisionResponse> updateRevisionMetadata(
    String kref,
    Map<String, String> metadata,
  ) async {
    final request = UpdateMetadataRequest()
      ..kref = Kref(uri: kref)
      ..metadata.addAll(metadata);
    return stub.updateRevisionMetadata(request, options: callOptions);
  }

  /// Tags a revision.
  ///
  /// Tags are used to mark revisions for easy retrieval (e.g., 'approved',
  /// 'published'). Some tags like 'published' have special semantics.
  ///
  /// Note: 'latest' is a reserved system tag managed by the server and cannot
  /// be set or removed manually.
  Future<StatusResponse> tagRevision(String kref, String tag) async {
    final request = TagRevisionRequest()
      ..kref = Kref(uri: kref)
      ..tag = tag;
    return stub.tagRevision(request, options: callOptions);
  }

  /// Removes a tag from a revision.
  Future<StatusResponse> untagRevision(String kref, String tag) async {
    final request = UnTagRevisionRequest()
      ..kref = Kref(uri: kref)
      ..tag = tag;
    return stub.unTagRevision(request, options: callOptions);
  }

  /// Checks if a revision currently has a tag.
  Future<bool> hasTag(String kref, String tag) async {
    final request = HasTagRequest()
      ..kref = Kref(uri: kref)
      ..tag = tag;
    final response = await stub.hasTag(request, options: callOptions);
    return response.hasTag;
  }

  /// Checks if a revision was ever tagged (including removed tags).
  ///
  /// Useful for audit trails and compliance checking.
  Future<bool> wasTagged(String kref, String tag) async {
    final request = WasTaggedRequest()
      ..kref = Kref(uri: kref)
      ..tag = tag;
    final response = await stub.wasTagged(request, options: callOptions);
    return response.wasTagged;
  }

  /// Sets the default artifact for a revision.
  ///
  /// The default artifact is used when resolving a kref to a location.
  Future<StatusResponse> setDefaultArtifact(
    String revisionKref,
    String artifactName,
  ) async {
    final request = SetDefaultArtifactRequest()
      ..revisionKref = Kref(uri: revisionKref)
      ..artifactName = artifactName;
    return stub.setDefaultArtifact(request, options: callOptions);
  }
}
