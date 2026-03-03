// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Kumiho model classes for fluent API usage.
///
/// This module exports all high-level domain objects that provide
/// a fluent, Pythonic API for interacting with Kumiho.
///
/// The symbols exported here are the ones surfaced in generated
/// `dartdoc` output. They wrap the underlying protobuf messages and
/// expose ergonomic methods instead of raw RPC stubs, so integrators
/// can stay in the model layer when building applications or tooling.
///
/// ```dart
/// import 'package:kumiho/models.dart';
///
/// // Or import everything via the main library
/// import 'package:kumiho/kumiho.dart';
/// ```
library;

export 'src/models/base.dart';
export 'src/models/project.dart';
export 'src/models/space.dart';
export 'src/models/item.dart';
export 'src/models/revision.dart';
export 'src/models/artifact.dart';
export 'src/models/edge.dart';
export 'src/models/bundle.dart';
