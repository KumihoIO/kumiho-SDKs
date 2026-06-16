// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'package:grpc/grpc.dart' show GrpcError, StatusCode;

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';
import '../models/base.dart' show KumihoError;

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
  /// [existsError] controls whether to throw if revision exists (default: `false`).
  Future<RevisionResponse> createRevision(
    String itemKref, {
    Map<String, String>? metadata,
    int? number,
    bool existsError = false,
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

  /// Gets a revision by its kref URI, with optional tag/time resolution.
  ///
  /// [kref] can include the revision number (e.g., '?r=1'), or a tag
  /// (`?t=`/`?tag=`) or timestamp (`?time=`) query parameter. When a tag or
  /// time is present the kref is resolved via [resolveKref]; otherwise the
  /// revision is fetched directly.
  Future<RevisionResponse> getRevision(String kref) async {
    var baseKref = kref;
    String? tag;
    String? time;

    final queryIndex = kref.indexOf('?');
    if (queryIndex >= 0) {
      baseKref = kref.substring(0, queryIndex);
      final params = kref.substring(queryIndex + 1).split('&');
      for (final param in params) {
        if (param.startsWith('t=') || param.startsWith('tag=')) {
          tag = param.substring(param.indexOf('=') + 1);
        } else if (param.startsWith('time=')) {
          time = param.substring(param.indexOf('=') + 1);
          // Validate time format (YYYYMMDDHHMM).
          if (!RegExp(r'^\d{12}$').hasMatch(time)) {
            throw const KumihoError('time must be in YYYYMMDDHHMM format');
          }
        }
      }
    }

    if (tag != null || time != null) {
      // Resolve the base (item) kref with the supplied constraints.
      return resolveKref(baseKref, tag: tag, time: time);
    }

    final request = KrefRequest()..kref = Kref(uri: kref);
    final response = await stub.getRevision(request, options: callOptions);
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
  /// Returns the full [ResolveLocationResponse] for the resolved revision's
  /// default artifact.
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

  /// Resolves a kref to a file location string, or `null` if it cannot be
  /// resolved.
  ///
  /// Mirrors Python's `client.resolve`: parses any tag (`?t=`/`?tag=`) or
  /// timestamp (`?time=`) from the kref, calls the `ResolveLocation` RPC, and
  /// returns the resulting location. Any RPC failure is swallowed and surfaced
  /// as `null`.
  Future<String?> resolve(String kref) async {
    String? tag;
    String? time;

    final queryIndex = kref.indexOf('?');
    if (queryIndex >= 0) {
      final params = kref.substring(queryIndex + 1).split('&');
      for (final param in params) {
        if (param.startsWith('t=') || param.startsWith('tag=')) {
          tag = param.substring(param.indexOf('=') + 1);
        } else if (param.startsWith('time=')) {
          time = param.substring(param.indexOf('=') + 1);
        }
      }
    }

    try {
      final response = await resolveLocation(kref, tag: tag, time: time);
      return response.location;
    } catch (_) {
      return null;
    }
  }

  /// Gets the latest revision for an item, or `null` if none exist.
  ///
  /// Mirrors Python's `get_latest_revision`: resolves the item kref via the
  /// `ResolveKref` RPC and returns `null` when the control plane reports the
  /// item has no revisions (NOT_FOUND).
  Future<RevisionResponse?> getLatestRevision(String itemKref) async {
    try {
      return await resolveKref(itemKref);
    } on GrpcError catch (e) {
      if (e.code == StatusCode.notFound) {
        return null;
      }
      rethrow;
    }
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
