// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'package:grpc/grpc.dart' show CallOptions;

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
  /// [cursor] resumes from a previous cursor position (Creator tier+). Pass
  /// the cursor from the last received event to continue after reconnection.
  /// [consumerGroup] enables load-balanced delivery across consumers in the
  /// same group (Enterprise tier only).
  /// [fromBeginning] starts from the earliest available events instead of
  /// live-only (Creator tier+, subject to retention).
  /// [timeout] optionally bounds the gRPC stream; when reached the stream
  /// terminates with a `DEADLINE_EXCEEDED` error.
  ///
  /// Returns a stream of [Event] objects. The stream stays open until
  /// cancelled, the connection is lost, or [timeout] elapses.
  Stream<Event> eventStream({
    String? routingKeyFilter,
    String? krefFilter,
    String? cursor,
    String? consumerGroup,
    bool fromBeginning = false,
    Duration? timeout,
  }) {
    final request = EventStreamRequest();
    if (routingKeyFilter != null && routingKeyFilter.isNotEmpty) {
      request.routingKeyFilter = routingKeyFilter;
    }
    if (krefFilter != null && krefFilter.isNotEmpty) {
      request.krefFilter = krefFilter;
    }
    if (cursor != null && cursor.isNotEmpty) {
      request.cursor = cursor;
    }
    if (consumerGroup != null && consumerGroup.isNotEmpty) {
      request.consumerGroup = consumerGroup;
    }
    if (fromBeginning) {
      request.fromBeginning = true;
    }
    final options =
        timeout == null ? callOptions : mergeOptions(CallOptions(timeout: timeout));
    return stub.eventStream(request, options: options);
  }

  /// Gets event streaming capabilities for the current tenant tier.
  ///
  /// Mirrors Python's `get_event_capabilities`. Use the returned
  /// [EventCapabilities] to determine which features (cursor resume, consumer
  /// groups, replay) are available before calling [eventStream].
  ///
  /// The returned fields are:
  /// - `supportsReplay`: can replay past events
  /// - `supportsCursor`: can resume from a cursor
  /// - `supportsConsumerGroups`: can use consumer groups (Enterprise)
  /// - `maxRetentionHours`: event retention period (-1 = unlimited)
  /// - `maxBufferSize`: max events in buffer (-1 = unlimited)
  /// - `tier`: tier name (free, creator, studio, enterprise)
  Future<EventCapabilities> getEventCapabilities() async {
    final request = GetEventCapabilitiesRequest();
    return stub.getEventCapabilities(request, options: callOptions);
  }
}

