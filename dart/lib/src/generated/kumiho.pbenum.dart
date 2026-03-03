// This is a generated file - do not edit.
//
// Generated from kumiho.proto.

// @dart = 3.3

// ignore_for_file: annotate_overrides, camel_case_types, comment_references
// ignore_for_file: constant_identifier_names
// ignore_for_file: curly_braces_in_flow_control_structures
// ignore_for_file: deprecated_member_use_from_same_package, library_prefixes
// ignore_for_file: non_constant_identifier_names, prefer_relative_imports

import 'dart:core' as $core;

import 'package:protobuf/protobuf.dart' as $pb;

class EdgeDirection extends $pb.ProtobufEnum {
  static const EdgeDirection OUTGOING =
      EdgeDirection._(0, _omitEnumNames ? '' : 'OUTGOING');
  static const EdgeDirection INCOMING =
      EdgeDirection._(1, _omitEnumNames ? '' : 'INCOMING');
  static const EdgeDirection BOTH =
      EdgeDirection._(2, _omitEnumNames ? '' : 'BOTH');

  static const $core.List<EdgeDirection> values = <EdgeDirection>[
    OUTGOING,
    INCOMING,
    BOTH,
  ];

  static final $core.List<EdgeDirection?> _byValue =
      $pb.ProtobufEnum.$_initByValueList(values, 2);
  static EdgeDirection? valueOf($core.int value) =>
      value < 0 || value >= _byValue.length ? null : _byValue[value];

  const EdgeDirection._(super.value, super.name);
}

const $core.bool _omitEnumNames =
    $core.bool.fromEnvironment('protobuf.omit_enum_names');
