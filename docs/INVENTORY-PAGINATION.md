# Inventory pagination with server/CE1.11.0

`GetChildSpaces` and direct `GetItems` return completion metadata in1.11.0.
Existing calls that omit the pagination message continue returning all eligible
rows. Explicit page requests now return only that page; callers must follow the
opaque cursor until the terminal page. No SDK silently auto-fetches all pages.

The wire fields already existed; this SDK change does not regenerate protobuf
or change any proto pin. Count and cursor are per caller/parent/filter/request.
Neither a stable count nor these SDK APIs freezes a tree under concurrent writes.

| SDK | Existing call retained | Metadata/inventory path |
| --- | --- | --- |
| Python | List-compatible `client.get_child_spaces` / `get_items` | `PagedList.total_count`, `.next_cursor`, `.has_more`, `.pagination_present`; Space forwards recursion/paging and `include_deprecated` |
| Dart | Existing `Future<List<Space>>` model methods | Model mapping preserves PagedList at runtime; typed `getChildSpacesPaged` / `getSpacesPaged`; items already return PagedList |
| C++ | Existing vector-returning methods and PagedList layout | `getChildSpacesPaged`, new direct `getItemsPaged`, model paged variants; count/cursor plus `paginationPresent()` and cursor-derived `hasMore()` |
| Go | Existing `Page` fields, struct literals and method return types | New `InventoryPage` and `GetChildSpacesPaged` / `GetItemsPaged` / model variants add `PaginationPresent` and `HasMore` |
| Rust | Existing `Page` fields, struct literals and return types | `pagination_present()` and cursor-derived `has_more()` accessors; `get_items_including_deprecated` on Space |

Check metadata presence before interpreting an empty cursor or zero count.
Missing metadata from an older server remains unknown; it is never upgraded
to a completion claim. Rust's convenience flag derives from the cursor/count
already stored by Page; C++ uses the same approach to preserve aggregate/ABI
layout. Raw protobuf still exposes the literal wire flag in both SDKs.
C++ terminal cursors remain an engaged optional containing an empty string:
checking `has_value()` alone is insufficient. Prefer `hasMore() == false` after
checking `paginationPresent()`. Build updated C++ libraries and headers together
to use the newly added methods.

Dart inventory Item models preserve safe dot-prefixed identities returned by
the server (including items inside dot-prefixed spaces). This response-only
path still rejects traversal, controls and malformed leaves. Public `Kref()`
and request validation retain their existing accepted grammar.

For a complete eligible space/item inventory with writers paused, list all
descendants recursively, then list direct items for the parent and every
returned space, explicitly including deprecated items. The virtual root is not
a real project. Hidden-marked/dot-prefixed data retains normal ownership scope.
Keep writers paused through destructive cleanup and take a backup first.

## Search is a separate RPC

`Project.get_items`/`GetItems`/`getItems` helpers retain their existing
`ItemSearch` project-search scope. C++ `Space::getItems` also retains its legacy
ItemSearch scope; use `Space::getItemsPaged` or `Client::getItemsPaged` for direct
GetItems inventory. The other languages' Space direct-item helpers are distinct
from Project search. On server1.11.0, ItemSearch ignores page requests and
omits pagination metadata; this SDK cannot synthesize a trustworthy count or
snapshot for it. New deprecated-search helpers preserve that search contract.

## Validation and release

SDK CI runs native tests for all five languages and uses
`scripts/verify-ce-inventory.py` to download the checksum-verified public Linux
CE1.11.0 binary and start a uniquely named disposable Neo4j container. The
language probes check unpaged1,004-row lists, four exactly full251-row pages,
unique identities, count/cursor/continuation and direct deprecated inventory.
No live Cloud authentication or user database is used.

The release versions for this change are Python0.16.0 (PyPI), Rust0.11.0
(crates.io), Go0.11.0 (`go/v0.11.0` module tag), Dart0.3.0 (Git source) and
C++1.1.0 (Git source). Follow [RELEASING.md](RELEASING.md) after review and
green CI. Dart retains `publish_to: none`; C++ has no registry publisher.
Default whole-list users do not need a coordinated wire upgrade. Users of
the newly exposed APIs need the updated SDK source/package after release.
Snapshot-bound cleanup remains a separate server capability. Production
export/load and historical CE1.6.3 were not tested here.
