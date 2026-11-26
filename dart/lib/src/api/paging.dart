// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../models/base.dart' show KumihoError;
import '../models/paged_list.dart';

/// Page size requested when following every page (kumiho-db's maximum).
const int followPageSize = 1000;

/// Follows `nextCursor` across pages and returns every item.
///
/// `fetchPage(cursor)` returns one [PagedList]; the first call gets a null
/// cursor. Stops when the server reports no more results or sent no
/// pagination field (kumiho-server CE answers GetEdges in one response
/// without one). A page may be empty while `hasMore` is true, because
/// kumiho-db caps each call's scan. A cursor that repeats, or `hasMore`
/// without a cursor, throws [KumihoError] rather than looping forever or
/// returning a silently partial list.
///
/// `key(item)` drops items an earlier page already returned: CE pages
/// GetRevisions by offset, newest first, so a revision created between two
/// pages shifts the window and the next page repeats a row.
Future<List<T>> collectPages<T>(
  String rpcName,
  Future<PagedList<T>> Function(String? cursor) fetchPage,
  Object Function(T item) key,
) async {
  final results = <T>[];
  final returned = <Object>{};
  final seen = <String>{};
  String? cursor;
  while (true) {
    final page = await fetchPage(cursor);
    for (final item in page) {
      if (returned.add(key(item))) {
        results.add(item);
      }
    }
    if (!page.paginationPresent || page.hasMore != true) {
      return results;
    }
    final next = page.nextCursor;
    if (next == null || next.isEmpty) {
      throw KumihoError(
        '$rpcName reported more results but returned no pagination cursor',
      );
    }
    if (!seen.add(next)) {
      throw KumihoError(
        '$rpcName returned a pagination cursor that did not advance',
      );
    }
    cursor = next;
  }
}
