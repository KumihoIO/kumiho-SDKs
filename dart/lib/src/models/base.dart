// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Base classes for Kumiho domain objects.
///
/// This module provides the base classes used by all Kumiho model objects.
library;

/// Base exception class for all Kumiho errors.
///
/// All custom exceptions raised by the Kumiho SDK inherit from this class,
/// making it easy to catch all Kumiho-related errors.
///
/// ```dart
/// try {
///   final project = await kumiho.getProject('nonexistent');
/// } on KumihoError catch (e) {
///   print('Kumiho error: $e');
/// }
/// ```
class KumihoError implements Exception {
  /// Creates a new [KumihoError] with the given [message].
  const KumihoError(this.message);

  /// The error message.
  final String message;

  @override
  String toString() => 'KumihoError: $message';
}

/// Item kinds that are reserved and cannot be created via `createItem`.
///
/// The `bundle` kind must be created with `createBundle` instead.
const Set<String> reservedKinds = {'bundle'};

/// Raised when attempting to create an item with a reserved kind.
///
/// Thrown by `createItem` when the requested kind (case-insensitive) is in
/// [reservedKinds] (e.g. `bundle`). Use `createBundle` instead. Mirrors the
/// Python SDK's `ReservedKindError`.
class ReservedKindError extends KumihoError {
  /// Creates a new [ReservedKindError] with the given [message].
  const ReservedKindError(super.message);

  @override
  String toString() => 'ReservedKindError: $message';
}

/// Forward declaration of the client type.
/// 
/// This allows model classes to hold a reference to the client
/// without creating circular dependencies.
abstract class KumihoClientBase {
  // Marker interface - actual implementation in kumiho_client.dart
}

/// Base class for all high-level Kumiho domain objects.
///
/// This abstract base class provides common functionality shared by all
/// Kumiho objects, including access to the client for making API calls.
/// Subclasses build on top of protobuf responses to provide an expressive,
/// documentable surface for SDK users.
///
/// All domain objects ([Project], [Space], [Item], [Revision], [Artifact],
/// [Edge], [Bundle]) inherit from this class.
abstract class KumihoObject {
  /// Creates a new [KumihoObject] with a client reference.
  KumihoObject(this.client);

  /// The client instance for making API calls.
  /// 
  /// This is exposed to subclasses for making API calls.
  final dynamic client;
}
