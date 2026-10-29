# Changelog

All notable changes to the Kumiho Go SDK are documented here, in the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. This file
starts with the kref parser release; earlier history is in the git log.

The grammar and the conformance corpus all SDKs share are in
[`../spec/kref/`](../spec/kref/README.md).

## [Unreleased]

### Fixed
- **Item krefs in nested spaces and with dotted names** (`kref://p/a/b/x.k`,
  `kref://p/s/my.file.v2.k`) are looked up as the kref names them by
  `Client.GetItemByKref`, `GetItemFromRevision` and `GetBundleByKref`: the parent
  path is everything before the last `/`, the item name everything before the
  last `.`. They used to be cut at the first `/` and the first `.`.
- **A bundle whose name contains a dot** (`kref://p/s/my.set.bundle`) is fetched.
  It used to be refused as "not a bundle" because the kind was read as
  `set.bundle`.

### Changed
- **`Kref.Kind()` is the text after the last `.`** of the item name
  (`kref://p/s/my.file.v2.k` is kind `k`, was `file.v2.k`).
- **An item kref with no kind is refused before sending** with
  `*InvalidArgumentError` (`kref://p/s.v1/x` names a space; it used to be sent as
  item `s`, kind `v1/x`). A kind that contains `/` is not valid and is refused
  the same way.
- Validation (`ValidateKref`) is unchanged, and every item kref is still
  validated before it is split.

### Added
- **`ParseKref`, `KrefParts`, `KrefErrorClass` and `KrefShape`**: one parser for
  the kumiho-db kernel's verdict and the parts of a kref, and
  `KrefParts.GetItemTuple()` for the `GetItem` request. It never fails.
- `Kref.Parts()`.

### Upgrading
- Code that derives an item name or kind from a kref: `Kref.Kind()` of a dotted
  item name changed, and an item stored with a dotted kind (`tar.gz`) has the
  kref `kref://p/s/x.tar.gz`, which the grammar reads as item `x.tar`, kind
  `gz`. Take the stored kind from the item the server returns, not from the
  kref. Do not split krefs by hand.

