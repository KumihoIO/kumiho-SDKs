// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Event API mixin for real-time event streaming.
///
/// Kumiho provides real-time event streaming for monitoring changes to
/// projects, spaces, items, revisions, and artifacts. Events can be
/// filtered by routing key patterns or kref patterns.
///
/// ## Routing Key Patterns
///
/// Events use dot-separated routing keys:
/// - `item.model.created` - model item created
/// - `revision.tagged.*` - any revision tagged
/// - `artifact.*.*` - any artifact event
///
/// ## Kref Patterns
///
/// Filter by object URI patterns:
/// - `kref://projectA/**/*.model` - all models in projectA
/// - `kref://*/characters/*` - all items in characters spaces
///
/// ```dart
/// // Subscribe to all events
/// client.eventStream().listen((event) {
///   print('Event: ${event.routingKey} on ${event.kref.uri}');
/// });
///
/// // Subscribe to specific events
/// client.eventStream(
///   routingKeyFilter: 'revision.tagged.*',
///   krefFilter: 'kref://my-project/**/*',
/// ).listen((event) {
///   print('Tagged: ${event.kref.uri}');
/// });
/// ```
mixin EventApi on KumihoClientBase {
  /// Subscribes to real-time events.
  ///
  /// [routingKeyFilter] filters by routing key pattern (supports wildcards).
  /// [krefFilter] filters by kref pattern (supports wildcards).
  ///
  /// Returns a stream of [Event] objects. The stream stays open until
  /// cancelled or the connection is lost.
  Stream<Event> eventStream({
    String? routingKeyFilter,
    String? krefFilter,
  }) {
    final request = EventStreamRequest();
    if (routingKeyFilter != null && routingKeyFilter.isNotEmpty) {
      request.routingKeyFilter = routingKeyFilter;
    }
    if (krefFilter != null && krefFilter.isNotEmpty) {
      request.krefFilter = krefFilter;
    }
    return stub.eventStream(request, options: callOptions);
  }
}

