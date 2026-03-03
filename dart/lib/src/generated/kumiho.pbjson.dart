// This is a generated file - do not edit.
//
// Generated from kumiho.proto.

// @dart = 3.3

// ignore_for_file: annotate_overrides, camel_case_types, comment_references
// ignore_for_file: constant_identifier_names
// ignore_for_file: curly_braces_in_flow_control_structures
// ignore_for_file: deprecated_member_use_from_same_package, library_prefixes
// ignore_for_file: non_constant_identifier_names, prefer_relative_imports
// ignore_for_file: unused_import

import 'dart:convert' as $convert;
import 'dart:core' as $core;
import 'dart:typed_data' as $typed_data;

@$core.Deprecated('Use edgeDirectionDescriptor instead')
const EdgeDirection$json = {
  '1': 'EdgeDirection',
  '2': [
    {'1': 'OUTGOING', '2': 0},
    {'1': 'INCOMING', '2': 1},
    {'1': 'BOTH', '2': 2},
  ],
};

/// Descriptor for `EdgeDirection`. Decode as a `google.protobuf.EnumDescriptorProto`.
final $typed_data.Uint8List edgeDirectionDescriptor = $convert.base64Decode(
    'Cg1FZGdlRGlyZWN0aW9uEgwKCE9VVEdPSU5HEAASDAoISU5DT01JTkcQARIICgRCT1RIEAI=');

@$core.Deprecated('Use krefDescriptor instead')
const Kref$json = {
  '1': 'Kref',
  '2': [
    {'1': 'uri', '3': 1, '4': 1, '5': 9, '10': 'uri'},
  ],
};

/// Descriptor for `Kref`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List krefDescriptor =
    $convert.base64Decode('CgRLcmVmEhAKA3VyaRgBIAEoCVIDdXJp');

@$core.Deprecated('Use edgeDescriptor instead')
const Edge$json = {
  '1': 'Edge',
  '2': [
    {
      '1': 'source_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'sourceKref'
    },
    {
      '1': 'target_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'targetKref'
    },
    {'1': 'edge_type', '3': 3, '4': 1, '5': 9, '10': 'edgeType'},
    {
      '1': 'metadata',
      '3': 4,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Edge.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'created_at', '3': 5, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'author', '3': 6, '4': 1, '5': 9, '10': 'author'},
    {'1': 'username', '3': 7, '4': 1, '5': 9, '10': 'username'},
  ],
  '3': [Edge_MetadataEntry$json],
};

@$core.Deprecated('Use edgeDescriptor instead')
const Edge_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `Edge`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List edgeDescriptor = $convert.base64Decode(
    'CgRFZGdlEi0KC3NvdXJjZV9rcmVmGAEgASgLMgwua3VtaWhvLktyZWZSCnNvdXJjZUtyZWYSLQ'
    'oLdGFyZ2V0X2tyZWYYAiABKAsyDC5rdW1paG8uS3JlZlIKdGFyZ2V0S3JlZhIbCgllZGdlX3R5'
    'cGUYAyABKAlSCGVkZ2VUeXBlEjYKCG1ldGFkYXRhGAQgAygLMhoua3VtaWhvLkVkZ2UuTWV0YW'
    'RhdGFFbnRyeVIIbWV0YWRhdGESHQoKY3JlYXRlZF9hdBgFIAEoCVIJY3JlYXRlZEF0EhYKBmF1'
    'dGhvchgGIAEoCVIGYXV0aG9yEhoKCHVzZXJuYW1lGAcgASgJUgh1c2VybmFtZRo7Cg1NZXRhZG'
    'F0YUVudHJ5EhAKA2tleRgBIAEoCVIDa2V5EhQKBXZhbHVlGAIgASgJUgV2YWx1ZToCOAE=');

@$core.Deprecated('Use statusResponseDescriptor instead')
const StatusResponse$json = {
  '1': 'StatusResponse',
  '2': [
    {'1': 'success', '3': 1, '4': 1, '5': 8, '10': 'success'},
    {'1': 'message', '3': 2, '4': 1, '5': 9, '10': 'message'},
  ],
};

/// Descriptor for `StatusResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List statusResponseDescriptor = $convert.base64Decode(
    'Cg5TdGF0dXNSZXNwb25zZRIYCgdzdWNjZXNzGAEgASgIUgdzdWNjZXNzEhgKB21lc3NhZ2UYAi'
    'ABKAlSB21lc3NhZ2U=');

@$core.Deprecated('Use paginationRequestDescriptor instead')
const PaginationRequest$json = {
  '1': 'PaginationRequest',
  '2': [
    {'1': 'page_size', '3': 1, '4': 1, '5': 5, '10': 'pageSize'},
    {'1': 'cursor', '3': 2, '4': 1, '5': 9, '10': 'cursor'},
  ],
};

/// Descriptor for `PaginationRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List paginationRequestDescriptor = $convert.base64Decode(
    'ChFQYWdpbmF0aW9uUmVxdWVzdBIbCglwYWdlX3NpemUYASABKAVSCHBhZ2VTaXplEhYKBmN1cn'
    'NvchgCIAEoCVIGY3Vyc29y');

@$core.Deprecated('Use paginationResponseDescriptor instead')
const PaginationResponse$json = {
  '1': 'PaginationResponse',
  '2': [
    {'1': 'next_cursor', '3': 1, '4': 1, '5': 9, '10': 'nextCursor'},
    {'1': 'has_more', '3': 2, '4': 1, '5': 8, '10': 'hasMore'},
    {'1': 'total_count', '3': 3, '4': 1, '5': 5, '10': 'totalCount'},
  ],
};

/// Descriptor for `PaginationResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List paginationResponseDescriptor = $convert.base64Decode(
    'ChJQYWdpbmF0aW9uUmVzcG9uc2USHwoLbmV4dF9jdXJzb3IYASABKAlSCm5leHRDdXJzb3ISGQ'
    'oIaGFzX21vcmUYAiABKAhSB2hhc01vcmUSHwoLdG90YWxfY291bnQYAyABKAVSCnRvdGFsQ291'
    'bnQ=');

@$core.Deprecated('Use krefRequestDescriptor instead')
const KrefRequest$json = {
  '1': 'KrefRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
  ],
};

/// Descriptor for `KrefRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List krefRequestDescriptor = $convert.base64Decode(
    'CgtLcmVmUmVxdWVzdBIgCgRrcmVmGAEgASgLMgwua3VtaWhvLktyZWZSBGtyZWY=');

@$core.Deprecated('Use resolveKrefRequestDescriptor instead')
const ResolveKrefRequest$json = {
  '1': 'ResolveKrefRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 9, '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '9': 0, '10': 'tag', '17': true},
    {'1': 'time', '3': 3, '4': 1, '5': 9, '9': 1, '10': 'time', '17': true},
  ],
  '8': [
    {'1': '_tag'},
    {'1': '_time'},
  ],
};

/// Descriptor for `ResolveKrefRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List resolveKrefRequestDescriptor = $convert.base64Decode(
    'ChJSZXNvbHZlS3JlZlJlcXVlc3QSEgoEa3JlZhgBIAEoCVIEa3JlZhIVCgN0YWcYAiABKAlIAF'
    'IDdGFniAEBEhcKBHRpbWUYAyABKAlIAVIEdGltZYgBAUIGCgRfdGFnQgcKBV90aW1l');

@$core.Deprecated('Use resolveLocationRequestDescriptor instead')
const ResolveLocationRequest$json = {
  '1': 'ResolveLocationRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 9, '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '9': 0, '10': 'tag', '17': true},
    {'1': 'time', '3': 3, '4': 1, '5': 9, '9': 1, '10': 'time', '17': true},
  ],
  '8': [
    {'1': '_tag'},
    {'1': '_time'},
  ],
};

/// Descriptor for `ResolveLocationRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List resolveLocationRequestDescriptor = $convert.base64Decode(
    'ChZSZXNvbHZlTG9jYXRpb25SZXF1ZXN0EhIKBGtyZWYYASABKAlSBGtyZWYSFQoDdGFnGAIgAS'
    'gJSABSA3RhZ4gBARIXCgR0aW1lGAMgASgJSAFSBHRpbWWIAQFCBgoEX3RhZ0IHCgVfdGltZQ==');

@$core.Deprecated('Use resolveLocationResponseDescriptor instead')
const ResolveLocationResponse$json = {
  '1': 'ResolveLocationResponse',
  '2': [
    {'1': 'location', '3': 1, '4': 1, '5': 9, '10': 'location'},
    {
      '1': 'resolved_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'resolvedKref'
    },
    {'1': 'artifact_name', '3': 3, '4': 1, '5': 9, '10': 'artifactName'},
  ],
};

/// Descriptor for `ResolveLocationResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List resolveLocationResponseDescriptor = $convert.base64Decode(
    'ChdSZXNvbHZlTG9jYXRpb25SZXNwb25zZRIaCghsb2NhdGlvbhgBIAEoCVIIbG9jYXRpb24SMQ'
    'oNcmVzb2x2ZWRfa3JlZhgCIAEoCzIMLmt1bWloby5LcmVmUgxyZXNvbHZlZEtyZWYSIwoNYXJ0'
    'aWZhY3RfbmFtZRgDIAEoCVIMYXJ0aWZhY3ROYW1l');

@$core.Deprecated('Use createSpaceRequestDescriptor instead')
const CreateSpaceRequest$json = {
  '1': 'CreateSpaceRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'space_name', '3': 2, '4': 1, '5': 9, '10': 'spaceName'},
    {'1': 'exists_error', '3': 3, '4': 1, '5': 8, '10': 'existsError'},
  ],
};

/// Descriptor for `CreateSpaceRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createSpaceRequestDescriptor = $convert.base64Decode(
    'ChJDcmVhdGVTcGFjZVJlcXVlc3QSHwoLcGFyZW50X3BhdGgYASABKAlSCnBhcmVudFBhdGgSHQ'
    'oKc3BhY2VfbmFtZRgCIAEoCVIJc3BhY2VOYW1lEiEKDGV4aXN0c19lcnJvchgDIAEoCFILZXhp'
    'c3RzRXJyb3I=');

@$core.Deprecated('Use spaceResponseDescriptor instead')
const SpaceResponse$json = {
  '1': 'SpaceResponse',
  '2': [
    {'1': 'path', '3': 1, '4': 1, '5': 9, '10': 'path'},
    {'1': 'created_at', '3': 2, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'modified_at', '3': 3, '4': 1, '5': 9, '10': 'modifiedAt'},
    {'1': 'author', '3': 4, '4': 1, '5': 9, '10': 'author'},
    {
      '1': 'metadata',
      '3': 5,
      '4': 3,
      '5': 11,
      '6': '.kumiho.SpaceResponse.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'username', '3': 6, '4': 1, '5': 9, '10': 'username'},
    {'1': 'name', '3': 7, '4': 1, '5': 9, '10': 'name'},
    {'1': 'type', '3': 8, '4': 1, '5': 9, '10': 'type'},
  ],
  '3': [SpaceResponse_MetadataEntry$json],
};

@$core.Deprecated('Use spaceResponseDescriptor instead')
const SpaceResponse_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `SpaceResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List spaceResponseDescriptor = $convert.base64Decode(
    'Cg1TcGFjZVJlc3BvbnNlEhIKBHBhdGgYASABKAlSBHBhdGgSHQoKY3JlYXRlZF9hdBgCIAEoCV'
    'IJY3JlYXRlZEF0Eh8KC21vZGlmaWVkX2F0GAMgASgJUgptb2RpZmllZEF0EhYKBmF1dGhvchgE'
    'IAEoCVIGYXV0aG9yEj8KCG1ldGFkYXRhGAUgAygLMiMua3VtaWhvLlNwYWNlUmVzcG9uc2UuTW'
    'V0YWRhdGFFbnRyeVIIbWV0YWRhdGESGgoIdXNlcm5hbWUYBiABKAlSCHVzZXJuYW1lEhIKBG5h'
    'bWUYByABKAlSBG5hbWUSEgoEdHlwZRgIIAEoCVIEdHlwZRo7Cg1NZXRhZGF0YUVudHJ5EhAKA2'
    'tleRgBIAEoCVIDa2V5EhQKBXZhbHVlGAIgASgJUgV2YWx1ZToCOAE=');

@$core.Deprecated('Use getSpaceRequestDescriptor instead')
const GetSpaceRequest$json = {
  '1': 'GetSpaceRequest',
  '2': [
    {'1': 'path_or_kref', '3': 1, '4': 1, '5': 9, '10': 'pathOrKref'},
  ],
};

/// Descriptor for `GetSpaceRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getSpaceRequestDescriptor = $convert.base64Decode(
    'Cg9HZXRTcGFjZVJlcXVlc3QSIAoMcGF0aF9vcl9rcmVmGAEgASgJUgpwYXRoT3JLcmVm');

@$core.Deprecated('Use deleteSpaceRequestDescriptor instead')
const DeleteSpaceRequest$json = {
  '1': 'DeleteSpaceRequest',
  '2': [
    {'1': 'path', '3': 1, '4': 1, '5': 9, '10': 'path'},
    {'1': 'force', '3': 2, '4': 1, '5': 8, '10': 'force'},
  ],
};

/// Descriptor for `DeleteSpaceRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteSpaceRequestDescriptor = $convert.base64Decode(
    'ChJEZWxldGVTcGFjZVJlcXVlc3QSEgoEcGF0aBgBIAEoCVIEcGF0aBIUCgVmb3JjZRgCIAEoCF'
    'IFZm9yY2U=');

@$core.Deprecated('Use getChildSpacesRequestDescriptor instead')
const GetChildSpacesRequest$json = {
  '1': 'GetChildSpacesRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'recursive', '3': 2, '4': 1, '5': 8, '10': 'recursive'},
    {
      '1': 'pagination',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetChildSpacesRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getChildSpacesRequestDescriptor = $convert.base64Decode(
    'ChVHZXRDaGlsZFNwYWNlc1JlcXVlc3QSHwoLcGFyZW50X3BhdGgYASABKAlSCnBhcmVudFBhdG'
    'gSHAoJcmVjdXJzaXZlGAIgASgIUglyZWN1cnNpdmUSPgoKcGFnaW5hdGlvbhgDIAEoCzIZLmt1'
    'bWloby5QYWdpbmF0aW9uUmVxdWVzdEgAUgpwYWdpbmF0aW9uiAEBQg0KC19wYWdpbmF0aW9u');

@$core.Deprecated('Use getChildSpacesResponseDescriptor instead')
const GetChildSpacesResponse$json = {
  '1': 'GetChildSpacesResponse',
  '2': [
    {
      '1': 'spaces',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.SpaceResponse',
      '10': 'spaces'
    },
    {
      '1': 'pagination',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationResponse',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetChildSpacesResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getChildSpacesResponseDescriptor = $convert.base64Decode(
    'ChZHZXRDaGlsZFNwYWNlc1Jlc3BvbnNlEi0KBnNwYWNlcxgBIAMoCzIVLmt1bWloby5TcGFjZV'
    'Jlc3BvbnNlUgZzcGFjZXMSPwoKcGFnaW5hdGlvbhgCIAEoCzIaLmt1bWloby5QYWdpbmF0aW9u'
    'UmVzcG9uc2VIAFIKcGFnaW5hdGlvbogBAUINCgtfcGFnaW5hdGlvbg==');

@$core.Deprecated('Use createItemRequestDescriptor instead')
const CreateItemRequest$json = {
  '1': 'CreateItemRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'item_name', '3': 2, '4': 1, '5': 9, '10': 'itemName'},
    {'1': 'kind', '3': 3, '4': 1, '5': 9, '10': 'kind'},
    {'1': 'exists_error', '3': 4, '4': 1, '5': 8, '10': 'existsError'},
  ],
};

/// Descriptor for `CreateItemRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createItemRequestDescriptor = $convert.base64Decode(
    'ChFDcmVhdGVJdGVtUmVxdWVzdBIfCgtwYXJlbnRfcGF0aBgBIAEoCVIKcGFyZW50UGF0aBIbCg'
    'lpdGVtX25hbWUYAiABKAlSCGl0ZW1OYW1lEhIKBGtpbmQYAyABKAlSBGtpbmQSIQoMZXhpc3Rz'
    'X2Vycm9yGAQgASgIUgtleGlzdHNFcnJvcg==');

@$core.Deprecated('Use getItemRequestDescriptor instead')
const GetItemRequest$json = {
  '1': 'GetItemRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'item_name', '3': 2, '4': 1, '5': 9, '10': 'itemName'},
    {'1': 'kind', '3': 3, '4': 1, '5': 9, '10': 'kind'},
  ],
};

/// Descriptor for `GetItemRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getItemRequestDescriptor = $convert.base64Decode(
    'Cg5HZXRJdGVtUmVxdWVzdBIfCgtwYXJlbnRfcGF0aBgBIAEoCVIKcGFyZW50UGF0aBIbCglpdG'
    'VtX25hbWUYAiABKAlSCGl0ZW1OYW1lEhIKBGtpbmQYAyABKAlSBGtpbmQ=');

@$core.Deprecated('Use itemResponseDescriptor instead')
const ItemResponse$json = {
  '1': 'ItemResponse',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'name', '3': 2, '4': 1, '5': 9, '10': 'name'},
    {'1': 'item_name', '3': 3, '4': 1, '5': 9, '10': 'itemName'},
    {'1': 'kind', '3': 4, '4': 1, '5': 9, '10': 'kind'},
    {'1': 'created_at', '3': 5, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'modified_at', '3': 6, '4': 1, '5': 9, '10': 'modifiedAt'},
    {'1': 'author', '3': 7, '4': 1, '5': 9, '10': 'author'},
    {
      '1': 'metadata',
      '3': 8,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ItemResponse.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'deprecated', '3': 9, '4': 1, '5': 8, '10': 'deprecated'},
    {'1': 'username', '3': 10, '4': 1, '5': 9, '10': 'username'},
  ],
  '3': [ItemResponse_MetadataEntry$json],
};

@$core.Deprecated('Use itemResponseDescriptor instead')
const ItemResponse_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `ItemResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List itemResponseDescriptor = $convert.base64Decode(
    'CgxJdGVtUmVzcG9uc2USIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcmVmEhIKBG5hbW'
    'UYAiABKAlSBG5hbWUSGwoJaXRlbV9uYW1lGAMgASgJUghpdGVtTmFtZRISCgRraW5kGAQgASgJ'
    'UgRraW5kEh0KCmNyZWF0ZWRfYXQYBSABKAlSCWNyZWF0ZWRBdBIfCgttb2RpZmllZF9hdBgGIA'
    'EoCVIKbW9kaWZpZWRBdBIWCgZhdXRob3IYByABKAlSBmF1dGhvchI+CghtZXRhZGF0YRgIIAMo'
    'CzIiLmt1bWloby5JdGVtUmVzcG9uc2UuTWV0YWRhdGFFbnRyeVIIbWV0YWRhdGESHgoKZGVwcm'
    'VjYXRlZBgJIAEoCFIKZGVwcmVjYXRlZBIaCgh1c2VybmFtZRgKIAEoCVIIdXNlcm5hbWUaOwoN'
    'TWV0YWRhdGFFbnRyeRIQCgNrZXkYASABKAlSA2tleRIUCgV2YWx1ZRgCIAEoCVIFdmFsdWU6Aj'
    'gB');

@$core.Deprecated('Use deleteItemRequestDescriptor instead')
const DeleteItemRequest$json = {
  '1': 'DeleteItemRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'force', '3': 2, '4': 1, '5': 8, '10': 'force'},
  ],
};

/// Descriptor for `DeleteItemRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteItemRequestDescriptor = $convert.base64Decode(
    'ChFEZWxldGVJdGVtUmVxdWVzdBIgCgRrcmVmGAEgASgLMgwua3VtaWhvLktyZWZSBGtyZWYSFA'
    'oFZm9yY2UYAiABKAhSBWZvcmNl');

@$core.Deprecated('Use getItemsRequestDescriptor instead')
const GetItemsRequest$json = {
  '1': 'GetItemsRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'item_name_filter', '3': 2, '4': 1, '5': 9, '10': 'itemNameFilter'},
    {'1': 'kind_filter', '3': 3, '4': 1, '5': 9, '10': 'kindFilter'},
    {
      '1': 'pagination',
      '3': 4,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
    {
      '1': 'include_deprecated',
      '3': 5,
      '4': 1,
      '5': 8,
      '10': 'includeDeprecated'
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetItemsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getItemsRequestDescriptor = $convert.base64Decode(
    'Cg9HZXRJdGVtc1JlcXVlc3QSHwoLcGFyZW50X3BhdGgYASABKAlSCnBhcmVudFBhdGgSKAoQaX'
    'RlbV9uYW1lX2ZpbHRlchgCIAEoCVIOaXRlbU5hbWVGaWx0ZXISHwoLa2luZF9maWx0ZXIYAyAB'
    'KAlSCmtpbmRGaWx0ZXISPgoKcGFnaW5hdGlvbhgEIAEoCzIZLmt1bWloby5QYWdpbmF0aW9uUm'
    'VxdWVzdEgAUgpwYWdpbmF0aW9uiAEBEi0KEmluY2x1ZGVfZGVwcmVjYXRlZBgFIAEoCFIRaW5j'
    'bHVkZURlcHJlY2F0ZWRCDQoLX3BhZ2luYXRpb24=');

@$core.Deprecated('Use getItemsResponseDescriptor instead')
const GetItemsResponse$json = {
  '1': 'GetItemsResponse',
  '2': [
    {
      '1': 'items',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ItemResponse',
      '10': 'items'
    },
    {
      '1': 'pagination',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationResponse',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetItemsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getItemsResponseDescriptor = $convert.base64Decode(
    'ChBHZXRJdGVtc1Jlc3BvbnNlEioKBWl0ZW1zGAEgAygLMhQua3VtaWhvLkl0ZW1SZXNwb25zZV'
    'IFaXRlbXMSPwoKcGFnaW5hdGlvbhgCIAEoCzIaLmt1bWloby5QYWdpbmF0aW9uUmVzcG9uc2VI'
    'AFIKcGFnaW5hdGlvbogBAUINCgtfcGFnaW5hdGlvbg==');

@$core.Deprecated('Use itemSearchRequestDescriptor instead')
const ItemSearchRequest$json = {
  '1': 'ItemSearchRequest',
  '2': [
    {'1': 'context_filter', '3': 1, '4': 1, '5': 9, '10': 'contextFilter'},
    {'1': 'item_name_filter', '3': 2, '4': 1, '5': 9, '10': 'itemNameFilter'},
    {'1': 'kind_filter', '3': 3, '4': 1, '5': 9, '10': 'kindFilter'},
    {
      '1': 'pagination',
      '3': 4,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
    {
      '1': 'include_deprecated',
      '3': 5,
      '4': 1,
      '5': 8,
      '10': 'includeDeprecated'
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `ItemSearchRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List itemSearchRequestDescriptor = $convert.base64Decode(
    'ChFJdGVtU2VhcmNoUmVxdWVzdBIlCg5jb250ZXh0X2ZpbHRlchgBIAEoCVINY29udGV4dEZpbH'
    'RlchIoChBpdGVtX25hbWVfZmlsdGVyGAIgASgJUg5pdGVtTmFtZUZpbHRlchIfCgtraW5kX2Zp'
    'bHRlchgDIAEoCVIKa2luZEZpbHRlchI+CgpwYWdpbmF0aW9uGAQgASgLMhkua3VtaWhvLlBhZ2'
    'luYXRpb25SZXF1ZXN0SABSCnBhZ2luYXRpb26IAQESLQoSaW5jbHVkZV9kZXByZWNhdGVkGAUg'
    'ASgIUhFpbmNsdWRlRGVwcmVjYXRlZEINCgtfcGFnaW5hdGlvbg==');

@$core.Deprecated('Use createRevisionRequestDescriptor instead')
const CreateRevisionRequest$json = {
  '1': 'CreateRevisionRequest',
  '2': [
    {
      '1': 'item_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {
      '1': 'metadata',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.CreateRevisionRequest.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'number', '3': 3, '4': 1, '5': 5, '10': 'number'},
    {'1': 'exists_error', '3': 4, '4': 1, '5': 8, '10': 'existsError'},
  ],
  '3': [CreateRevisionRequest_MetadataEntry$json],
};

@$core.Deprecated('Use createRevisionRequestDescriptor instead')
const CreateRevisionRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `CreateRevisionRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createRevisionRequestDescriptor = $convert.base64Decode(
    'ChVDcmVhdGVSZXZpc2lvblJlcXVlc3QSKQoJaXRlbV9rcmVmGAEgASgLMgwua3VtaWhvLktyZW'
    'ZSCGl0ZW1LcmVmEkcKCG1ldGFkYXRhGAIgAygLMisua3VtaWhvLkNyZWF0ZVJldmlzaW9uUmVx'
    'dWVzdC5NZXRhZGF0YUVudHJ5UghtZXRhZGF0YRIWCgZudW1iZXIYAyABKAVSBm51bWJlchIhCg'
    'xleGlzdHNfZXJyb3IYBCABKAhSC2V4aXN0c0Vycm9yGjsKDU1ldGFkYXRhRW50cnkSEAoDa2V5'
    'GAEgASgJUgNrZXkSFAoFdmFsdWUYAiABKAlSBXZhbHVlOgI4AQ==');

@$core.Deprecated('Use revisionResponseDescriptor instead')
const RevisionResponse$json = {
  '1': 'RevisionResponse',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {
      '1': 'item_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {'1': 'number', '3': 3, '4': 1, '5': 5, '10': 'number'},
    {'1': 'tags', '3': 4, '4': 3, '5': 9, '10': 'tags'},
    {
      '1': 'metadata',
      '3': 5,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RevisionResponse.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'created_at', '3': 6, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'modified_at', '3': 7, '4': 1, '5': 9, '10': 'modifiedAt'},
    {'1': 'author', '3': 8, '4': 1, '5': 9, '10': 'author'},
    {'1': 'deprecated', '3': 9, '4': 1, '5': 8, '10': 'deprecated'},
    {'1': 'published', '3': 10, '4': 1, '5': 8, '10': 'published'},
    {'1': 'latest', '3': 11, '4': 1, '5': 8, '10': 'latest'},
    {'1': 'username', '3': 12, '4': 1, '5': 9, '10': 'username'},
    {
      '1': 'default_artifact',
      '3': 13,
      '4': 1,
      '5': 9,
      '9': 0,
      '10': 'defaultArtifact',
      '17': true
    },
    {'1': 'name', '3': 14, '4': 1, '5': 9, '10': 'name'},
  ],
  '3': [RevisionResponse_MetadataEntry$json],
  '8': [
    {'1': '_default_artifact'},
  ],
};

@$core.Deprecated('Use revisionResponseDescriptor instead')
const RevisionResponse_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `RevisionResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List revisionResponseDescriptor = $convert.base64Decode(
    'ChBSZXZpc2lvblJlc3BvbnNlEiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZhIpCg'
    'lpdGVtX2tyZWYYAiABKAsyDC5rdW1paG8uS3JlZlIIaXRlbUtyZWYSFgoGbnVtYmVyGAMgASgF'
    'UgZudW1iZXISEgoEdGFncxgEIAMoCVIEdGFncxJCCghtZXRhZGF0YRgFIAMoCzImLmt1bWloby'
    '5SZXZpc2lvblJlc3BvbnNlLk1ldGFkYXRhRW50cnlSCG1ldGFkYXRhEh0KCmNyZWF0ZWRfYXQY'
    'BiABKAlSCWNyZWF0ZWRBdBIfCgttb2RpZmllZF9hdBgHIAEoCVIKbW9kaWZpZWRBdBIWCgZhdX'
    'Rob3IYCCABKAlSBmF1dGhvchIeCgpkZXByZWNhdGVkGAkgASgIUgpkZXByZWNhdGVkEhwKCXB1'
    'Ymxpc2hlZBgKIAEoCFIJcHVibGlzaGVkEhYKBmxhdGVzdBgLIAEoCFIGbGF0ZXN0EhoKCHVzZX'
    'JuYW1lGAwgASgJUgh1c2VybmFtZRIuChBkZWZhdWx0X2FydGlmYWN0GA0gASgJSABSD2RlZmF1'
    'bHRBcnRpZmFjdIgBARISCgRuYW1lGA4gASgJUgRuYW1lGjsKDU1ldGFkYXRhRW50cnkSEAoDa2'
    'V5GAEgASgJUgNrZXkSFAoFdmFsdWUYAiABKAlSBXZhbHVlOgI4AUITChFfZGVmYXVsdF9hcnRp'
    'ZmFjdA==');

@$core.Deprecated('Use deleteRevisionRequestDescriptor instead')
const DeleteRevisionRequest$json = {
  '1': 'DeleteRevisionRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'force', '3': 2, '4': 1, '5': 8, '10': 'force'},
  ],
};

/// Descriptor for `DeleteRevisionRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteRevisionRequestDescriptor = $convert.base64Decode(
    'ChVEZWxldGVSZXZpc2lvblJlcXVlc3QSIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcm'
    'VmEhQKBWZvcmNlGAIgASgIUgVmb3JjZQ==');

@$core.Deprecated('Use getRevisionsRequestDescriptor instead')
const GetRevisionsRequest$json = {
  '1': 'GetRevisionsRequest',
  '2': [
    {
      '1': 'item_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {
      '1': 'pagination',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetRevisionsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getRevisionsRequestDescriptor = $convert.base64Decode(
    'ChNHZXRSZXZpc2lvbnNSZXF1ZXN0EikKCWl0ZW1fa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUg'
    'hpdGVtS3JlZhI+CgpwYWdpbmF0aW9uGAIgASgLMhkua3VtaWhvLlBhZ2luYXRpb25SZXF1ZXN0'
    'SABSCnBhZ2luYXRpb26IAQFCDQoLX3BhZ2luYXRpb24=');

@$core.Deprecated('Use getRevisionsResponseDescriptor instead')
const GetRevisionsResponse$json = {
  '1': 'GetRevisionsResponse',
  '2': [
    {
      '1': 'revisions',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RevisionResponse',
      '10': 'revisions'
    },
    {
      '1': 'pagination',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationResponse',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetRevisionsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getRevisionsResponseDescriptor = $convert.base64Decode(
    'ChRHZXRSZXZpc2lvbnNSZXNwb25zZRI2CglyZXZpc2lvbnMYASADKAsyGC5rdW1paG8uUmV2aX'
    'Npb25SZXNwb25zZVIJcmV2aXNpb25zEj8KCnBhZ2luYXRpb24YAiABKAsyGi5rdW1paG8uUGFn'
    'aW5hdGlvblJlc3BvbnNlSABSCnBhZ2luYXRpb26IAQFCDQoLX3BhZ2luYXRpb24=');

@$core.Deprecated('Use createArtifactRequestDescriptor instead')
const CreateArtifactRequest$json = {
  '1': 'CreateArtifactRequest',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {'1': 'name', '3': 2, '4': 1, '5': 9, '10': 'name'},
    {'1': 'location', '3': 3, '4': 1, '5': 9, '10': 'location'},
    {'1': 'exists_error', '3': 4, '4': 1, '5': 8, '10': 'existsError'},
    {
      '1': 'metadata',
      '3': 5,
      '4': 3,
      '5': 11,
      '6': '.kumiho.CreateArtifactRequest.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [CreateArtifactRequest_MetadataEntry$json],
};

@$core.Deprecated('Use createArtifactRequestDescriptor instead')
const CreateArtifactRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `CreateArtifactRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createArtifactRequestDescriptor = $convert.base64Decode(
    'ChVDcmVhdGVBcnRpZmFjdFJlcXVlc3QSMQoNcmV2aXNpb25fa3JlZhgBIAEoCzIMLmt1bWloby'
    '5LcmVmUgxyZXZpc2lvbktyZWYSEgoEbmFtZRgCIAEoCVIEbmFtZRIaCghsb2NhdGlvbhgDIAEo'
    'CVIIbG9jYXRpb24SIQoMZXhpc3RzX2Vycm9yGAQgASgIUgtleGlzdHNFcnJvchJHCghtZXRhZG'
    'F0YRgFIAMoCzIrLmt1bWloby5DcmVhdGVBcnRpZmFjdFJlcXVlc3QuTWV0YWRhdGFFbnRyeVII'
    'bWV0YWRhdGEaOwoNTWV0YWRhdGFFbnRyeRIQCgNrZXkYASABKAlSA2tleRIUCgV2YWx1ZRgCIA'
    'EoCVIFdmFsdWU6AjgB');

@$core.Deprecated('Use artifactResponseDescriptor instead')
const ArtifactResponse$json = {
  '1': 'ArtifactResponse',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'location', '3': 2, '4': 1, '5': 9, '10': 'location'},
    {
      '1': 'revision_kref',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {
      '1': 'item_kref',
      '3': 4,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {'1': 'created_at', '3': 5, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'modified_at', '3': 6, '4': 1, '5': 9, '10': 'modifiedAt'},
    {'1': 'author', '3': 7, '4': 1, '5': 9, '10': 'author'},
    {
      '1': 'metadata',
      '3': 8,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ArtifactResponse.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'deprecated', '3': 9, '4': 1, '5': 8, '10': 'deprecated'},
    {'1': 'username', '3': 10, '4': 1, '5': 9, '10': 'username'},
    {'1': 'name', '3': 11, '4': 1, '5': 9, '10': 'name'},
  ],
  '3': [ArtifactResponse_MetadataEntry$json],
};

@$core.Deprecated('Use artifactResponseDescriptor instead')
const ArtifactResponse_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `ArtifactResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List artifactResponseDescriptor = $convert.base64Decode(
    'ChBBcnRpZmFjdFJlc3BvbnNlEiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZhIaCg'
    'hsb2NhdGlvbhgCIAEoCVIIbG9jYXRpb24SMQoNcmV2aXNpb25fa3JlZhgDIAEoCzIMLmt1bWlo'
    'by5LcmVmUgxyZXZpc2lvbktyZWYSKQoJaXRlbV9rcmVmGAQgASgLMgwua3VtaWhvLktyZWZSCG'
    'l0ZW1LcmVmEh0KCmNyZWF0ZWRfYXQYBSABKAlSCWNyZWF0ZWRBdBIfCgttb2RpZmllZF9hdBgG'
    'IAEoCVIKbW9kaWZpZWRBdBIWCgZhdXRob3IYByABKAlSBmF1dGhvchJCCghtZXRhZGF0YRgIIA'
    'MoCzImLmt1bWloby5BcnRpZmFjdFJlc3BvbnNlLk1ldGFkYXRhRW50cnlSCG1ldGFkYXRhEh4K'
    'CmRlcHJlY2F0ZWQYCSABKAhSCmRlcHJlY2F0ZWQSGgoIdXNlcm5hbWUYCiABKAlSCHVzZXJuYW'
    '1lEhIKBG5hbWUYCyABKAlSBG5hbWUaOwoNTWV0YWRhdGFFbnRyeRIQCgNrZXkYASABKAlSA2tl'
    'eRIUCgV2YWx1ZRgCIAEoCVIFdmFsdWU6AjgB');

@$core.Deprecated('Use getArtifactRequestDescriptor instead')
const GetArtifactRequest$json = {
  '1': 'GetArtifactRequest',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {'1': 'name', '3': 2, '4': 1, '5': 9, '10': 'name'},
  ],
};

/// Descriptor for `GetArtifactRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getArtifactRequestDescriptor = $convert.base64Decode(
    'ChJHZXRBcnRpZmFjdFJlcXVlc3QSMQoNcmV2aXNpb25fa3JlZhgBIAEoCzIMLmt1bWloby5Lcm'
    'VmUgxyZXZpc2lvbktyZWYSEgoEbmFtZRgCIAEoCVIEbmFtZQ==');

@$core.Deprecated('Use getArtifactsRequestDescriptor instead')
const GetArtifactsRequest$json = {
  '1': 'GetArtifactsRequest',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
  ],
};

/// Descriptor for `GetArtifactsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getArtifactsRequestDescriptor = $convert.base64Decode(
    'ChNHZXRBcnRpZmFjdHNSZXF1ZXN0EjEKDXJldmlzaW9uX2tyZWYYASABKAsyDC5rdW1paG8uS3'
    'JlZlIMcmV2aXNpb25LcmVm');

@$core.Deprecated('Use getArtifactsResponseDescriptor instead')
const GetArtifactsResponse$json = {
  '1': 'GetArtifactsResponse',
  '2': [
    {
      '1': 'artifacts',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ArtifactResponse',
      '10': 'artifacts'
    },
  ],
};

/// Descriptor for `GetArtifactsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getArtifactsResponseDescriptor = $convert.base64Decode(
    'ChRHZXRBcnRpZmFjdHNSZXNwb25zZRI2CglhcnRpZmFjdHMYASADKAsyGC5rdW1paG8uQXJ0aW'
    'ZhY3RSZXNwb25zZVIJYXJ0aWZhY3Rz');

@$core.Deprecated('Use deleteArtifactRequestDescriptor instead')
const DeleteArtifactRequest$json = {
  '1': 'DeleteArtifactRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'force', '3': 2, '4': 1, '5': 8, '10': 'force'},
  ],
};

/// Descriptor for `DeleteArtifactRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteArtifactRequestDescriptor = $convert.base64Decode(
    'ChVEZWxldGVBcnRpZmFjdFJlcXVlc3QSIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcm'
    'VmEhQKBWZvcmNlGAIgASgIUgVmb3JjZQ==');

@$core.Deprecated('Use getArtifactsByLocationRequestDescriptor instead')
const GetArtifactsByLocationRequest$json = {
  '1': 'GetArtifactsByLocationRequest',
  '2': [
    {'1': 'location', '3': 1, '4': 1, '5': 9, '10': 'location'},
  ],
};

/// Descriptor for `GetArtifactsByLocationRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getArtifactsByLocationRequestDescriptor =
    $convert.base64Decode(
        'Ch1HZXRBcnRpZmFjdHNCeUxvY2F0aW9uUmVxdWVzdBIaCghsb2NhdGlvbhgBIAEoCVIIbG9jYX'
        'Rpb24=');

@$core.Deprecated('Use getArtifactsByLocationResponseDescriptor instead')
const GetArtifactsByLocationResponse$json = {
  '1': 'GetArtifactsByLocationResponse',
  '2': [
    {
      '1': 'artifacts',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ArtifactResponse',
      '10': 'artifacts'
    },
  ],
};

/// Descriptor for `GetArtifactsByLocationResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getArtifactsByLocationResponseDescriptor =
    $convert.base64Decode(
        'Ch5HZXRBcnRpZmFjdHNCeUxvY2F0aW9uUmVzcG9uc2USNgoJYXJ0aWZhY3RzGAEgAygLMhgua3'
        'VtaWhvLkFydGlmYWN0UmVzcG9uc2VSCWFydGlmYWN0cw==');

@$core.Deprecated('Use tagRevisionRequestDescriptor instead')
const TagRevisionRequest$json = {
  '1': 'TagRevisionRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '10': 'tag'},
  ],
};

/// Descriptor for `TagRevisionRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List tagRevisionRequestDescriptor = $convert.base64Decode(
    'ChJUYWdSZXZpc2lvblJlcXVlc3QSIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcmVmEh'
    'AKA3RhZxgCIAEoCVIDdGFn');

@$core.Deprecated('Use unTagRevisionRequestDescriptor instead')
const UnTagRevisionRequest$json = {
  '1': 'UnTagRevisionRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '10': 'tag'},
  ],
};

/// Descriptor for `UnTagRevisionRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List unTagRevisionRequestDescriptor = $convert.base64Decode(
    'ChRVblRhZ1JldmlzaW9uUmVxdWVzdBIgCgRrcmVmGAEgASgLMgwua3VtaWhvLktyZWZSBGtyZW'
    'YSEAoDdGFnGAIgASgJUgN0YWc=');

@$core.Deprecated('Use hasTagRequestDescriptor instead')
const HasTagRequest$json = {
  '1': 'HasTagRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '10': 'tag'},
  ],
};

/// Descriptor for `HasTagRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List hasTagRequestDescriptor = $convert.base64Decode(
    'Cg1IYXNUYWdSZXF1ZXN0EiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZhIQCgN0YW'
    'cYAiABKAlSA3RhZw==');

@$core.Deprecated('Use hasTagResponseDescriptor instead')
const HasTagResponse$json = {
  '1': 'HasTagResponse',
  '2': [
    {'1': 'has_tag', '3': 1, '4': 1, '5': 8, '10': 'hasTag'},
  ],
};

/// Descriptor for `HasTagResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List hasTagResponseDescriptor = $convert
    .base64Decode('Cg5IYXNUYWdSZXNwb25zZRIXCgdoYXNfdGFnGAEgASgIUgZoYXNUYWc=');

@$core.Deprecated('Use wasTaggedRequestDescriptor instead')
const WasTaggedRequest$json = {
  '1': 'WasTaggedRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'tag', '3': 2, '4': 1, '5': 9, '10': 'tag'},
  ],
};

/// Descriptor for `WasTaggedRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List wasTaggedRequestDescriptor = $convert.base64Decode(
    'ChBXYXNUYWdnZWRSZXF1ZXN0EiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZhIQCg'
    'N0YWcYAiABKAlSA3RhZw==');

@$core.Deprecated('Use wasTaggedResponseDescriptor instead')
const WasTaggedResponse$json = {
  '1': 'WasTaggedResponse',
  '2': [
    {'1': 'was_tagged', '3': 1, '4': 1, '5': 8, '10': 'wasTagged'},
  ],
};

/// Descriptor for `WasTaggedResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List wasTaggedResponseDescriptor = $convert.base64Decode(
    'ChFXYXNUYWdnZWRSZXNwb25zZRIdCgp3YXNfdGFnZ2VkGAEgASgIUgl3YXNUYWdnZWQ=');

@$core.Deprecated('Use setDefaultArtifactRequestDescriptor instead')
const SetDefaultArtifactRequest$json = {
  '1': 'SetDefaultArtifactRequest',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {'1': 'artifact_name', '3': 2, '4': 1, '5': 9, '10': 'artifactName'},
  ],
};

/// Descriptor for `SetDefaultArtifactRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List setDefaultArtifactRequestDescriptor = $convert.base64Decode(
    'ChlTZXREZWZhdWx0QXJ0aWZhY3RSZXF1ZXN0EjEKDXJldmlzaW9uX2tyZWYYASABKAsyDC5rdW'
    '1paG8uS3JlZlIMcmV2aXNpb25LcmVmEiMKDWFydGlmYWN0X25hbWUYAiABKAlSDGFydGlmYWN0'
    'TmFtZQ==');

@$core.Deprecated('Use createEdgeRequestDescriptor instead')
const CreateEdgeRequest$json = {
  '1': 'CreateEdgeRequest',
  '2': [
    {
      '1': 'source_revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'sourceRevisionKref'
    },
    {
      '1': 'target_revision_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'targetRevisionKref'
    },
    {'1': 'edge_type', '3': 3, '4': 1, '5': 9, '10': 'edgeType'},
    {
      '1': 'metadata',
      '3': 4,
      '4': 3,
      '5': 11,
      '6': '.kumiho.CreateEdgeRequest.MetadataEntry',
      '10': 'metadata'
    },
    {'1': 'exists_error', '3': 5, '4': 1, '5': 8, '10': 'existsError'},
  ],
  '3': [CreateEdgeRequest_MetadataEntry$json],
};

@$core.Deprecated('Use createEdgeRequestDescriptor instead')
const CreateEdgeRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `CreateEdgeRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createEdgeRequestDescriptor = $convert.base64Decode(
    'ChFDcmVhdGVFZGdlUmVxdWVzdBI+ChRzb3VyY2VfcmV2aXNpb25fa3JlZhgBIAEoCzIMLmt1bW'
    'loby5LcmVmUhJzb3VyY2VSZXZpc2lvbktyZWYSPgoUdGFyZ2V0X3JldmlzaW9uX2tyZWYYAiAB'
    'KAsyDC5rdW1paG8uS3JlZlISdGFyZ2V0UmV2aXNpb25LcmVmEhsKCWVkZ2VfdHlwZRgDIAEoCV'
    'IIZWRnZVR5cGUSQwoIbWV0YWRhdGEYBCADKAsyJy5rdW1paG8uQ3JlYXRlRWRnZVJlcXVlc3Qu'
    'TWV0YWRhdGFFbnRyeVIIbWV0YWRhdGESIQoMZXhpc3RzX2Vycm9yGAUgASgIUgtleGlzdHNFcn'
    'Jvcho7Cg1NZXRhZGF0YUVudHJ5EhAKA2tleRgBIAEoCVIDa2V5EhQKBXZhbHVlGAIgASgJUgV2'
    'YWx1ZToCOAE=');

@$core.Deprecated('Use updateMetadataRequestDescriptor instead')
const UpdateMetadataRequest$json = {
  '1': 'UpdateMetadataRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {
      '1': 'metadata',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.UpdateMetadataRequest.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [UpdateMetadataRequest_MetadataEntry$json],
};

@$core.Deprecated('Use updateMetadataRequestDescriptor instead')
const UpdateMetadataRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `UpdateMetadataRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List updateMetadataRequestDescriptor = $convert.base64Decode(
    'ChVVcGRhdGVNZXRhZGF0YVJlcXVlc3QSIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcm'
    'VmEkcKCG1ldGFkYXRhGAIgAygLMisua3VtaWhvLlVwZGF0ZU1ldGFkYXRhUmVxdWVzdC5NZXRh'
    'ZGF0YUVudHJ5UghtZXRhZGF0YRo7Cg1NZXRhZGF0YUVudHJ5EhAKA2tleRgBIAEoCVIDa2V5Eh'
    'QKBXZhbHVlGAIgASgJUgV2YWx1ZToCOAE=');

@$core.Deprecated('Use setAttributeRequestDescriptor instead')
const SetAttributeRequest$json = {
  '1': 'SetAttributeRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'key', '3': 2, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 3, '4': 1, '5': 9, '10': 'value'},
  ],
};

/// Descriptor for `SetAttributeRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List setAttributeRequestDescriptor = $convert.base64Decode(
    'ChNTZXRBdHRyaWJ1dGVSZXF1ZXN0EiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZh'
    'IQCgNrZXkYAiABKAlSA2tleRIUCgV2YWx1ZRgDIAEoCVIFdmFsdWU=');

@$core.Deprecated('Use getAttributeRequestDescriptor instead')
const GetAttributeRequest$json = {
  '1': 'GetAttributeRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'key', '3': 2, '4': 1, '5': 9, '10': 'key'},
  ],
};

/// Descriptor for `GetAttributeRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getAttributeRequestDescriptor = $convert.base64Decode(
    'ChNHZXRBdHRyaWJ1dGVSZXF1ZXN0EiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3JlZh'
    'IQCgNrZXkYAiABKAlSA2tleQ==');

@$core.Deprecated('Use getAttributeResponseDescriptor instead')
const GetAttributeResponse$json = {
  '1': 'GetAttributeResponse',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
    {'1': 'exists', '3': 3, '4': 1, '5': 8, '10': 'exists'},
  ],
};

/// Descriptor for `GetAttributeResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getAttributeResponseDescriptor = $convert.base64Decode(
    'ChRHZXRBdHRyaWJ1dGVSZXNwb25zZRIQCgNrZXkYASABKAlSA2tleRIUCgV2YWx1ZRgCIAEoCV'
    'IFdmFsdWUSFgoGZXhpc3RzGAMgASgIUgZleGlzdHM=');

@$core.Deprecated('Use deleteAttributeRequestDescriptor instead')
const DeleteAttributeRequest$json = {
  '1': 'DeleteAttributeRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'key', '3': 2, '4': 1, '5': 9, '10': 'key'},
  ],
};

/// Descriptor for `DeleteAttributeRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteAttributeRequestDescriptor =
    $convert.base64Decode(
        'ChZEZWxldGVBdHRyaWJ1dGVSZXF1ZXN0EiAKBGtyZWYYASABKAsyDC5rdW1paG8uS3JlZlIEa3'
        'JlZhIQCgNrZXkYAiABKAlSA2tleQ==');

@$core.Deprecated('Use peekNextRevisionRequestDescriptor instead')
const PeekNextRevisionRequest$json = {
  '1': 'PeekNextRevisionRequest',
  '2': [
    {
      '1': 'item_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
  ],
};

/// Descriptor for `PeekNextRevisionRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List peekNextRevisionRequestDescriptor =
    $convert.base64Decode(
        'ChdQZWVrTmV4dFJldmlzaW9uUmVxdWVzdBIpCglpdGVtX2tyZWYYASABKAsyDC5rdW1paG8uS3'
        'JlZlIIaXRlbUtyZWY=');

@$core.Deprecated('Use peekNextRevisionResponseDescriptor instead')
const PeekNextRevisionResponse$json = {
  '1': 'PeekNextRevisionResponse',
  '2': [
    {'1': 'number', '3': 1, '4': 1, '5': 5, '10': 'number'},
  ],
};

/// Descriptor for `PeekNextRevisionResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List peekNextRevisionResponseDescriptor =
    $convert.base64Decode(
        'ChhQZWVrTmV4dFJldmlzaW9uUmVzcG9uc2USFgoGbnVtYmVyGAEgASgFUgZudW1iZXI=');

@$core.Deprecated('Use getEdgesRequestDescriptor instead')
const GetEdgesRequest$json = {
  '1': 'GetEdgesRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'edge_type_filter', '3': 2, '4': 1, '5': 9, '10': 'edgeTypeFilter'},
    {
      '1': 'direction',
      '3': 3,
      '4': 1,
      '5': 14,
      '6': '.kumiho.EdgeDirection',
      '10': 'direction'
    },
    {
      '1': 'pagination',
      '3': 4,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetEdgesRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getEdgesRequestDescriptor = $convert.base64Decode(
    'Cg9HZXRFZGdlc1JlcXVlc3QSIAoEa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUgRrcmVmEigKEG'
    'VkZ2VfdHlwZV9maWx0ZXIYAiABKAlSDmVkZ2VUeXBlRmlsdGVyEjMKCWRpcmVjdGlvbhgDIAEo'
    'DjIVLmt1bWloby5FZGdlRGlyZWN0aW9uUglkaXJlY3Rpb24SPgoKcGFnaW5hdGlvbhgEIAEoCz'
    'IZLmt1bWloby5QYWdpbmF0aW9uUmVxdWVzdEgAUgpwYWdpbmF0aW9uiAEBQg0KC19wYWdpbmF0'
    'aW9u');

@$core.Deprecated('Use getEdgesResponseDescriptor instead')
const GetEdgesResponse$json = {
  '1': 'GetEdgesResponse',
  '2': [
    {'1': 'edges', '3': 1, '4': 3, '5': 11, '6': '.kumiho.Edge', '10': 'edges'},
    {
      '1': 'revision_krefs',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKrefs'
    },
    {
      '1': 'pagination',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationResponse',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `GetEdgesResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getEdgesResponseDescriptor = $convert.base64Decode(
    'ChBHZXRFZGdlc1Jlc3BvbnNlEiIKBWVkZ2VzGAEgAygLMgwua3VtaWhvLkVkZ2VSBWVkZ2VzEj'
    'MKDnJldmlzaW9uX2tyZWZzGAIgAygLMgwua3VtaWhvLktyZWZSDXJldmlzaW9uS3JlZnMSPwoK'
    'cGFnaW5hdGlvbhgDIAEoCzIaLmt1bWloby5QYWdpbmF0aW9uUmVzcG9uc2VIAFIKcGFnaW5hdG'
    'lvbogBAUINCgtfcGFnaW5hdGlvbg==');

@$core.Deprecated('Use deleteEdgeRequestDescriptor instead')
const DeleteEdgeRequest$json = {
  '1': 'DeleteEdgeRequest',
  '2': [
    {
      '1': 'source_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'sourceKref'
    },
    {
      '1': 'target_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'targetKref'
    },
    {'1': 'edge_type', '3': 3, '4': 1, '5': 9, '10': 'edgeType'},
  ],
};

/// Descriptor for `DeleteEdgeRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteEdgeRequestDescriptor = $convert.base64Decode(
    'ChFEZWxldGVFZGdlUmVxdWVzdBItCgtzb3VyY2Vfa3JlZhgBIAEoCzIMLmt1bWloby5LcmVmUg'
    'pzb3VyY2VLcmVmEi0KC3RhcmdldF9rcmVmGAIgASgLMgwua3VtaWhvLktyZWZSCnRhcmdldEty'
    'ZWYSGwoJZWRnZV90eXBlGAMgASgJUghlZGdlVHlwZQ==');

@$core.Deprecated('Use pathStepDescriptor instead')
const PathStep$json = {
  '1': 'PathStep',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {'1': 'edge_type', '3': 2, '4': 1, '5': 9, '10': 'edgeType'},
    {'1': 'depth', '3': 3, '4': 1, '5': 5, '10': 'depth'},
  ],
};

/// Descriptor for `PathStep`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List pathStepDescriptor = $convert.base64Decode(
    'CghQYXRoU3RlcBIxCg1yZXZpc2lvbl9rcmVmGAEgASgLMgwua3VtaWhvLktyZWZSDHJldmlzaW'
    '9uS3JlZhIbCgllZGdlX3R5cGUYAiABKAlSCGVkZ2VUeXBlEhQKBWRlcHRoGAMgASgFUgVkZXB0'
    'aA==');

@$core.Deprecated('Use revisionPathDescriptor instead')
const RevisionPath$json = {
  '1': 'RevisionPath',
  '2': [
    {
      '1': 'steps',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.PathStep',
      '10': 'steps'
    },
    {'1': 'total_depth', '3': 2, '4': 1, '5': 5, '10': 'totalDepth'},
  ],
};

/// Descriptor for `RevisionPath`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List revisionPathDescriptor = $convert.base64Decode(
    'CgxSZXZpc2lvblBhdGgSJgoFc3RlcHMYASADKAsyEC5rdW1paG8uUGF0aFN0ZXBSBXN0ZXBzEh'
    '8KC3RvdGFsX2RlcHRoGAIgASgFUgp0b3RhbERlcHRo');

@$core.Deprecated('Use traverseEdgesRequestDescriptor instead')
const TraverseEdgesRequest$json = {
  '1': 'TraverseEdgesRequest',
  '2': [
    {
      '1': 'origin_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'originKref'
    },
    {
      '1': 'direction',
      '3': 2,
      '4': 1,
      '5': 14,
      '6': '.kumiho.EdgeDirection',
      '10': 'direction'
    },
    {'1': 'edge_type_filter', '3': 3, '4': 3, '5': 9, '10': 'edgeTypeFilter'},
    {'1': 'max_depth', '3': 4, '4': 1, '5': 5, '10': 'maxDepth'},
    {'1': 'limit', '3': 5, '4': 1, '5': 5, '10': 'limit'},
    {'1': 'include_path', '3': 6, '4': 1, '5': 8, '10': 'includePath'},
  ],
};

/// Descriptor for `TraverseEdgesRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List traverseEdgesRequestDescriptor = $convert.base64Decode(
    'ChRUcmF2ZXJzZUVkZ2VzUmVxdWVzdBItCgtvcmlnaW5fa3JlZhgBIAEoCzIMLmt1bWloby5Lcm'
    'VmUgpvcmlnaW5LcmVmEjMKCWRpcmVjdGlvbhgCIAEoDjIVLmt1bWloby5FZGdlRGlyZWN0aW9u'
    'UglkaXJlY3Rpb24SKAoQZWRnZV90eXBlX2ZpbHRlchgDIAMoCVIOZWRnZVR5cGVGaWx0ZXISGw'
    'oJbWF4X2RlcHRoGAQgASgFUghtYXhEZXB0aBIUCgVsaW1pdBgFIAEoBVIFbGltaXQSIQoMaW5j'
    'bHVkZV9wYXRoGAYgASgIUgtpbmNsdWRlUGF0aA==');

@$core.Deprecated('Use traverseEdgesResponseDescriptor instead')
const TraverseEdgesResponse$json = {
  '1': 'TraverseEdgesResponse',
  '2': [
    {
      '1': 'paths',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RevisionPath',
      '10': 'paths'
    },
    {
      '1': 'revision_krefs',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKrefs'
    },
    {'1': 'edges', '3': 3, '4': 3, '5': 11, '6': '.kumiho.Edge', '10': 'edges'},
    {'1': 'total_count', '3': 4, '4': 1, '5': 5, '10': 'totalCount'},
    {'1': 'truncated', '3': 5, '4': 1, '5': 8, '10': 'truncated'},
  ],
};

/// Descriptor for `TraverseEdgesResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List traverseEdgesResponseDescriptor = $convert.base64Decode(
    'ChVUcmF2ZXJzZUVkZ2VzUmVzcG9uc2USKgoFcGF0aHMYASADKAsyFC5rdW1paG8uUmV2aXNpb2'
    '5QYXRoUgVwYXRocxIzCg5yZXZpc2lvbl9rcmVmcxgCIAMoCzIMLmt1bWloby5LcmVmUg1yZXZp'
    'c2lvbktyZWZzEiIKBWVkZ2VzGAMgAygLMgwua3VtaWhvLkVkZ2VSBWVkZ2VzEh8KC3RvdGFsX2'
    'NvdW50GAQgASgFUgp0b3RhbENvdW50EhwKCXRydW5jYXRlZBgFIAEoCFIJdHJ1bmNhdGVk');

@$core.Deprecated('Use shortestPathRequestDescriptor instead')
const ShortestPathRequest$json = {
  '1': 'ShortestPathRequest',
  '2': [
    {
      '1': 'source_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'sourceKref'
    },
    {
      '1': 'target_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'targetKref'
    },
    {'1': 'edge_type_filter', '3': 3, '4': 3, '5': 9, '10': 'edgeTypeFilter'},
    {'1': 'max_depth', '3': 4, '4': 1, '5': 5, '10': 'maxDepth'},
    {'1': 'all_shortest', '3': 5, '4': 1, '5': 8, '10': 'allShortest'},
  ],
};

/// Descriptor for `ShortestPathRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List shortestPathRequestDescriptor = $convert.base64Decode(
    'ChNTaG9ydGVzdFBhdGhSZXF1ZXN0Ei0KC3NvdXJjZV9rcmVmGAEgASgLMgwua3VtaWhvLktyZW'
    'ZSCnNvdXJjZUtyZWYSLQoLdGFyZ2V0X2tyZWYYAiABKAsyDC5rdW1paG8uS3JlZlIKdGFyZ2V0'
    'S3JlZhIoChBlZGdlX3R5cGVfZmlsdGVyGAMgAygJUg5lZGdlVHlwZUZpbHRlchIbCgltYXhfZG'
    'VwdGgYBCABKAVSCG1heERlcHRoEiEKDGFsbF9zaG9ydGVzdBgFIAEoCFILYWxsU2hvcnRlc3Q=');

@$core.Deprecated('Use shortestPathResponseDescriptor instead')
const ShortestPathResponse$json = {
  '1': 'ShortestPathResponse',
  '2': [
    {
      '1': 'paths',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RevisionPath',
      '10': 'paths'
    },
    {'1': 'path_exists', '3': 2, '4': 1, '5': 8, '10': 'pathExists'},
    {'1': 'path_length', '3': 3, '4': 1, '5': 5, '10': 'pathLength'},
  ],
};

/// Descriptor for `ShortestPathResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List shortestPathResponseDescriptor = $convert.base64Decode(
    'ChRTaG9ydGVzdFBhdGhSZXNwb25zZRIqCgVwYXRocxgBIAMoCzIULmt1bWloby5SZXZpc2lvbl'
    'BhdGhSBXBhdGhzEh8KC3BhdGhfZXhpc3RzGAIgASgIUgpwYXRoRXhpc3RzEh8KC3BhdGhfbGVu'
    'Z3RoGAMgASgFUgpwYXRoTGVuZ3Ro');

@$core.Deprecated('Use impactAnalysisRequestDescriptor instead')
const ImpactAnalysisRequest$json = {
  '1': 'ImpactAnalysisRequest',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {'1': 'edge_type_filter', '3': 2, '4': 3, '5': 9, '10': 'edgeTypeFilter'},
    {'1': 'max_depth', '3': 3, '4': 1, '5': 5, '10': 'maxDepth'},
    {'1': 'limit', '3': 4, '4': 1, '5': 5, '10': 'limit'},
  ],
};

/// Descriptor for `ImpactAnalysisRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List impactAnalysisRequestDescriptor = $convert.base64Decode(
    'ChVJbXBhY3RBbmFseXNpc1JlcXVlc3QSMQoNcmV2aXNpb25fa3JlZhgBIAEoCzIMLmt1bWloby'
    '5LcmVmUgxyZXZpc2lvbktyZWYSKAoQZWRnZV90eXBlX2ZpbHRlchgCIAMoCVIOZWRnZVR5cGVG'
    'aWx0ZXISGwoJbWF4X2RlcHRoGAMgASgFUghtYXhEZXB0aBIUCgVsaW1pdBgEIAEoBVIFbGltaX'
    'Q=');

@$core.Deprecated('Use impactedRevisionDescriptor instead')
const ImpactedRevision$json = {
  '1': 'ImpactedRevision',
  '2': [
    {
      '1': 'revision_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKref'
    },
    {
      '1': 'item_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {'1': 'impact_depth', '3': 3, '4': 1, '5': 5, '10': 'impactDepth'},
    {'1': 'impact_path_types', '3': 4, '4': 3, '5': 9, '10': 'impactPathTypes'},
  ],
};

/// Descriptor for `ImpactedRevision`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List impactedRevisionDescriptor = $convert.base64Decode(
    'ChBJbXBhY3RlZFJldmlzaW9uEjEKDXJldmlzaW9uX2tyZWYYASABKAsyDC5rdW1paG8uS3JlZl'
    'IMcmV2aXNpb25LcmVmEikKCWl0ZW1fa3JlZhgCIAEoCzIMLmt1bWloby5LcmVmUghpdGVtS3Jl'
    'ZhIhCgxpbXBhY3RfZGVwdGgYAyABKAVSC2ltcGFjdERlcHRoEioKEWltcGFjdF9wYXRoX3R5cG'
    'VzGAQgAygJUg9pbXBhY3RQYXRoVHlwZXM=');

@$core.Deprecated('Use impactAnalysisResponseDescriptor instead')
const ImpactAnalysisResponse$json = {
  '1': 'ImpactAnalysisResponse',
  '2': [
    {
      '1': 'impacted_revisions',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ImpactedRevision',
      '10': 'impactedRevisions'
    },
    {'1': 'total_impacted', '3': 2, '4': 1, '5': 5, '10': 'totalImpacted'},
    {'1': 'truncated', '3': 3, '4': 1, '5': 8, '10': 'truncated'},
  ],
};

/// Descriptor for `ImpactAnalysisResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List impactAnalysisResponseDescriptor = $convert.base64Decode(
    'ChZJbXBhY3RBbmFseXNpc1Jlc3BvbnNlEkcKEmltcGFjdGVkX3JldmlzaW9ucxgBIAMoCzIYLm'
    't1bWloby5JbXBhY3RlZFJldmlzaW9uUhFpbXBhY3RlZFJldmlzaW9ucxIlCg50b3RhbF9pbXBh'
    'Y3RlZBgCIAEoBVINdG90YWxJbXBhY3RlZBIcCgl0cnVuY2F0ZWQYAyABKAhSCXRydW5jYXRlZA'
    '==');

@$core.Deprecated('Use createBundleRequestDescriptor instead')
const CreateBundleRequest$json = {
  '1': 'CreateBundleRequest',
  '2': [
    {'1': 'parent_path', '3': 1, '4': 1, '5': 9, '10': 'parentPath'},
    {'1': 'bundle_name', '3': 2, '4': 1, '5': 9, '10': 'bundleName'},
    {
      '1': 'metadata',
      '3': 3,
      '4': 3,
      '5': 11,
      '6': '.kumiho.CreateBundleRequest.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [CreateBundleRequest_MetadataEntry$json],
};

@$core.Deprecated('Use createBundleRequestDescriptor instead')
const CreateBundleRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `CreateBundleRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createBundleRequestDescriptor = $convert.base64Decode(
    'ChNDcmVhdGVCdW5kbGVSZXF1ZXN0Eh8KC3BhcmVudF9wYXRoGAEgASgJUgpwYXJlbnRQYXRoEh'
    '8KC2J1bmRsZV9uYW1lGAIgASgJUgpidW5kbGVOYW1lEkUKCG1ldGFkYXRhGAMgAygLMikua3Vt'
    'aWhvLkNyZWF0ZUJ1bmRsZVJlcXVlc3QuTWV0YWRhdGFFbnRyeVIIbWV0YWRhdGEaOwoNTWV0YW'
    'RhdGFFbnRyeRIQCgNrZXkYASABKAlSA2tleRIUCgV2YWx1ZRgCIAEoCVIFdmFsdWU6AjgB');

@$core.Deprecated('Use bundleMemberDescriptor instead')
const BundleMember$json = {
  '1': 'BundleMember',
  '2': [
    {
      '1': 'item_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKref'
    },
    {'1': 'added_at', '3': 2, '4': 1, '5': 9, '10': 'addedAt'},
    {'1': 'added_by', '3': 3, '4': 1, '5': 9, '10': 'addedBy'},
    {'1': 'added_by_username', '3': 4, '4': 1, '5': 9, '10': 'addedByUsername'},
    {'1': 'added_in_revision', '3': 5, '4': 1, '5': 5, '10': 'addedInRevision'},
  ],
};

/// Descriptor for `BundleMember`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List bundleMemberDescriptor = $convert.base64Decode(
    'CgxCdW5kbGVNZW1iZXISKQoJaXRlbV9rcmVmGAEgASgLMgwua3VtaWhvLktyZWZSCGl0ZW1Lcm'
    'VmEhkKCGFkZGVkX2F0GAIgASgJUgdhZGRlZEF0EhkKCGFkZGVkX2J5GAMgASgJUgdhZGRlZEJ5'
    'EioKEWFkZGVkX2J5X3VzZXJuYW1lGAQgASgJUg9hZGRlZEJ5VXNlcm5hbWUSKgoRYWRkZWRfaW'
    '5fcmV2aXNpb24YBSABKAVSD2FkZGVkSW5SZXZpc2lvbg==');

@$core.Deprecated('Use addBundleMemberRequestDescriptor instead')
const AddBundleMemberRequest$json = {
  '1': 'AddBundleMemberRequest',
  '2': [
    {
      '1': 'bundle_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'bundleKref'
    },
    {
      '1': 'member_item_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'memberItemKref'
    },
    {
      '1': 'metadata',
      '3': 3,
      '4': 3,
      '5': 11,
      '6': '.kumiho.AddBundleMemberRequest.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [AddBundleMemberRequest_MetadataEntry$json],
};

@$core.Deprecated('Use addBundleMemberRequestDescriptor instead')
const AddBundleMemberRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `AddBundleMemberRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List addBundleMemberRequestDescriptor = $convert.base64Decode(
    'ChZBZGRCdW5kbGVNZW1iZXJSZXF1ZXN0Ei0KC2J1bmRsZV9rcmVmGAEgASgLMgwua3VtaWhvLk'
    'tyZWZSCmJ1bmRsZUtyZWYSNgoQbWVtYmVyX2l0ZW1fa3JlZhgCIAEoCzIMLmt1bWloby5LcmVm'
    'Ug5tZW1iZXJJdGVtS3JlZhJICghtZXRhZGF0YRgDIAMoCzIsLmt1bWloby5BZGRCdW5kbGVNZW'
    '1iZXJSZXF1ZXN0Lk1ldGFkYXRhRW50cnlSCG1ldGFkYXRhGjsKDU1ldGFkYXRhRW50cnkSEAoD'
    'a2V5GAEgASgJUgNrZXkSFAoFdmFsdWUYAiABKAlSBXZhbHVlOgI4AQ==');

@$core.Deprecated('Use addBundleMemberResponseDescriptor instead')
const AddBundleMemberResponse$json = {
  '1': 'AddBundleMemberResponse',
  '2': [
    {'1': 'success', '3': 1, '4': 1, '5': 8, '10': 'success'},
    {'1': 'message', '3': 2, '4': 1, '5': 9, '10': 'message'},
    {
      '1': 'new_revision',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.RevisionResponse',
      '10': 'newRevision'
    },
  ],
};

/// Descriptor for `AddBundleMemberResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List addBundleMemberResponseDescriptor = $convert.base64Decode(
    'ChdBZGRCdW5kbGVNZW1iZXJSZXNwb25zZRIYCgdzdWNjZXNzGAEgASgIUgdzdWNjZXNzEhgKB2'
    '1lc3NhZ2UYAiABKAlSB21lc3NhZ2USOwoMbmV3X3JldmlzaW9uGAMgASgLMhgua3VtaWhvLlJl'
    'dmlzaW9uUmVzcG9uc2VSC25ld1JldmlzaW9u');

@$core.Deprecated('Use removeBundleMemberRequestDescriptor instead')
const RemoveBundleMemberRequest$json = {
  '1': 'RemoveBundleMemberRequest',
  '2': [
    {
      '1': 'bundle_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'bundleKref'
    },
    {
      '1': 'member_item_kref',
      '3': 2,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'memberItemKref'
    },
    {
      '1': 'metadata',
      '3': 3,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RemoveBundleMemberRequest.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [RemoveBundleMemberRequest_MetadataEntry$json],
};

@$core.Deprecated('Use removeBundleMemberRequestDescriptor instead')
const RemoveBundleMemberRequest_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `RemoveBundleMemberRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List removeBundleMemberRequestDescriptor = $convert.base64Decode(
    'ChlSZW1vdmVCdW5kbGVNZW1iZXJSZXF1ZXN0Ei0KC2J1bmRsZV9rcmVmGAEgASgLMgwua3VtaW'
    'hvLktyZWZSCmJ1bmRsZUtyZWYSNgoQbWVtYmVyX2l0ZW1fa3JlZhgCIAEoCzIMLmt1bWloby5L'
    'cmVmUg5tZW1iZXJJdGVtS3JlZhJLCghtZXRhZGF0YRgDIAMoCzIvLmt1bWloby5SZW1vdmVCdW'
    '5kbGVNZW1iZXJSZXF1ZXN0Lk1ldGFkYXRhRW50cnlSCG1ldGFkYXRhGjsKDU1ldGFkYXRhRW50'
    'cnkSEAoDa2V5GAEgASgJUgNrZXkSFAoFdmFsdWUYAiABKAlSBXZhbHVlOgI4AQ==');

@$core.Deprecated('Use removeBundleMemberResponseDescriptor instead')
const RemoveBundleMemberResponse$json = {
  '1': 'RemoveBundleMemberResponse',
  '2': [
    {'1': 'success', '3': 1, '4': 1, '5': 8, '10': 'success'},
    {'1': 'message', '3': 2, '4': 1, '5': 9, '10': 'message'},
    {
      '1': 'new_revision',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.RevisionResponse',
      '10': 'newRevision'
    },
  ],
};

/// Descriptor for `RemoveBundleMemberResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List removeBundleMemberResponseDescriptor =
    $convert.base64Decode(
        'ChpSZW1vdmVCdW5kbGVNZW1iZXJSZXNwb25zZRIYCgdzdWNjZXNzGAEgASgIUgdzdWNjZXNzEh'
        'gKB21lc3NhZ2UYAiABKAlSB21lc3NhZ2USOwoMbmV3X3JldmlzaW9uGAMgASgLMhgua3VtaWhv'
        'LlJldmlzaW9uUmVzcG9uc2VSC25ld1JldmlzaW9u');

@$core.Deprecated('Use getBundleMembersRequestDescriptor instead')
const GetBundleMembersRequest$json = {
  '1': 'GetBundleMembersRequest',
  '2': [
    {
      '1': 'bundle_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'bundleKref'
    },
    {
      '1': 'revision_number',
      '3': 2,
      '4': 1,
      '5': 5,
      '9': 0,
      '10': 'revisionNumber',
      '17': true
    },
  ],
  '8': [
    {'1': '_revision_number'},
  ],
};

/// Descriptor for `GetBundleMembersRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getBundleMembersRequestDescriptor = $convert.base64Decode(
    'ChdHZXRCdW5kbGVNZW1iZXJzUmVxdWVzdBItCgtidW5kbGVfa3JlZhgBIAEoCzIMLmt1bWloby'
    '5LcmVmUgpidW5kbGVLcmVmEiwKD3JldmlzaW9uX251bWJlchgCIAEoBUgAUg5yZXZpc2lvbk51'
    'bWJlcogBAUISChBfcmV2aXNpb25fbnVtYmVy');

@$core.Deprecated('Use getBundleMembersResponseDescriptor instead')
const GetBundleMembersResponse$json = {
  '1': 'GetBundleMembersResponse',
  '2': [
    {
      '1': 'members',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.BundleMember',
      '10': 'members'
    },
    {'1': 'revision_number', '3': 2, '4': 1, '5': 5, '10': 'revisionNumber'},
    {'1': 'total_count', '3': 3, '4': 1, '5': 5, '10': 'totalCount'},
  ],
};

/// Descriptor for `GetBundleMembersResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getBundleMembersResponseDescriptor = $convert.base64Decode(
    'ChhHZXRCdW5kbGVNZW1iZXJzUmVzcG9uc2USLgoHbWVtYmVycxgBIAMoCzIULmt1bWloby5CdW'
    '5kbGVNZW1iZXJSB21lbWJlcnMSJwoPcmV2aXNpb25fbnVtYmVyGAIgASgFUg5yZXZpc2lvbk51'
    'bWJlchIfCgt0b3RhbF9jb3VudBgDIAEoBVIKdG90YWxDb3VudA==');

@$core.Deprecated('Use bundleRevisionHistoryDescriptor instead')
const BundleRevisionHistory$json = {
  '1': 'BundleRevisionHistory',
  '2': [
    {'1': 'revision_number', '3': 1, '4': 1, '5': 5, '10': 'revisionNumber'},
    {'1': 'action', '3': 2, '4': 1, '5': 9, '10': 'action'},
    {
      '1': 'member_item_kref',
      '3': 3,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'memberItemKref'
    },
    {'1': 'author', '3': 4, '4': 1, '5': 9, '10': 'author'},
    {'1': 'username', '3': 5, '4': 1, '5': 9, '10': 'username'},
    {'1': 'created_at', '3': 6, '4': 1, '5': 9, '10': 'createdAt'},
    {
      '1': 'metadata',
      '3': 7,
      '4': 3,
      '5': 11,
      '6': '.kumiho.BundleRevisionHistory.MetadataEntry',
      '10': 'metadata'
    },
  ],
  '3': [BundleRevisionHistory_MetadataEntry$json],
};

@$core.Deprecated('Use bundleRevisionHistoryDescriptor instead')
const BundleRevisionHistory_MetadataEntry$json = {
  '1': 'MetadataEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `BundleRevisionHistory`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List bundleRevisionHistoryDescriptor = $convert.base64Decode(
    'ChVCdW5kbGVSZXZpc2lvbkhpc3RvcnkSJwoPcmV2aXNpb25fbnVtYmVyGAEgASgFUg5yZXZpc2'
    'lvbk51bWJlchIWCgZhY3Rpb24YAiABKAlSBmFjdGlvbhI2ChBtZW1iZXJfaXRlbV9rcmVmGAMg'
    'ASgLMgwua3VtaWhvLktyZWZSDm1lbWJlckl0ZW1LcmVmEhYKBmF1dGhvchgEIAEoCVIGYXV0aG'
    '9yEhoKCHVzZXJuYW1lGAUgASgJUgh1c2VybmFtZRIdCgpjcmVhdGVkX2F0GAYgASgJUgljcmVh'
    'dGVkQXQSRwoIbWV0YWRhdGEYByADKAsyKy5rdW1paG8uQnVuZGxlUmV2aXNpb25IaXN0b3J5Lk'
    '1ldGFkYXRhRW50cnlSCG1ldGFkYXRhGjsKDU1ldGFkYXRhRW50cnkSEAoDa2V5GAEgASgJUgNr'
    'ZXkSFAoFdmFsdWUYAiABKAlSBXZhbHVlOgI4AQ==');

@$core.Deprecated('Use getBundleHistoryRequestDescriptor instead')
const GetBundleHistoryRequest$json = {
  '1': 'GetBundleHistoryRequest',
  '2': [
    {
      '1': 'bundle_kref',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'bundleKref'
    },
  ],
};

/// Descriptor for `GetBundleHistoryRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getBundleHistoryRequestDescriptor =
    $convert.base64Decode(
        'ChdHZXRCdW5kbGVIaXN0b3J5UmVxdWVzdBItCgtidW5kbGVfa3JlZhgBIAEoCzIMLmt1bWloby'
        '5LcmVmUgpidW5kbGVLcmVm');

@$core.Deprecated('Use getBundleHistoryResponseDescriptor instead')
const GetBundleHistoryResponse$json = {
  '1': 'GetBundleHistoryResponse',
  '2': [
    {
      '1': 'history',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.BundleRevisionHistory',
      '10': 'history'
    },
  ],
};

/// Descriptor for `GetBundleHistoryResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getBundleHistoryResponseDescriptor =
    $convert.base64Decode(
        'ChhHZXRCdW5kbGVIaXN0b3J5UmVzcG9uc2USNwoHaGlzdG9yeRgBIAMoCzIdLmt1bWloby5CdW'
        '5kbGVSZXZpc2lvbkhpc3RvcnlSB2hpc3Rvcnk=');

@$core.Deprecated('Use eventStreamRequestDescriptor instead')
const EventStreamRequest$json = {
  '1': 'EventStreamRequest',
  '2': [
    {
      '1': 'routing_key_filter',
      '3': 1,
      '4': 1,
      '5': 9,
      '10': 'routingKeyFilter'
    },
    {'1': 'kref_filter', '3': 2, '4': 1, '5': 9, '10': 'krefFilter'},
    {'1': 'cursor', '3': 3, '4': 1, '5': 9, '9': 1, '10': 'cursor', '17': true},
    {
      '1': 'consumer_group',
      '3': 4,
      '4': 1,
      '5': 9,
      '9': 2,
      '10': 'consumerGroup',
      '17': true
    },
    {'1': 'from_latest', '3': 5, '4': 1, '5': 8, '9': 0, '10': 'fromLatest'},
    {'1': 'from_cursor', '3': 6, '4': 1, '5': 9, '9': 0, '10': 'fromCursor'},
    {
      '1': 'from_timestamp',
      '3': 7,
      '4': 1,
      '5': 9,
      '9': 0,
      '10': 'fromTimestamp'
    },
    {
      '1': 'from_beginning',
      '3': 8,
      '4': 1,
      '5': 8,
      '9': 0,
      '10': 'fromBeginning'
    },
  ],
  '8': [
    {'1': 'start_position'},
    {'1': '_cursor'},
    {'1': '_consumer_group'},
  ],
};

/// Descriptor for `EventStreamRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List eventStreamRequestDescriptor = $convert.base64Decode(
    'ChJFdmVudFN0cmVhbVJlcXVlc3QSLAoScm91dGluZ19rZXlfZmlsdGVyGAEgASgJUhByb3V0aW'
    '5nS2V5RmlsdGVyEh8KC2tyZWZfZmlsdGVyGAIgASgJUgprcmVmRmlsdGVyEhsKBmN1cnNvchgD'
    'IAEoCUgBUgZjdXJzb3KIAQESKgoOY29uc3VtZXJfZ3JvdXAYBCABKAlIAlINY29uc3VtZXJHcm'
    '91cIgBARIhCgtmcm9tX2xhdGVzdBgFIAEoCEgAUgpmcm9tTGF0ZXN0EiEKC2Zyb21fY3Vyc29y'
    'GAYgASgJSABSCmZyb21DdXJzb3ISJwoOZnJvbV90aW1lc3RhbXAYByABKAlIAFINZnJvbVRpbW'
    'VzdGFtcBInCg5mcm9tX2JlZ2lubmluZxgIIAEoCEgAUg1mcm9tQmVnaW5uaW5nQhAKDnN0YXJ0'
    'X3Bvc2l0aW9uQgkKB19jdXJzb3JCEQoPX2NvbnN1bWVyX2dyb3Vw');

@$core.Deprecated('Use eventDescriptor instead')
const Event$json = {
  '1': 'Event',
  '2': [
    {'1': 'routing_key', '3': 1, '4': 1, '5': 9, '10': 'routingKey'},
    {'1': 'kref', '3': 2, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'timestamp', '3': 3, '4': 1, '5': 9, '10': 'timestamp'},
    {'1': 'author', '3': 4, '4': 1, '5': 9, '10': 'author'},
    {'1': 'tenant_id', '3': 5, '4': 1, '5': 9, '10': 'tenantId'},
    {
      '1': 'details',
      '3': 6,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Event.DetailsEntry',
      '10': 'details'
    },
    {'1': 'username', '3': 7, '4': 1, '5': 9, '10': 'username'},
    {'1': 'cursor', '3': 8, '4': 1, '5': 9, '10': 'cursor'},
  ],
  '3': [Event_DetailsEntry$json],
};

@$core.Deprecated('Use eventDescriptor instead')
const Event_DetailsEntry$json = {
  '1': 'DetailsEntry',
  '2': [
    {'1': 'key', '3': 1, '4': 1, '5': 9, '10': 'key'},
    {'1': 'value', '3': 2, '4': 1, '5': 9, '10': 'value'},
  ],
  '7': {'7': true},
};

/// Descriptor for `Event`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List eventDescriptor = $convert.base64Decode(
    'CgVFdmVudBIfCgtyb3V0aW5nX2tleRgBIAEoCVIKcm91dGluZ0tleRIgCgRrcmVmGAIgASgLMg'
    'wua3VtaWhvLktyZWZSBGtyZWYSHAoJdGltZXN0YW1wGAMgASgJUgl0aW1lc3RhbXASFgoGYXV0'
    'aG9yGAQgASgJUgZhdXRob3ISGwoJdGVuYW50X2lkGAUgASgJUgh0ZW5hbnRJZBI0CgdkZXRhaW'
    'xzGAYgAygLMhoua3VtaWhvLkV2ZW50LkRldGFpbHNFbnRyeVIHZGV0YWlscxIaCgh1c2VybmFt'
    'ZRgHIAEoCVIIdXNlcm5hbWUSFgoGY3Vyc29yGAggASgJUgZjdXJzb3IaOgoMRGV0YWlsc0VudH'
    'J5EhAKA2tleRgBIAEoCVIDa2V5EhQKBXZhbHVlGAIgASgJUgV2YWx1ZToCOAE=');

@$core.Deprecated('Use getEventCapabilitiesRequestDescriptor instead')
const GetEventCapabilitiesRequest$json = {
  '1': 'GetEventCapabilitiesRequest',
};

/// Descriptor for `GetEventCapabilitiesRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getEventCapabilitiesRequestDescriptor =
    $convert.base64Decode('ChtHZXRFdmVudENhcGFiaWxpdGllc1JlcXVlc3Q=');

@$core.Deprecated('Use eventCapabilitiesDescriptor instead')
const EventCapabilities$json = {
  '1': 'EventCapabilities',
  '2': [
    {'1': 'supports_replay', '3': 1, '4': 1, '5': 8, '10': 'supportsReplay'},
    {'1': 'supports_cursor', '3': 2, '4': 1, '5': 8, '10': 'supportsCursor'},
    {
      '1': 'supports_consumer_groups',
      '3': 3,
      '4': 1,
      '5': 8,
      '10': 'supportsConsumerGroups'
    },
    {
      '1': 'max_retention_hours',
      '3': 4,
      '4': 1,
      '5': 3,
      '10': 'maxRetentionHours'
    },
    {'1': 'max_buffer_size', '3': 5, '4': 1, '5': 3, '10': 'maxBufferSize'},
    {'1': 'tier', '3': 6, '4': 1, '5': 9, '10': 'tier'},
  ],
};

/// Descriptor for `EventCapabilities`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List eventCapabilitiesDescriptor = $convert.base64Decode(
    'ChFFdmVudENhcGFiaWxpdGllcxInCg9zdXBwb3J0c19yZXBsYXkYASABKAhSDnN1cHBvcnRzUm'
    'VwbGF5EicKD3N1cHBvcnRzX2N1cnNvchgCIAEoCFIOc3VwcG9ydHNDdXJzb3ISOAoYc3VwcG9y'
    'dHNfY29uc3VtZXJfZ3JvdXBzGAMgASgIUhZzdXBwb3J0c0NvbnN1bWVyR3JvdXBzEi4KE21heF'
    '9yZXRlbnRpb25faG91cnMYBCABKANSEW1heFJldGVudGlvbkhvdXJzEiYKD21heF9idWZmZXJf'
    'c2l6ZRgFIAEoA1INbWF4QnVmZmVyU2l6ZRISCgR0aWVyGAYgASgJUgR0aWVy');

@$core.Deprecated('Use createProjectRequestDescriptor instead')
const CreateProjectRequest$json = {
  '1': 'CreateProjectRequest',
  '2': [
    {'1': 'name', '3': 1, '4': 1, '5': 9, '10': 'name'},
    {'1': 'description', '3': 2, '4': 1, '5': 9, '10': 'description'},
  ],
};

/// Descriptor for `CreateProjectRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List createProjectRequestDescriptor = $convert.base64Decode(
    'ChRDcmVhdGVQcm9qZWN0UmVxdWVzdBISCgRuYW1lGAEgASgJUgRuYW1lEiAKC2Rlc2NyaXB0aW'
    '9uGAIgASgJUgtkZXNjcmlwdGlvbg==');

@$core.Deprecated('Use projectResponseDescriptor instead')
const ProjectResponse$json = {
  '1': 'ProjectResponse',
  '2': [
    {'1': 'project_id', '3': 1, '4': 1, '5': 9, '10': 'projectId'},
    {'1': 'name', '3': 2, '4': 1, '5': 9, '10': 'name'},
    {'1': 'description', '3': 3, '4': 1, '5': 9, '10': 'description'},
    {'1': 'created_at', '3': 4, '4': 1, '5': 9, '10': 'createdAt'},
    {'1': 'updated_at', '3': 5, '4': 1, '5': 9, '10': 'updatedAt'},
    {'1': 'deprecated', '3': 6, '4': 1, '5': 8, '10': 'deprecated'},
    {'1': 'allow_public', '3': 7, '4': 1, '5': 8, '10': 'allowPublic'},
  ],
};

/// Descriptor for `ProjectResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List projectResponseDescriptor = $convert.base64Decode(
    'Cg9Qcm9qZWN0UmVzcG9uc2USHQoKcHJvamVjdF9pZBgBIAEoCVIJcHJvamVjdElkEhIKBG5hbW'
    'UYAiABKAlSBG5hbWUSIAoLZGVzY3JpcHRpb24YAyABKAlSC2Rlc2NyaXB0aW9uEh0KCmNyZWF0'
    'ZWRfYXQYBCABKAlSCWNyZWF0ZWRBdBIdCgp1cGRhdGVkX2F0GAUgASgJUgl1cGRhdGVkQXQSHg'
    'oKZGVwcmVjYXRlZBgGIAEoCFIKZGVwcmVjYXRlZBIhCgxhbGxvd19wdWJsaWMYByABKAhSC2Fs'
    'bG93UHVibGlj');

@$core.Deprecated('Use getProjectsRequestDescriptor instead')
const GetProjectsRequest$json = {
  '1': 'GetProjectsRequest',
};

/// Descriptor for `GetProjectsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getProjectsRequestDescriptor =
    $convert.base64Decode('ChJHZXRQcm9qZWN0c1JlcXVlc3Q=');

@$core.Deprecated('Use getProjectsResponseDescriptor instead')
const GetProjectsResponse$json = {
  '1': 'GetProjectsResponse',
  '2': [
    {
      '1': 'projects',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ProjectResponse',
      '10': 'projects'
    },
  ],
};

/// Descriptor for `GetProjectsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getProjectsResponseDescriptor = $convert.base64Decode(
    'ChNHZXRQcm9qZWN0c1Jlc3BvbnNlEjMKCHByb2plY3RzGAEgAygLMhcua3VtaWhvLlByb2plY3'
    'RSZXNwb25zZVIIcHJvamVjdHM=');

@$core.Deprecated('Use deleteProjectRequestDescriptor instead')
const DeleteProjectRequest$json = {
  '1': 'DeleteProjectRequest',
  '2': [
    {'1': 'project_id', '3': 1, '4': 1, '5': 9, '10': 'projectId'},
    {'1': 'force', '3': 2, '4': 1, '5': 8, '10': 'force'},
  ],
};

/// Descriptor for `DeleteProjectRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List deleteProjectRequestDescriptor = $convert.base64Decode(
    'ChREZWxldGVQcm9qZWN0UmVxdWVzdBIdCgpwcm9qZWN0X2lkGAEgASgJUglwcm9qZWN0SWQSFA'
    'oFZm9yY2UYAiABKAhSBWZvcmNl');

@$core.Deprecated('Use updateProjectRequestDescriptor instead')
const UpdateProjectRequest$json = {
  '1': 'UpdateProjectRequest',
  '2': [
    {'1': 'project_id', '3': 1, '4': 1, '5': 9, '10': 'projectId'},
    {
      '1': 'allow_public',
      '3': 2,
      '4': 1,
      '5': 8,
      '9': 0,
      '10': 'allowPublic',
      '17': true
    },
    {
      '1': 'description',
      '3': 3,
      '4': 1,
      '5': 9,
      '9': 1,
      '10': 'description',
      '17': true
    },
  ],
  '8': [
    {'1': '_allow_public'},
    {'1': '_description'},
  ],
};

/// Descriptor for `UpdateProjectRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List updateProjectRequestDescriptor = $convert.base64Decode(
    'ChRVcGRhdGVQcm9qZWN0UmVxdWVzdBIdCgpwcm9qZWN0X2lkGAEgASgJUglwcm9qZWN0SWQSJg'
    'oMYWxsb3dfcHVibGljGAIgASgISABSC2FsbG93UHVibGljiAEBEiUKC2Rlc2NyaXB0aW9uGAMg'
    'ASgJSAFSC2Rlc2NyaXB0aW9uiAEBQg8KDV9hbGxvd19wdWJsaWNCDgoMX2Rlc2NyaXB0aW9u');

@$core.Deprecated('Use setDeprecatedRequestDescriptor instead')
const SetDeprecatedRequest$json = {
  '1': 'SetDeprecatedRequest',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'deprecated', '3': 2, '4': 1, '5': 8, '10': 'deprecated'},
  ],
};

/// Descriptor for `SetDeprecatedRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List setDeprecatedRequestDescriptor = $convert.base64Decode(
    'ChRTZXREZXByZWNhdGVkUmVxdWVzdBIgCgRrcmVmGAEgASgLMgwua3VtaWhvLktyZWZSBGtyZW'
    'YSHgoKZGVwcmVjYXRlZBgCIAEoCFIKZGVwcmVjYXRlZA==');

@$core.Deprecated('Use getTenantUsageRequestDescriptor instead')
const GetTenantUsageRequest$json = {
  '1': 'GetTenantUsageRequest',
};

/// Descriptor for `GetTenantUsageRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List getTenantUsageRequestDescriptor =
    $convert.base64Decode('ChVHZXRUZW5hbnRVc2FnZVJlcXVlc3Q=');

@$core.Deprecated('Use tenantUsageResponseDescriptor instead')
const TenantUsageResponse$json = {
  '1': 'TenantUsageResponse',
  '2': [
    {'1': 'node_count', '3': 1, '4': 1, '5': 3, '10': 'nodeCount'},
    {'1': 'node_limit', '3': 2, '4': 1, '5': 3, '10': 'nodeLimit'},
    {'1': 'tenant_id', '3': 3, '4': 1, '5': 9, '10': 'tenantId'},
  ],
};

/// Descriptor for `TenantUsageResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List tenantUsageResponseDescriptor = $convert.base64Decode(
    'ChNUZW5hbnRVc2FnZVJlc3BvbnNlEh0KCm5vZGVfY291bnQYASABKANSCW5vZGVDb3VudBIdCg'
    'pub2RlX2xpbWl0GAIgASgDUglub2RlTGltaXQSGwoJdGVuYW50X2lkGAMgASgJUgh0ZW5hbnRJ'
    'ZA==');

const $core.Map<$core.String, $core.dynamic> KumihoServiceBase$json = {
  '1': 'KumihoService',
  '2': [
    {
      '1': 'CreateProject',
      '2': '.kumiho.CreateProjectRequest',
      '3': '.kumiho.ProjectResponse'
    },
    {
      '1': 'GetProjects',
      '2': '.kumiho.GetProjectsRequest',
      '3': '.kumiho.GetProjectsResponse'
    },
    {
      '1': 'UpdateProject',
      '2': '.kumiho.UpdateProjectRequest',
      '3': '.kumiho.ProjectResponse'
    },
    {
      '1': 'DeleteProject',
      '2': '.kumiho.DeleteProjectRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'CreateSpace',
      '2': '.kumiho.CreateSpaceRequest',
      '3': '.kumiho.SpaceResponse'
    },
    {
      '1': 'GetSpace',
      '2': '.kumiho.GetSpaceRequest',
      '3': '.kumiho.SpaceResponse'
    },
    {
      '1': 'GetChildSpaces',
      '2': '.kumiho.GetChildSpacesRequest',
      '3': '.kumiho.GetChildSpacesResponse'
    },
    {
      '1': 'DeleteSpace',
      '2': '.kumiho.DeleteSpaceRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'UpdateSpaceMetadata',
      '2': '.kumiho.UpdateMetadataRequest',
      '3': '.kumiho.SpaceResponse'
    },
    {
      '1': 'CreateItem',
      '2': '.kumiho.CreateItemRequest',
      '3': '.kumiho.ItemResponse'
    },
    {
      '1': 'GetItem',
      '2': '.kumiho.GetItemRequest',
      '3': '.kumiho.ItemResponse'
    },
    {
      '1': 'GetItems',
      '2': '.kumiho.GetItemsRequest',
      '3': '.kumiho.GetItemsResponse'
    },
    {
      '1': 'ItemSearch',
      '2': '.kumiho.ItemSearchRequest',
      '3': '.kumiho.GetItemsResponse'
    },
    {
      '1': 'DeleteItem',
      '2': '.kumiho.DeleteItemRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'UpdateItemMetadata',
      '2': '.kumiho.UpdateMetadataRequest',
      '3': '.kumiho.ItemResponse'
    },
    {
      '1': 'ResolveKref',
      '2': '.kumiho.ResolveKrefRequest',
      '3': '.kumiho.RevisionResponse'
    },
    {
      '1': 'ResolveLocation',
      '2': '.kumiho.ResolveLocationRequest',
      '3': '.kumiho.ResolveLocationResponse'
    },
    {
      '1': 'CreateRevision',
      '2': '.kumiho.CreateRevisionRequest',
      '3': '.kumiho.RevisionResponse'
    },
    {
      '1': 'GetRevision',
      '2': '.kumiho.KrefRequest',
      '3': '.kumiho.RevisionResponse'
    },
    {
      '1': 'GetRevisions',
      '2': '.kumiho.GetRevisionsRequest',
      '3': '.kumiho.GetRevisionsResponse'
    },
    {
      '1': 'DeleteRevision',
      '2': '.kumiho.DeleteRevisionRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'PeekNextRevision',
      '2': '.kumiho.PeekNextRevisionRequest',
      '3': '.kumiho.PeekNextRevisionResponse'
    },
    {
      '1': 'UpdateRevisionMetadata',
      '2': '.kumiho.UpdateMetadataRequest',
      '3': '.kumiho.RevisionResponse'
    },
    {
      '1': 'TagRevision',
      '2': '.kumiho.TagRevisionRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'UnTagRevision',
      '2': '.kumiho.UnTagRevisionRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'HasTag',
      '2': '.kumiho.HasTagRequest',
      '3': '.kumiho.HasTagResponse'
    },
    {
      '1': 'WasTagged',
      '2': '.kumiho.WasTaggedRequest',
      '3': '.kumiho.WasTaggedResponse'
    },
    {
      '1': 'SetDefaultArtifact',
      '2': '.kumiho.SetDefaultArtifactRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'CreateArtifact',
      '2': '.kumiho.CreateArtifactRequest',
      '3': '.kumiho.ArtifactResponse'
    },
    {
      '1': 'GetArtifact',
      '2': '.kumiho.GetArtifactRequest',
      '3': '.kumiho.ArtifactResponse'
    },
    {
      '1': 'GetArtifacts',
      '2': '.kumiho.GetArtifactsRequest',
      '3': '.kumiho.GetArtifactsResponse'
    },
    {
      '1': 'GetArtifactsByLocation',
      '2': '.kumiho.GetArtifactsByLocationRequest',
      '3': '.kumiho.GetArtifactsByLocationResponse'
    },
    {
      '1': 'DeleteArtifact',
      '2': '.kumiho.DeleteArtifactRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'UpdateArtifactMetadata',
      '2': '.kumiho.UpdateMetadataRequest',
      '3': '.kumiho.ArtifactResponse'
    },
    {
      '1': 'SetAttribute',
      '2': '.kumiho.SetAttributeRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'GetAttribute',
      '2': '.kumiho.GetAttributeRequest',
      '3': '.kumiho.GetAttributeResponse'
    },
    {
      '1': 'DeleteAttribute',
      '2': '.kumiho.DeleteAttributeRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'CreateEdge',
      '2': '.kumiho.CreateEdgeRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'GetEdges',
      '2': '.kumiho.GetEdgesRequest',
      '3': '.kumiho.GetEdgesResponse'
    },
    {
      '1': 'DeleteEdge',
      '2': '.kumiho.DeleteEdgeRequest',
      '3': '.kumiho.StatusResponse'
    },
    {
      '1': 'TraverseEdges',
      '2': '.kumiho.TraverseEdgesRequest',
      '3': '.kumiho.TraverseEdgesResponse'
    },
    {
      '1': 'FindShortestPath',
      '2': '.kumiho.ShortestPathRequest',
      '3': '.kumiho.ShortestPathResponse'
    },
    {
      '1': 'AnalyzeImpact',
      '2': '.kumiho.ImpactAnalysisRequest',
      '3': '.kumiho.ImpactAnalysisResponse'
    },
    {
      '1': 'CreateBundle',
      '2': '.kumiho.CreateBundleRequest',
      '3': '.kumiho.ItemResponse'
    },
    {
      '1': 'AddBundleMember',
      '2': '.kumiho.AddBundleMemberRequest',
      '3': '.kumiho.AddBundleMemberResponse'
    },
    {
      '1': 'RemoveBundleMember',
      '2': '.kumiho.RemoveBundleMemberRequest',
      '3': '.kumiho.RemoveBundleMemberResponse'
    },
    {
      '1': 'GetBundleMembers',
      '2': '.kumiho.GetBundleMembersRequest',
      '3': '.kumiho.GetBundleMembersResponse'
    },
    {
      '1': 'GetBundleHistory',
      '2': '.kumiho.GetBundleHistoryRequest',
      '3': '.kumiho.GetBundleHistoryResponse'
    },
    {
      '1': 'GetTenantUsage',
      '2': '.kumiho.GetTenantUsageRequest',
      '3': '.kumiho.TenantUsageResponse'
    },
    {
      '1': 'EventStream',
      '2': '.kumiho.EventStreamRequest',
      '3': '.kumiho.Event',
      '6': true
    },
    {
      '1': 'GetEventCapabilities',
      '2': '.kumiho.GetEventCapabilitiesRequest',
      '3': '.kumiho.EventCapabilities'
    },
    {
      '1': 'SetDeprecated',
      '2': '.kumiho.SetDeprecatedRequest',
      '3': '.kumiho.StatusResponse'
    },
  ],
};

@$core.Deprecated('Use kumihoServiceDescriptor instead')
const $core.Map<$core.String, $core.Map<$core.String, $core.dynamic>>
    KumihoServiceBase$messageJson = {
  '.kumiho.CreateProjectRequest': CreateProjectRequest$json,
  '.kumiho.ProjectResponse': ProjectResponse$json,
  '.kumiho.GetProjectsRequest': GetProjectsRequest$json,
  '.kumiho.GetProjectsResponse': GetProjectsResponse$json,
  '.kumiho.UpdateProjectRequest': UpdateProjectRequest$json,
  '.kumiho.DeleteProjectRequest': DeleteProjectRequest$json,
  '.kumiho.StatusResponse': StatusResponse$json,
  '.kumiho.CreateSpaceRequest': CreateSpaceRequest$json,
  '.kumiho.SpaceResponse': SpaceResponse$json,
  '.kumiho.SpaceResponse.MetadataEntry': SpaceResponse_MetadataEntry$json,
  '.kumiho.GetSpaceRequest': GetSpaceRequest$json,
  '.kumiho.GetChildSpacesRequest': GetChildSpacesRequest$json,
  '.kumiho.PaginationRequest': PaginationRequest$json,
  '.kumiho.GetChildSpacesResponse': GetChildSpacesResponse$json,
  '.kumiho.PaginationResponse': PaginationResponse$json,
  '.kumiho.DeleteSpaceRequest': DeleteSpaceRequest$json,
  '.kumiho.UpdateMetadataRequest': UpdateMetadataRequest$json,
  '.kumiho.Kref': Kref$json,
  '.kumiho.UpdateMetadataRequest.MetadataEntry':
      UpdateMetadataRequest_MetadataEntry$json,
  '.kumiho.CreateItemRequest': CreateItemRequest$json,
  '.kumiho.ItemResponse': ItemResponse$json,
  '.kumiho.ItemResponse.MetadataEntry': ItemResponse_MetadataEntry$json,
  '.kumiho.GetItemRequest': GetItemRequest$json,
  '.kumiho.GetItemsRequest': GetItemsRequest$json,
  '.kumiho.GetItemsResponse': GetItemsResponse$json,
  '.kumiho.ItemSearchRequest': ItemSearchRequest$json,
  '.kumiho.DeleteItemRequest': DeleteItemRequest$json,
  '.kumiho.ResolveKrefRequest': ResolveKrefRequest$json,
  '.kumiho.RevisionResponse': RevisionResponse$json,
  '.kumiho.RevisionResponse.MetadataEntry': RevisionResponse_MetadataEntry$json,
  '.kumiho.ResolveLocationRequest': ResolveLocationRequest$json,
  '.kumiho.ResolveLocationResponse': ResolveLocationResponse$json,
  '.kumiho.CreateRevisionRequest': CreateRevisionRequest$json,
  '.kumiho.CreateRevisionRequest.MetadataEntry':
      CreateRevisionRequest_MetadataEntry$json,
  '.kumiho.KrefRequest': KrefRequest$json,
  '.kumiho.GetRevisionsRequest': GetRevisionsRequest$json,
  '.kumiho.GetRevisionsResponse': GetRevisionsResponse$json,
  '.kumiho.DeleteRevisionRequest': DeleteRevisionRequest$json,
  '.kumiho.PeekNextRevisionRequest': PeekNextRevisionRequest$json,
  '.kumiho.PeekNextRevisionResponse': PeekNextRevisionResponse$json,
  '.kumiho.TagRevisionRequest': TagRevisionRequest$json,
  '.kumiho.UnTagRevisionRequest': UnTagRevisionRequest$json,
  '.kumiho.HasTagRequest': HasTagRequest$json,
  '.kumiho.HasTagResponse': HasTagResponse$json,
  '.kumiho.WasTaggedRequest': WasTaggedRequest$json,
  '.kumiho.WasTaggedResponse': WasTaggedResponse$json,
  '.kumiho.SetDefaultArtifactRequest': SetDefaultArtifactRequest$json,
  '.kumiho.CreateArtifactRequest': CreateArtifactRequest$json,
  '.kumiho.CreateArtifactRequest.MetadataEntry':
      CreateArtifactRequest_MetadataEntry$json,
  '.kumiho.ArtifactResponse': ArtifactResponse$json,
  '.kumiho.ArtifactResponse.MetadataEntry': ArtifactResponse_MetadataEntry$json,
  '.kumiho.GetArtifactRequest': GetArtifactRequest$json,
  '.kumiho.GetArtifactsRequest': GetArtifactsRequest$json,
  '.kumiho.GetArtifactsResponse': GetArtifactsResponse$json,
  '.kumiho.GetArtifactsByLocationRequest': GetArtifactsByLocationRequest$json,
  '.kumiho.GetArtifactsByLocationResponse': GetArtifactsByLocationResponse$json,
  '.kumiho.DeleteArtifactRequest': DeleteArtifactRequest$json,
  '.kumiho.SetAttributeRequest': SetAttributeRequest$json,
  '.kumiho.GetAttributeRequest': GetAttributeRequest$json,
  '.kumiho.GetAttributeResponse': GetAttributeResponse$json,
  '.kumiho.DeleteAttributeRequest': DeleteAttributeRequest$json,
  '.kumiho.CreateEdgeRequest': CreateEdgeRequest$json,
  '.kumiho.CreateEdgeRequest.MetadataEntry':
      CreateEdgeRequest_MetadataEntry$json,
  '.kumiho.GetEdgesRequest': GetEdgesRequest$json,
  '.kumiho.GetEdgesResponse': GetEdgesResponse$json,
  '.kumiho.Edge': Edge$json,
  '.kumiho.Edge.MetadataEntry': Edge_MetadataEntry$json,
  '.kumiho.DeleteEdgeRequest': DeleteEdgeRequest$json,
  '.kumiho.TraverseEdgesRequest': TraverseEdgesRequest$json,
  '.kumiho.TraverseEdgesResponse': TraverseEdgesResponse$json,
  '.kumiho.RevisionPath': RevisionPath$json,
  '.kumiho.PathStep': PathStep$json,
  '.kumiho.ShortestPathRequest': ShortestPathRequest$json,
  '.kumiho.ShortestPathResponse': ShortestPathResponse$json,
  '.kumiho.ImpactAnalysisRequest': ImpactAnalysisRequest$json,
  '.kumiho.ImpactAnalysisResponse': ImpactAnalysisResponse$json,
  '.kumiho.ImpactedRevision': ImpactedRevision$json,
  '.kumiho.CreateBundleRequest': CreateBundleRequest$json,
  '.kumiho.CreateBundleRequest.MetadataEntry':
      CreateBundleRequest_MetadataEntry$json,
  '.kumiho.AddBundleMemberRequest': AddBundleMemberRequest$json,
  '.kumiho.AddBundleMemberRequest.MetadataEntry':
      AddBundleMemberRequest_MetadataEntry$json,
  '.kumiho.AddBundleMemberResponse': AddBundleMemberResponse$json,
  '.kumiho.RemoveBundleMemberRequest': RemoveBundleMemberRequest$json,
  '.kumiho.RemoveBundleMemberRequest.MetadataEntry':
      RemoveBundleMemberRequest_MetadataEntry$json,
  '.kumiho.RemoveBundleMemberResponse': RemoveBundleMemberResponse$json,
  '.kumiho.GetBundleMembersRequest': GetBundleMembersRequest$json,
  '.kumiho.GetBundleMembersResponse': GetBundleMembersResponse$json,
  '.kumiho.BundleMember': BundleMember$json,
  '.kumiho.GetBundleHistoryRequest': GetBundleHistoryRequest$json,
  '.kumiho.GetBundleHistoryResponse': GetBundleHistoryResponse$json,
  '.kumiho.BundleRevisionHistory': BundleRevisionHistory$json,
  '.kumiho.BundleRevisionHistory.MetadataEntry':
      BundleRevisionHistory_MetadataEntry$json,
  '.kumiho.GetTenantUsageRequest': GetTenantUsageRequest$json,
  '.kumiho.TenantUsageResponse': TenantUsageResponse$json,
  '.kumiho.EventStreamRequest': EventStreamRequest$json,
  '.kumiho.Event': Event$json,
  '.kumiho.Event.DetailsEntry': Event_DetailsEntry$json,
  '.kumiho.GetEventCapabilitiesRequest': GetEventCapabilitiesRequest$json,
  '.kumiho.EventCapabilities': EventCapabilities$json,
  '.kumiho.SetDeprecatedRequest': SetDeprecatedRequest$json,
};

/// Descriptor for `KumihoService`. Decode as a `google.protobuf.ServiceDescriptorProto`.
final $typed_data.Uint8List kumihoServiceDescriptor = $convert.base64Decode(
    'Cg1LdW1paG9TZXJ2aWNlEkYKDUNyZWF0ZVByb2plY3QSHC5rdW1paG8uQ3JlYXRlUHJvamVjdF'
    'JlcXVlc3QaFy5rdW1paG8uUHJvamVjdFJlc3BvbnNlEkYKC0dldFByb2plY3RzEhoua3VtaWhv'
    'LkdldFByb2plY3RzUmVxdWVzdBobLmt1bWloby5HZXRQcm9qZWN0c1Jlc3BvbnNlEkYKDVVwZG'
    'F0ZVByb2plY3QSHC5rdW1paG8uVXBkYXRlUHJvamVjdFJlcXVlc3QaFy5rdW1paG8uUHJvamVj'
    'dFJlc3BvbnNlEkUKDURlbGV0ZVByb2plY3QSHC5rdW1paG8uRGVsZXRlUHJvamVjdFJlcXVlc3'
    'QaFi5rdW1paG8uU3RhdHVzUmVzcG9uc2USQAoLQ3JlYXRlU3BhY2USGi5rdW1paG8uQ3JlYXRl'
    'U3BhY2VSZXF1ZXN0GhUua3VtaWhvLlNwYWNlUmVzcG9uc2USOgoIR2V0U3BhY2USFy5rdW1paG'
    '8uR2V0U3BhY2VSZXF1ZXN0GhUua3VtaWhvLlNwYWNlUmVzcG9uc2USTwoOR2V0Q2hpbGRTcGFj'
    'ZXMSHS5rdW1paG8uR2V0Q2hpbGRTcGFjZXNSZXF1ZXN0Gh4ua3VtaWhvLkdldENoaWxkU3BhY2'
    'VzUmVzcG9uc2USQQoLRGVsZXRlU3BhY2USGi5rdW1paG8uRGVsZXRlU3BhY2VSZXF1ZXN0GhYu'
    'a3VtaWhvLlN0YXR1c1Jlc3BvbnNlEksKE1VwZGF0ZVNwYWNlTWV0YWRhdGESHS5rdW1paG8uVX'
    'BkYXRlTWV0YWRhdGFSZXF1ZXN0GhUua3VtaWhvLlNwYWNlUmVzcG9uc2USPQoKQ3JlYXRlSXRl'
    'bRIZLmt1bWloby5DcmVhdGVJdGVtUmVxdWVzdBoULmt1bWloby5JdGVtUmVzcG9uc2USNwoHR2'
    'V0SXRlbRIWLmt1bWloby5HZXRJdGVtUmVxdWVzdBoULmt1bWloby5JdGVtUmVzcG9uc2USPQoI'
    'R2V0SXRlbXMSFy5rdW1paG8uR2V0SXRlbXNSZXF1ZXN0Ghgua3VtaWhvLkdldEl0ZW1zUmVzcG'
    '9uc2USQQoKSXRlbVNlYXJjaBIZLmt1bWloby5JdGVtU2VhcmNoUmVxdWVzdBoYLmt1bWloby5H'
    'ZXRJdGVtc1Jlc3BvbnNlEj8KCkRlbGV0ZUl0ZW0SGS5rdW1paG8uRGVsZXRlSXRlbVJlcXVlc3'
    'QaFi5rdW1paG8uU3RhdHVzUmVzcG9uc2USSQoSVXBkYXRlSXRlbU1ldGFkYXRhEh0ua3VtaWhv'
    'LlVwZGF0ZU1ldGFkYXRhUmVxdWVzdBoULmt1bWloby5JdGVtUmVzcG9uc2USQwoLUmVzb2x2ZU'
    'tyZWYSGi5rdW1paG8uUmVzb2x2ZUtyZWZSZXF1ZXN0Ghgua3VtaWhvLlJldmlzaW9uUmVzcG9u'
    'c2USUgoPUmVzb2x2ZUxvY2F0aW9uEh4ua3VtaWhvLlJlc29sdmVMb2NhdGlvblJlcXVlc3QaHy'
    '5rdW1paG8uUmVzb2x2ZUxvY2F0aW9uUmVzcG9uc2USSQoOQ3JlYXRlUmV2aXNpb24SHS5rdW1p'
    'aG8uQ3JlYXRlUmV2aXNpb25SZXF1ZXN0Ghgua3VtaWhvLlJldmlzaW9uUmVzcG9uc2USPAoLR2'
    'V0UmV2aXNpb24SEy5rdW1paG8uS3JlZlJlcXVlc3QaGC5rdW1paG8uUmV2aXNpb25SZXNwb25z'
    'ZRJJCgxHZXRSZXZpc2lvbnMSGy5rdW1paG8uR2V0UmV2aXNpb25zUmVxdWVzdBocLmt1bWloby'
    '5HZXRSZXZpc2lvbnNSZXNwb25zZRJHCg5EZWxldGVSZXZpc2lvbhIdLmt1bWloby5EZWxldGVS'
    'ZXZpc2lvblJlcXVlc3QaFi5rdW1paG8uU3RhdHVzUmVzcG9uc2USVQoQUGVla05leHRSZXZpc2'
    'lvbhIfLmt1bWloby5QZWVrTmV4dFJldmlzaW9uUmVxdWVzdBogLmt1bWloby5QZWVrTmV4dFJl'
    'dmlzaW9uUmVzcG9uc2USUQoWVXBkYXRlUmV2aXNpb25NZXRhZGF0YRIdLmt1bWloby5VcGRhdG'
    'VNZXRhZGF0YVJlcXVlc3QaGC5rdW1paG8uUmV2aXNpb25SZXNwb25zZRJBCgtUYWdSZXZpc2lv'
    'bhIaLmt1bWloby5UYWdSZXZpc2lvblJlcXVlc3QaFi5rdW1paG8uU3RhdHVzUmVzcG9uc2USRQ'
    'oNVW5UYWdSZXZpc2lvbhIcLmt1bWloby5VblRhZ1JldmlzaW9uUmVxdWVzdBoWLmt1bWloby5T'
    'dGF0dXNSZXNwb25zZRI3CgZIYXNUYWcSFS5rdW1paG8uSGFzVGFnUmVxdWVzdBoWLmt1bWloby'
    '5IYXNUYWdSZXNwb25zZRJACglXYXNUYWdnZWQSGC5rdW1paG8uV2FzVGFnZ2VkUmVxdWVzdBoZ'
    'Lmt1bWloby5XYXNUYWdnZWRSZXNwb25zZRJPChJTZXREZWZhdWx0QXJ0aWZhY3QSIS5rdW1paG'
    '8uU2V0RGVmYXVsdEFydGlmYWN0UmVxdWVzdBoWLmt1bWloby5TdGF0dXNSZXNwb25zZRJJCg5D'
    'cmVhdGVBcnRpZmFjdBIdLmt1bWloby5DcmVhdGVBcnRpZmFjdFJlcXVlc3QaGC5rdW1paG8uQX'
    'J0aWZhY3RSZXNwb25zZRJDCgtHZXRBcnRpZmFjdBIaLmt1bWloby5HZXRBcnRpZmFjdFJlcXVl'
    'c3QaGC5rdW1paG8uQXJ0aWZhY3RSZXNwb25zZRJJCgxHZXRBcnRpZmFjdHMSGy5rdW1paG8uR2'
    'V0QXJ0aWZhY3RzUmVxdWVzdBocLmt1bWloby5HZXRBcnRpZmFjdHNSZXNwb25zZRJnChZHZXRB'
    'cnRpZmFjdHNCeUxvY2F0aW9uEiUua3VtaWhvLkdldEFydGlmYWN0c0J5TG9jYXRpb25SZXF1ZX'
    'N0GiYua3VtaWhvLkdldEFydGlmYWN0c0J5TG9jYXRpb25SZXNwb25zZRJHCg5EZWxldGVBcnRp'
    'ZmFjdBIdLmt1bWloby5EZWxldGVBcnRpZmFjdFJlcXVlc3QaFi5rdW1paG8uU3RhdHVzUmVzcG'
    '9uc2USUQoWVXBkYXRlQXJ0aWZhY3RNZXRhZGF0YRIdLmt1bWloby5VcGRhdGVNZXRhZGF0YVJl'
    'cXVlc3QaGC5rdW1paG8uQXJ0aWZhY3RSZXNwb25zZRJDCgxTZXRBdHRyaWJ1dGUSGy5rdW1paG'
    '8uU2V0QXR0cmlidXRlUmVxdWVzdBoWLmt1bWloby5TdGF0dXNSZXNwb25zZRJJCgxHZXRBdHRy'
    'aWJ1dGUSGy5rdW1paG8uR2V0QXR0cmlidXRlUmVxdWVzdBocLmt1bWloby5HZXRBdHRyaWJ1dG'
    'VSZXNwb25zZRJJCg9EZWxldGVBdHRyaWJ1dGUSHi5rdW1paG8uRGVsZXRlQXR0cmlidXRlUmVx'
    'dWVzdBoWLmt1bWloby5TdGF0dXNSZXNwb25zZRI/CgpDcmVhdGVFZGdlEhkua3VtaWhvLkNyZW'
    'F0ZUVkZ2VSZXF1ZXN0GhYua3VtaWhvLlN0YXR1c1Jlc3BvbnNlEj0KCEdldEVkZ2VzEhcua3Vt'
    'aWhvLkdldEVkZ2VzUmVxdWVzdBoYLmt1bWloby5HZXRFZGdlc1Jlc3BvbnNlEj8KCkRlbGV0ZU'
    'VkZ2USGS5rdW1paG8uRGVsZXRlRWRnZVJlcXVlc3QaFi5rdW1paG8uU3RhdHVzUmVzcG9uc2US'
    'TAoNVHJhdmVyc2VFZGdlcxIcLmt1bWloby5UcmF2ZXJzZUVkZ2VzUmVxdWVzdBodLmt1bWloby'
    '5UcmF2ZXJzZUVkZ2VzUmVzcG9uc2USTQoQRmluZFNob3J0ZXN0UGF0aBIbLmt1bWloby5TaG9y'
    'dGVzdFBhdGhSZXF1ZXN0Ghwua3VtaWhvLlNob3J0ZXN0UGF0aFJlc3BvbnNlEk4KDUFuYWx5em'
    'VJbXBhY3QSHS5rdW1paG8uSW1wYWN0QW5hbHlzaXNSZXF1ZXN0Gh4ua3VtaWhvLkltcGFjdEFu'
    'YWx5c2lzUmVzcG9uc2USQQoMQ3JlYXRlQnVuZGxlEhsua3VtaWhvLkNyZWF0ZUJ1bmRsZVJlcX'
    'Vlc3QaFC5rdW1paG8uSXRlbVJlc3BvbnNlElIKD0FkZEJ1bmRsZU1lbWJlchIeLmt1bWloby5B'
    'ZGRCdW5kbGVNZW1iZXJSZXF1ZXN0Gh8ua3VtaWhvLkFkZEJ1bmRsZU1lbWJlclJlc3BvbnNlEl'
    'sKElJlbW92ZUJ1bmRsZU1lbWJlchIhLmt1bWloby5SZW1vdmVCdW5kbGVNZW1iZXJSZXF1ZXN0'
    'GiIua3VtaWhvLlJlbW92ZUJ1bmRsZU1lbWJlclJlc3BvbnNlElUKEEdldEJ1bmRsZU1lbWJlcn'
    'MSHy5rdW1paG8uR2V0QnVuZGxlTWVtYmVyc1JlcXVlc3QaIC5rdW1paG8uR2V0QnVuZGxlTWVt'
    'YmVyc1Jlc3BvbnNlElUKEEdldEJ1bmRsZUhpc3RvcnkSHy5rdW1paG8uR2V0QnVuZGxlSGlzdG'
    '9yeVJlcXVlc3QaIC5rdW1paG8uR2V0QnVuZGxlSGlzdG9yeVJlc3BvbnNlEkwKDkdldFRlbmFu'
    'dFVzYWdlEh0ua3VtaWhvLkdldFRlbmFudFVzYWdlUmVxdWVzdBobLmt1bWloby5UZW5hbnRVc2'
    'FnZVJlc3BvbnNlEjoKC0V2ZW50U3RyZWFtEhoua3VtaWhvLkV2ZW50U3RyZWFtUmVxdWVzdBoN'
    'Lmt1bWloby5FdmVudDABElYKFEdldEV2ZW50Q2FwYWJpbGl0aWVzEiMua3VtaWhvLkdldEV2ZW'
    '50Q2FwYWJpbGl0aWVzUmVxdWVzdBoZLmt1bWloby5FdmVudENhcGFiaWxpdGllcxJFCg1TZXRE'
    'ZXByZWNhdGVkEhwua3VtaWhvLlNldERlcHJlY2F0ZWRSZXF1ZXN0GhYua3VtaWhvLlN0YXR1c1'
    'Jlc3BvbnNl');
