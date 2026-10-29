# Changelog

All notable changes to the Kumiho Dart SDK are documented here, in the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. This file
starts with the kref parser release; earlier history is in the git log.

The grammar and the conformance corpus all SDKs share are in
[`../spec/kref/`](../spec/kref/README.md).

## [Unreleased]

### Changed
- No change to the library. `KumihoClient.getItemByKref` already split an item
  kref at its last `/` and its last `.`, and `Kref.itemName` and `Kref.kind`
  already read the text before and after the last `.`, so nested spaces, dotted
  item names, dotted spaces and bundles with dotted names were already looked up
  as the kref names them. An item kref with no kind (`kref://p/s.v1/x`) was
  already refused with `ArgumentError` before sending.
- A kind that contains `/` is not valid and cannot be named by a kref, so
  `getItemByKref` refuses it the same way.

### Added
- `test/kref_vectors_test.dart` verifies the client against the shared kref
  conformance corpus (`spec/kref/vectors.json`): for every kref the Python SDK
  accepts, the `GetItem` request is the corpus's, and a leaf with no `.` where an
  item is required is refused before anything is sent. The only difference is
  the legacy `kref:///s/x.k` spelling, which Dart sends as `/s` where the corpus
  has `//s` (kumiho-server normalizes both to the same space).

### Upgrading
- Nothing to do. The same rules now hold across the Python, Rust, Go, C++ and
  Dart SDKs: derive the item name and kind from the text before and after the
  last `.` of a kref's last segment, and take the stored kind from the item the
  server returns.

