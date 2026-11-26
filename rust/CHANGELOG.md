# Changelog

All notable changes to the Kumiho Rust SDK are documented here, in the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. This file
starts with the kref parser release; earlier history is in the git log.

The grammar and the conformance corpus all SDKs share are in
[`../spec/kref/`](../spec/kref/README.md).

## [Unreleased]

## [0.11.1] - 2026-11-26

### Fixed
- **`Client::get_revisions` and `Client::get_edges` return every row.** They
  sent no pagination and read only the first page, so on kumiho-db they
  returned at most 100 rows with no error. They now follow `next_cursor`,
  asking for 1000 rows per page, until the server reports no more. A page can
  be empty while more remain; that is followed too. The dashboard reads
  revisions and edges through these calls and is fixed with them.
- If the server sends no pagination field (kumiho-server CE `GetEdges`), the
  single response is treated as complete.
- A cursor that repeats, or `has_more` with an empty cursor, is returned as
  `Error::Rpc` with code `Internal` instead of looping or returning a partial
  list.
- A row that repeats across pages is returned once. kumiho-server CE pages
  `GetRevisions` by offset, newest first, so a revision created during the walk
  shifts the next page by one row. Revisions are keyed by kref, edges by
  (source, target, edge type).

### Added
- `Client::get_revisions_page` and `Client::get_edges_page` return one
  `Page` with its `next_cursor`, like `get_items` and `item_search`.

## [0.11.0] - 2026-11-04

### Fixed
- **Item krefs in nested spaces and with dotted names** (`kref://p/a/b/x.k`,
  `kref://p/s/my.file.v2.k`) are looked up as the kref names them by
  `Client::get_item_by_kref`, `get_item_from_revision` and `get_bundle_by_kref`:
  the parent path is everything before the last `/`, the item name everything
  before the last `.`. They used to be cut at the first `/` and the first `.`.
- **A bundle whose name contains a dot** (`kref://p/s/my.set.bundle`) is fetched.
  It used to be refused as "not a bundle" because the kind was read as
  `set.bundle`.

### Changed
- **`Kref::kind()` is the text after the last `.`** of the item name
  (`kref://p/s/my.file.v2.k` is kind `k`, was `file.v2.k`).
- **An item kref with no kind is refused before sending** with
  `Error::InvalidArgument` (`kref://p/s.v1/x` names a space; it used to be sent
  as item `s`, kind `v1/x`). A kind that contains `/` is not valid and is refused
  the same way.
- Validation (`validate_kref`, `Kref::new`) is unchanged, and every item kref is
  still validated before it is split.

### Added
- **`parse_kref()`, `KrefParts`, `KrefErrorClass` and `KrefShape`**: one parser
  for the kumiho-db kernel's verdict and the parts of a kref, and
  `KrefParts::get_item_tuple()` for the `GetItem` request. It never fails.
  `KrefErrorClass` implements `Display` as its corpus spelling. The three types
  are `#[non_exhaustive]`.
- `Kref::parts()`.

### Upgrading
- Code that derives an item name or kind from a kref: `Kref::kind()` of a dotted
  item name changed (the dashboard's event classification reads it), and an item
  stored with a dotted kind (`tar.gz`) has the kref `kref://p/s/x.tar.gz`, which
  the grammar reads as item `x.tar`, kind `gz`. Take the stored kind from the
  item the server returns, not from the kref. Do not split krefs by hand.

