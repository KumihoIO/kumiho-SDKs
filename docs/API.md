# Kumiho Python SDK – Object-Oriented API Reference

The Python SDK is designed to be driven through the object model rather than
issuing raw gRPC calls. Each object mirrors a domain entity on the server and
provides helper methods that traverse the hierarchy from **project → space →
item → revision → artifact**, using [Kref](kumiho/kref.py) URIs to address and
resolve objects.

## Bootstrapping clients

Most scripts should rely on the lazily created default client exposed at the
`kumiho` package root. Call `kumiho.auto_configure_from_discovery()` to hydrate
it from cached credentials and the control-plane discovery endpoint; subsequent
helper calls reuse the same client.

Use the `Client` class directly only when you need to override transport
behaviour (custom metadata, explicit target, discovery flags, or token
selection). Otherwise, prefer the factory and object helpers:

```python
import kumiho

client = kumiho.auto_configure_from_discovery()
projects = kumiho.get_projects()
```

### Package-level convenience helpers

The package root exposes a few shortcuts that delegate to the default client so
you can stay in the object-oriented flow:

- `get_item(kref)` retrieves an `Item` by its Kref URI.
- `get_bundle(kref)` retrieves a `Bundle` by its Kref URI (validates kind is
  "bundle").
- `get_revision(kref)` retrieves a `Revision` by its Kref URI.
- `get_artifact(kref)` retrieves an `Artifact` by its Kref URI.
- `item_search(context_filter="", name_filter="", kind_filter="")` returns
  a list of `Item` objects matching the provided context, name, or kind
  filters.
- `resolve(kref)` maps an item, revision, or artifact Kref to a concrete
  artifact location while respecting default-location semantics. This mirrors
  `Client.resolve` but avoids manual client access.
- `get_artifacts_by_location(location)` finds all `Artifact` objects whose
  backing location matches the provided file path.

## Kref utility

`Kref` represents artifact references as URI strings and includes helpers such
as `get_path()`, `get_space()`, `get_item_name()`, and `get_artifact_name()`
to decompose paths. Use `Kref.to_pb()` when passing references back to the
client, and prefer constructing downstream objects via their Kref-aware helper
methods instead of manual string parsing.

## Projects

`Project` objects wrap server responses and expose space-centric helpers. Obtain
one via `kumiho.create_project`, `kumiho.get_project`, or iteration over
`kumiho.get_projects`. Key methods:

- `create_space(name, parent_path=None)`: creates a child space under the
  project root or a supplied path.
- `get_space(name, parent_path=None)`: returns an existing child space.
- `get_spaces(parent_path=None)`: lists immediate child spaces under the
  project.
- `create_item(item_name, kind, parent_path=None, metadata=None)`: creates an
  item at the project root or specified path.
- `get_item(item_name, kind, parent_path=None)`: retrieves an item by name and
  kind from the project root or specified path.
- `create_bundle(bundle_name, parent_path=None, metadata=None)`: creates a
  bundle item at the project root or specified path.
- `get_bundle(bundle_name, parent_path=None)`: retrieves a bundle by name from
  the project root or specified path.
- `delete(force=False)`: deprecates or deletes the project.

## Spaces

`Space` encapsulates a hierarchical container. Start from a `Project` or call
`Space.get_child_spaces()` to traverse downward. Core helpers:

- `create_space(name)`, `get_space(name)`, and `get_child_spaces()` maintain the
  nested hierarchy without manual path concatenation.
- `create_item(item_name, kind)` and `get_items(...)` manage
  items within the space.
- `get_item(item_name, kind)`: retrieves a specific item by name and kind.
- `create_bundle(bundle_name, metadata=None)`: creates a bundle item in this
  space.
- `get_bundle(bundle_name)`: retrieves a bundle by name from this space.
- `set_metadata(metadata)` replaces all metadata; `set_attribute(key, value)`,
  `get_attribute(key)`, and `delete_attribute(key)` provide granular updates.
- `delete(force=False)` removes the space via the client.

## Items

An `Item` represents a revisioned asset. Retrieve one via a `Space`, a
`Client` search helper, or by resolving an item Kref (`Client.get_item_by_kref`).
Notable operations:

- `create_revision(metadata=None, number=0)`, `get_revisions()`, and
  `get_latest_revision()` manage the revision lineage.
- `get_revision(number)`, `get_revision_by_tag(tag)`, and `get_revision_by_time(time)`
  resolve a specific snapshot.
- `peek_next_revision()` inspects the next auto-incremented revision number.
- `set_metadata(metadata)` and `delete(force=False)` delegate updates to the
  client.

## Revisions

`Revision` instances expose artifact and tagging workflows while automatically
refreshing tag lists when stale. Primary helpers:

- `create_artifact(name, location)`, `get_artifact(name)`, and `get_artifacts()`
  manage artifacts attached to the revision.
- `tag(tag)`, `untag(tag)`, `has_tag(tag)`, and `was_tagged(tag)` apply and query
  tags; `set_metadata(metadata)` updates metadata.
- `get_locations()` returns artifact locations; `get_item()` and `get_space()`
  climb back up the hierarchy.

## Artifacts

`Artifact` models a file or asset associated with a revision. Access artifacts
through their parent `Revision` helpers or via `Client.get_artifact` when you
already have a revision Kref. Helpers include:

- `name` property derived from the Kref (no manual parsing required).
- `set_metadata(metadata)` to update metadata.
- `delete(force=False)` to remove the artifact.

## Bundles

`Bundle` is a specialized item type that aggregates other items. Bundles track
membership changes through revision history, providing an audit trail of what
items were added or removed over time. Access bundles via:

- `kumiho.get_bundle(kref)`: retrieves a bundle by its full Kref URI.
- `project.get_bundle(bundle_name, parent_path=None)`: retrieves a bundle from
  a project.
- `space.get_bundle(bundle_name)`: retrieves a bundle from a space.

Bundle helpers include:

- `add_member(item, metadata=None)`: adds an item to the bundle.
- `remove_member(item)`: removes an item from the bundle.
- `get_members()`: returns a list of `BundleMember` objects.
- `get_revision_history()`: returns `BundleRevisionHistory` showing membership
  changes across bundle revisions.

## Edges

`Edge` represents relationships between revisions. Create them via
`Client.create_edge(source_revision, target_revision, edge_type, metadata=None)`
and fetch them with `Client.get_edges(kref, edge_type_filter="", direction=0)`.
Use direction constants `kumiho.OUTGOING` (default), `kumiho.INCOMING`, or
`kumiho.BOTH` to control which edges are returned. Call `Edge.delete()` to
remove a relationship.

## Graph Traversal

The SDK provides powerful graph traversal methods on `Revision` objects:

- `get_all_dependencies(max_depth=10, edge_type_filter=None, limit=100)` finds
  all revisions this revision depends on (following outgoing edges).
- `get_all_dependents(max_depth=10, edge_type_filter=None, limit=100)` finds all
  revisions that depend on this revision (following incoming edges).
- `find_path_to(target_revision, edge_type_filter=None, max_depth=10)` returns a
  `ShortestPathResult` with steps between the source and target.
- `analyze_impact(edge_type_filter=None, max_depth=10, limit=100)` returns
  `ImpactedRevision` objects showing what would be affected by changes.

## Events

The SDK provides real-time event streaming with tier-based capabilities.

### Event Streaming

`kumiho.event_stream(routing_key_filter="", kref_filter="", cursor=None, consumer_group=None, from_beginning=False)` 
yields `Event` objects from the server so you can react to changes.

**Parameters:**
- `routing_key_filter`: Filter by event type with wildcards (e.g., `"revision.*"`)
- `kref_filter`: Filter by kref glob pattern (e.g., `"kref://project/**/*.model"`)
- `cursor`: Resume from cursor position (Creator+ tiers, Coming Soon)
- `consumer_group`: Consumer group for load balancing (Enterprise tier, Coming Soon)
- `from_beginning`: Start from beginning of buffer (Creator+ tiers, Coming Soon)

**Event object attributes:**
- `routing_key`: Event type (e.g., `"revision.created"`)
- `kref`: Affected resource Kref URI
- `action`: Action performed (`"created"`, `"updated"`, `"deleted"`, `"tagged"`)
- `timestamp`: When the event occurred
- `metadata`: Additional event metadata dict
- `cursor`: Cursor for resumable streaming (Creator+ tiers)

```python
import kumiho

# Basic streaming
for event in kumiho.event_stream(routing_key_filter="revision.*"):
    print(f"{event.action}: {event.kref}")
    
# With cursor resume (Creator+ tiers, Coming Soon)
for event in kumiho.event_stream(cursor=saved_cursor):
    process(event)
    save_cursor(event.cursor)
```

### EventCapabilities

`kumiho.get_event_capabilities()` returns an `EventCapabilities` dataclass 
describing your tenant's streaming capabilities.

**EventCapabilities attributes:**
- `supports_replay`: `bool` - Can replay past events
- `supports_cursor`: `bool` - Cursor-based resume available
- `supports_consumer_groups`: `bool` - Consumer group support (Enterprise)
- `max_retention_hours`: `int` - Event retention window (0 = no persistence)
- `max_buffer_size`: `int` - Maximum events in buffer
- `tier`: `str` - Current tier name (`"free"`, `"creator"`, `"studio"`, `"enterprise"`)

```python
from kumiho import get_event_capabilities

caps = get_event_capabilities()
if caps.supports_cursor:
    stream = kumiho.event_stream(cursor=last_cursor)
else:
    stream = kumiho.event_stream()
```

### Tier Capabilities

| Feature | Free | Creator | Studio | Enterprise |
|---------|------|---------|--------|------------|
| Real-time streaming | ✅ | ✅ | ✅ | ✅ |
| `supports_replay` | ❌ | ✅ | ✅ | ✅ |
| `supports_cursor` | ❌ | ✅ | ✅ | ✅ |
| `supports_consumer_groups` | ❌ | ❌ | ❌ | ✅ |
| `max_retention_hours` | 0 | 1 | 24 | 720 |
| `max_buffer_size` | 100 | 10,000 | 100,000 | ∞ |

> **Note**: Creator tier and above features are **Coming Soon**. Currently only Free tier is available.

## Kref resolution and artifact lookup

The `Client.resolve(kref)` helper walks the hierarchy for you:

- An item Kref resolves to its latest revision and default (or first) artifact
  location.
- A revision Kref resolves to the default or first artifact location for that
  revision.
- An artifact Kref returns the artifact's location directly.

Prefer this resolver over manual string handling so Kref semantics stay
consistent.
