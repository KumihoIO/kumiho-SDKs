# Changelog

All notable changes to the Kumiho C++ SDK are documented here, in the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. This file
starts with the kref parser release; earlier history is in the git log.

The grammar and the conformance corpus all SDKs share are in
[`../spec/kref/`](../spec/kref/README.md).

## [Unreleased]

## [1.1.1] - 2026-11-26

### Fixed
- **`Client::getRevisions` and `Client::getEdges` return every row.** They sent
  no pagination and read only the first page, so on kumiho-db they returned at
  most 100 rows with no error. They now follow `next_cursor`, asking for 1000
  rows per page, until the server reports no more. A page can be empty while
  more remain; that is followed too.
- If the server sends no pagination field (kumiho-server CE `GetEdges`), the
  single response is treated as complete.
- A cursor that repeats, or `has_more` with an empty cursor, throws `RpcError`
  (code `INTERNAL`) instead of looping or returning a partial list.
- A row that repeats across pages is returned once. kumiho-server CE pages
  `GetRevisions` by offset, newest first, so a revision created during the walk
  shifts the next page by one row. Revisions are keyed by kref, edges by
  (source, target, edge type).

### Added
- `Client::getRevisionsPaged` and `Client::getEdgesPaged` return one
  `PagedList` with its `next_cursor`, like `getItemsPaged`.

## [1.1.0] - 2026-11-04

### Fixed
- **Item krefs with dotted names** (`kref://p/s/my.file.v2.k`) are looked up as
  the kref names them by `Client::getItemByKref` and `getItemFromRevision`: the
  item name is everything before the last `.`. They were cut at the first `.`,
  so the kind sent was `file.v2.k`. (Nested spaces already worked: this SDK split
  at the last `/`.)
- **`Client::getBundleByKref` fetches the bundle the kref names.** It looked the
  bundle up correctly and re-fetched it under the text before the *first* dot, so
  `kref://p/s/my.set.bundle` came back as `my.bundle`. The lookup and the
  re-fetch now use one split.

### Changed
- **`Kref::getKind()` is the text after the last `.`**, and so are
  **`Kref::getItemName()` and its alias `getProductName()`**, which are the text
  before it: `kref://p/s/my.file.v2.k` is item `my.file.v2`, kind `k` (it was
  item `my`, kind `file.v2.k`). Item names may contain dots; kinds never do.
- A leaf with no `.` where an item is required (`kref://p/s.v1/x`) still throws
  `ValidationError` before sending, as before. The SDK still does not validate
  krefs; that is unchanged.

### Added
- **`parseKref()` and `KrefParts`** (`kumiho/kref_parts.hpp`): one parser for the
  kumiho-db kernel's verdict and the parts of a kref, and
  `KrefParts::getItemTuple()` for the `GetItem` request. It never throws.

### Upgrading
- Code that derives an item name or kind from a kref: `getKind()`,
  `getItemName()` and `getProductName()` of a dotted item name changed, and an
  item stored with a dotted kind (`tar.gz`) has the kref `kref://p/s/x.tar.gz`,
  which the grammar reads as item `x.tar`, kind `gz`. Take the stored kind from
  the item the server returns (`Item::getKind()`), not from the kref. Do not
  split krefs by hand.

