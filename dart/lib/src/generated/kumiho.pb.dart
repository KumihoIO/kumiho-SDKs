// This is a generated file - do not edit.
//
// Generated from kumiho.proto.

// @dart = 3.3

// ignore_for_file: annotate_overrides, camel_case_types, comment_references
// ignore_for_file: constant_identifier_names
// ignore_for_file: curly_braces_in_flow_control_structures
// ignore_for_file: deprecated_member_use_from_same_package, library_prefixes
// ignore_for_file: non_constant_identifier_names, prefer_relative_imports

import 'dart:async' as $async;
import 'dart:core' as $core;

import 'package:fixnum/fixnum.dart' as $fixnum;
import 'package:protobuf/protobuf.dart' as $pb;

import 'kumiho.pbenum.dart';

export 'package:protobuf/protobuf.dart' show GeneratedMessageGenericExtensions;

export 'kumiho.pbenum.dart';

/// A Kumiho Reference (Kref) uniquely identifies any object in the system.
class Kref extends $pb.GeneratedMessage {
  factory Kref({
    $core.String? uri,
  }) {
    final result = create();
    if (uri != null) result.uri = uri;
    return result;
  }

  Kref._();

  factory Kref.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory Kref.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'Kref',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'uri')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Kref clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Kref copyWith(void Function(Kref) updates) =>
      super.copyWith((message) => updates(message as Kref)) as Kref;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static Kref create() => Kref._();
  @$core.override
  Kref createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static Kref getDefault() =>
      _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Kref>(create);
  static Kref? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get uri => $_getSZ(0);
  @$pb.TagNumber(1)
  set uri($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasUri() => $_has(0);
  @$pb.TagNumber(1)
  void clearUri() => $_clearField(1);
}

/// An Edge represents a directed, typed relationship between two revisions.
class Edge extends $pb.GeneratedMessage {
  factory Edge({
    Kref? sourceKref,
    Kref? targetKref,
    $core.String? edgeType,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.String? createdAt,
    $core.String? author,
    $core.String? username,
  }) {
    final result = create();
    if (sourceKref != null) result.sourceKref = sourceKref;
    if (targetKref != null) result.targetKref = targetKref;
    if (edgeType != null) result.edgeType = edgeType;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (createdAt != null) result.createdAt = createdAt;
    if (author != null) result.author = author;
    if (username != null) result.username = username;
    return result;
  }

  Edge._();

  factory Edge.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory Edge.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'Edge',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'sourceKref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'targetKref', subBuilder: Kref.create)
    ..aOS(3, _omitFieldNames ? '' : 'edgeType')
    ..m<$core.String, $core.String>(4, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'Edge.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOS(5, _omitFieldNames ? '' : 'createdAt')
    ..aOS(6, _omitFieldNames ? '' : 'author')
    ..aOS(7, _omitFieldNames ? '' : 'username')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Edge clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Edge copyWith(void Function(Edge) updates) =>
      super.copyWith((message) => updates(message as Edge)) as Edge;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static Edge create() => Edge._();
  @$core.override
  Edge createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static Edge getDefault() =>
      _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Edge>(create);
  static Edge? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get sourceKref => $_getN(0);
  @$pb.TagNumber(1)
  set sourceKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasSourceKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearSourceKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureSourceKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get targetKref => $_getN(1);
  @$pb.TagNumber(2)
  set targetKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasTargetKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearTargetKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureTargetKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.String get edgeType => $_getSZ(2);
  @$pb.TagNumber(3)
  set edgeType($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasEdgeType() => $_has(2);
  @$pb.TagNumber(3)
  void clearEdgeType() => $_clearField(3);

  @$pb.TagNumber(4)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(3);

  @$pb.TagNumber(5)
  $core.String get createdAt => $_getSZ(4);
  @$pb.TagNumber(5)
  set createdAt($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasCreatedAt() => $_has(4);
  @$pb.TagNumber(5)
  void clearCreatedAt() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.String get author => $_getSZ(5);
  @$pb.TagNumber(6)
  set author($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasAuthor() => $_has(5);
  @$pb.TagNumber(6)
  void clearAuthor() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get username => $_getSZ(6);
  @$pb.TagNumber(7)
  set username($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasUsername() => $_has(6);
  @$pb.TagNumber(7)
  void clearUsername() => $_clearField(7);
}

class StatusResponse extends $pb.GeneratedMessage {
  factory StatusResponse({
    $core.bool? success,
    $core.String? message,
  }) {
    final result = create();
    if (success != null) result.success = success;
    if (message != null) result.message = message;
    return result;
  }

  StatusResponse._();

  factory StatusResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory StatusResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'StatusResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'success')
    ..aOS(2, _omitFieldNames ? '' : 'message')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  StatusResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  StatusResponse copyWith(void Function(StatusResponse) updates) =>
      super.copyWith((message) => updates(message as StatusResponse))
          as StatusResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static StatusResponse create() => StatusResponse._();
  @$core.override
  StatusResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static StatusResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<StatusResponse>(create);
  static StatusResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get success => $_getBF(0);
  @$pb.TagNumber(1)
  set success($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasSuccess() => $_has(0);
  @$pb.TagNumber(1)
  void clearSuccess() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get message => $_getSZ(1);
  @$pb.TagNumber(2)
  set message($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasMessage() => $_has(1);
  @$pb.TagNumber(2)
  void clearMessage() => $_clearField(2);
}

/// Pagination parameters for list requests
class PaginationRequest extends $pb.GeneratedMessage {
  factory PaginationRequest({
    $core.int? pageSize,
    $core.String? cursor,
  }) {
    final result = create();
    if (pageSize != null) result.pageSize = pageSize;
    if (cursor != null) result.cursor = cursor;
    return result;
  }

  PaginationRequest._();

  factory PaginationRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory PaginationRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'PaginationRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aI(1, _omitFieldNames ? '' : 'pageSize')
    ..aOS(2, _omitFieldNames ? '' : 'cursor')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PaginationRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PaginationRequest copyWith(void Function(PaginationRequest) updates) =>
      super.copyWith((message) => updates(message as PaginationRequest))
          as PaginationRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static PaginationRequest create() => PaginationRequest._();
  @$core.override
  PaginationRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static PaginationRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<PaginationRequest>(create);
  static PaginationRequest? _defaultInstance;

  /// Maximum number of items to return (default: 100, max: 1000)
  @$pb.TagNumber(1)
  $core.int get pageSize => $_getIZ(0);
  @$pb.TagNumber(1)
  set pageSize($core.int value) => $_setSignedInt32(0, value);
  @$pb.TagNumber(1)
  $core.bool hasPageSize() => $_has(0);
  @$pb.TagNumber(1)
  void clearPageSize() => $_clearField(1);

  /// Cursor for the next page (opaque string from previous response)
  @$pb.TagNumber(2)
  $core.String get cursor => $_getSZ(1);
  @$pb.TagNumber(2)
  set cursor($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasCursor() => $_has(1);
  @$pb.TagNumber(2)
  void clearCursor() => $_clearField(2);
}

/// Pagination info in list responses
class PaginationResponse extends $pb.GeneratedMessage {
  factory PaginationResponse({
    $core.String? nextCursor,
    $core.bool? hasMore,
    $core.int? totalCount,
  }) {
    final result = create();
    if (nextCursor != null) result.nextCursor = nextCursor;
    if (hasMore != null) result.hasMore = hasMore;
    if (totalCount != null) result.totalCount = totalCount;
    return result;
  }

  PaginationResponse._();

  factory PaginationResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory PaginationResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'PaginationResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'nextCursor')
    ..aOB(2, _omitFieldNames ? '' : 'hasMore')
    ..aI(3, _omitFieldNames ? '' : 'totalCount')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PaginationResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PaginationResponse copyWith(void Function(PaginationResponse) updates) =>
      super.copyWith((message) => updates(message as PaginationResponse))
          as PaginationResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static PaginationResponse create() => PaginationResponse._();
  @$core.override
  PaginationResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static PaginationResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<PaginationResponse>(create);
  static PaginationResponse? _defaultInstance;

  /// Cursor for the next page, empty if no more results
  @$pb.TagNumber(1)
  $core.String get nextCursor => $_getSZ(0);
  @$pb.TagNumber(1)
  set nextCursor($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasNextCursor() => $_has(0);
  @$pb.TagNumber(1)
  void clearNextCursor() => $_clearField(1);

  /// Whether there are more results available
  @$pb.TagNumber(2)
  $core.bool get hasMore => $_getBF(1);
  @$pb.TagNumber(2)
  set hasMore($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasHasMore() => $_has(1);
  @$pb.TagNumber(2)
  void clearHasMore() => $_clearField(2);

  /// Total count of items (if available, -1 if unknown)
  @$pb.TagNumber(3)
  $core.int get totalCount => $_getIZ(2);
  @$pb.TagNumber(3)
  set totalCount($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTotalCount() => $_has(2);
  @$pb.TagNumber(3)
  void clearTotalCount() => $_clearField(3);
}

class KrefRequest extends $pb.GeneratedMessage {
  factory KrefRequest({
    Kref? kref,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    return result;
  }

  KrefRequest._();

  factory KrefRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory KrefRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'KrefRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  KrefRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  KrefRequest copyWith(void Function(KrefRequest) updates) =>
      super.copyWith((message) => updates(message as KrefRequest))
          as KrefRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static KrefRequest create() => KrefRequest._();
  @$core.override
  KrefRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static KrefRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<KrefRequest>(create);
  static KrefRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);
}

class ResolveKrefRequest extends $pb.GeneratedMessage {
  factory ResolveKrefRequest({
    $core.String? kref,
    $core.String? tag,
    $core.String? time,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    if (time != null) result.time = time;
    return result;
  }

  ResolveKrefRequest._();

  factory ResolveKrefRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ResolveKrefRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ResolveKrefRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'kref')
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..aOS(3, _omitFieldNames ? '' : 'time')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveKrefRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveKrefRequest copyWith(void Function(ResolveKrefRequest) updates) =>
      super.copyWith((message) => updates(message as ResolveKrefRequest))
          as ResolveKrefRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ResolveKrefRequest create() => ResolveKrefRequest._();
  @$core.override
  ResolveKrefRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ResolveKrefRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ResolveKrefRequest>(create);
  static ResolveKrefRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get kref => $_getSZ(0);
  @$pb.TagNumber(1)
  set kref($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get time => $_getSZ(2);
  @$pb.TagNumber(3)
  set time($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTime() => $_has(2);
  @$pb.TagNumber(3)
  void clearTime() => $_clearField(3);
}

class ResolveLocationRequest extends $pb.GeneratedMessage {
  factory ResolveLocationRequest({
    $core.String? kref,
    $core.String? tag,
    $core.String? time,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    if (time != null) result.time = time;
    return result;
  }

  ResolveLocationRequest._();

  factory ResolveLocationRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ResolveLocationRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ResolveLocationRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'kref')
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..aOS(3, _omitFieldNames ? '' : 'time')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveLocationRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveLocationRequest copyWith(
          void Function(ResolveLocationRequest) updates) =>
      super.copyWith((message) => updates(message as ResolveLocationRequest))
          as ResolveLocationRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ResolveLocationRequest create() => ResolveLocationRequest._();
  @$core.override
  ResolveLocationRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ResolveLocationRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ResolveLocationRequest>(create);
  static ResolveLocationRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get kref => $_getSZ(0);
  @$pb.TagNumber(1)
  set kref($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get time => $_getSZ(2);
  @$pb.TagNumber(3)
  set time($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTime() => $_has(2);
  @$pb.TagNumber(3)
  void clearTime() => $_clearField(3);
}

class ResolveLocationResponse extends $pb.GeneratedMessage {
  factory ResolveLocationResponse({
    $core.String? location,
    Kref? resolvedKref,
    $core.String? artifactName,
  }) {
    final result = create();
    if (location != null) result.location = location;
    if (resolvedKref != null) result.resolvedKref = resolvedKref;
    if (artifactName != null) result.artifactName = artifactName;
    return result;
  }

  ResolveLocationResponse._();

  factory ResolveLocationResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ResolveLocationResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ResolveLocationResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'location')
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'resolvedKref',
        subBuilder: Kref.create)
    ..aOS(3, _omitFieldNames ? '' : 'artifactName')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveLocationResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ResolveLocationResponse copyWith(
          void Function(ResolveLocationResponse) updates) =>
      super.copyWith((message) => updates(message as ResolveLocationResponse))
          as ResolveLocationResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ResolveLocationResponse create() => ResolveLocationResponse._();
  @$core.override
  ResolveLocationResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ResolveLocationResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ResolveLocationResponse>(create);
  static ResolveLocationResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get location => $_getSZ(0);
  @$pb.TagNumber(1)
  set location($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasLocation() => $_has(0);
  @$pb.TagNumber(1)
  void clearLocation() => $_clearField(1);

  @$pb.TagNumber(2)
  Kref get resolvedKref => $_getN(1);
  @$pb.TagNumber(2)
  set resolvedKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasResolvedKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearResolvedKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureResolvedKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.String get artifactName => $_getSZ(2);
  @$pb.TagNumber(3)
  set artifactName($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasArtifactName() => $_has(2);
  @$pb.TagNumber(3)
  void clearArtifactName() => $_clearField(3);
}

class CreateSpaceRequest extends $pb.GeneratedMessage {
  factory CreateSpaceRequest({
    $core.String? parentPath,
    $core.String? spaceName,
    $core.bool? existsError,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (spaceName != null) result.spaceName = spaceName;
    if (existsError != null) result.existsError = existsError;
    return result;
  }

  CreateSpaceRequest._();

  factory CreateSpaceRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateSpaceRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateSpaceRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOS(2, _omitFieldNames ? '' : 'spaceName')
    ..aOB(3, _omitFieldNames ? '' : 'existsError')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateSpaceRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateSpaceRequest copyWith(void Function(CreateSpaceRequest) updates) =>
      super.copyWith((message) => updates(message as CreateSpaceRequest))
          as CreateSpaceRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateSpaceRequest create() => CreateSpaceRequest._();
  @$core.override
  CreateSpaceRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateSpaceRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateSpaceRequest>(create);
  static CreateSpaceRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get spaceName => $_getSZ(1);
  @$pb.TagNumber(2)
  set spaceName($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasSpaceName() => $_has(1);
  @$pb.TagNumber(2)
  void clearSpaceName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.bool get existsError => $_getBF(2);
  @$pb.TagNumber(3)
  set existsError($core.bool value) => $_setBool(2, value);
  @$pb.TagNumber(3)
  $core.bool hasExistsError() => $_has(2);
  @$pb.TagNumber(3)
  void clearExistsError() => $_clearField(3);
}

class SpaceResponse extends $pb.GeneratedMessage {
  factory SpaceResponse({
    $core.String? path,
    $core.String? createdAt,
    $core.String? modifiedAt,
    $core.String? author,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.String? username,
    $core.String? name,
    $core.String? type,
  }) {
    final result = create();
    if (path != null) result.path = path;
    if (createdAt != null) result.createdAt = createdAt;
    if (modifiedAt != null) result.modifiedAt = modifiedAt;
    if (author != null) result.author = author;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (username != null) result.username = username;
    if (name != null) result.name = name;
    if (type != null) result.type = type;
    return result;
  }

  SpaceResponse._();

  factory SpaceResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory SpaceResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'SpaceResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'path')
    ..aOS(2, _omitFieldNames ? '' : 'createdAt')
    ..aOS(3, _omitFieldNames ? '' : 'modifiedAt')
    ..aOS(4, _omitFieldNames ? '' : 'author')
    ..m<$core.String, $core.String>(5, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'SpaceResponse.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOS(6, _omitFieldNames ? '' : 'username')
    ..aOS(7, _omitFieldNames ? '' : 'name')
    ..aOS(8, _omitFieldNames ? '' : 'type')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SpaceResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SpaceResponse copyWith(void Function(SpaceResponse) updates) =>
      super.copyWith((message) => updates(message as SpaceResponse))
          as SpaceResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static SpaceResponse create() => SpaceResponse._();
  @$core.override
  SpaceResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static SpaceResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<SpaceResponse>(create);
  static SpaceResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get path => $_getSZ(0);
  @$pb.TagNumber(1)
  set path($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get createdAt => $_getSZ(1);
  @$pb.TagNumber(2)
  set createdAt($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasCreatedAt() => $_has(1);
  @$pb.TagNumber(2)
  void clearCreatedAt() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get modifiedAt => $_getSZ(2);
  @$pb.TagNumber(3)
  set modifiedAt($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasModifiedAt() => $_has(2);
  @$pb.TagNumber(3)
  void clearModifiedAt() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.String get author => $_getSZ(3);
  @$pb.TagNumber(4)
  set author($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasAuthor() => $_has(3);
  @$pb.TagNumber(4)
  void clearAuthor() => $_clearField(4);

  @$pb.TagNumber(5)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(4);

  @$pb.TagNumber(6)
  $core.String get username => $_getSZ(5);
  @$pb.TagNumber(6)
  set username($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasUsername() => $_has(5);
  @$pb.TagNumber(6)
  void clearUsername() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get name => $_getSZ(6);
  @$pb.TagNumber(7)
  set name($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasName() => $_has(6);
  @$pb.TagNumber(7)
  void clearName() => $_clearField(7);

  @$pb.TagNumber(8)
  $core.String get type => $_getSZ(7);
  @$pb.TagNumber(8)
  set type($core.String value) => $_setString(7, value);
  @$pb.TagNumber(8)
  $core.bool hasType() => $_has(7);
  @$pb.TagNumber(8)
  void clearType() => $_clearField(8);
}

class GetSpaceRequest extends $pb.GeneratedMessage {
  factory GetSpaceRequest({
    $core.String? pathOrKref,
  }) {
    final result = create();
    if (pathOrKref != null) result.pathOrKref = pathOrKref;
    return result;
  }

  GetSpaceRequest._();

  factory GetSpaceRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetSpaceRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetSpaceRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'pathOrKref')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetSpaceRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetSpaceRequest copyWith(void Function(GetSpaceRequest) updates) =>
      super.copyWith((message) => updates(message as GetSpaceRequest))
          as GetSpaceRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetSpaceRequest create() => GetSpaceRequest._();
  @$core.override
  GetSpaceRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetSpaceRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetSpaceRequest>(create);
  static GetSpaceRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get pathOrKref => $_getSZ(0);
  @$pb.TagNumber(1)
  set pathOrKref($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasPathOrKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearPathOrKref() => $_clearField(1);
}

class DeleteSpaceRequest extends $pb.GeneratedMessage {
  factory DeleteSpaceRequest({
    $core.String? path,
    $core.bool? force,
  }) {
    final result = create();
    if (path != null) result.path = path;
    if (force != null) result.force = force;
    return result;
  }

  DeleteSpaceRequest._();

  factory DeleteSpaceRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteSpaceRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteSpaceRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'path')
    ..aOB(2, _omitFieldNames ? '' : 'force')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteSpaceRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteSpaceRequest copyWith(void Function(DeleteSpaceRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteSpaceRequest))
          as DeleteSpaceRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteSpaceRequest create() => DeleteSpaceRequest._();
  @$core.override
  DeleteSpaceRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteSpaceRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteSpaceRequest>(create);
  static DeleteSpaceRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get path => $_getSZ(0);
  @$pb.TagNumber(1)
  set path($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.bool get force => $_getBF(1);
  @$pb.TagNumber(2)
  set force($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasForce() => $_has(1);
  @$pb.TagNumber(2)
  void clearForce() => $_clearField(2);
}

class GetChildSpacesRequest extends $pb.GeneratedMessage {
  factory GetChildSpacesRequest({
    $core.String? parentPath,
    $core.bool? recursive,
    PaginationRequest? pagination,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (recursive != null) result.recursive = recursive;
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetChildSpacesRequest._();

  factory GetChildSpacesRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetChildSpacesRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetChildSpacesRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOB(2, _omitFieldNames ? '' : 'recursive')
    ..aOM<PaginationRequest>(3, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationRequest.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetChildSpacesRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetChildSpacesRequest copyWith(
          void Function(GetChildSpacesRequest) updates) =>
      super.copyWith((message) => updates(message as GetChildSpacesRequest))
          as GetChildSpacesRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetChildSpacesRequest create() => GetChildSpacesRequest._();
  @$core.override
  GetChildSpacesRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetChildSpacesRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetChildSpacesRequest>(create);
  static GetChildSpacesRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.bool get recursive => $_getBF(1);
  @$pb.TagNumber(2)
  set recursive($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasRecursive() => $_has(1);
  @$pb.TagNumber(2)
  void clearRecursive() => $_clearField(2);

  /// Optional pagination parameters
  @$pb.TagNumber(3)
  PaginationRequest get pagination => $_getN(2);
  @$pb.TagNumber(3)
  set pagination(PaginationRequest value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasPagination() => $_has(2);
  @$pb.TagNumber(3)
  void clearPagination() => $_clearField(3);
  @$pb.TagNumber(3)
  PaginationRequest ensurePagination() => $_ensure(2);
}

class GetChildSpacesResponse extends $pb.GeneratedMessage {
  factory GetChildSpacesResponse({
    $core.Iterable<SpaceResponse>? spaces,
    PaginationResponse? pagination,
  }) {
    final result = create();
    if (spaces != null) result.spaces.addAll(spaces);
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetChildSpacesResponse._();

  factory GetChildSpacesResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetChildSpacesResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetChildSpacesResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<SpaceResponse>(1, _omitFieldNames ? '' : 'spaces',
        subBuilder: SpaceResponse.create)
    ..aOM<PaginationResponse>(2, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetChildSpacesResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetChildSpacesResponse copyWith(
          void Function(GetChildSpacesResponse) updates) =>
      super.copyWith((message) => updates(message as GetChildSpacesResponse))
          as GetChildSpacesResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetChildSpacesResponse create() => GetChildSpacesResponse._();
  @$core.override
  GetChildSpacesResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetChildSpacesResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetChildSpacesResponse>(create);
  static GetChildSpacesResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<SpaceResponse> get spaces => $_getList(0);

  /// Pagination info for the response
  @$pb.TagNumber(2)
  PaginationResponse get pagination => $_getN(1);
  @$pb.TagNumber(2)
  set pagination(PaginationResponse value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasPagination() => $_has(1);
  @$pb.TagNumber(2)
  void clearPagination() => $_clearField(2);
  @$pb.TagNumber(2)
  PaginationResponse ensurePagination() => $_ensure(1);
}

class CreateItemRequest extends $pb.GeneratedMessage {
  factory CreateItemRequest({
    $core.String? parentPath,
    $core.String? itemName,
    $core.String? kind,
    $core.bool? existsError,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (itemName != null) result.itemName = itemName;
    if (kind != null) result.kind = kind;
    if (existsError != null) result.existsError = existsError;
    return result;
  }

  CreateItemRequest._();

  factory CreateItemRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateItemRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateItemRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOS(2, _omitFieldNames ? '' : 'itemName')
    ..aOS(3, _omitFieldNames ? '' : 'kind')
    ..aOB(4, _omitFieldNames ? '' : 'existsError')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateItemRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateItemRequest copyWith(void Function(CreateItemRequest) updates) =>
      super.copyWith((message) => updates(message as CreateItemRequest))
          as CreateItemRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateItemRequest create() => CreateItemRequest._();
  @$core.override
  CreateItemRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateItemRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateItemRequest>(create);
  static CreateItemRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get itemName => $_getSZ(1);
  @$pb.TagNumber(2)
  set itemName($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasItemName() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get kind => $_getSZ(2);
  @$pb.TagNumber(3)
  set kind($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasKind() => $_has(2);
  @$pb.TagNumber(3)
  void clearKind() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.bool get existsError => $_getBF(3);
  @$pb.TagNumber(4)
  set existsError($core.bool value) => $_setBool(3, value);
  @$pb.TagNumber(4)
  $core.bool hasExistsError() => $_has(3);
  @$pb.TagNumber(4)
  void clearExistsError() => $_clearField(4);
}

class GetItemRequest extends $pb.GeneratedMessage {
  factory GetItemRequest({
    $core.String? parentPath,
    $core.String? itemName,
    $core.String? kind,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (itemName != null) result.itemName = itemName;
    if (kind != null) result.kind = kind;
    return result;
  }

  GetItemRequest._();

  factory GetItemRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetItemRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetItemRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOS(2, _omitFieldNames ? '' : 'itemName')
    ..aOS(3, _omitFieldNames ? '' : 'kind')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemRequest copyWith(void Function(GetItemRequest) updates) =>
      super.copyWith((message) => updates(message as GetItemRequest))
          as GetItemRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetItemRequest create() => GetItemRequest._();
  @$core.override
  GetItemRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetItemRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetItemRequest>(create);
  static GetItemRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get itemName => $_getSZ(1);
  @$pb.TagNumber(2)
  set itemName($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasItemName() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get kind => $_getSZ(2);
  @$pb.TagNumber(3)
  set kind($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasKind() => $_has(2);
  @$pb.TagNumber(3)
  void clearKind() => $_clearField(3);
}

class ItemResponse extends $pb.GeneratedMessage {
  factory ItemResponse({
    Kref? kref,
    $core.String? name,
    $core.String? itemName,
    $core.String? kind,
    $core.String? createdAt,
    $core.String? modifiedAt,
    $core.String? author,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.bool? deprecated,
    $core.String? username,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (name != null) result.name = name;
    if (itemName != null) result.itemName = itemName;
    if (kind != null) result.kind = kind;
    if (createdAt != null) result.createdAt = createdAt;
    if (modifiedAt != null) result.modifiedAt = modifiedAt;
    if (author != null) result.author = author;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (deprecated != null) result.deprecated = deprecated;
    if (username != null) result.username = username;
    return result;
  }

  ItemResponse._();

  factory ItemResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ItemResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ItemResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'name')
    ..aOS(3, _omitFieldNames ? '' : 'itemName')
    ..aOS(4, _omitFieldNames ? '' : 'kind')
    ..aOS(5, _omitFieldNames ? '' : 'createdAt')
    ..aOS(6, _omitFieldNames ? '' : 'modifiedAt')
    ..aOS(7, _omitFieldNames ? '' : 'author')
    ..m<$core.String, $core.String>(8, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'ItemResponse.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOB(9, _omitFieldNames ? '' : 'deprecated')
    ..aOS(10, _omitFieldNames ? '' : 'username')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ItemResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ItemResponse copyWith(void Function(ItemResponse) updates) =>
      super.copyWith((message) => updates(message as ItemResponse))
          as ItemResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ItemResponse create() => ItemResponse._();
  @$core.override
  ItemResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ItemResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ItemResponse>(create);
  static ItemResponse? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get name => $_getSZ(1);
  @$pb.TagNumber(2)
  set name($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasName() => $_has(1);
  @$pb.TagNumber(2)
  void clearName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get itemName => $_getSZ(2);
  @$pb.TagNumber(3)
  set itemName($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasItemName() => $_has(2);
  @$pb.TagNumber(3)
  void clearItemName() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.String get kind => $_getSZ(3);
  @$pb.TagNumber(4)
  set kind($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasKind() => $_has(3);
  @$pb.TagNumber(4)
  void clearKind() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.String get createdAt => $_getSZ(4);
  @$pb.TagNumber(5)
  set createdAt($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasCreatedAt() => $_has(4);
  @$pb.TagNumber(5)
  void clearCreatedAt() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.String get modifiedAt => $_getSZ(5);
  @$pb.TagNumber(6)
  set modifiedAt($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasModifiedAt() => $_has(5);
  @$pb.TagNumber(6)
  void clearModifiedAt() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get author => $_getSZ(6);
  @$pb.TagNumber(7)
  set author($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasAuthor() => $_has(6);
  @$pb.TagNumber(7)
  void clearAuthor() => $_clearField(7);

  @$pb.TagNumber(8)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(7);

  @$pb.TagNumber(9)
  $core.bool get deprecated => $_getBF(8);
  @$pb.TagNumber(9)
  set deprecated($core.bool value) => $_setBool(8, value);
  @$pb.TagNumber(9)
  $core.bool hasDeprecated() => $_has(8);
  @$pb.TagNumber(9)
  void clearDeprecated() => $_clearField(9);

  @$pb.TagNumber(10)
  $core.String get username => $_getSZ(9);
  @$pb.TagNumber(10)
  set username($core.String value) => $_setString(9, value);
  @$pb.TagNumber(10)
  $core.bool hasUsername() => $_has(9);
  @$pb.TagNumber(10)
  void clearUsername() => $_clearField(10);
}

class DeleteItemRequest extends $pb.GeneratedMessage {
  factory DeleteItemRequest({
    Kref? kref,
    $core.bool? force,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (force != null) result.force = force;
    return result;
  }

  DeleteItemRequest._();

  factory DeleteItemRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteItemRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteItemRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOB(2, _omitFieldNames ? '' : 'force')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteItemRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteItemRequest copyWith(void Function(DeleteItemRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteItemRequest))
          as DeleteItemRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteItemRequest create() => DeleteItemRequest._();
  @$core.override
  DeleteItemRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteItemRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteItemRequest>(create);
  static DeleteItemRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get force => $_getBF(1);
  @$pb.TagNumber(2)
  set force($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasForce() => $_has(1);
  @$pb.TagNumber(2)
  void clearForce() => $_clearField(2);
}

class GetItemsRequest extends $pb.GeneratedMessage {
  factory GetItemsRequest({
    $core.String? parentPath,
    $core.String? itemNameFilter,
    $core.String? kindFilter,
    PaginationRequest? pagination,
    $core.bool? includeDeprecated,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (itemNameFilter != null) result.itemNameFilter = itemNameFilter;
    if (kindFilter != null) result.kindFilter = kindFilter;
    if (pagination != null) result.pagination = pagination;
    if (includeDeprecated != null) result.includeDeprecated = includeDeprecated;
    return result;
  }

  GetItemsRequest._();

  factory GetItemsRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetItemsRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetItemsRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOS(2, _omitFieldNames ? '' : 'itemNameFilter')
    ..aOS(3, _omitFieldNames ? '' : 'kindFilter')
    ..aOM<PaginationRequest>(4, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationRequest.create)
    ..aOB(5, _omitFieldNames ? '' : 'includeDeprecated')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemsRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemsRequest copyWith(void Function(GetItemsRequest) updates) =>
      super.copyWith((message) => updates(message as GetItemsRequest))
          as GetItemsRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetItemsRequest create() => GetItemsRequest._();
  @$core.override
  GetItemsRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetItemsRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetItemsRequest>(create);
  static GetItemsRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get itemNameFilter => $_getSZ(1);
  @$pb.TagNumber(2)
  set itemNameFilter($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasItemNameFilter() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemNameFilter() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get kindFilter => $_getSZ(2);
  @$pb.TagNumber(3)
  set kindFilter($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasKindFilter() => $_has(2);
  @$pb.TagNumber(3)
  void clearKindFilter() => $_clearField(3);

  /// Optional pagination parameters
  @$pb.TagNumber(4)
  PaginationRequest get pagination => $_getN(3);
  @$pb.TagNumber(4)
  set pagination(PaginationRequest value) => $_setField(4, value);
  @$pb.TagNumber(4)
  $core.bool hasPagination() => $_has(3);
  @$pb.TagNumber(4)
  void clearPagination() => $_clearField(4);
  @$pb.TagNumber(4)
  PaginationRequest ensurePagination() => $_ensure(3);

  @$pb.TagNumber(5)
  $core.bool get includeDeprecated => $_getBF(4);
  @$pb.TagNumber(5)
  set includeDeprecated($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasIncludeDeprecated() => $_has(4);
  @$pb.TagNumber(5)
  void clearIncludeDeprecated() => $_clearField(5);
}

class GetItemsResponse extends $pb.GeneratedMessage {
  factory GetItemsResponse({
    $core.Iterable<ItemResponse>? items,
    PaginationResponse? pagination,
  }) {
    final result = create();
    if (items != null) result.items.addAll(items);
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetItemsResponse._();

  factory GetItemsResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetItemsResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetItemsResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<ItemResponse>(1, _omitFieldNames ? '' : 'items',
        subBuilder: ItemResponse.create)
    ..aOM<PaginationResponse>(2, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemsResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetItemsResponse copyWith(void Function(GetItemsResponse) updates) =>
      super.copyWith((message) => updates(message as GetItemsResponse))
          as GetItemsResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetItemsResponse create() => GetItemsResponse._();
  @$core.override
  GetItemsResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetItemsResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetItemsResponse>(create);
  static GetItemsResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<ItemResponse> get items => $_getList(0);

  /// Pagination info for the response
  @$pb.TagNumber(2)
  PaginationResponse get pagination => $_getN(1);
  @$pb.TagNumber(2)
  set pagination(PaginationResponse value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasPagination() => $_has(1);
  @$pb.TagNumber(2)
  void clearPagination() => $_clearField(2);
  @$pb.TagNumber(2)
  PaginationResponse ensurePagination() => $_ensure(1);
}

class ItemSearchRequest extends $pb.GeneratedMessage {
  factory ItemSearchRequest({
    $core.String? contextFilter,
    $core.String? itemNameFilter,
    $core.String? kindFilter,
    PaginationRequest? pagination,
    $core.bool? includeDeprecated,
  }) {
    final result = create();
    if (contextFilter != null) result.contextFilter = contextFilter;
    if (itemNameFilter != null) result.itemNameFilter = itemNameFilter;
    if (kindFilter != null) result.kindFilter = kindFilter;
    if (pagination != null) result.pagination = pagination;
    if (includeDeprecated != null) result.includeDeprecated = includeDeprecated;
    return result;
  }

  ItemSearchRequest._();

  factory ItemSearchRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ItemSearchRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ItemSearchRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'contextFilter')
    ..aOS(2, _omitFieldNames ? '' : 'itemNameFilter')
    ..aOS(3, _omitFieldNames ? '' : 'kindFilter')
    ..aOM<PaginationRequest>(4, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationRequest.create)
    ..aOB(5, _omitFieldNames ? '' : 'includeDeprecated')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ItemSearchRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ItemSearchRequest copyWith(void Function(ItemSearchRequest) updates) =>
      super.copyWith((message) => updates(message as ItemSearchRequest))
          as ItemSearchRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ItemSearchRequest create() => ItemSearchRequest._();
  @$core.override
  ItemSearchRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ItemSearchRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ItemSearchRequest>(create);
  static ItemSearchRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get contextFilter => $_getSZ(0);
  @$pb.TagNumber(1)
  set contextFilter($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasContextFilter() => $_has(0);
  @$pb.TagNumber(1)
  void clearContextFilter() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get itemNameFilter => $_getSZ(1);
  @$pb.TagNumber(2)
  set itemNameFilter($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasItemNameFilter() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemNameFilter() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get kindFilter => $_getSZ(2);
  @$pb.TagNumber(3)
  set kindFilter($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasKindFilter() => $_has(2);
  @$pb.TagNumber(3)
  void clearKindFilter() => $_clearField(3);

  /// Optional pagination parameters
  @$pb.TagNumber(4)
  PaginationRequest get pagination => $_getN(3);
  @$pb.TagNumber(4)
  set pagination(PaginationRequest value) => $_setField(4, value);
  @$pb.TagNumber(4)
  $core.bool hasPagination() => $_has(3);
  @$pb.TagNumber(4)
  void clearPagination() => $_clearField(4);
  @$pb.TagNumber(4)
  PaginationRequest ensurePagination() => $_ensure(3);

  @$pb.TagNumber(5)
  $core.bool get includeDeprecated => $_getBF(4);
  @$pb.TagNumber(5)
  set includeDeprecated($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasIncludeDeprecated() => $_has(4);
  @$pb.TagNumber(5)
  void clearIncludeDeprecated() => $_clearField(5);
}

class CreateRevisionRequest extends $pb.GeneratedMessage {
  factory CreateRevisionRequest({
    Kref? itemKref,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.int? number,
    $core.bool? existsError,
  }) {
    final result = create();
    if (itemKref != null) result.itemKref = itemKref;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (number != null) result.number = number;
    if (existsError != null) result.existsError = existsError;
    return result;
  }

  CreateRevisionRequest._();

  factory CreateRevisionRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateRevisionRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateRevisionRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..m<$core.String, $core.String>(2, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'CreateRevisionRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aI(3, _omitFieldNames ? '' : 'number')
    ..aOB(4, _omitFieldNames ? '' : 'existsError')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateRevisionRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateRevisionRequest copyWith(
          void Function(CreateRevisionRequest) updates) =>
      super.copyWith((message) => updates(message as CreateRevisionRequest))
          as CreateRevisionRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateRevisionRequest create() => CreateRevisionRequest._();
  @$core.override
  CreateRevisionRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateRevisionRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateRevisionRequest>(create);
  static CreateRevisionRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get itemKref => $_getN(0);
  @$pb.TagNumber(1)
  set itemKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasItemKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearItemKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureItemKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(1);

  @$pb.TagNumber(3)
  $core.int get number => $_getIZ(2);
  @$pb.TagNumber(3)
  set number($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasNumber() => $_has(2);
  @$pb.TagNumber(3)
  void clearNumber() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.bool get existsError => $_getBF(3);
  @$pb.TagNumber(4)
  set existsError($core.bool value) => $_setBool(3, value);
  @$pb.TagNumber(4)
  $core.bool hasExistsError() => $_has(3);
  @$pb.TagNumber(4)
  void clearExistsError() => $_clearField(4);
}

class RevisionResponse extends $pb.GeneratedMessage {
  factory RevisionResponse({
    Kref? kref,
    Kref? itemKref,
    $core.int? number,
    $core.Iterable<$core.String>? tags,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.String? createdAt,
    $core.String? modifiedAt,
    $core.String? author,
    $core.bool? deprecated,
    $core.bool? published,
    $core.bool? latest,
    $core.String? username,
    $core.String? defaultArtifact,
    $core.String? name,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (itemKref != null) result.itemKref = itemKref;
    if (number != null) result.number = number;
    if (tags != null) result.tags.addAll(tags);
    if (metadata != null) result.metadata.addEntries(metadata);
    if (createdAt != null) result.createdAt = createdAt;
    if (modifiedAt != null) result.modifiedAt = modifiedAt;
    if (author != null) result.author = author;
    if (deprecated != null) result.deprecated = deprecated;
    if (published != null) result.published = published;
    if (latest != null) result.latest = latest;
    if (username != null) result.username = username;
    if (defaultArtifact != null) result.defaultArtifact = defaultArtifact;
    if (name != null) result.name = name;
    return result;
  }

  RevisionResponse._();

  factory RevisionResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory RevisionResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'RevisionResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..aI(3, _omitFieldNames ? '' : 'number')
    ..pPS(4, _omitFieldNames ? '' : 'tags')
    ..m<$core.String, $core.String>(5, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'RevisionResponse.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOS(6, _omitFieldNames ? '' : 'createdAt')
    ..aOS(7, _omitFieldNames ? '' : 'modifiedAt')
    ..aOS(8, _omitFieldNames ? '' : 'author')
    ..aOB(9, _omitFieldNames ? '' : 'deprecated')
    ..aOB(10, _omitFieldNames ? '' : 'published')
    ..aOB(11, _omitFieldNames ? '' : 'latest')
    ..aOS(12, _omitFieldNames ? '' : 'username')
    ..aOS(13, _omitFieldNames ? '' : 'defaultArtifact')
    ..aOS(14, _omitFieldNames ? '' : 'name')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RevisionResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RevisionResponse copyWith(void Function(RevisionResponse) updates) =>
      super.copyWith((message) => updates(message as RevisionResponse))
          as RevisionResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static RevisionResponse create() => RevisionResponse._();
  @$core.override
  RevisionResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static RevisionResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<RevisionResponse>(create);
  static RevisionResponse? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get itemKref => $_getN(1);
  @$pb.TagNumber(2)
  set itemKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasItemKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureItemKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.int get number => $_getIZ(2);
  @$pb.TagNumber(3)
  set number($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasNumber() => $_has(2);
  @$pb.TagNumber(3)
  void clearNumber() => $_clearField(3);

  @$pb.TagNumber(4)
  $pb.PbList<$core.String> get tags => $_getList(3);

  @$pb.TagNumber(5)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(4);

  @$pb.TagNumber(6)
  $core.String get createdAt => $_getSZ(5);
  @$pb.TagNumber(6)
  set createdAt($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasCreatedAt() => $_has(5);
  @$pb.TagNumber(6)
  void clearCreatedAt() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get modifiedAt => $_getSZ(6);
  @$pb.TagNumber(7)
  set modifiedAt($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasModifiedAt() => $_has(6);
  @$pb.TagNumber(7)
  void clearModifiedAt() => $_clearField(7);

  @$pb.TagNumber(8)
  $core.String get author => $_getSZ(7);
  @$pb.TagNumber(8)
  set author($core.String value) => $_setString(7, value);
  @$pb.TagNumber(8)
  $core.bool hasAuthor() => $_has(7);
  @$pb.TagNumber(8)
  void clearAuthor() => $_clearField(8);

  @$pb.TagNumber(9)
  $core.bool get deprecated => $_getBF(8);
  @$pb.TagNumber(9)
  set deprecated($core.bool value) => $_setBool(8, value);
  @$pb.TagNumber(9)
  $core.bool hasDeprecated() => $_has(8);
  @$pb.TagNumber(9)
  void clearDeprecated() => $_clearField(9);

  @$pb.TagNumber(10)
  $core.bool get published => $_getBF(9);
  @$pb.TagNumber(10)
  set published($core.bool value) => $_setBool(9, value);
  @$pb.TagNumber(10)
  $core.bool hasPublished() => $_has(9);
  @$pb.TagNumber(10)
  void clearPublished() => $_clearField(10);

  @$pb.TagNumber(11)
  $core.bool get latest => $_getBF(10);
  @$pb.TagNumber(11)
  set latest($core.bool value) => $_setBool(10, value);
  @$pb.TagNumber(11)
  $core.bool hasLatest() => $_has(10);
  @$pb.TagNumber(11)
  void clearLatest() => $_clearField(11);

  @$pb.TagNumber(12)
  $core.String get username => $_getSZ(11);
  @$pb.TagNumber(12)
  set username($core.String value) => $_setString(11, value);
  @$pb.TagNumber(12)
  $core.bool hasUsername() => $_has(11);
  @$pb.TagNumber(12)
  void clearUsername() => $_clearField(12);

  @$pb.TagNumber(13)
  $core.String get defaultArtifact => $_getSZ(12);
  @$pb.TagNumber(13)
  set defaultArtifact($core.String value) => $_setString(12, value);
  @$pb.TagNumber(13)
  $core.bool hasDefaultArtifact() => $_has(12);
  @$pb.TagNumber(13)
  void clearDefaultArtifact() => $_clearField(13);

  @$pb.TagNumber(14)
  $core.String get name => $_getSZ(13);
  @$pb.TagNumber(14)
  set name($core.String value) => $_setString(13, value);
  @$pb.TagNumber(14)
  $core.bool hasName() => $_has(13);
  @$pb.TagNumber(14)
  void clearName() => $_clearField(14);
}

class DeleteRevisionRequest extends $pb.GeneratedMessage {
  factory DeleteRevisionRequest({
    Kref? kref,
    $core.bool? force,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (force != null) result.force = force;
    return result;
  }

  DeleteRevisionRequest._();

  factory DeleteRevisionRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteRevisionRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteRevisionRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOB(2, _omitFieldNames ? '' : 'force')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteRevisionRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteRevisionRequest copyWith(
          void Function(DeleteRevisionRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteRevisionRequest))
          as DeleteRevisionRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteRevisionRequest create() => DeleteRevisionRequest._();
  @$core.override
  DeleteRevisionRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteRevisionRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteRevisionRequest>(create);
  static DeleteRevisionRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get force => $_getBF(1);
  @$pb.TagNumber(2)
  set force($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasForce() => $_has(1);
  @$pb.TagNumber(2)
  void clearForce() => $_clearField(2);
}

class GetRevisionsRequest extends $pb.GeneratedMessage {
  factory GetRevisionsRequest({
    Kref? itemKref,
    PaginationRequest? pagination,
  }) {
    final result = create();
    if (itemKref != null) result.itemKref = itemKref;
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetRevisionsRequest._();

  factory GetRevisionsRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetRevisionsRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetRevisionsRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..aOM<PaginationRequest>(2, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationRequest.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetRevisionsRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetRevisionsRequest copyWith(void Function(GetRevisionsRequest) updates) =>
      super.copyWith((message) => updates(message as GetRevisionsRequest))
          as GetRevisionsRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetRevisionsRequest create() => GetRevisionsRequest._();
  @$core.override
  GetRevisionsRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetRevisionsRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetRevisionsRequest>(create);
  static GetRevisionsRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get itemKref => $_getN(0);
  @$pb.TagNumber(1)
  set itemKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasItemKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearItemKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureItemKref() => $_ensure(0);

  /// Optional pagination parameters
  @$pb.TagNumber(2)
  PaginationRequest get pagination => $_getN(1);
  @$pb.TagNumber(2)
  set pagination(PaginationRequest value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasPagination() => $_has(1);
  @$pb.TagNumber(2)
  void clearPagination() => $_clearField(2);
  @$pb.TagNumber(2)
  PaginationRequest ensurePagination() => $_ensure(1);
}

class GetRevisionsResponse extends $pb.GeneratedMessage {
  factory GetRevisionsResponse({
    $core.Iterable<RevisionResponse>? revisions,
    PaginationResponse? pagination,
  }) {
    final result = create();
    if (revisions != null) result.revisions.addAll(revisions);
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetRevisionsResponse._();

  factory GetRevisionsResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetRevisionsResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetRevisionsResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<RevisionResponse>(1, _omitFieldNames ? '' : 'revisions',
        subBuilder: RevisionResponse.create)
    ..aOM<PaginationResponse>(2, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetRevisionsResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetRevisionsResponse copyWith(void Function(GetRevisionsResponse) updates) =>
      super.copyWith((message) => updates(message as GetRevisionsResponse))
          as GetRevisionsResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetRevisionsResponse create() => GetRevisionsResponse._();
  @$core.override
  GetRevisionsResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetRevisionsResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetRevisionsResponse>(create);
  static GetRevisionsResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<RevisionResponse> get revisions => $_getList(0);

  /// Pagination info for the response
  @$pb.TagNumber(2)
  PaginationResponse get pagination => $_getN(1);
  @$pb.TagNumber(2)
  set pagination(PaginationResponse value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasPagination() => $_has(1);
  @$pb.TagNumber(2)
  void clearPagination() => $_clearField(2);
  @$pb.TagNumber(2)
  PaginationResponse ensurePagination() => $_ensure(1);
}

class CreateArtifactRequest extends $pb.GeneratedMessage {
  factory CreateArtifactRequest({
    Kref? revisionKref,
    $core.String? name,
    $core.String? location,
    $core.bool? existsError,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (name != null) result.name = name;
    if (location != null) result.location = location;
    if (existsError != null) result.existsError = existsError;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  CreateArtifactRequest._();

  factory CreateArtifactRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateArtifactRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateArtifactRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'name')
    ..aOS(3, _omitFieldNames ? '' : 'location')
    ..aOB(4, _omitFieldNames ? '' : 'existsError')
    ..m<$core.String, $core.String>(5, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'CreateArtifactRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateArtifactRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateArtifactRequest copyWith(
          void Function(CreateArtifactRequest) updates) =>
      super.copyWith((message) => updates(message as CreateArtifactRequest))
          as CreateArtifactRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateArtifactRequest create() => CreateArtifactRequest._();
  @$core.override
  CreateArtifactRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateArtifactRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateArtifactRequest>(create);
  static CreateArtifactRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get name => $_getSZ(1);
  @$pb.TagNumber(2)
  set name($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasName() => $_has(1);
  @$pb.TagNumber(2)
  void clearName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get location => $_getSZ(2);
  @$pb.TagNumber(3)
  set location($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasLocation() => $_has(2);
  @$pb.TagNumber(3)
  void clearLocation() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.bool get existsError => $_getBF(3);
  @$pb.TagNumber(4)
  set existsError($core.bool value) => $_setBool(3, value);
  @$pb.TagNumber(4)
  $core.bool hasExistsError() => $_has(3);
  @$pb.TagNumber(4)
  void clearExistsError() => $_clearField(4);

  @$pb.TagNumber(5)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(4);
}

class ArtifactResponse extends $pb.GeneratedMessage {
  factory ArtifactResponse({
    Kref? kref,
    $core.String? location,
    Kref? revisionKref,
    Kref? itemKref,
    $core.String? createdAt,
    $core.String? modifiedAt,
    $core.String? author,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.bool? deprecated,
    $core.String? username,
    $core.String? name,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (location != null) result.location = location;
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (itemKref != null) result.itemKref = itemKref;
    if (createdAt != null) result.createdAt = createdAt;
    if (modifiedAt != null) result.modifiedAt = modifiedAt;
    if (author != null) result.author = author;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (deprecated != null) result.deprecated = deprecated;
    if (username != null) result.username = username;
    if (name != null) result.name = name;
    return result;
  }

  ArtifactResponse._();

  factory ArtifactResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ArtifactResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ArtifactResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'location')
    ..aOM<Kref>(3, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOM<Kref>(4, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..aOS(5, _omitFieldNames ? '' : 'createdAt')
    ..aOS(6, _omitFieldNames ? '' : 'modifiedAt')
    ..aOS(7, _omitFieldNames ? '' : 'author')
    ..m<$core.String, $core.String>(8, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'ArtifactResponse.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOB(9, _omitFieldNames ? '' : 'deprecated')
    ..aOS(10, _omitFieldNames ? '' : 'username')
    ..aOS(11, _omitFieldNames ? '' : 'name')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ArtifactResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ArtifactResponse copyWith(void Function(ArtifactResponse) updates) =>
      super.copyWith((message) => updates(message as ArtifactResponse))
          as ArtifactResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ArtifactResponse create() => ArtifactResponse._();
  @$core.override
  ArtifactResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ArtifactResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ArtifactResponse>(create);
  static ArtifactResponse? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get location => $_getSZ(1);
  @$pb.TagNumber(2)
  set location($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasLocation() => $_has(1);
  @$pb.TagNumber(2)
  void clearLocation() => $_clearField(2);

  @$pb.TagNumber(3)
  Kref get revisionKref => $_getN(2);
  @$pb.TagNumber(3)
  set revisionKref(Kref value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasRevisionKref() => $_has(2);
  @$pb.TagNumber(3)
  void clearRevisionKref() => $_clearField(3);
  @$pb.TagNumber(3)
  Kref ensureRevisionKref() => $_ensure(2);

  @$pb.TagNumber(4)
  Kref get itemKref => $_getN(3);
  @$pb.TagNumber(4)
  set itemKref(Kref value) => $_setField(4, value);
  @$pb.TagNumber(4)
  $core.bool hasItemKref() => $_has(3);
  @$pb.TagNumber(4)
  void clearItemKref() => $_clearField(4);
  @$pb.TagNumber(4)
  Kref ensureItemKref() => $_ensure(3);

  @$pb.TagNumber(5)
  $core.String get createdAt => $_getSZ(4);
  @$pb.TagNumber(5)
  set createdAt($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasCreatedAt() => $_has(4);
  @$pb.TagNumber(5)
  void clearCreatedAt() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.String get modifiedAt => $_getSZ(5);
  @$pb.TagNumber(6)
  set modifiedAt($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasModifiedAt() => $_has(5);
  @$pb.TagNumber(6)
  void clearModifiedAt() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get author => $_getSZ(6);
  @$pb.TagNumber(7)
  set author($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasAuthor() => $_has(6);
  @$pb.TagNumber(7)
  void clearAuthor() => $_clearField(7);

  @$pb.TagNumber(8)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(7);

  @$pb.TagNumber(9)
  $core.bool get deprecated => $_getBF(8);
  @$pb.TagNumber(9)
  set deprecated($core.bool value) => $_setBool(8, value);
  @$pb.TagNumber(9)
  $core.bool hasDeprecated() => $_has(8);
  @$pb.TagNumber(9)
  void clearDeprecated() => $_clearField(9);

  @$pb.TagNumber(10)
  $core.String get username => $_getSZ(9);
  @$pb.TagNumber(10)
  set username($core.String value) => $_setString(9, value);
  @$pb.TagNumber(10)
  $core.bool hasUsername() => $_has(9);
  @$pb.TagNumber(10)
  void clearUsername() => $_clearField(10);

  @$pb.TagNumber(11)
  $core.String get name => $_getSZ(10);
  @$pb.TagNumber(11)
  set name($core.String value) => $_setString(10, value);
  @$pb.TagNumber(11)
  $core.bool hasName() => $_has(10);
  @$pb.TagNumber(11)
  void clearName() => $_clearField(11);
}

class GetArtifactRequest extends $pb.GeneratedMessage {
  factory GetArtifactRequest({
    Kref? revisionKref,
    $core.String? name,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (name != null) result.name = name;
    return result;
  }

  GetArtifactRequest._();

  factory GetArtifactRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetArtifactRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetArtifactRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'name')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactRequest copyWith(void Function(GetArtifactRequest) updates) =>
      super.copyWith((message) => updates(message as GetArtifactRequest))
          as GetArtifactRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetArtifactRequest create() => GetArtifactRequest._();
  @$core.override
  GetArtifactRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetArtifactRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetArtifactRequest>(create);
  static GetArtifactRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get name => $_getSZ(1);
  @$pb.TagNumber(2)
  set name($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasName() => $_has(1);
  @$pb.TagNumber(2)
  void clearName() => $_clearField(2);
}

class GetArtifactsRequest extends $pb.GeneratedMessage {
  factory GetArtifactsRequest({
    Kref? revisionKref,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    return result;
  }

  GetArtifactsRequest._();

  factory GetArtifactsRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetArtifactsRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetArtifactsRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsRequest copyWith(void Function(GetArtifactsRequest) updates) =>
      super.copyWith((message) => updates(message as GetArtifactsRequest))
          as GetArtifactsRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetArtifactsRequest create() => GetArtifactsRequest._();
  @$core.override
  GetArtifactsRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetArtifactsRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetArtifactsRequest>(create);
  static GetArtifactsRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);
}

class GetArtifactsResponse extends $pb.GeneratedMessage {
  factory GetArtifactsResponse({
    $core.Iterable<ArtifactResponse>? artifacts,
  }) {
    final result = create();
    if (artifacts != null) result.artifacts.addAll(artifacts);
    return result;
  }

  GetArtifactsResponse._();

  factory GetArtifactsResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetArtifactsResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetArtifactsResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<ArtifactResponse>(1, _omitFieldNames ? '' : 'artifacts',
        subBuilder: ArtifactResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsResponse copyWith(void Function(GetArtifactsResponse) updates) =>
      super.copyWith((message) => updates(message as GetArtifactsResponse))
          as GetArtifactsResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetArtifactsResponse create() => GetArtifactsResponse._();
  @$core.override
  GetArtifactsResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetArtifactsResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetArtifactsResponse>(create);
  static GetArtifactsResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<ArtifactResponse> get artifacts => $_getList(0);
}

class DeleteArtifactRequest extends $pb.GeneratedMessage {
  factory DeleteArtifactRequest({
    Kref? kref,
    $core.bool? force,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (force != null) result.force = force;
    return result;
  }

  DeleteArtifactRequest._();

  factory DeleteArtifactRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteArtifactRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteArtifactRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOB(2, _omitFieldNames ? '' : 'force')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteArtifactRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteArtifactRequest copyWith(
          void Function(DeleteArtifactRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteArtifactRequest))
          as DeleteArtifactRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteArtifactRequest create() => DeleteArtifactRequest._();
  @$core.override
  DeleteArtifactRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteArtifactRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteArtifactRequest>(create);
  static DeleteArtifactRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get force => $_getBF(1);
  @$pb.TagNumber(2)
  set force($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasForce() => $_has(1);
  @$pb.TagNumber(2)
  void clearForce() => $_clearField(2);
}

class GetArtifactsByLocationRequest extends $pb.GeneratedMessage {
  factory GetArtifactsByLocationRequest({
    $core.String? location,
  }) {
    final result = create();
    if (location != null) result.location = location;
    return result;
  }

  GetArtifactsByLocationRequest._();

  factory GetArtifactsByLocationRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetArtifactsByLocationRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetArtifactsByLocationRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'location')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsByLocationRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsByLocationRequest copyWith(
          void Function(GetArtifactsByLocationRequest) updates) =>
      super.copyWith(
              (message) => updates(message as GetArtifactsByLocationRequest))
          as GetArtifactsByLocationRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetArtifactsByLocationRequest create() =>
      GetArtifactsByLocationRequest._();
  @$core.override
  GetArtifactsByLocationRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetArtifactsByLocationRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetArtifactsByLocationRequest>(create);
  static GetArtifactsByLocationRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get location => $_getSZ(0);
  @$pb.TagNumber(1)
  set location($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasLocation() => $_has(0);
  @$pb.TagNumber(1)
  void clearLocation() => $_clearField(1);
}

class GetArtifactsByLocationResponse extends $pb.GeneratedMessage {
  factory GetArtifactsByLocationResponse({
    $core.Iterable<ArtifactResponse>? artifacts,
  }) {
    final result = create();
    if (artifacts != null) result.artifacts.addAll(artifacts);
    return result;
  }

  GetArtifactsByLocationResponse._();

  factory GetArtifactsByLocationResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetArtifactsByLocationResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetArtifactsByLocationResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<ArtifactResponse>(1, _omitFieldNames ? '' : 'artifacts',
        subBuilder: ArtifactResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsByLocationResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetArtifactsByLocationResponse copyWith(
          void Function(GetArtifactsByLocationResponse) updates) =>
      super.copyWith(
              (message) => updates(message as GetArtifactsByLocationResponse))
          as GetArtifactsByLocationResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetArtifactsByLocationResponse create() =>
      GetArtifactsByLocationResponse._();
  @$core.override
  GetArtifactsByLocationResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetArtifactsByLocationResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetArtifactsByLocationResponse>(create);
  static GetArtifactsByLocationResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<ArtifactResponse> get artifacts => $_getList(0);
}

class TagRevisionRequest extends $pb.GeneratedMessage {
  factory TagRevisionRequest({
    Kref? kref,
    $core.String? tag,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    return result;
  }

  TagRevisionRequest._();

  factory TagRevisionRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory TagRevisionRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'TagRevisionRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TagRevisionRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TagRevisionRequest copyWith(void Function(TagRevisionRequest) updates) =>
      super.copyWith((message) => updates(message as TagRevisionRequest))
          as TagRevisionRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static TagRevisionRequest create() => TagRevisionRequest._();
  @$core.override
  TagRevisionRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static TagRevisionRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<TagRevisionRequest>(create);
  static TagRevisionRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);
}

class UnTagRevisionRequest extends $pb.GeneratedMessage {
  factory UnTagRevisionRequest({
    Kref? kref,
    $core.String? tag,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    return result;
  }

  UnTagRevisionRequest._();

  factory UnTagRevisionRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory UnTagRevisionRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'UnTagRevisionRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UnTagRevisionRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UnTagRevisionRequest copyWith(void Function(UnTagRevisionRequest) updates) =>
      super.copyWith((message) => updates(message as UnTagRevisionRequest))
          as UnTagRevisionRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static UnTagRevisionRequest create() => UnTagRevisionRequest._();
  @$core.override
  UnTagRevisionRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static UnTagRevisionRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<UnTagRevisionRequest>(create);
  static UnTagRevisionRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);
}

class HasTagRequest extends $pb.GeneratedMessage {
  factory HasTagRequest({
    Kref? kref,
    $core.String? tag,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    return result;
  }

  HasTagRequest._();

  factory HasTagRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory HasTagRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'HasTagRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  HasTagRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  HasTagRequest copyWith(void Function(HasTagRequest) updates) =>
      super.copyWith((message) => updates(message as HasTagRequest))
          as HasTagRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static HasTagRequest create() => HasTagRequest._();
  @$core.override
  HasTagRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static HasTagRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<HasTagRequest>(create);
  static HasTagRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);
}

class HasTagResponse extends $pb.GeneratedMessage {
  factory HasTagResponse({
    $core.bool? hasTag,
  }) {
    final result = create();
    if (hasTag != null) result.hasTag = hasTag;
    return result;
  }

  HasTagResponse._();

  factory HasTagResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory HasTagResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'HasTagResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'hasTag')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  HasTagResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  HasTagResponse copyWith(void Function(HasTagResponse) updates) =>
      super.copyWith((message) => updates(message as HasTagResponse))
          as HasTagResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static HasTagResponse create() => HasTagResponse._();
  @$core.override
  HasTagResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static HasTagResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<HasTagResponse>(create);
  static HasTagResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get hasTag => $_getBF(0);
  @$pb.TagNumber(1)
  set hasTag($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasHasTag() => $_has(0);
  @$pb.TagNumber(1)
  void clearHasTag() => $_clearField(1);
}

class WasTaggedRequest extends $pb.GeneratedMessage {
  factory WasTaggedRequest({
    Kref? kref,
    $core.String? tag,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (tag != null) result.tag = tag;
    return result;
  }

  WasTaggedRequest._();

  factory WasTaggedRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory WasTaggedRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'WasTaggedRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'tag')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  WasTaggedRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  WasTaggedRequest copyWith(void Function(WasTaggedRequest) updates) =>
      super.copyWith((message) => updates(message as WasTaggedRequest))
          as WasTaggedRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static WasTaggedRequest create() => WasTaggedRequest._();
  @$core.override
  WasTaggedRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static WasTaggedRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<WasTaggedRequest>(create);
  static WasTaggedRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get tag => $_getSZ(1);
  @$pb.TagNumber(2)
  set tag($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTag() => $_has(1);
  @$pb.TagNumber(2)
  void clearTag() => $_clearField(2);
}

class WasTaggedResponse extends $pb.GeneratedMessage {
  factory WasTaggedResponse({
    $core.bool? wasTagged,
  }) {
    final result = create();
    if (wasTagged != null) result.wasTagged = wasTagged;
    return result;
  }

  WasTaggedResponse._();

  factory WasTaggedResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory WasTaggedResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'WasTaggedResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'wasTagged')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  WasTaggedResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  WasTaggedResponse copyWith(void Function(WasTaggedResponse) updates) =>
      super.copyWith((message) => updates(message as WasTaggedResponse))
          as WasTaggedResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static WasTaggedResponse create() => WasTaggedResponse._();
  @$core.override
  WasTaggedResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static WasTaggedResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<WasTaggedResponse>(create);
  static WasTaggedResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get wasTagged => $_getBF(0);
  @$pb.TagNumber(1)
  set wasTagged($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasWasTagged() => $_has(0);
  @$pb.TagNumber(1)
  void clearWasTagged() => $_clearField(1);
}

class SetDefaultArtifactRequest extends $pb.GeneratedMessage {
  factory SetDefaultArtifactRequest({
    Kref? revisionKref,
    $core.String? artifactName,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (artifactName != null) result.artifactName = artifactName;
    return result;
  }

  SetDefaultArtifactRequest._();

  factory SetDefaultArtifactRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory SetDefaultArtifactRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'SetDefaultArtifactRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'artifactName')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetDefaultArtifactRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetDefaultArtifactRequest copyWith(
          void Function(SetDefaultArtifactRequest) updates) =>
      super.copyWith((message) => updates(message as SetDefaultArtifactRequest))
          as SetDefaultArtifactRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static SetDefaultArtifactRequest create() => SetDefaultArtifactRequest._();
  @$core.override
  SetDefaultArtifactRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static SetDefaultArtifactRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<SetDefaultArtifactRequest>(create);
  static SetDefaultArtifactRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get artifactName => $_getSZ(1);
  @$pb.TagNumber(2)
  set artifactName($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasArtifactName() => $_has(1);
  @$pb.TagNumber(2)
  void clearArtifactName() => $_clearField(2);
}

class CreateEdgeRequest extends $pb.GeneratedMessage {
  factory CreateEdgeRequest({
    Kref? sourceRevisionKref,
    Kref? targetRevisionKref,
    $core.String? edgeType,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
    $core.bool? existsError,
  }) {
    final result = create();
    if (sourceRevisionKref != null)
      result.sourceRevisionKref = sourceRevisionKref;
    if (targetRevisionKref != null)
      result.targetRevisionKref = targetRevisionKref;
    if (edgeType != null) result.edgeType = edgeType;
    if (metadata != null) result.metadata.addEntries(metadata);
    if (existsError != null) result.existsError = existsError;
    return result;
  }

  CreateEdgeRequest._();

  factory CreateEdgeRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateEdgeRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateEdgeRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'sourceRevisionKref',
        subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'targetRevisionKref',
        subBuilder: Kref.create)
    ..aOS(3, _omitFieldNames ? '' : 'edgeType')
    ..m<$core.String, $core.String>(4, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'CreateEdgeRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOB(5, _omitFieldNames ? '' : 'existsError')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateEdgeRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateEdgeRequest copyWith(void Function(CreateEdgeRequest) updates) =>
      super.copyWith((message) => updates(message as CreateEdgeRequest))
          as CreateEdgeRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateEdgeRequest create() => CreateEdgeRequest._();
  @$core.override
  CreateEdgeRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateEdgeRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateEdgeRequest>(create);
  static CreateEdgeRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get sourceRevisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set sourceRevisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasSourceRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearSourceRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureSourceRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get targetRevisionKref => $_getN(1);
  @$pb.TagNumber(2)
  set targetRevisionKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasTargetRevisionKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearTargetRevisionKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureTargetRevisionKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.String get edgeType => $_getSZ(2);
  @$pb.TagNumber(3)
  set edgeType($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasEdgeType() => $_has(2);
  @$pb.TagNumber(3)
  void clearEdgeType() => $_clearField(3);

  @$pb.TagNumber(4)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(3);

  @$pb.TagNumber(5)
  $core.bool get existsError => $_getBF(4);
  @$pb.TagNumber(5)
  set existsError($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasExistsError() => $_has(4);
  @$pb.TagNumber(5)
  void clearExistsError() => $_clearField(5);
}

/// --- Metadata Update Messages ---
class UpdateMetadataRequest extends $pb.GeneratedMessage {
  factory UpdateMetadataRequest({
    Kref? kref,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  UpdateMetadataRequest._();

  factory UpdateMetadataRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory UpdateMetadataRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'UpdateMetadataRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..m<$core.String, $core.String>(2, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'UpdateMetadataRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UpdateMetadataRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UpdateMetadataRequest copyWith(
          void Function(UpdateMetadataRequest) updates) =>
      super.copyWith((message) => updates(message as UpdateMetadataRequest))
          as UpdateMetadataRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static UpdateMetadataRequest create() => UpdateMetadataRequest._();
  @$core.override
  UpdateMetadataRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static UpdateMetadataRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<UpdateMetadataRequest>(create);
  static UpdateMetadataRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(1);
}

/// Set a single metadata attribute (upsert)
class SetAttributeRequest extends $pb.GeneratedMessage {
  factory SetAttributeRequest({
    Kref? kref,
    $core.String? key,
    $core.String? value,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (key != null) result.key = key;
    if (value != null) result.value = value;
    return result;
  }

  SetAttributeRequest._();

  factory SetAttributeRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory SetAttributeRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'SetAttributeRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'key')
    ..aOS(3, _omitFieldNames ? '' : 'value')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetAttributeRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetAttributeRequest copyWith(void Function(SetAttributeRequest) updates) =>
      super.copyWith((message) => updates(message as SetAttributeRequest))
          as SetAttributeRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static SetAttributeRequest create() => SetAttributeRequest._();
  @$core.override
  SetAttributeRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static SetAttributeRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<SetAttributeRequest>(create);
  static SetAttributeRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get key => $_getSZ(1);
  @$pb.TagNumber(2)
  set key($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasKey() => $_has(1);
  @$pb.TagNumber(2)
  void clearKey() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get value => $_getSZ(2);
  @$pb.TagNumber(3)
  set value($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasValue() => $_has(2);
  @$pb.TagNumber(3)
  void clearValue() => $_clearField(3);
}

/// Get a single metadata attribute
class GetAttributeRequest extends $pb.GeneratedMessage {
  factory GetAttributeRequest({
    Kref? kref,
    $core.String? key,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (key != null) result.key = key;
    return result;
  }

  GetAttributeRequest._();

  factory GetAttributeRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetAttributeRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetAttributeRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'key')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetAttributeRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetAttributeRequest copyWith(void Function(GetAttributeRequest) updates) =>
      super.copyWith((message) => updates(message as GetAttributeRequest))
          as GetAttributeRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetAttributeRequest create() => GetAttributeRequest._();
  @$core.override
  GetAttributeRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetAttributeRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetAttributeRequest>(create);
  static GetAttributeRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get key => $_getSZ(1);
  @$pb.TagNumber(2)
  set key($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasKey() => $_has(1);
  @$pb.TagNumber(2)
  void clearKey() => $_clearField(2);
}

class GetAttributeResponse extends $pb.GeneratedMessage {
  factory GetAttributeResponse({
    $core.String? key,
    $core.String? value,
    $core.bool? exists,
  }) {
    final result = create();
    if (key != null) result.key = key;
    if (value != null) result.value = value;
    if (exists != null) result.exists = exists;
    return result;
  }

  GetAttributeResponse._();

  factory GetAttributeResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetAttributeResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetAttributeResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'key')
    ..aOS(2, _omitFieldNames ? '' : 'value')
    ..aOB(3, _omitFieldNames ? '' : 'exists')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetAttributeResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetAttributeResponse copyWith(void Function(GetAttributeResponse) updates) =>
      super.copyWith((message) => updates(message as GetAttributeResponse))
          as GetAttributeResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetAttributeResponse create() => GetAttributeResponse._();
  @$core.override
  GetAttributeResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetAttributeResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetAttributeResponse>(create);
  static GetAttributeResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get key => $_getSZ(0);
  @$pb.TagNumber(1)
  set key($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasKey() => $_has(0);
  @$pb.TagNumber(1)
  void clearKey() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get value => $_getSZ(1);
  @$pb.TagNumber(2)
  set value($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasValue() => $_has(1);
  @$pb.TagNumber(2)
  void clearValue() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.bool get exists => $_getBF(2);
  @$pb.TagNumber(3)
  set exists($core.bool value) => $_setBool(2, value);
  @$pb.TagNumber(3)
  $core.bool hasExists() => $_has(2);
  @$pb.TagNumber(3)
  void clearExists() => $_clearField(3);
}

/// Delete a single metadata attribute
class DeleteAttributeRequest extends $pb.GeneratedMessage {
  factory DeleteAttributeRequest({
    Kref? kref,
    $core.String? key,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (key != null) result.key = key;
    return result;
  }

  DeleteAttributeRequest._();

  factory DeleteAttributeRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteAttributeRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteAttributeRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'key')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteAttributeRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteAttributeRequest copyWith(
          void Function(DeleteAttributeRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteAttributeRequest))
          as DeleteAttributeRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteAttributeRequest create() => DeleteAttributeRequest._();
  @$core.override
  DeleteAttributeRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteAttributeRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteAttributeRequest>(create);
  static DeleteAttributeRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get key => $_getSZ(1);
  @$pb.TagNumber(2)
  set key($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasKey() => $_has(1);
  @$pb.TagNumber(2)
  void clearKey() => $_clearField(2);
}

/// --- Peek Next Revision Messages ---
class PeekNextRevisionRequest extends $pb.GeneratedMessage {
  factory PeekNextRevisionRequest({
    Kref? itemKref,
  }) {
    final result = create();
    if (itemKref != null) result.itemKref = itemKref;
    return result;
  }

  PeekNextRevisionRequest._();

  factory PeekNextRevisionRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory PeekNextRevisionRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'PeekNextRevisionRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PeekNextRevisionRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PeekNextRevisionRequest copyWith(
          void Function(PeekNextRevisionRequest) updates) =>
      super.copyWith((message) => updates(message as PeekNextRevisionRequest))
          as PeekNextRevisionRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static PeekNextRevisionRequest create() => PeekNextRevisionRequest._();
  @$core.override
  PeekNextRevisionRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static PeekNextRevisionRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<PeekNextRevisionRequest>(create);
  static PeekNextRevisionRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get itemKref => $_getN(0);
  @$pb.TagNumber(1)
  set itemKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasItemKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearItemKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureItemKref() => $_ensure(0);
}

class PeekNextRevisionResponse extends $pb.GeneratedMessage {
  factory PeekNextRevisionResponse({
    $core.int? number,
  }) {
    final result = create();
    if (number != null) result.number = number;
    return result;
  }

  PeekNextRevisionResponse._();

  factory PeekNextRevisionResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory PeekNextRevisionResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'PeekNextRevisionResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aI(1, _omitFieldNames ? '' : 'number')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PeekNextRevisionResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PeekNextRevisionResponse copyWith(
          void Function(PeekNextRevisionResponse) updates) =>
      super.copyWith((message) => updates(message as PeekNextRevisionResponse))
          as PeekNextRevisionResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static PeekNextRevisionResponse create() => PeekNextRevisionResponse._();
  @$core.override
  PeekNextRevisionResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static PeekNextRevisionResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<PeekNextRevisionResponse>(create);
  static PeekNextRevisionResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get number => $_getIZ(0);
  @$pb.TagNumber(1)
  set number($core.int value) => $_setSignedInt32(0, value);
  @$pb.TagNumber(1)
  $core.bool hasNumber() => $_has(0);
  @$pb.TagNumber(1)
  void clearNumber() => $_clearField(1);
}

class GetEdgesRequest extends $pb.GeneratedMessage {
  factory GetEdgesRequest({
    Kref? kref,
    $core.String? edgeTypeFilter,
    EdgeDirection? direction,
    PaginationRequest? pagination,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (edgeTypeFilter != null) result.edgeTypeFilter = edgeTypeFilter;
    if (direction != null) result.direction = direction;
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetEdgesRequest._();

  factory GetEdgesRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetEdgesRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetEdgesRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'edgeTypeFilter')
    ..aE<EdgeDirection>(3, _omitFieldNames ? '' : 'direction',
        enumValues: EdgeDirection.values)
    ..aOM<PaginationRequest>(4, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationRequest.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEdgesRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEdgesRequest copyWith(void Function(GetEdgesRequest) updates) =>
      super.copyWith((message) => updates(message as GetEdgesRequest))
          as GetEdgesRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetEdgesRequest create() => GetEdgesRequest._();
  @$core.override
  GetEdgesRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetEdgesRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetEdgesRequest>(create);
  static GetEdgesRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get edgeTypeFilter => $_getSZ(1);
  @$pb.TagNumber(2)
  set edgeTypeFilter($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasEdgeTypeFilter() => $_has(1);
  @$pb.TagNumber(2)
  void clearEdgeTypeFilter() => $_clearField(2);

  @$pb.TagNumber(3)
  EdgeDirection get direction => $_getN(2);
  @$pb.TagNumber(3)
  set direction(EdgeDirection value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasDirection() => $_has(2);
  @$pb.TagNumber(3)
  void clearDirection() => $_clearField(3);

  /// Optional pagination parameters
  @$pb.TagNumber(4)
  PaginationRequest get pagination => $_getN(3);
  @$pb.TagNumber(4)
  set pagination(PaginationRequest value) => $_setField(4, value);
  @$pb.TagNumber(4)
  $core.bool hasPagination() => $_has(3);
  @$pb.TagNumber(4)
  void clearPagination() => $_clearField(4);
  @$pb.TagNumber(4)
  PaginationRequest ensurePagination() => $_ensure(3);
}

class GetEdgesResponse extends $pb.GeneratedMessage {
  factory GetEdgesResponse({
    $core.Iterable<Edge>? edges,
    $core.Iterable<Kref>? revisionKrefs,
    PaginationResponse? pagination,
  }) {
    final result = create();
    if (edges != null) result.edges.addAll(edges);
    if (revisionKrefs != null) result.revisionKrefs.addAll(revisionKrefs);
    if (pagination != null) result.pagination = pagination;
    return result;
  }

  GetEdgesResponse._();

  factory GetEdgesResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetEdgesResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetEdgesResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<Edge>(1, _omitFieldNames ? '' : 'edges', subBuilder: Edge.create)
    ..pPM<Kref>(2, _omitFieldNames ? '' : 'revisionKrefs',
        subBuilder: Kref.create)
    ..aOM<PaginationResponse>(3, _omitFieldNames ? '' : 'pagination',
        subBuilder: PaginationResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEdgesResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEdgesResponse copyWith(void Function(GetEdgesResponse) updates) =>
      super.copyWith((message) => updates(message as GetEdgesResponse))
          as GetEdgesResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetEdgesResponse create() => GetEdgesResponse._();
  @$core.override
  GetEdgesResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetEdgesResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetEdgesResponse>(create);
  static GetEdgesResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<Edge> get edges => $_getList(0);

  @$pb.TagNumber(2)
  $pb.PbList<Kref> get revisionKrefs => $_getList(1);

  /// Pagination info for the response
  @$pb.TagNumber(3)
  PaginationResponse get pagination => $_getN(2);
  @$pb.TagNumber(3)
  set pagination(PaginationResponse value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasPagination() => $_has(2);
  @$pb.TagNumber(3)
  void clearPagination() => $_clearField(3);
  @$pb.TagNumber(3)
  PaginationResponse ensurePagination() => $_ensure(2);
}

class DeleteEdgeRequest extends $pb.GeneratedMessage {
  factory DeleteEdgeRequest({
    Kref? sourceKref,
    Kref? targetKref,
    $core.String? edgeType,
  }) {
    final result = create();
    if (sourceKref != null) result.sourceKref = sourceKref;
    if (targetKref != null) result.targetKref = targetKref;
    if (edgeType != null) result.edgeType = edgeType;
    return result;
  }

  DeleteEdgeRequest._();

  factory DeleteEdgeRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteEdgeRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteEdgeRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'sourceKref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'targetKref', subBuilder: Kref.create)
    ..aOS(3, _omitFieldNames ? '' : 'edgeType')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteEdgeRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteEdgeRequest copyWith(void Function(DeleteEdgeRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteEdgeRequest))
          as DeleteEdgeRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteEdgeRequest create() => DeleteEdgeRequest._();
  @$core.override
  DeleteEdgeRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteEdgeRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteEdgeRequest>(create);
  static DeleteEdgeRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get sourceKref => $_getN(0);
  @$pb.TagNumber(1)
  set sourceKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasSourceKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearSourceKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureSourceKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get targetKref => $_getN(1);
  @$pb.TagNumber(2)
  set targetKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasTargetKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearTargetKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureTargetKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.String get edgeType => $_getSZ(2);
  @$pb.TagNumber(3)
  set edgeType($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasEdgeType() => $_has(2);
  @$pb.TagNumber(3)
  void clearEdgeType() => $_clearField(3);
}

/// Represents a single step in a traversal path
class PathStep extends $pb.GeneratedMessage {
  factory PathStep({
    Kref? revisionKref,
    $core.String? edgeType,
    $core.int? depth,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (edgeType != null) result.edgeType = edgeType;
    if (depth != null) result.depth = depth;
    return result;
  }

  PathStep._();

  factory PathStep.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory PathStep.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'PathStep',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'edgeType')
    ..aI(3, _omitFieldNames ? '' : 'depth')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PathStep clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  PathStep copyWith(void Function(PathStep) updates) =>
      super.copyWith((message) => updates(message as PathStep)) as PathStep;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static PathStep create() => PathStep._();
  @$core.override
  PathStep createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static PathStep getDefault() =>
      _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<PathStep>(create);
  static PathStep? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get edgeType => $_getSZ(1);
  @$pb.TagNumber(2)
  set edgeType($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasEdgeType() => $_has(1);
  @$pb.TagNumber(2)
  void clearEdgeType() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.int get depth => $_getIZ(2);
  @$pb.TagNumber(3)
  set depth($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasDepth() => $_has(2);
  @$pb.TagNumber(3)
  void clearDepth() => $_clearField(3);
}

/// Represents a complete path between two revisions
class RevisionPath extends $pb.GeneratedMessage {
  factory RevisionPath({
    $core.Iterable<PathStep>? steps,
    $core.int? totalDepth,
  }) {
    final result = create();
    if (steps != null) result.steps.addAll(steps);
    if (totalDepth != null) result.totalDepth = totalDepth;
    return result;
  }

  RevisionPath._();

  factory RevisionPath.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory RevisionPath.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'RevisionPath',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<PathStep>(1, _omitFieldNames ? '' : 'steps',
        subBuilder: PathStep.create)
    ..aI(2, _omitFieldNames ? '' : 'totalDepth')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RevisionPath clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RevisionPath copyWith(void Function(RevisionPath) updates) =>
      super.copyWith((message) => updates(message as RevisionPath))
          as RevisionPath;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static RevisionPath create() => RevisionPath._();
  @$core.override
  RevisionPath createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static RevisionPath getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<RevisionPath>(create);
  static RevisionPath? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<PathStep> get steps => $_getList(0);

  @$pb.TagNumber(2)
  $core.int get totalDepth => $_getIZ(1);
  @$pb.TagNumber(2)
  set totalDepth($core.int value) => $_setSignedInt32(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTotalDepth() => $_has(1);
  @$pb.TagNumber(2)
  void clearTotalDepth() => $_clearField(2);
}

/// Request for transitive dependency/dependents traversal
class TraverseEdgesRequest extends $pb.GeneratedMessage {
  factory TraverseEdgesRequest({
    Kref? originKref,
    EdgeDirection? direction,
    $core.Iterable<$core.String>? edgeTypeFilter,
    $core.int? maxDepth,
    $core.int? limit,
    $core.bool? includePath,
  }) {
    final result = create();
    if (originKref != null) result.originKref = originKref;
    if (direction != null) result.direction = direction;
    if (edgeTypeFilter != null) result.edgeTypeFilter.addAll(edgeTypeFilter);
    if (maxDepth != null) result.maxDepth = maxDepth;
    if (limit != null) result.limit = limit;
    if (includePath != null) result.includePath = includePath;
    return result;
  }

  TraverseEdgesRequest._();

  factory TraverseEdgesRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory TraverseEdgesRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'TraverseEdgesRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'originKref', subBuilder: Kref.create)
    ..aE<EdgeDirection>(2, _omitFieldNames ? '' : 'direction',
        enumValues: EdgeDirection.values)
    ..pPS(3, _omitFieldNames ? '' : 'edgeTypeFilter')
    ..aI(4, _omitFieldNames ? '' : 'maxDepth')
    ..aI(5, _omitFieldNames ? '' : 'limit')
    ..aOB(6, _omitFieldNames ? '' : 'includePath')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TraverseEdgesRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TraverseEdgesRequest copyWith(void Function(TraverseEdgesRequest) updates) =>
      super.copyWith((message) => updates(message as TraverseEdgesRequest))
          as TraverseEdgesRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static TraverseEdgesRequest create() => TraverseEdgesRequest._();
  @$core.override
  TraverseEdgesRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static TraverseEdgesRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<TraverseEdgesRequest>(create);
  static TraverseEdgesRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get originKref => $_getN(0);
  @$pb.TagNumber(1)
  set originKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasOriginKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearOriginKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureOriginKref() => $_ensure(0);

  @$pb.TagNumber(2)
  EdgeDirection get direction => $_getN(1);
  @$pb.TagNumber(2)
  set direction(EdgeDirection value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasDirection() => $_has(1);
  @$pb.TagNumber(2)
  void clearDirection() => $_clearField(2);

  @$pb.TagNumber(3)
  $pb.PbList<$core.String> get edgeTypeFilter => $_getList(2);

  @$pb.TagNumber(4)
  $core.int get maxDepth => $_getIZ(3);
  @$pb.TagNumber(4)
  set maxDepth($core.int value) => $_setSignedInt32(3, value);
  @$pb.TagNumber(4)
  $core.bool hasMaxDepth() => $_has(3);
  @$pb.TagNumber(4)
  void clearMaxDepth() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.int get limit => $_getIZ(4);
  @$pb.TagNumber(5)
  set limit($core.int value) => $_setSignedInt32(4, value);
  @$pb.TagNumber(5)
  $core.bool hasLimit() => $_has(4);
  @$pb.TagNumber(5)
  void clearLimit() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.bool get includePath => $_getBF(5);
  @$pb.TagNumber(6)
  set includePath($core.bool value) => $_setBool(5, value);
  @$pb.TagNumber(6)
  $core.bool hasIncludePath() => $_has(5);
  @$pb.TagNumber(6)
  void clearIncludePath() => $_clearField(6);
}

class TraverseEdgesResponse extends $pb.GeneratedMessage {
  factory TraverseEdgesResponse({
    $core.Iterable<RevisionPath>? paths,
    $core.Iterable<Kref>? revisionKrefs,
    $core.Iterable<Edge>? edges,
    $core.int? totalCount,
    $core.bool? truncated,
  }) {
    final result = create();
    if (paths != null) result.paths.addAll(paths);
    if (revisionKrefs != null) result.revisionKrefs.addAll(revisionKrefs);
    if (edges != null) result.edges.addAll(edges);
    if (totalCount != null) result.totalCount = totalCount;
    if (truncated != null) result.truncated = truncated;
    return result;
  }

  TraverseEdgesResponse._();

  factory TraverseEdgesResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory TraverseEdgesResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'TraverseEdgesResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<RevisionPath>(1, _omitFieldNames ? '' : 'paths',
        subBuilder: RevisionPath.create)
    ..pPM<Kref>(2, _omitFieldNames ? '' : 'revisionKrefs',
        subBuilder: Kref.create)
    ..pPM<Edge>(3, _omitFieldNames ? '' : 'edges', subBuilder: Edge.create)
    ..aI(4, _omitFieldNames ? '' : 'totalCount')
    ..aOB(5, _omitFieldNames ? '' : 'truncated')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TraverseEdgesResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TraverseEdgesResponse copyWith(
          void Function(TraverseEdgesResponse) updates) =>
      super.copyWith((message) => updates(message as TraverseEdgesResponse))
          as TraverseEdgesResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static TraverseEdgesResponse create() => TraverseEdgesResponse._();
  @$core.override
  TraverseEdgesResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static TraverseEdgesResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<TraverseEdgesResponse>(create);
  static TraverseEdgesResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<RevisionPath> get paths => $_getList(0);

  @$pb.TagNumber(2)
  $pb.PbList<Kref> get revisionKrefs => $_getList(1);

  @$pb.TagNumber(3)
  $pb.PbList<Edge> get edges => $_getList(2);

  @$pb.TagNumber(4)
  $core.int get totalCount => $_getIZ(3);
  @$pb.TagNumber(4)
  set totalCount($core.int value) => $_setSignedInt32(3, value);
  @$pb.TagNumber(4)
  $core.bool hasTotalCount() => $_has(3);
  @$pb.TagNumber(4)
  void clearTotalCount() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.bool get truncated => $_getBF(4);
  @$pb.TagNumber(5)
  set truncated($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasTruncated() => $_has(4);
  @$pb.TagNumber(5)
  void clearTruncated() => $_clearField(5);
}

/// Request for shortest path between two revisions
class ShortestPathRequest extends $pb.GeneratedMessage {
  factory ShortestPathRequest({
    Kref? sourceKref,
    Kref? targetKref,
    $core.Iterable<$core.String>? edgeTypeFilter,
    $core.int? maxDepth,
    $core.bool? allShortest,
  }) {
    final result = create();
    if (sourceKref != null) result.sourceKref = sourceKref;
    if (targetKref != null) result.targetKref = targetKref;
    if (edgeTypeFilter != null) result.edgeTypeFilter.addAll(edgeTypeFilter);
    if (maxDepth != null) result.maxDepth = maxDepth;
    if (allShortest != null) result.allShortest = allShortest;
    return result;
  }

  ShortestPathRequest._();

  factory ShortestPathRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ShortestPathRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ShortestPathRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'sourceKref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'targetKref', subBuilder: Kref.create)
    ..pPS(3, _omitFieldNames ? '' : 'edgeTypeFilter')
    ..aI(4, _omitFieldNames ? '' : 'maxDepth')
    ..aOB(5, _omitFieldNames ? '' : 'allShortest')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ShortestPathRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ShortestPathRequest copyWith(void Function(ShortestPathRequest) updates) =>
      super.copyWith((message) => updates(message as ShortestPathRequest))
          as ShortestPathRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ShortestPathRequest create() => ShortestPathRequest._();
  @$core.override
  ShortestPathRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ShortestPathRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ShortestPathRequest>(create);
  static ShortestPathRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get sourceKref => $_getN(0);
  @$pb.TagNumber(1)
  set sourceKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasSourceKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearSourceKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureSourceKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get targetKref => $_getN(1);
  @$pb.TagNumber(2)
  set targetKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasTargetKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearTargetKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureTargetKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $pb.PbList<$core.String> get edgeTypeFilter => $_getList(2);

  @$pb.TagNumber(4)
  $core.int get maxDepth => $_getIZ(3);
  @$pb.TagNumber(4)
  set maxDepth($core.int value) => $_setSignedInt32(3, value);
  @$pb.TagNumber(4)
  $core.bool hasMaxDepth() => $_has(3);
  @$pb.TagNumber(4)
  void clearMaxDepth() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.bool get allShortest => $_getBF(4);
  @$pb.TagNumber(5)
  set allShortest($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasAllShortest() => $_has(4);
  @$pb.TagNumber(5)
  void clearAllShortest() => $_clearField(5);
}

class ShortestPathResponse extends $pb.GeneratedMessage {
  factory ShortestPathResponse({
    $core.Iterable<RevisionPath>? paths,
    $core.bool? pathExists,
    $core.int? pathLength,
  }) {
    final result = create();
    if (paths != null) result.paths.addAll(paths);
    if (pathExists != null) result.pathExists = pathExists;
    if (pathLength != null) result.pathLength = pathLength;
    return result;
  }

  ShortestPathResponse._();

  factory ShortestPathResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ShortestPathResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ShortestPathResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<RevisionPath>(1, _omitFieldNames ? '' : 'paths',
        subBuilder: RevisionPath.create)
    ..aOB(2, _omitFieldNames ? '' : 'pathExists')
    ..aI(3, _omitFieldNames ? '' : 'pathLength')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ShortestPathResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ShortestPathResponse copyWith(void Function(ShortestPathResponse) updates) =>
      super.copyWith((message) => updates(message as ShortestPathResponse))
          as ShortestPathResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ShortestPathResponse create() => ShortestPathResponse._();
  @$core.override
  ShortestPathResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ShortestPathResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ShortestPathResponse>(create);
  static ShortestPathResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<RevisionPath> get paths => $_getList(0);

  @$pb.TagNumber(2)
  $core.bool get pathExists => $_getBF(1);
  @$pb.TagNumber(2)
  set pathExists($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasPathExists() => $_has(1);
  @$pb.TagNumber(2)
  void clearPathExists() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.int get pathLength => $_getIZ(2);
  @$pb.TagNumber(3)
  set pathLength($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasPathLength() => $_has(2);
  @$pb.TagNumber(3)
  void clearPathLength() => $_clearField(3);
}

/// Request for impact analysis (what depends on this revision, transitively)
class ImpactAnalysisRequest extends $pb.GeneratedMessage {
  factory ImpactAnalysisRequest({
    Kref? revisionKref,
    $core.Iterable<$core.String>? edgeTypeFilter,
    $core.int? maxDepth,
    $core.int? limit,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (edgeTypeFilter != null) result.edgeTypeFilter.addAll(edgeTypeFilter);
    if (maxDepth != null) result.maxDepth = maxDepth;
    if (limit != null) result.limit = limit;
    return result;
  }

  ImpactAnalysisRequest._();

  factory ImpactAnalysisRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ImpactAnalysisRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ImpactAnalysisRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..pPS(2, _omitFieldNames ? '' : 'edgeTypeFilter')
    ..aI(3, _omitFieldNames ? '' : 'maxDepth')
    ..aI(4, _omitFieldNames ? '' : 'limit')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactAnalysisRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactAnalysisRequest copyWith(
          void Function(ImpactAnalysisRequest) updates) =>
      super.copyWith((message) => updates(message as ImpactAnalysisRequest))
          as ImpactAnalysisRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ImpactAnalysisRequest create() => ImpactAnalysisRequest._();
  @$core.override
  ImpactAnalysisRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ImpactAnalysisRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ImpactAnalysisRequest>(create);
  static ImpactAnalysisRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $pb.PbList<$core.String> get edgeTypeFilter => $_getList(1);

  @$pb.TagNumber(3)
  $core.int get maxDepth => $_getIZ(2);
  @$pb.TagNumber(3)
  set maxDepth($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasMaxDepth() => $_has(2);
  @$pb.TagNumber(3)
  void clearMaxDepth() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.int get limit => $_getIZ(3);
  @$pb.TagNumber(4)
  set limit($core.int value) => $_setSignedInt32(3, value);
  @$pb.TagNumber(4)
  $core.bool hasLimit() => $_has(3);
  @$pb.TagNumber(4)
  void clearLimit() => $_clearField(4);
}

class ImpactedRevision extends $pb.GeneratedMessage {
  factory ImpactedRevision({
    Kref? revisionKref,
    Kref? itemKref,
    $core.int? impactDepth,
    $core.Iterable<$core.String>? impactPathTypes,
  }) {
    final result = create();
    if (revisionKref != null) result.revisionKref = revisionKref;
    if (itemKref != null) result.itemKref = itemKref;
    if (impactDepth != null) result.impactDepth = impactDepth;
    if (impactPathTypes != null) result.impactPathTypes.addAll(impactPathTypes);
    return result;
  }

  ImpactedRevision._();

  factory ImpactedRevision.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ImpactedRevision.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ImpactedRevision',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'revisionKref',
        subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..aI(3, _omitFieldNames ? '' : 'impactDepth')
    ..pPS(4, _omitFieldNames ? '' : 'impactPathTypes')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactedRevision clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactedRevision copyWith(void Function(ImpactedRevision) updates) =>
      super.copyWith((message) => updates(message as ImpactedRevision))
          as ImpactedRevision;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ImpactedRevision create() => ImpactedRevision._();
  @$core.override
  ImpactedRevision createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ImpactedRevision getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ImpactedRevision>(create);
  static ImpactedRevision? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get revisionKref => $_getN(0);
  @$pb.TagNumber(1)
  set revisionKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureRevisionKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get itemKref => $_getN(1);
  @$pb.TagNumber(2)
  set itemKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasItemKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearItemKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureItemKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.int get impactDepth => $_getIZ(2);
  @$pb.TagNumber(3)
  set impactDepth($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasImpactDepth() => $_has(2);
  @$pb.TagNumber(3)
  void clearImpactDepth() => $_clearField(3);

  @$pb.TagNumber(4)
  $pb.PbList<$core.String> get impactPathTypes => $_getList(3);
}

class ImpactAnalysisResponse extends $pb.GeneratedMessage {
  factory ImpactAnalysisResponse({
    $core.Iterable<ImpactedRevision>? impactedRevisions,
    $core.int? totalImpacted,
    $core.bool? truncated,
  }) {
    final result = create();
    if (impactedRevisions != null)
      result.impactedRevisions.addAll(impactedRevisions);
    if (totalImpacted != null) result.totalImpacted = totalImpacted;
    if (truncated != null) result.truncated = truncated;
    return result;
  }

  ImpactAnalysisResponse._();

  factory ImpactAnalysisResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ImpactAnalysisResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ImpactAnalysisResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<ImpactedRevision>(1, _omitFieldNames ? '' : 'impactedRevisions',
        subBuilder: ImpactedRevision.create)
    ..aI(2, _omitFieldNames ? '' : 'totalImpacted')
    ..aOB(3, _omitFieldNames ? '' : 'truncated')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactAnalysisResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ImpactAnalysisResponse copyWith(
          void Function(ImpactAnalysisResponse) updates) =>
      super.copyWith((message) => updates(message as ImpactAnalysisResponse))
          as ImpactAnalysisResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ImpactAnalysisResponse create() => ImpactAnalysisResponse._();
  @$core.override
  ImpactAnalysisResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ImpactAnalysisResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ImpactAnalysisResponse>(create);
  static ImpactAnalysisResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<ImpactedRevision> get impactedRevisions => $_getList(0);

  @$pb.TagNumber(2)
  $core.int get totalImpacted => $_getIZ(1);
  @$pb.TagNumber(2)
  set totalImpacted($core.int value) => $_setSignedInt32(1, value);
  @$pb.TagNumber(2)
  $core.bool hasTotalImpacted() => $_has(1);
  @$pb.TagNumber(2)
  void clearTotalImpacted() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.bool get truncated => $_getBF(2);
  @$pb.TagNumber(3)
  set truncated($core.bool value) => $_setBool(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTruncated() => $_has(2);
  @$pb.TagNumber(3)
  void clearTruncated() => $_clearField(3);
}

class CreateBundleRequest extends $pb.GeneratedMessage {
  factory CreateBundleRequest({
    $core.String? parentPath,
    $core.String? bundleName,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (parentPath != null) result.parentPath = parentPath;
    if (bundleName != null) result.bundleName = bundleName;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  CreateBundleRequest._();

  factory CreateBundleRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateBundleRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateBundleRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'parentPath')
    ..aOS(2, _omitFieldNames ? '' : 'bundleName')
    ..m<$core.String, $core.String>(3, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'CreateBundleRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateBundleRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateBundleRequest copyWith(void Function(CreateBundleRequest) updates) =>
      super.copyWith((message) => updates(message as CreateBundleRequest))
          as CreateBundleRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateBundleRequest create() => CreateBundleRequest._();
  @$core.override
  CreateBundleRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateBundleRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateBundleRequest>(create);
  static CreateBundleRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get parentPath => $_getSZ(0);
  @$pb.TagNumber(1)
  set parentPath($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasParentPath() => $_has(0);
  @$pb.TagNumber(1)
  void clearParentPath() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get bundleName => $_getSZ(1);
  @$pb.TagNumber(2)
  set bundleName($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasBundleName() => $_has(1);
  @$pb.TagNumber(2)
  void clearBundleName() => $_clearField(2);

  @$pb.TagNumber(3)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(2);
}

class BundleMember extends $pb.GeneratedMessage {
  factory BundleMember({
    Kref? itemKref,
    $core.String? addedAt,
    $core.String? addedBy,
    $core.String? addedByUsername,
    $core.int? addedInRevision,
  }) {
    final result = create();
    if (itemKref != null) result.itemKref = itemKref;
    if (addedAt != null) result.addedAt = addedAt;
    if (addedBy != null) result.addedBy = addedBy;
    if (addedByUsername != null) result.addedByUsername = addedByUsername;
    if (addedInRevision != null) result.addedInRevision = addedInRevision;
    return result;
  }

  BundleMember._();

  factory BundleMember.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory BundleMember.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'BundleMember',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'itemKref', subBuilder: Kref.create)
    ..aOS(2, _omitFieldNames ? '' : 'addedAt')
    ..aOS(3, _omitFieldNames ? '' : 'addedBy')
    ..aOS(4, _omitFieldNames ? '' : 'addedByUsername')
    ..aI(5, _omitFieldNames ? '' : 'addedInRevision')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  BundleMember clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  BundleMember copyWith(void Function(BundleMember) updates) =>
      super.copyWith((message) => updates(message as BundleMember))
          as BundleMember;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static BundleMember create() => BundleMember._();
  @$core.override
  BundleMember createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static BundleMember getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<BundleMember>(create);
  static BundleMember? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get itemKref => $_getN(0);
  @$pb.TagNumber(1)
  set itemKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasItemKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearItemKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureItemKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.String get addedAt => $_getSZ(1);
  @$pb.TagNumber(2)
  set addedAt($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasAddedAt() => $_has(1);
  @$pb.TagNumber(2)
  void clearAddedAt() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get addedBy => $_getSZ(2);
  @$pb.TagNumber(3)
  set addedBy($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasAddedBy() => $_has(2);
  @$pb.TagNumber(3)
  void clearAddedBy() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.String get addedByUsername => $_getSZ(3);
  @$pb.TagNumber(4)
  set addedByUsername($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasAddedByUsername() => $_has(3);
  @$pb.TagNumber(4)
  void clearAddedByUsername() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.int get addedInRevision => $_getIZ(4);
  @$pb.TagNumber(5)
  set addedInRevision($core.int value) => $_setSignedInt32(4, value);
  @$pb.TagNumber(5)
  $core.bool hasAddedInRevision() => $_has(4);
  @$pb.TagNumber(5)
  void clearAddedInRevision() => $_clearField(5);
}

class AddBundleMemberRequest extends $pb.GeneratedMessage {
  factory AddBundleMemberRequest({
    Kref? bundleKref,
    Kref? memberItemKref,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (bundleKref != null) result.bundleKref = bundleKref;
    if (memberItemKref != null) result.memberItemKref = memberItemKref;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  AddBundleMemberRequest._();

  factory AddBundleMemberRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory AddBundleMemberRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'AddBundleMemberRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'bundleKref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'memberItemKref',
        subBuilder: Kref.create)
    ..m<$core.String, $core.String>(3, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'AddBundleMemberRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  AddBundleMemberRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  AddBundleMemberRequest copyWith(
          void Function(AddBundleMemberRequest) updates) =>
      super.copyWith((message) => updates(message as AddBundleMemberRequest))
          as AddBundleMemberRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static AddBundleMemberRequest create() => AddBundleMemberRequest._();
  @$core.override
  AddBundleMemberRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static AddBundleMemberRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<AddBundleMemberRequest>(create);
  static AddBundleMemberRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get bundleKref => $_getN(0);
  @$pb.TagNumber(1)
  set bundleKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasBundleKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearBundleKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureBundleKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get memberItemKref => $_getN(1);
  @$pb.TagNumber(2)
  set memberItemKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasMemberItemKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearMemberItemKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureMemberItemKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(2);
}

class AddBundleMemberResponse extends $pb.GeneratedMessage {
  factory AddBundleMemberResponse({
    $core.bool? success,
    $core.String? message,
    RevisionResponse? newRevision,
  }) {
    final result = create();
    if (success != null) result.success = success;
    if (message != null) result.message = message;
    if (newRevision != null) result.newRevision = newRevision;
    return result;
  }

  AddBundleMemberResponse._();

  factory AddBundleMemberResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory AddBundleMemberResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'AddBundleMemberResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'success')
    ..aOS(2, _omitFieldNames ? '' : 'message')
    ..aOM<RevisionResponse>(3, _omitFieldNames ? '' : 'newRevision',
        subBuilder: RevisionResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  AddBundleMemberResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  AddBundleMemberResponse copyWith(
          void Function(AddBundleMemberResponse) updates) =>
      super.copyWith((message) => updates(message as AddBundleMemberResponse))
          as AddBundleMemberResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static AddBundleMemberResponse create() => AddBundleMemberResponse._();
  @$core.override
  AddBundleMemberResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static AddBundleMemberResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<AddBundleMemberResponse>(create);
  static AddBundleMemberResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get success => $_getBF(0);
  @$pb.TagNumber(1)
  set success($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasSuccess() => $_has(0);
  @$pb.TagNumber(1)
  void clearSuccess() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get message => $_getSZ(1);
  @$pb.TagNumber(2)
  set message($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasMessage() => $_has(1);
  @$pb.TagNumber(2)
  void clearMessage() => $_clearField(2);

  @$pb.TagNumber(3)
  RevisionResponse get newRevision => $_getN(2);
  @$pb.TagNumber(3)
  set newRevision(RevisionResponse value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasNewRevision() => $_has(2);
  @$pb.TagNumber(3)
  void clearNewRevision() => $_clearField(3);
  @$pb.TagNumber(3)
  RevisionResponse ensureNewRevision() => $_ensure(2);
}

class RemoveBundleMemberRequest extends $pb.GeneratedMessage {
  factory RemoveBundleMemberRequest({
    Kref? bundleKref,
    Kref? memberItemKref,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (bundleKref != null) result.bundleKref = bundleKref;
    if (memberItemKref != null) result.memberItemKref = memberItemKref;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  RemoveBundleMemberRequest._();

  factory RemoveBundleMemberRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory RemoveBundleMemberRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'RemoveBundleMemberRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'bundleKref', subBuilder: Kref.create)
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'memberItemKref',
        subBuilder: Kref.create)
    ..m<$core.String, $core.String>(3, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'RemoveBundleMemberRequest.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RemoveBundleMemberRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RemoveBundleMemberRequest copyWith(
          void Function(RemoveBundleMemberRequest) updates) =>
      super.copyWith((message) => updates(message as RemoveBundleMemberRequest))
          as RemoveBundleMemberRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static RemoveBundleMemberRequest create() => RemoveBundleMemberRequest._();
  @$core.override
  RemoveBundleMemberRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static RemoveBundleMemberRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<RemoveBundleMemberRequest>(create);
  static RemoveBundleMemberRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get bundleKref => $_getN(0);
  @$pb.TagNumber(1)
  set bundleKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasBundleKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearBundleKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureBundleKref() => $_ensure(0);

  @$pb.TagNumber(2)
  Kref get memberItemKref => $_getN(1);
  @$pb.TagNumber(2)
  set memberItemKref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasMemberItemKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearMemberItemKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureMemberItemKref() => $_ensure(1);

  @$pb.TagNumber(3)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(2);
}

class RemoveBundleMemberResponse extends $pb.GeneratedMessage {
  factory RemoveBundleMemberResponse({
    $core.bool? success,
    $core.String? message,
    RevisionResponse? newRevision,
  }) {
    final result = create();
    if (success != null) result.success = success;
    if (message != null) result.message = message;
    if (newRevision != null) result.newRevision = newRevision;
    return result;
  }

  RemoveBundleMemberResponse._();

  factory RemoveBundleMemberResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory RemoveBundleMemberResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'RemoveBundleMemberResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'success')
    ..aOS(2, _omitFieldNames ? '' : 'message')
    ..aOM<RevisionResponse>(3, _omitFieldNames ? '' : 'newRevision',
        subBuilder: RevisionResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RemoveBundleMemberResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  RemoveBundleMemberResponse copyWith(
          void Function(RemoveBundleMemberResponse) updates) =>
      super.copyWith(
              (message) => updates(message as RemoveBundleMemberResponse))
          as RemoveBundleMemberResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static RemoveBundleMemberResponse create() => RemoveBundleMemberResponse._();
  @$core.override
  RemoveBundleMemberResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static RemoveBundleMemberResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<RemoveBundleMemberResponse>(create);
  static RemoveBundleMemberResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get success => $_getBF(0);
  @$pb.TagNumber(1)
  set success($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasSuccess() => $_has(0);
  @$pb.TagNumber(1)
  void clearSuccess() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get message => $_getSZ(1);
  @$pb.TagNumber(2)
  set message($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasMessage() => $_has(1);
  @$pb.TagNumber(2)
  void clearMessage() => $_clearField(2);

  @$pb.TagNumber(3)
  RevisionResponse get newRevision => $_getN(2);
  @$pb.TagNumber(3)
  set newRevision(RevisionResponse value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasNewRevision() => $_has(2);
  @$pb.TagNumber(3)
  void clearNewRevision() => $_clearField(3);
  @$pb.TagNumber(3)
  RevisionResponse ensureNewRevision() => $_ensure(2);
}

class GetBundleMembersRequest extends $pb.GeneratedMessage {
  factory GetBundleMembersRequest({
    Kref? bundleKref,
    $core.int? revisionNumber,
  }) {
    final result = create();
    if (bundleKref != null) result.bundleKref = bundleKref;
    if (revisionNumber != null) result.revisionNumber = revisionNumber;
    return result;
  }

  GetBundleMembersRequest._();

  factory GetBundleMembersRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetBundleMembersRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetBundleMembersRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'bundleKref', subBuilder: Kref.create)
    ..aI(2, _omitFieldNames ? '' : 'revisionNumber')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleMembersRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleMembersRequest copyWith(
          void Function(GetBundleMembersRequest) updates) =>
      super.copyWith((message) => updates(message as GetBundleMembersRequest))
          as GetBundleMembersRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetBundleMembersRequest create() => GetBundleMembersRequest._();
  @$core.override
  GetBundleMembersRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetBundleMembersRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetBundleMembersRequest>(create);
  static GetBundleMembersRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get bundleKref => $_getN(0);
  @$pb.TagNumber(1)
  set bundleKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasBundleKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearBundleKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureBundleKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.int get revisionNumber => $_getIZ(1);
  @$pb.TagNumber(2)
  set revisionNumber($core.int value) => $_setSignedInt32(1, value);
  @$pb.TagNumber(2)
  $core.bool hasRevisionNumber() => $_has(1);
  @$pb.TagNumber(2)
  void clearRevisionNumber() => $_clearField(2);
}

class GetBundleMembersResponse extends $pb.GeneratedMessage {
  factory GetBundleMembersResponse({
    $core.Iterable<BundleMember>? members,
    $core.int? revisionNumber,
    $core.int? totalCount,
  }) {
    final result = create();
    if (members != null) result.members.addAll(members);
    if (revisionNumber != null) result.revisionNumber = revisionNumber;
    if (totalCount != null) result.totalCount = totalCount;
    return result;
  }

  GetBundleMembersResponse._();

  factory GetBundleMembersResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetBundleMembersResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetBundleMembersResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<BundleMember>(1, _omitFieldNames ? '' : 'members',
        subBuilder: BundleMember.create)
    ..aI(2, _omitFieldNames ? '' : 'revisionNumber')
    ..aI(3, _omitFieldNames ? '' : 'totalCount')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleMembersResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleMembersResponse copyWith(
          void Function(GetBundleMembersResponse) updates) =>
      super.copyWith((message) => updates(message as GetBundleMembersResponse))
          as GetBundleMembersResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetBundleMembersResponse create() => GetBundleMembersResponse._();
  @$core.override
  GetBundleMembersResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetBundleMembersResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetBundleMembersResponse>(create);
  static GetBundleMembersResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<BundleMember> get members => $_getList(0);

  @$pb.TagNumber(2)
  $core.int get revisionNumber => $_getIZ(1);
  @$pb.TagNumber(2)
  set revisionNumber($core.int value) => $_setSignedInt32(1, value);
  @$pb.TagNumber(2)
  $core.bool hasRevisionNumber() => $_has(1);
  @$pb.TagNumber(2)
  void clearRevisionNumber() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.int get totalCount => $_getIZ(2);
  @$pb.TagNumber(3)
  set totalCount($core.int value) => $_setSignedInt32(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTotalCount() => $_has(2);
  @$pb.TagNumber(3)
  void clearTotalCount() => $_clearField(3);
}

class BundleRevisionHistory extends $pb.GeneratedMessage {
  factory BundleRevisionHistory({
    $core.int? revisionNumber,
    $core.String? action,
    Kref? memberItemKref,
    $core.String? author,
    $core.String? username,
    $core.String? createdAt,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? metadata,
  }) {
    final result = create();
    if (revisionNumber != null) result.revisionNumber = revisionNumber;
    if (action != null) result.action = action;
    if (memberItemKref != null) result.memberItemKref = memberItemKref;
    if (author != null) result.author = author;
    if (username != null) result.username = username;
    if (createdAt != null) result.createdAt = createdAt;
    if (metadata != null) result.metadata.addEntries(metadata);
    return result;
  }

  BundleRevisionHistory._();

  factory BundleRevisionHistory.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory BundleRevisionHistory.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'BundleRevisionHistory',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aI(1, _omitFieldNames ? '' : 'revisionNumber')
    ..aOS(2, _omitFieldNames ? '' : 'action')
    ..aOM<Kref>(3, _omitFieldNames ? '' : 'memberItemKref',
        subBuilder: Kref.create)
    ..aOS(4, _omitFieldNames ? '' : 'author')
    ..aOS(5, _omitFieldNames ? '' : 'username')
    ..aOS(6, _omitFieldNames ? '' : 'createdAt')
    ..m<$core.String, $core.String>(7, _omitFieldNames ? '' : 'metadata',
        entryClassName: 'BundleRevisionHistory.MetadataEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  BundleRevisionHistory clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  BundleRevisionHistory copyWith(
          void Function(BundleRevisionHistory) updates) =>
      super.copyWith((message) => updates(message as BundleRevisionHistory))
          as BundleRevisionHistory;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static BundleRevisionHistory create() => BundleRevisionHistory._();
  @$core.override
  BundleRevisionHistory createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static BundleRevisionHistory getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<BundleRevisionHistory>(create);
  static BundleRevisionHistory? _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get revisionNumber => $_getIZ(0);
  @$pb.TagNumber(1)
  set revisionNumber($core.int value) => $_setSignedInt32(0, value);
  @$pb.TagNumber(1)
  $core.bool hasRevisionNumber() => $_has(0);
  @$pb.TagNumber(1)
  void clearRevisionNumber() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get action => $_getSZ(1);
  @$pb.TagNumber(2)
  set action($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasAction() => $_has(1);
  @$pb.TagNumber(2)
  void clearAction() => $_clearField(2);

  @$pb.TagNumber(3)
  Kref get memberItemKref => $_getN(2);
  @$pb.TagNumber(3)
  set memberItemKref(Kref value) => $_setField(3, value);
  @$pb.TagNumber(3)
  $core.bool hasMemberItemKref() => $_has(2);
  @$pb.TagNumber(3)
  void clearMemberItemKref() => $_clearField(3);
  @$pb.TagNumber(3)
  Kref ensureMemberItemKref() => $_ensure(2);

  @$pb.TagNumber(4)
  $core.String get author => $_getSZ(3);
  @$pb.TagNumber(4)
  set author($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasAuthor() => $_has(3);
  @$pb.TagNumber(4)
  void clearAuthor() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.String get username => $_getSZ(4);
  @$pb.TagNumber(5)
  set username($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasUsername() => $_has(4);
  @$pb.TagNumber(5)
  void clearUsername() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.String get createdAt => $_getSZ(5);
  @$pb.TagNumber(6)
  set createdAt($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasCreatedAt() => $_has(5);
  @$pb.TagNumber(6)
  void clearCreatedAt() => $_clearField(6);

  @$pb.TagNumber(7)
  $pb.PbMap<$core.String, $core.String> get metadata => $_getMap(6);
}

class GetBundleHistoryRequest extends $pb.GeneratedMessage {
  factory GetBundleHistoryRequest({
    Kref? bundleKref,
  }) {
    final result = create();
    if (bundleKref != null) result.bundleKref = bundleKref;
    return result;
  }

  GetBundleHistoryRequest._();

  factory GetBundleHistoryRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetBundleHistoryRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetBundleHistoryRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'bundleKref', subBuilder: Kref.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleHistoryRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleHistoryRequest copyWith(
          void Function(GetBundleHistoryRequest) updates) =>
      super.copyWith((message) => updates(message as GetBundleHistoryRequest))
          as GetBundleHistoryRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetBundleHistoryRequest create() => GetBundleHistoryRequest._();
  @$core.override
  GetBundleHistoryRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetBundleHistoryRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetBundleHistoryRequest>(create);
  static GetBundleHistoryRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get bundleKref => $_getN(0);
  @$pb.TagNumber(1)
  set bundleKref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasBundleKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearBundleKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureBundleKref() => $_ensure(0);
}

class GetBundleHistoryResponse extends $pb.GeneratedMessage {
  factory GetBundleHistoryResponse({
    $core.Iterable<BundleRevisionHistory>? history,
  }) {
    final result = create();
    if (history != null) result.history.addAll(history);
    return result;
  }

  GetBundleHistoryResponse._();

  factory GetBundleHistoryResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetBundleHistoryResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetBundleHistoryResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<BundleRevisionHistory>(1, _omitFieldNames ? '' : 'history',
        subBuilder: BundleRevisionHistory.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleHistoryResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetBundleHistoryResponse copyWith(
          void Function(GetBundleHistoryResponse) updates) =>
      super.copyWith((message) => updates(message as GetBundleHistoryResponse))
          as GetBundleHistoryResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetBundleHistoryResponse create() => GetBundleHistoryResponse._();
  @$core.override
  GetBundleHistoryResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetBundleHistoryResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetBundleHistoryResponse>(create);
  static GetBundleHistoryResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<BundleRevisionHistory> get history => $_getList(0);
}

enum EventStreamRequest_StartPosition {
  fromLatest,
  fromCursor,
  fromTimestamp,
  fromBeginning,
  notSet
}

class EventStreamRequest extends $pb.GeneratedMessage {
  factory EventStreamRequest({
    $core.String? routingKeyFilter,
    $core.String? krefFilter,
    $core.String? cursor,
    $core.String? consumerGroup,
    $core.bool? fromLatest,
    $core.String? fromCursor,
    $core.String? fromTimestamp,
    $core.bool? fromBeginning,
  }) {
    final result = create();
    if (routingKeyFilter != null) result.routingKeyFilter = routingKeyFilter;
    if (krefFilter != null) result.krefFilter = krefFilter;
    if (cursor != null) result.cursor = cursor;
    if (consumerGroup != null) result.consumerGroup = consumerGroup;
    if (fromLatest != null) result.fromLatest = fromLatest;
    if (fromCursor != null) result.fromCursor = fromCursor;
    if (fromTimestamp != null) result.fromTimestamp = fromTimestamp;
    if (fromBeginning != null) result.fromBeginning = fromBeginning;
    return result;
  }

  EventStreamRequest._();

  factory EventStreamRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory EventStreamRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static const $core.Map<$core.int, EventStreamRequest_StartPosition>
      _EventStreamRequest_StartPositionByTag = {
    5: EventStreamRequest_StartPosition.fromLatest,
    6: EventStreamRequest_StartPosition.fromCursor,
    7: EventStreamRequest_StartPosition.fromTimestamp,
    8: EventStreamRequest_StartPosition.fromBeginning,
    0: EventStreamRequest_StartPosition.notSet
  };
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'EventStreamRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..oo(0, [5, 6, 7, 8])
    ..aOS(1, _omitFieldNames ? '' : 'routingKeyFilter')
    ..aOS(2, _omitFieldNames ? '' : 'krefFilter')
    ..aOS(3, _omitFieldNames ? '' : 'cursor')
    ..aOS(4, _omitFieldNames ? '' : 'consumerGroup')
    ..aOB(5, _omitFieldNames ? '' : 'fromLatest')
    ..aOS(6, _omitFieldNames ? '' : 'fromCursor')
    ..aOS(7, _omitFieldNames ? '' : 'fromTimestamp')
    ..aOB(8, _omitFieldNames ? '' : 'fromBeginning')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  EventStreamRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  EventStreamRequest copyWith(void Function(EventStreamRequest) updates) =>
      super.copyWith((message) => updates(message as EventStreamRequest))
          as EventStreamRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static EventStreamRequest create() => EventStreamRequest._();
  @$core.override
  EventStreamRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static EventStreamRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<EventStreamRequest>(create);
  static EventStreamRequest? _defaultInstance;

  @$pb.TagNumber(5)
  @$pb.TagNumber(6)
  @$pb.TagNumber(7)
  @$pb.TagNumber(8)
  EventStreamRequest_StartPosition whichStartPosition() =>
      _EventStreamRequest_StartPositionByTag[$_whichOneof(0)]!;
  @$pb.TagNumber(5)
  @$pb.TagNumber(6)
  @$pb.TagNumber(7)
  @$pb.TagNumber(8)
  void clearStartPosition() => $_clearField($_whichOneof(0));

  /// A routing key filter, e.g., "item.model.created" or "revision.tagged.*"
  /// An empty string subscribes to all events.
  @$pb.TagNumber(1)
  $core.String get routingKeyFilter => $_getSZ(0);
  @$pb.TagNumber(1)
  set routingKeyFilter($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasRoutingKeyFilter() => $_has(0);
  @$pb.TagNumber(1)
  void clearRoutingKeyFilter() => $_clearField(1);

  /// A kref filter for filtering by object URI patterns, e.g., "kref://projectA/**/*.model"
  /// Supports wildcards. An empty string means no kref filtering.
  @$pb.TagNumber(2)
  $core.String get krefFilter => $_getSZ(1);
  @$pb.TagNumber(2)
  set krefFilter($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasKrefFilter() => $_has(1);
  @$pb.TagNumber(2)
  void clearKrefFilter() => $_clearField(2);

  /// Cursor-based resume (Creator tier and above)
  /// Resume from a previous event cursor to avoid missing events during disconnection.
  @$pb.TagNumber(3)
  $core.String get cursor => $_getSZ(2);
  @$pb.TagNumber(3)
  set cursor($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasCursor() => $_has(2);
  @$pb.TagNumber(3)
  void clearCursor() => $_clearField(3);

  /// Consumer group for load-balanced delivery (Enterprise tier only)
  /// Multiple consumers in the same group will each receive different events.
  @$pb.TagNumber(4)
  $core.String get consumerGroup => $_getSZ(3);
  @$pb.TagNumber(4)
  set consumerGroup($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasConsumerGroup() => $_has(3);
  @$pb.TagNumber(4)
  void clearConsumerGroup() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.bool get fromLatest => $_getBF(4);
  @$pb.TagNumber(5)
  set fromLatest($core.bool value) => $_setBool(4, value);
  @$pb.TagNumber(5)
  $core.bool hasFromLatest() => $_has(4);
  @$pb.TagNumber(5)
  void clearFromLatest() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.String get fromCursor => $_getSZ(5);
  @$pb.TagNumber(6)
  set fromCursor($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasFromCursor() => $_has(5);
  @$pb.TagNumber(6)
  void clearFromCursor() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.String get fromTimestamp => $_getSZ(6);
  @$pb.TagNumber(7)
  set fromTimestamp($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasFromTimestamp() => $_has(6);
  @$pb.TagNumber(7)
  void clearFromTimestamp() => $_clearField(7);

  @$pb.TagNumber(8)
  $core.bool get fromBeginning => $_getBF(7);
  @$pb.TagNumber(8)
  set fromBeginning($core.bool value) => $_setBool(7, value);
  @$pb.TagNumber(8)
  $core.bool hasFromBeginning() => $_has(7);
  @$pb.TagNumber(8)
  void clearFromBeginning() => $_clearField(8);
}

class Event extends $pb.GeneratedMessage {
  factory Event({
    $core.String? routingKey,
    Kref? kref,
    $core.String? timestamp,
    $core.String? author,
    $core.String? tenantId,
    $core.Iterable<$core.MapEntry<$core.String, $core.String>>? details,
    $core.String? username,
    $core.String? cursor,
  }) {
    final result = create();
    if (routingKey != null) result.routingKey = routingKey;
    if (kref != null) result.kref = kref;
    if (timestamp != null) result.timestamp = timestamp;
    if (author != null) result.author = author;
    if (tenantId != null) result.tenantId = tenantId;
    if (details != null) result.details.addEntries(details);
    if (username != null) result.username = username;
    if (cursor != null) result.cursor = cursor;
    return result;
  }

  Event._();

  factory Event.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory Event.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'Event',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'routingKey')
    ..aOM<Kref>(2, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOS(3, _omitFieldNames ? '' : 'timestamp')
    ..aOS(4, _omitFieldNames ? '' : 'author')
    ..aOS(5, _omitFieldNames ? '' : 'tenantId')
    ..m<$core.String, $core.String>(6, _omitFieldNames ? '' : 'details',
        entryClassName: 'Event.DetailsEntry',
        keyFieldType: $pb.PbFieldType.OS,
        valueFieldType: $pb.PbFieldType.OS,
        packageName: const $pb.PackageName('kumiho'))
    ..aOS(7, _omitFieldNames ? '' : 'username')
    ..aOS(8, _omitFieldNames ? '' : 'cursor')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Event clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  Event copyWith(void Function(Event) updates) =>
      super.copyWith((message) => updates(message as Event)) as Event;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static Event create() => Event._();
  @$core.override
  Event createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static Event getDefault() =>
      _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Event>(create);
  static Event? _defaultInstance;

  /// A routing key describing the event, e.g., "item.model.created"
  @$pb.TagNumber(1)
  $core.String get routingKey => $_getSZ(0);
  @$pb.TagNumber(1)
  set routingKey($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasRoutingKey() => $_has(0);
  @$pb.TagNumber(1)
  void clearRoutingKey() => $_clearField(1);

  /// The Kref of the object that was affected.
  @$pb.TagNumber(2)
  Kref get kref => $_getN(1);
  @$pb.TagNumber(2)
  set kref(Kref value) => $_setField(2, value);
  @$pb.TagNumber(2)
  $core.bool hasKref() => $_has(1);
  @$pb.TagNumber(2)
  void clearKref() => $_clearField(2);
  @$pb.TagNumber(2)
  Kref ensureKref() => $_ensure(1);

  /// Timestamp of the event.
  @$pb.TagNumber(3)
  $core.String get timestamp => $_getSZ(2);
  @$pb.TagNumber(3)
  set timestamp($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTimestamp() => $_has(2);
  @$pb.TagNumber(3)
  void clearTimestamp() => $_clearField(3);

  /// The user who triggered the event.
  @$pb.TagNumber(4)
  $core.String get author => $_getSZ(3);
  @$pb.TagNumber(4)
  set author($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasAuthor() => $_has(3);
  @$pb.TagNumber(4)
  void clearAuthor() => $_clearField(4);

  /// Tenant scope for isolation in shared deployments.
  @$pb.TagNumber(5)
  $core.String get tenantId => $_getSZ(4);
  @$pb.TagNumber(5)
  set tenantId($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasTenantId() => $_has(4);
  @$pb.TagNumber(5)
  void clearTenantId() => $_clearField(5);

  /// Additional details about the event, e.g., the tag that was added.
  @$pb.TagNumber(6)
  $pb.PbMap<$core.String, $core.String> get details => $_getMap(5);

  @$pb.TagNumber(7)
  $core.String get username => $_getSZ(6);
  @$pb.TagNumber(7)
  set username($core.String value) => $_setString(6, value);
  @$pb.TagNumber(7)
  $core.bool hasUsername() => $_has(6);
  @$pb.TagNumber(7)
  void clearUsername() => $_clearField(7);

  /// Cursor for resumable streaming (Creator tier and above).
  /// Save this cursor and pass it in EventStreamRequest.cursor to resume
  /// from this point after reconnection.
  @$pb.TagNumber(8)
  $core.String get cursor => $_getSZ(7);
  @$pb.TagNumber(8)
  set cursor($core.String value) => $_setString(7, value);
  @$pb.TagNumber(8)
  $core.bool hasCursor() => $_has(7);
  @$pb.TagNumber(8)
  void clearCursor() => $_clearField(8);
}

/// Request for event streaming capabilities
class GetEventCapabilitiesRequest extends $pb.GeneratedMessage {
  factory GetEventCapabilitiesRequest() => create();

  GetEventCapabilitiesRequest._();

  factory GetEventCapabilitiesRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetEventCapabilitiesRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetEventCapabilitiesRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEventCapabilitiesRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetEventCapabilitiesRequest copyWith(
          void Function(GetEventCapabilitiesRequest) updates) =>
      super.copyWith(
              (message) => updates(message as GetEventCapabilitiesRequest))
          as GetEventCapabilitiesRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetEventCapabilitiesRequest create() =>
      GetEventCapabilitiesRequest._();
  @$core.override
  GetEventCapabilitiesRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetEventCapabilitiesRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetEventCapabilitiesRequest>(create);
  static GetEventCapabilitiesRequest? _defaultInstance;
}

/// Event streaming capabilities for the current tenant tier
class EventCapabilities extends $pb.GeneratedMessage {
  factory EventCapabilities({
    $core.bool? supportsReplay,
    $core.bool? supportsCursor,
    $core.bool? supportsConsumerGroups,
    $fixnum.Int64? maxRetentionHours,
    $fixnum.Int64? maxBufferSize,
    $core.String? tier,
  }) {
    final result = create();
    if (supportsReplay != null) result.supportsReplay = supportsReplay;
    if (supportsCursor != null) result.supportsCursor = supportsCursor;
    if (supportsConsumerGroups != null)
      result.supportsConsumerGroups = supportsConsumerGroups;
    if (maxRetentionHours != null) result.maxRetentionHours = maxRetentionHours;
    if (maxBufferSize != null) result.maxBufferSize = maxBufferSize;
    if (tier != null) result.tier = tier;
    return result;
  }

  EventCapabilities._();

  factory EventCapabilities.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory EventCapabilities.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'EventCapabilities',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOB(1, _omitFieldNames ? '' : 'supportsReplay')
    ..aOB(2, _omitFieldNames ? '' : 'supportsCursor')
    ..aOB(3, _omitFieldNames ? '' : 'supportsConsumerGroups')
    ..aInt64(4, _omitFieldNames ? '' : 'maxRetentionHours')
    ..aInt64(5, _omitFieldNames ? '' : 'maxBufferSize')
    ..aOS(6, _omitFieldNames ? '' : 'tier')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  EventCapabilities clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  EventCapabilities copyWith(void Function(EventCapabilities) updates) =>
      super.copyWith((message) => updates(message as EventCapabilities))
          as EventCapabilities;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static EventCapabilities create() => EventCapabilities._();
  @$core.override
  EventCapabilities createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static EventCapabilities getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<EventCapabilities>(create);
  static EventCapabilities? _defaultInstance;

  /// Whether this tier supports replaying past events
  @$pb.TagNumber(1)
  $core.bool get supportsReplay => $_getBF(0);
  @$pb.TagNumber(1)
  set supportsReplay($core.bool value) => $_setBool(0, value);
  @$pb.TagNumber(1)
  $core.bool hasSupportsReplay() => $_has(0);
  @$pb.TagNumber(1)
  void clearSupportsReplay() => $_clearField(1);

  /// Whether cursor-based resume is supported
  @$pb.TagNumber(2)
  $core.bool get supportsCursor => $_getBF(1);
  @$pb.TagNumber(2)
  set supportsCursor($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasSupportsCursor() => $_has(1);
  @$pb.TagNumber(2)
  void clearSupportsCursor() => $_clearField(2);

  /// Whether consumer groups are supported (Enterprise only)
  @$pb.TagNumber(3)
  $core.bool get supportsConsumerGroups => $_getBF(2);
  @$pb.TagNumber(3)
  set supportsConsumerGroups($core.bool value) => $_setBool(2, value);
  @$pb.TagNumber(3)
  $core.bool hasSupportsConsumerGroups() => $_has(2);
  @$pb.TagNumber(3)
  void clearSupportsConsumerGroups() => $_clearField(3);

  /// Maximum event retention in hours (0 = none, -1 = unlimited)
  @$pb.TagNumber(4)
  $fixnum.Int64 get maxRetentionHours => $_getI64(3);
  @$pb.TagNumber(4)
  set maxRetentionHours($fixnum.Int64 value) => $_setInt64(3, value);
  @$pb.TagNumber(4)
  $core.bool hasMaxRetentionHours() => $_has(3);
  @$pb.TagNumber(4)
  void clearMaxRetentionHours() => $_clearField(4);

  /// Maximum events in buffer (0 = none, -1 = unlimited)
  @$pb.TagNumber(5)
  $fixnum.Int64 get maxBufferSize => $_getI64(4);
  @$pb.TagNumber(5)
  set maxBufferSize($fixnum.Int64 value) => $_setInt64(4, value);
  @$pb.TagNumber(5)
  $core.bool hasMaxBufferSize() => $_has(4);
  @$pb.TagNumber(5)
  void clearMaxBufferSize() => $_clearField(5);

  /// Tier identifier (free, creator, studio, enterprise)
  @$pb.TagNumber(6)
  $core.String get tier => $_getSZ(5);
  @$pb.TagNumber(6)
  set tier($core.String value) => $_setString(5, value);
  @$pb.TagNumber(6)
  $core.bool hasTier() => $_has(5);
  @$pb.TagNumber(6)
  void clearTier() => $_clearField(6);
}

class CreateProjectRequest extends $pb.GeneratedMessage {
  factory CreateProjectRequest({
    $core.String? name,
    $core.String? description,
  }) {
    final result = create();
    if (name != null) result.name = name;
    if (description != null) result.description = description;
    return result;
  }

  CreateProjectRequest._();

  factory CreateProjectRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory CreateProjectRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'CreateProjectRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'name')
    ..aOS(2, _omitFieldNames ? '' : 'description')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateProjectRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  CreateProjectRequest copyWith(void Function(CreateProjectRequest) updates) =>
      super.copyWith((message) => updates(message as CreateProjectRequest))
          as CreateProjectRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static CreateProjectRequest create() => CreateProjectRequest._();
  @$core.override
  CreateProjectRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static CreateProjectRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<CreateProjectRequest>(create);
  static CreateProjectRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get name => $_getSZ(0);
  @$pb.TagNumber(1)
  set name($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasName() => $_has(0);
  @$pb.TagNumber(1)
  void clearName() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get description => $_getSZ(1);
  @$pb.TagNumber(2)
  set description($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasDescription() => $_has(1);
  @$pb.TagNumber(2)
  void clearDescription() => $_clearField(2);
}

class ProjectResponse extends $pb.GeneratedMessage {
  factory ProjectResponse({
    $core.String? projectId,
    $core.String? name,
    $core.String? description,
    $core.String? createdAt,
    $core.String? updatedAt,
    $core.bool? deprecated,
    $core.bool? allowPublic,
  }) {
    final result = create();
    if (projectId != null) result.projectId = projectId;
    if (name != null) result.name = name;
    if (description != null) result.description = description;
    if (createdAt != null) result.createdAt = createdAt;
    if (updatedAt != null) result.updatedAt = updatedAt;
    if (deprecated != null) result.deprecated = deprecated;
    if (allowPublic != null) result.allowPublic = allowPublic;
    return result;
  }

  ProjectResponse._();

  factory ProjectResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory ProjectResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'ProjectResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'projectId')
    ..aOS(2, _omitFieldNames ? '' : 'name')
    ..aOS(3, _omitFieldNames ? '' : 'description')
    ..aOS(4, _omitFieldNames ? '' : 'createdAt')
    ..aOS(5, _omitFieldNames ? '' : 'updatedAt')
    ..aOB(6, _omitFieldNames ? '' : 'deprecated')
    ..aOB(7, _omitFieldNames ? '' : 'allowPublic')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ProjectResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  ProjectResponse copyWith(void Function(ProjectResponse) updates) =>
      super.copyWith((message) => updates(message as ProjectResponse))
          as ProjectResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static ProjectResponse create() => ProjectResponse._();
  @$core.override
  ProjectResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static ProjectResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<ProjectResponse>(create);
  static ProjectResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get projectId => $_getSZ(0);
  @$pb.TagNumber(1)
  set projectId($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasProjectId() => $_has(0);
  @$pb.TagNumber(1)
  void clearProjectId() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.String get name => $_getSZ(1);
  @$pb.TagNumber(2)
  set name($core.String value) => $_setString(1, value);
  @$pb.TagNumber(2)
  $core.bool hasName() => $_has(1);
  @$pb.TagNumber(2)
  void clearName() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get description => $_getSZ(2);
  @$pb.TagNumber(3)
  set description($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasDescription() => $_has(2);
  @$pb.TagNumber(3)
  void clearDescription() => $_clearField(3);

  @$pb.TagNumber(4)
  $core.String get createdAt => $_getSZ(3);
  @$pb.TagNumber(4)
  set createdAt($core.String value) => $_setString(3, value);
  @$pb.TagNumber(4)
  $core.bool hasCreatedAt() => $_has(3);
  @$pb.TagNumber(4)
  void clearCreatedAt() => $_clearField(4);

  @$pb.TagNumber(5)
  $core.String get updatedAt => $_getSZ(4);
  @$pb.TagNumber(5)
  set updatedAt($core.String value) => $_setString(4, value);
  @$pb.TagNumber(5)
  $core.bool hasUpdatedAt() => $_has(4);
  @$pb.TagNumber(5)
  void clearUpdatedAt() => $_clearField(5);

  @$pb.TagNumber(6)
  $core.bool get deprecated => $_getBF(5);
  @$pb.TagNumber(6)
  set deprecated($core.bool value) => $_setBool(5, value);
  @$pb.TagNumber(6)
  $core.bool hasDeprecated() => $_has(5);
  @$pb.TagNumber(6)
  void clearDeprecated() => $_clearField(6);

  @$pb.TagNumber(7)
  $core.bool get allowPublic => $_getBF(6);
  @$pb.TagNumber(7)
  set allowPublic($core.bool value) => $_setBool(6, value);
  @$pb.TagNumber(7)
  $core.bool hasAllowPublic() => $_has(6);
  @$pb.TagNumber(7)
  void clearAllowPublic() => $_clearField(7);
}

class GetProjectsRequest extends $pb.GeneratedMessage {
  factory GetProjectsRequest() => create();

  GetProjectsRequest._();

  factory GetProjectsRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetProjectsRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetProjectsRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetProjectsRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetProjectsRequest copyWith(void Function(GetProjectsRequest) updates) =>
      super.copyWith((message) => updates(message as GetProjectsRequest))
          as GetProjectsRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetProjectsRequest create() => GetProjectsRequest._();
  @$core.override
  GetProjectsRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetProjectsRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetProjectsRequest>(create);
  static GetProjectsRequest? _defaultInstance;
}

class GetProjectsResponse extends $pb.GeneratedMessage {
  factory GetProjectsResponse({
    $core.Iterable<ProjectResponse>? projects,
  }) {
    final result = create();
    if (projects != null) result.projects.addAll(projects);
    return result;
  }

  GetProjectsResponse._();

  factory GetProjectsResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetProjectsResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetProjectsResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..pPM<ProjectResponse>(1, _omitFieldNames ? '' : 'projects',
        subBuilder: ProjectResponse.create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetProjectsResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetProjectsResponse copyWith(void Function(GetProjectsResponse) updates) =>
      super.copyWith((message) => updates(message as GetProjectsResponse))
          as GetProjectsResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetProjectsResponse create() => GetProjectsResponse._();
  @$core.override
  GetProjectsResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetProjectsResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetProjectsResponse>(create);
  static GetProjectsResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $pb.PbList<ProjectResponse> get projects => $_getList(0);
}

class DeleteProjectRequest extends $pb.GeneratedMessage {
  factory DeleteProjectRequest({
    $core.String? projectId,
    $core.bool? force,
  }) {
    final result = create();
    if (projectId != null) result.projectId = projectId;
    if (force != null) result.force = force;
    return result;
  }

  DeleteProjectRequest._();

  factory DeleteProjectRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory DeleteProjectRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'DeleteProjectRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'projectId')
    ..aOB(2, _omitFieldNames ? '' : 'force')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteProjectRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  DeleteProjectRequest copyWith(void Function(DeleteProjectRequest) updates) =>
      super.copyWith((message) => updates(message as DeleteProjectRequest))
          as DeleteProjectRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static DeleteProjectRequest create() => DeleteProjectRequest._();
  @$core.override
  DeleteProjectRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static DeleteProjectRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<DeleteProjectRequest>(create);
  static DeleteProjectRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get projectId => $_getSZ(0);
  @$pb.TagNumber(1)
  set projectId($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasProjectId() => $_has(0);
  @$pb.TagNumber(1)
  void clearProjectId() => $_clearField(1);

  /// force=true lets owner/admin hard-delete; otherwise deprecates.
  @$pb.TagNumber(2)
  $core.bool get force => $_getBF(1);
  @$pb.TagNumber(2)
  set force($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasForce() => $_has(1);
  @$pb.TagNumber(2)
  void clearForce() => $_clearField(2);
}

class UpdateProjectRequest extends $pb.GeneratedMessage {
  factory UpdateProjectRequest({
    $core.String? projectId,
    $core.bool? allowPublic,
    $core.String? description,
  }) {
    final result = create();
    if (projectId != null) result.projectId = projectId;
    if (allowPublic != null) result.allowPublic = allowPublic;
    if (description != null) result.description = description;
    return result;
  }

  UpdateProjectRequest._();

  factory UpdateProjectRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory UpdateProjectRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'UpdateProjectRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOS(1, _omitFieldNames ? '' : 'projectId')
    ..aOB(2, _omitFieldNames ? '' : 'allowPublic')
    ..aOS(3, _omitFieldNames ? '' : 'description')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UpdateProjectRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  UpdateProjectRequest copyWith(void Function(UpdateProjectRequest) updates) =>
      super.copyWith((message) => updates(message as UpdateProjectRequest))
          as UpdateProjectRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static UpdateProjectRequest create() => UpdateProjectRequest._();
  @$core.override
  UpdateProjectRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static UpdateProjectRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<UpdateProjectRequest>(create);
  static UpdateProjectRequest? _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get projectId => $_getSZ(0);
  @$pb.TagNumber(1)
  set projectId($core.String value) => $_setString(0, value);
  @$pb.TagNumber(1)
  $core.bool hasProjectId() => $_has(0);
  @$pb.TagNumber(1)
  void clearProjectId() => $_clearField(1);

  @$pb.TagNumber(2)
  $core.bool get allowPublic => $_getBF(1);
  @$pb.TagNumber(2)
  set allowPublic($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasAllowPublic() => $_has(1);
  @$pb.TagNumber(2)
  void clearAllowPublic() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get description => $_getSZ(2);
  @$pb.TagNumber(3)
  set description($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasDescription() => $_has(2);
  @$pb.TagNumber(3)
  void clearDescription() => $_clearField(3);
}

class SetDeprecatedRequest extends $pb.GeneratedMessage {
  factory SetDeprecatedRequest({
    Kref? kref,
    $core.bool? deprecated,
  }) {
    final result = create();
    if (kref != null) result.kref = kref;
    if (deprecated != null) result.deprecated = deprecated;
    return result;
  }

  SetDeprecatedRequest._();

  factory SetDeprecatedRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory SetDeprecatedRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'SetDeprecatedRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aOM<Kref>(1, _omitFieldNames ? '' : 'kref', subBuilder: Kref.create)
    ..aOB(2, _omitFieldNames ? '' : 'deprecated')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetDeprecatedRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  SetDeprecatedRequest copyWith(void Function(SetDeprecatedRequest) updates) =>
      super.copyWith((message) => updates(message as SetDeprecatedRequest))
          as SetDeprecatedRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static SetDeprecatedRequest create() => SetDeprecatedRequest._();
  @$core.override
  SetDeprecatedRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static SetDeprecatedRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<SetDeprecatedRequest>(create);
  static SetDeprecatedRequest? _defaultInstance;

  @$pb.TagNumber(1)
  Kref get kref => $_getN(0);
  @$pb.TagNumber(1)
  set kref(Kref value) => $_setField(1, value);
  @$pb.TagNumber(1)
  $core.bool hasKref() => $_has(0);
  @$pb.TagNumber(1)
  void clearKref() => $_clearField(1);
  @$pb.TagNumber(1)
  Kref ensureKref() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get deprecated => $_getBF(1);
  @$pb.TagNumber(2)
  set deprecated($core.bool value) => $_setBool(1, value);
  @$pb.TagNumber(2)
  $core.bool hasDeprecated() => $_has(1);
  @$pb.TagNumber(2)
  void clearDeprecated() => $_clearField(2);
}

class GetTenantUsageRequest extends $pb.GeneratedMessage {
  factory GetTenantUsageRequest() => create();

  GetTenantUsageRequest._();

  factory GetTenantUsageRequest.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory GetTenantUsageRequest.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'GetTenantUsageRequest',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetTenantUsageRequest clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  GetTenantUsageRequest copyWith(
          void Function(GetTenantUsageRequest) updates) =>
      super.copyWith((message) => updates(message as GetTenantUsageRequest))
          as GetTenantUsageRequest;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static GetTenantUsageRequest create() => GetTenantUsageRequest._();
  @$core.override
  GetTenantUsageRequest createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static GetTenantUsageRequest getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<GetTenantUsageRequest>(create);
  static GetTenantUsageRequest? _defaultInstance;
}

class TenantUsageResponse extends $pb.GeneratedMessage {
  factory TenantUsageResponse({
    $fixnum.Int64? nodeCount,
    $fixnum.Int64? nodeLimit,
    $core.String? tenantId,
  }) {
    final result = create();
    if (nodeCount != null) result.nodeCount = nodeCount;
    if (nodeLimit != null) result.nodeLimit = nodeLimit;
    if (tenantId != null) result.tenantId = tenantId;
    return result;
  }

  TenantUsageResponse._();

  factory TenantUsageResponse.fromBuffer($core.List<$core.int> data,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromBuffer(data, registry);
  factory TenantUsageResponse.fromJson($core.String json,
          [$pb.ExtensionRegistry registry = $pb.ExtensionRegistry.EMPTY]) =>
      create()..mergeFromJson(json, registry);

  static final $pb.BuilderInfo _i = $pb.BuilderInfo(
      _omitMessageNames ? '' : 'TenantUsageResponse',
      package: const $pb.PackageName(_omitMessageNames ? '' : 'kumiho'),
      createEmptyInstance: create)
    ..aInt64(1, _omitFieldNames ? '' : 'nodeCount')
    ..aInt64(2, _omitFieldNames ? '' : 'nodeLimit')
    ..aOS(3, _omitFieldNames ? '' : 'tenantId')
    ..hasRequiredFields = false;

  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TenantUsageResponse clone() => deepCopy();
  @$core.Deprecated('See https://github.com/google/protobuf.dart/issues/998.')
  TenantUsageResponse copyWith(void Function(TenantUsageResponse) updates) =>
      super.copyWith((message) => updates(message as TenantUsageResponse))
          as TenantUsageResponse;

  @$core.override
  $pb.BuilderInfo get info_ => _i;

  @$core.pragma('dart2js:noInline')
  static TenantUsageResponse create() => TenantUsageResponse._();
  @$core.override
  TenantUsageResponse createEmptyInstance() => create();
  @$core.pragma('dart2js:noInline')
  static TenantUsageResponse getDefault() => _defaultInstance ??=
      $pb.GeneratedMessage.$_defaultFor<TenantUsageResponse>(create);
  static TenantUsageResponse? _defaultInstance;

  @$pb.TagNumber(1)
  $fixnum.Int64 get nodeCount => $_getI64(0);
  @$pb.TagNumber(1)
  set nodeCount($fixnum.Int64 value) => $_setInt64(0, value);
  @$pb.TagNumber(1)
  $core.bool hasNodeCount() => $_has(0);
  @$pb.TagNumber(1)
  void clearNodeCount() => $_clearField(1);

  @$pb.TagNumber(2)
  $fixnum.Int64 get nodeLimit => $_getI64(1);
  @$pb.TagNumber(2)
  set nodeLimit($fixnum.Int64 value) => $_setInt64(1, value);
  @$pb.TagNumber(2)
  $core.bool hasNodeLimit() => $_has(1);
  @$pb.TagNumber(2)
  void clearNodeLimit() => $_clearField(2);

  @$pb.TagNumber(3)
  $core.String get tenantId => $_getSZ(2);
  @$pb.TagNumber(3)
  set tenantId($core.String value) => $_setString(2, value);
  @$pb.TagNumber(3)
  $core.bool hasTenantId() => $_has(2);
  @$pb.TagNumber(3)
  void clearTenantId() => $_clearField(3);
}

/// The Kumiho service definition.
class KumihoServiceApi {
  final $pb.RpcClient _client;

  KumihoServiceApi(this._client);

  /// Project methods
  $async.Future<ProjectResponse> createProject(
          $pb.ClientContext? ctx, CreateProjectRequest request) =>
      _client.invoke<ProjectResponse>(
          ctx, 'KumihoService', 'CreateProject', request, ProjectResponse());
  $async.Future<GetProjectsResponse> getProjects(
          $pb.ClientContext? ctx, GetProjectsRequest request) =>
      _client.invoke<GetProjectsResponse>(
          ctx, 'KumihoService', 'GetProjects', request, GetProjectsResponse());
  $async.Future<ProjectResponse> updateProject(
          $pb.ClientContext? ctx, UpdateProjectRequest request) =>
      _client.invoke<ProjectResponse>(
          ctx, 'KumihoService', 'UpdateProject', request, ProjectResponse());
  $async.Future<StatusResponse> deleteProject(
          $pb.ClientContext? ctx, DeleteProjectRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteProject', request, StatusResponse());

  /// Space methods
  $async.Future<SpaceResponse> createSpace(
          $pb.ClientContext? ctx, CreateSpaceRequest request) =>
      _client.invoke<SpaceResponse>(
          ctx, 'KumihoService', 'CreateSpace', request, SpaceResponse());
  $async.Future<SpaceResponse> getSpace(
          $pb.ClientContext? ctx, GetSpaceRequest request) =>
      _client.invoke<SpaceResponse>(
          ctx, 'KumihoService', 'GetSpace', request, SpaceResponse());
  $async.Future<GetChildSpacesResponse> getChildSpaces(
          $pb.ClientContext? ctx, GetChildSpacesRequest request) =>
      _client.invoke<GetChildSpacesResponse>(ctx, 'KumihoService',
          'GetChildSpaces', request, GetChildSpacesResponse());
  $async.Future<StatusResponse> deleteSpace(
          $pb.ClientContext? ctx, DeleteSpaceRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteSpace', request, StatusResponse());
  $async.Future<SpaceResponse> updateSpaceMetadata(
          $pb.ClientContext? ctx, UpdateMetadataRequest request) =>
      _client.invoke<SpaceResponse>(ctx, 'KumihoService', 'UpdateSpaceMetadata',
          request, SpaceResponse());

  /// Item methods
  $async.Future<ItemResponse> createItem(
          $pb.ClientContext? ctx, CreateItemRequest request) =>
      _client.invoke<ItemResponse>(
          ctx, 'KumihoService', 'CreateItem', request, ItemResponse());
  $async.Future<ItemResponse> getItem(
          $pb.ClientContext? ctx, GetItemRequest request) =>
      _client.invoke<ItemResponse>(
          ctx, 'KumihoService', 'GetItem', request, ItemResponse());
  $async.Future<GetItemsResponse> getItems(
          $pb.ClientContext? ctx, GetItemsRequest request) =>
      _client.invoke<GetItemsResponse>(
          ctx, 'KumihoService', 'GetItems', request, GetItemsResponse());
  $async.Future<GetItemsResponse> itemSearch(
          $pb.ClientContext? ctx, ItemSearchRequest request) =>
      _client.invoke<GetItemsResponse>(
          ctx, 'KumihoService', 'ItemSearch', request, GetItemsResponse());
  $async.Future<StatusResponse> deleteItem(
          $pb.ClientContext? ctx, DeleteItemRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteItem', request, StatusResponse());
  $async.Future<ItemResponse> updateItemMetadata(
          $pb.ClientContext? ctx, UpdateMetadataRequest request) =>
      _client.invoke<ItemResponse>(
          ctx, 'KumihoService', 'UpdateItemMetadata', request, ItemResponse());

  /// Revision methods
  $async.Future<RevisionResponse> resolveKref(
          $pb.ClientContext? ctx, ResolveKrefRequest request) =>
      _client.invoke<RevisionResponse>(
          ctx, 'KumihoService', 'ResolveKref', request, RevisionResponse());
  $async.Future<ResolveLocationResponse> resolveLocation(
          $pb.ClientContext? ctx, ResolveLocationRequest request) =>
      _client.invoke<ResolveLocationResponse>(ctx, 'KumihoService',
          'ResolveLocation', request, ResolveLocationResponse());
  $async.Future<RevisionResponse> createRevision(
          $pb.ClientContext? ctx, CreateRevisionRequest request) =>
      _client.invoke<RevisionResponse>(
          ctx, 'KumihoService', 'CreateRevision', request, RevisionResponse());
  $async.Future<RevisionResponse> getRevision(
          $pb.ClientContext? ctx, KrefRequest request) =>
      _client.invoke<RevisionResponse>(
          ctx, 'KumihoService', 'GetRevision', request, RevisionResponse());
  $async.Future<GetRevisionsResponse> getRevisions(
          $pb.ClientContext? ctx, GetRevisionsRequest request) =>
      _client.invoke<GetRevisionsResponse>(ctx, 'KumihoService', 'GetRevisions',
          request, GetRevisionsResponse());
  $async.Future<StatusResponse> deleteRevision(
          $pb.ClientContext? ctx, DeleteRevisionRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteRevision', request, StatusResponse());
  $async.Future<PeekNextRevisionResponse> peekNextRevision(
          $pb.ClientContext? ctx, PeekNextRevisionRequest request) =>
      _client.invoke<PeekNextRevisionResponse>(ctx, 'KumihoService',
          'PeekNextRevision', request, PeekNextRevisionResponse());
  $async.Future<RevisionResponse> updateRevisionMetadata(
          $pb.ClientContext? ctx, UpdateMetadataRequest request) =>
      _client.invoke<RevisionResponse>(ctx, 'KumihoService',
          'UpdateRevisionMetadata', request, RevisionResponse());
  $async.Future<StatusResponse> tagRevision(
          $pb.ClientContext? ctx, TagRevisionRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'TagRevision', request, StatusResponse());
  $async.Future<StatusResponse> unTagRevision(
          $pb.ClientContext? ctx, UnTagRevisionRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'UnTagRevision', request, StatusResponse());
  $async.Future<HasTagResponse> hasTag(
          $pb.ClientContext? ctx, HasTagRequest request) =>
      _client.invoke<HasTagResponse>(
          ctx, 'KumihoService', 'HasTag', request, HasTagResponse());
  $async.Future<WasTaggedResponse> wasTagged(
          $pb.ClientContext? ctx, WasTaggedRequest request) =>
      _client.invoke<WasTaggedResponse>(
          ctx, 'KumihoService', 'WasTagged', request, WasTaggedResponse());
  $async.Future<StatusResponse> setDefaultArtifact(
          $pb.ClientContext? ctx, SetDefaultArtifactRequest request) =>
      _client.invoke<StatusResponse>(ctx, 'KumihoService', 'SetDefaultArtifact',
          request, StatusResponse());

  /// Artifact methods
  $async.Future<ArtifactResponse> createArtifact(
          $pb.ClientContext? ctx, CreateArtifactRequest request) =>
      _client.invoke<ArtifactResponse>(
          ctx, 'KumihoService', 'CreateArtifact', request, ArtifactResponse());
  $async.Future<ArtifactResponse> getArtifact(
          $pb.ClientContext? ctx, GetArtifactRequest request) =>
      _client.invoke<ArtifactResponse>(
          ctx, 'KumihoService', 'GetArtifact', request, ArtifactResponse());
  $async.Future<GetArtifactsResponse> getArtifacts(
          $pb.ClientContext? ctx, GetArtifactsRequest request) =>
      _client.invoke<GetArtifactsResponse>(ctx, 'KumihoService', 'GetArtifacts',
          request, GetArtifactsResponse());
  $async.Future<GetArtifactsByLocationResponse> getArtifactsByLocation(
          $pb.ClientContext? ctx, GetArtifactsByLocationRequest request) =>
      _client.invoke<GetArtifactsByLocationResponse>(ctx, 'KumihoService',
          'GetArtifactsByLocation', request, GetArtifactsByLocationResponse());
  $async.Future<StatusResponse> deleteArtifact(
          $pb.ClientContext? ctx, DeleteArtifactRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteArtifact', request, StatusResponse());
  $async.Future<ArtifactResponse> updateArtifactMetadata(
          $pb.ClientContext? ctx, UpdateMetadataRequest request) =>
      _client.invoke<ArtifactResponse>(ctx, 'KumihoService',
          'UpdateArtifactMetadata', request, ArtifactResponse());

  /// Attribute methods (granular metadata operations)
  /// These work on any entity type (Revision, Item, Artifact, Space) identified by kref
  $async.Future<StatusResponse> setAttribute(
          $pb.ClientContext? ctx, SetAttributeRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'SetAttribute', request, StatusResponse());
  $async.Future<GetAttributeResponse> getAttribute(
          $pb.ClientContext? ctx, GetAttributeRequest request) =>
      _client.invoke<GetAttributeResponse>(ctx, 'KumihoService', 'GetAttribute',
          request, GetAttributeResponse());
  $async.Future<StatusResponse> deleteAttribute(
          $pb.ClientContext? ctx, DeleteAttributeRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteAttribute', request, StatusResponse());

  /// Edge methods
  $async.Future<StatusResponse> createEdge(
          $pb.ClientContext? ctx, CreateEdgeRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'CreateEdge', request, StatusResponse());
  $async.Future<GetEdgesResponse> getEdges(
          $pb.ClientContext? ctx, GetEdgesRequest request) =>
      _client.invoke<GetEdgesResponse>(
          ctx, 'KumihoService', 'GetEdges', request, GetEdgesResponse());
  $async.Future<StatusResponse> deleteEdge(
          $pb.ClientContext? ctx, DeleteEdgeRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'DeleteEdge', request, StatusResponse());

  /// Graph Traversal methods
  $async.Future<TraverseEdgesResponse> traverseEdges(
          $pb.ClientContext? ctx, TraverseEdgesRequest request) =>
      _client.invoke<TraverseEdgesResponse>(ctx, 'KumihoService',
          'TraverseEdges', request, TraverseEdgesResponse());
  $async.Future<ShortestPathResponse> findShortestPath(
          $pb.ClientContext? ctx, ShortestPathRequest request) =>
      _client.invoke<ShortestPathResponse>(ctx, 'KumihoService',
          'FindShortestPath', request, ShortestPathResponse());
  $async.Future<ImpactAnalysisResponse> analyzeImpact(
          $pb.ClientContext? ctx, ImpactAnalysisRequest request) =>
      _client.invoke<ImpactAnalysisResponse>(ctx, 'KumihoService',
          'AnalyzeImpact', request, ImpactAnalysisResponse());

  /// Bundle methods
  $async.Future<ItemResponse> createBundle(
          $pb.ClientContext? ctx, CreateBundleRequest request) =>
      _client.invoke<ItemResponse>(
          ctx, 'KumihoService', 'CreateBundle', request, ItemResponse());
  $async.Future<AddBundleMemberResponse> addBundleMember(
          $pb.ClientContext? ctx, AddBundleMemberRequest request) =>
      _client.invoke<AddBundleMemberResponse>(ctx, 'KumihoService',
          'AddBundleMember', request, AddBundleMemberResponse());
  $async.Future<RemoveBundleMemberResponse> removeBundleMember(
          $pb.ClientContext? ctx, RemoveBundleMemberRequest request) =>
      _client.invoke<RemoveBundleMemberResponse>(ctx, 'KumihoService',
          'RemoveBundleMember', request, RemoveBundleMemberResponse());
  $async.Future<GetBundleMembersResponse> getBundleMembers(
          $pb.ClientContext? ctx, GetBundleMembersRequest request) =>
      _client.invoke<GetBundleMembersResponse>(ctx, 'KumihoService',
          'GetBundleMembers', request, GetBundleMembersResponse());
  $async.Future<GetBundleHistoryResponse> getBundleHistory(
          $pb.ClientContext? ctx, GetBundleHistoryRequest request) =>
      _client.invoke<GetBundleHistoryResponse>(ctx, 'KumihoService',
          'GetBundleHistory', request, GetBundleHistoryResponse());

  /// Tenant methods
  $async.Future<TenantUsageResponse> getTenantUsage(
          $pb.ClientContext? ctx, GetTenantUsageRequest request) =>
      _client.invoke<TenantUsageResponse>(ctx, 'KumihoService',
          'GetTenantUsage', request, TenantUsageResponse());

  /// Event Streaming
  $async.Future<Event> eventStream(
          $pb.ClientContext? ctx, EventStreamRequest request) =>
      _client.invoke<Event>(
          ctx, 'KumihoService', 'EventStream', request, Event());

  /// Get event streaming capabilities for the authenticated tenant's tier
  $async.Future<EventCapabilities> getEventCapabilities(
          $pb.ClientContext? ctx, GetEventCapabilitiesRequest request) =>
      _client.invoke<EventCapabilities>(ctx, 'KumihoService',
          'GetEventCapabilities', request, EventCapabilities());

  /// Deprecation methods
  $async.Future<StatusResponse> setDeprecated(
          $pb.ClientContext? ctx, SetDeprecatedRequest request) =>
      _client.invoke<StatusResponse>(
          ctx, 'KumihoService', 'SetDeprecated', request, StatusResponse());
}

const $core.bool _omitFieldNames =
    $core.bool.fromEnvironment('protobuf.omit_field_names');
const $core.bool _omitMessageNames =
    $core.bool.fromEnvironment('protobuf.omit_message_names');
