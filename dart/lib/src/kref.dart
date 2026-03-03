// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Kref module for Kumiho artifact references.
///
/// The [Kref] class represents a Kumiho Artifact Reference—a URI-based unique
/// identifier for any object in the Kumiho system.
///
/// ## Kref Format
///
/// The kref URI follows this pattern:
/// ```
/// kref://project/space/item.kind?r=REVISION&a=ARTIFACT
/// ```
///
/// Components:
/// - `project`: The project name
/// - `space`: The space path (can be nested: `space/subspace`)
/// - `item.kind`: Item name and kind separated by dot
/// - `?r=REVISION`: Optional revision number
/// - `&a=ARTIFACT`: Optional artifact name
///
/// ## Examples
///
/// Item kref:
/// ```dart
/// Kref('kref://film-2024/characters/hero.model')
/// ```
///
/// Revision kref:
/// ```dart
/// Kref('kref://film-2024/characters/hero.model?r=3')
/// ```
///
/// Artifact kref:
/// ```dart
/// Kref('kref://film-2024/characters/hero.model?r=3&a=mesh')
/// ```
library;

/// Exception thrown when a Kref URI is invalid or contains malicious patterns.
class KrefValidationError implements Exception {
  /// Creates a new [KrefValidationError] with the given [message].
  const KrefValidationError(this.message);

  /// The error message.
  final String message;

  @override
  String toString() => 'KrefValidationError: $message';
}

/// Regex pattern for validating Kref URIs.
final _krefPattern = RegExp(
  r'^kref://'
  r'(/[a-zA-Z0-9][a-zA-Z0-9._-]*'
  r'(/[a-zA-Z0-9][a-zA-Z0-9._-]*)*'
  r'|'
  r'[a-zA-Z0-9][a-zA-Z0-9._-]*'
  r'(/[a-zA-Z0-9][a-zA-Z0-9._-]*)*)'
  r'(\?r=\d+(&a=[a-zA-Z0-9._-]+)?)?$',
);

/// Validates a Kref URI for security and correctness.
///
/// Checks for:
/// - Proper `kref://` scheme
/// - No path traversal patterns (`..`)
/// - No control characters
/// - Valid path segment format
///
/// Throws a [KrefValidationError] if the URI is invalid.
///
/// ```dart
/// try {
///   validateKref('kref://project/space/item.kind?r=1');
/// } on KrefValidationError catch (e) {
///   print('Invalid kref: $e');
/// }
/// ```
void validateKref(String uri) {
  if (uri.contains('..')) {
    throw KrefValidationError(
      "Invalid kref URI '$uri': path traversal (..) not allowed",
    );
  }

  // Check for control characters
  for (var i = 0; i < uri.length; i++) {
    final code = uri.codeUnitAt(i);
    if (code < 32 || code == 127) {
      throw KrefValidationError(
        "Invalid kref URI '$uri': control characters not allowed",
      );
    }
  }

  if (!_krefPattern.hasMatch(uri)) {
    throw KrefValidationError(
      "Invalid kref URI '$uri': must be format kref://project/space/item.kind",
    );
  }
}

/// Checks if a Kref URI is valid without throwing exceptions.
///
/// Returns `true` if the URI is valid, `false` otherwise.
bool isValidKref(String uri) {
  try {
    validateKref(uri);
    return true;
  } on KrefValidationError {
    return false;
  }
}

/// A Kumiho Artifact Reference (URI-based unique identifier).
///
/// Kref provides utility methods for parsing and extracting components
/// from the URI while behaving like a regular String.
///
/// ```dart
/// final kref = Kref('kref://project/models/hero.model?r=2&a=mesh');
///
/// print(kref.project);       // 'project'
/// print(kref.space);         // 'models'
/// print(kref.itemName);      // 'hero'
/// print(kref.kind);          // 'model'
/// print(kref.revision);      // 2
/// print(kref.artifactName);  // 'mesh'
/// ```
class Kref {
  /// Creates a new [Kref] from the given URI string.
  ///
  /// Optionally validates the URI format if [validate] is `true` (default).
  Kref(this.uri, {bool validate = true}) {
    if (validate) {
      validateKref(uri);
    }
  }

  /// The raw URI string.
  final String uri;

  /// Gets the project name from the kref.
  ///
  /// Returns the first path segment after `kref://`.
  String get project {
    final path = _getPath();
    final segments = path.split('/').where((s) => s.isNotEmpty).toList();
    return segments.isNotEmpty ? segments.first : '';
  }

  /// Gets the space path from the kref.
  ///
  /// Returns the path segments between project and item.
  String get space {
    final path = _getPath();
    final segments = path.split('/').where((s) => s.isNotEmpty).toList();
    if (segments.length <= 2) return '';

    // Last segment is item.kind, first is project
    return segments.sublist(1, segments.length - 1).join('/');
  }

  /// Gets the full item name including kind (e.g., "hero.model").
  String get fullItemName {
    final path = _getPath();
    final segments = path.split('/').where((s) => s.isNotEmpty).toList();
    return segments.isNotEmpty ? segments.last : '';
  }

  /// Gets the item name without kind (e.g., "hero").
  String get itemName {
    final full = fullItemName;
    final dotIndex = full.lastIndexOf('.');
    return dotIndex > 0 ? full.substring(0, dotIndex) : full;
  }

  /// Gets the item kind (e.g., "model").
  String get kind {
    final full = fullItemName;
    final dotIndex = full.lastIndexOf('.');
    return dotIndex > 0 ? full.substring(dotIndex + 1) : '';
  }

  /// Gets the revision number, or `null` if not specified.
  int? get revision {
    final match = RegExp(r'\?r=(\d+)').firstMatch(uri);
    if (match == null) return null;
    return int.tryParse(match.group(1)!);
  }

  /// Gets the artifact name, or `null` if not specified.
  String? get artifactName {
    final match = RegExp(r'&a=([a-zA-Z0-9._-]+)').firstMatch(uri);
    return match?.group(1);
  }

  /// Gets the item kref (without revision or artifact).
  Kref get itemKref {
    final path = _getPath();
    return Kref('kref://$path', validate: false);
  }

  /// Gets the revision kref (without artifact).
  Kref? get revisionKref {
    final rev = revision;
    if (rev == null) return null;
    final path = _getPath();
    return Kref('kref://$path?r=$rev', validate: false);
  }

  String _getPath() {
    var path = uri.replaceFirst('kref://', '');
    // Remove query parameters
    final queryIndex = path.indexOf('?');
    if (queryIndex >= 0) {
      path = path.substring(0, queryIndex);
    }
    return path;
  }

  /// Creates a new kref with a revision number.
  Kref withRevision(int number) {
    final path = _getPath();
    return Kref('kref://$path?r=$number', validate: false);
  }

  /// Creates a new kref with an artifact name.
  Kref withArtifact(String name) {
    final rev = revision;
    if (rev == null) {
      throw StateError('Cannot add artifact to kref without revision');
    }
    final path = _getPath();
    return Kref('kref://$path?r=$rev&a=$name', validate: false);
  }

  @override
  String toString() => uri;

  @override
  bool operator ==(Object other) =>
      identical(this, other) || (other is Kref && other.uri == uri);

  @override
  int get hashCode => uri.hashCode;
}
