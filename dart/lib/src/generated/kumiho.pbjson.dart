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

@$core.Deprecated('Use searchRequestDescriptor instead')
const SearchRequest$json = {
  '1': 'SearchRequest',
  '2': [
    {'1': 'query', '3': 1, '4': 1, '5': 9, '10': 'query'},
    {'1': 'context_filter', '3': 2, '4': 1, '5': 9, '10': 'contextFilter'},
    {'1': 'kind_filter', '3': 3, '4': 1, '5': 9, '10': 'kindFilter'},
    {
      '1': 'include_deprecated',
      '3': 4,
      '4': 1,
      '5': 8,
      '10': 'includeDeprecated'
    },
    {
      '1': 'pagination',
      '3': 5,
      '4': 1,
      '5': 11,
      '6': '.kumiho.PaginationRequest',
      '9': 0,
      '10': 'pagination',
      '17': true
    },
    {'1': 'min_score', '3': 6, '4': 1, '5': 2, '10': 'minScore'},
    {
      '1': 'include_revision_metadata',
      '3': 7,
      '4': 1,
      '5': 8,
      '10': 'includeRevisionMetadata'
    },
    {
      '1': 'include_artifact_metadata',
      '3': 8,
      '4': 1,
      '5': 8,
      '10': 'includeArtifactMetadata'
    },
  ],
  '8': [
    {'1': '_pagination'},
  ],
};

/// Descriptor for `SearchRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List searchRequestDescriptor = $convert.base64Decode(
    'Cg1TZWFyY2hSZXF1ZXN0EhQKBXF1ZXJ5GAEgASgJUgVxdWVyeRIlCg5jb250ZXh0X2ZpbHRlch'
    'gCIAEoCVINY29udGV4dEZpbHRlchIfCgtraW5kX2ZpbHRlchgDIAEoCVIKa2luZEZpbHRlchIt'
    'ChJpbmNsdWRlX2RlcHJlY2F0ZWQYBCABKAhSEWluY2x1ZGVEZXByZWNhdGVkEj4KCnBhZ2luYX'
    'Rpb24YBSABKAsyGS5rdW1paG8uUGFnaW5hdGlvblJlcXVlc3RIAFIKcGFnaW5hdGlvbogBARIb'
    'CgltaW5fc2NvcmUYBiABKAJSCG1pblNjb3JlEjoKGWluY2x1ZGVfcmV2aXNpb25fbWV0YWRhdG'
    'EYByABKAhSF2luY2x1ZGVSZXZpc2lvbk1ldGFkYXRhEjoKGWluY2x1ZGVfYXJ0aWZhY3RfbWV0'
    'YWRhdGEYCCABKAhSF2luY2x1ZGVBcnRpZmFjdE1ldGFkYXRhQg0KC19wYWdpbmF0aW9u');

@$core.Deprecated('Use searchResultDescriptor instead')
const SearchResult$json = {
  '1': 'SearchResult',
  '2': [
    {
      '1': 'item',
      '3': 1,
      '4': 1,
      '5': 11,
      '6': '.kumiho.ItemResponse',
      '10': 'item'
    },
    {'1': 'score', '3': 2, '4': 1, '5': 2, '10': 'score'},
    {'1': 'matched_in', '3': 3, '4': 3, '5': 9, '10': 'matchedIn'},
  ],
};

/// Descriptor for `SearchResult`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List searchResultDescriptor = $convert.base64Decode(
    'CgxTZWFyY2hSZXN1bHQSKAoEaXRlbRgBIAEoCzIULmt1bWloby5JdGVtUmVzcG9uc2VSBGl0ZW'
    '0SFAoFc2NvcmUYAiABKAJSBXNjb3JlEh0KCm1hdGNoZWRfaW4YAyADKAlSCW1hdGNoZWRJbg==');

@$core.Deprecated('Use searchResponseDescriptor instead')
const SearchResponse$json = {
  '1': 'SearchResponse',
  '2': [
    {
      '1': 'results',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.SearchResult',
      '10': 'results'
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
    {
      '1': 'search_mode',
      '3': 3,
      '4': 1,
      '5': 9,
      '9': 1,
      '10': 'searchMode',
      '17': true
    },
  ],
  '8': [
    {'1': '_pagination'},
    {'1': '_search_mode'},
  ],
};

/// Descriptor for `SearchResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List searchResponseDescriptor = $convert.base64Decode(
    'Cg5TZWFyY2hSZXNwb25zZRIuCgdyZXN1bHRzGAEgAygLMhQua3VtaWhvLlNlYXJjaFJlc3VsdF'
    'IHcmVzdWx0cxI/CgpwYWdpbmF0aW9uGAIgASgLMhoua3VtaWhvLlBhZ2luYXRpb25SZXNwb25z'
    'ZUgAUgpwYWdpbmF0aW9uiAEBEiQKC3NlYXJjaF9tb2RlGAMgASgJSAFSCnNlYXJjaE1vZGWIAQ'
    'FCDQoLX3BhZ2luYXRpb25CDgoMX3NlYXJjaF9tb2Rl');

@$core.Deprecated('Use scoreRevisionsRequestDescriptor instead')
const ScoreRevisionsRequest$json = {
  '1': 'ScoreRevisionsRequest',
  '2': [
    {'1': 'query', '3': 1, '4': 1, '5': 9, '10': 'query'},
    {
      '1': 'revision_krefs',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKrefs'
    },
    {'1': 'score_fields', '3': 3, '4': 3, '5': 9, '10': 'scoreFields'},
  ],
};

/// Descriptor for `ScoreRevisionsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List scoreRevisionsRequestDescriptor = $convert.base64Decode(
    'ChVTY29yZVJldmlzaW9uc1JlcXVlc3QSFAoFcXVlcnkYASABKAlSBXF1ZXJ5EjMKDnJldmlzaW'
    '9uX2tyZWZzGAIgAygLMgwua3VtaWhvLktyZWZSDXJldmlzaW9uS3JlZnMSIQoMc2NvcmVfZmll'
    'bGRzGAMgAygJUgtzY29yZUZpZWxkcw==');

@$core.Deprecated('Use scoredRevisionDescriptor instead')
const ScoredRevision$json = {
  '1': 'ScoredRevision',
  '2': [
    {'1': 'kref', '3': 1, '4': 1, '5': 11, '6': '.kumiho.Kref', '10': 'kref'},
    {'1': 'score', '3': 2, '4': 1, '5': 2, '10': 'score'},
    {'1': 'score_method', '3': 3, '4': 1, '5': 9, '10': 'scoreMethod'},
  ],
};

/// Descriptor for `ScoredRevision`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List scoredRevisionDescriptor = $convert.base64Decode(
    'Cg5TY29yZWRSZXZpc2lvbhIgCgRrcmVmGAEgASgLMgwua3VtaWhvLktyZWZSBGtyZWYSFAoFc2'
    'NvcmUYAiABKAJSBXNjb3JlEiEKDHNjb3JlX21ldGhvZBgDIAEoCVILc2NvcmVNZXRob2Q=');

@$core.Deprecated('Use scoreRevisionsResponseDescriptor instead')
const ScoreRevisionsResponse$json = {
  '1': 'ScoreRevisionsResponse',
  '2': [
    {
      '1': 'scored_revisions',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.ScoredRevision',
      '10': 'scoredRevisions'
    },
    {'1': 'search_mode', '3': 2, '4': 1, '5': 9, '10': 'searchMode'},
  ],
};

/// Descriptor for `ScoreRevisionsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List scoreRevisionsResponseDescriptor = $convert.base64Decode(
    'ChZTY29yZVJldmlzaW9uc1Jlc3BvbnNlEkEKEHNjb3JlZF9yZXZpc2lvbnMYASADKAsyFi5rdW'
    '1paG8uU2NvcmVkUmV2aXNpb25SD3Njb3JlZFJldmlzaW9ucxIfCgtzZWFyY2hfbW9kZRgCIAEo'
    'CVIKc2VhcmNoTW9kZQ==');

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
    {'1': 'embedding_text', '3': 5, '4': 1, '5': 9, '10': 'embeddingText'},
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
    'xleGlzdHNfZXJyb3IYBCABKAhSC2V4aXN0c0Vycm9yEiUKDmVtYmVkZGluZ190ZXh0GAUgASgJ'
    'Ug1lbWJlZGRpbmdUZXh0GjsKDU1ldGFkYXRhRW50cnkSEAoDa2V5GAEgASgJUgNrZXkSFAoFdm'
    'FsdWUYAiABKAlSBXZhbHVlOgI4AQ==');

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

@$core.Deprecated('Use batchGetRevisionsRequestDescriptor instead')
const BatchGetRevisionsRequest$json = {
  '1': 'BatchGetRevisionsRequest',
  '2': [
    {
      '1': 'revision_krefs',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'revisionKrefs'
    },
    {
      '1': 'item_krefs',
      '3': 2,
      '4': 3,
      '5': 11,
      '6': '.kumiho.Kref',
      '10': 'itemKrefs'
    },
    {'1': 'tag', '3': 3, '4': 1, '5': 9, '10': 'tag'},
    {'1': 'allow_partial', '3': 4, '4': 1, '5': 8, '10': 'allowPartial'},
  ],
};

/// Descriptor for `BatchGetRevisionsRequest`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List batchGetRevisionsRequestDescriptor = $convert.base64Decode(
    'ChhCYXRjaEdldFJldmlzaW9uc1JlcXVlc3QSMwoOcmV2aXNpb25fa3JlZnMYASADKAsyDC5rdW'
    '1paG8uS3JlZlINcmV2aXNpb25LcmVmcxIrCgppdGVtX2tyZWZzGAIgAygLMgwua3VtaWhvLkty'
    'ZWZSCWl0ZW1LcmVmcxIQCgN0YWcYAyABKAlSA3RhZxIjCg1hbGxvd19wYXJ0aWFsGAQgASgIUg'
    'xhbGxvd1BhcnRpYWw=');

@$core.Deprecated('Use batchGetRevisionsResponseDescriptor instead')
const BatchGetRevisionsResponse$json = {
  '1': 'BatchGetRevisionsResponse',
  '2': [
    {
      '1': 'revisions',
      '3': 1,
      '4': 3,
      '5': 11,
      '6': '.kumiho.RevisionResponse',
      '10': 'revisions'
    },
    {'1': 'not_found', '3': 2, '4': 3, '5': 9, '10': 'notFound'},
    {'1': 'requested_count', '3': 3, '4': 1, '5': 5, '10': 'requestedCount'},
    {'1': 'found_count', '3': 4, '4': 1, '5': 5, '10': 'foundCount'},
  ],
};

/// Descriptor for `BatchGetRevisionsResponse`. Decode as a `google.protobuf.DescriptorProto`.
final $typed_data.Uint8List batchGetRevisionsResponseDescriptor = $convert.base64Decode(
    'ChlCYXRjaEdldFJldmlzaW9uc1Jlc3BvbnNlEjYKCXJldmlzaW9ucxgBIAMoCzIYLmt1bWloby'
    '5SZXZpc2lvblJlc3BvbnNlUglyZXZpc2lvbnMSGwoJbm90X2ZvdW5kGAIgAygJUghub3RGb3Vu'
    'ZBInCg9yZXF1ZXN0ZWRfY291bnQYAyABKAVSDnJlcXVlc3RlZENvdW50Eh8KC2ZvdW5kX2NvdW'
    '50GAQgASgFUgpmb3VuZENvdW50');

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
