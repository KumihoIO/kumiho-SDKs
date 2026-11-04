// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'dart:collection';

/// A list that also contains pagination information.
class PagedList<T> extends ListBase<T> {
  final List<T> _inner;

  /// The cursor for the next page of results.
  final String? nextCursor;

  /// The total number of items available.
  final int? totalCount;

  /// Server continuation flag; null when the server omitted metadata.
  final bool? hasMore;

  /// Distinguishes an empty final page from an older response without metadata.
  final bool paginationPresent;

  PagedList(
    this._inner, {
    this.nextCursor,
    this.totalCount,
    this.hasMore,
    bool? paginationPresent,
  }) : paginationPresent =
           paginationPresent ??
           (nextCursor != null || totalCount != null || hasMore != null);

  @override
  int get length => _inner.length;

  @override
  set length(int newLength) => _inner.length = newLength;

  @override
  T operator [](int index) => _inner[index];

  @override
  void operator []=(int index, T value) => _inner[index] = value;
}
