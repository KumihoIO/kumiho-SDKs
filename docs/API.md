# Kumiho Python SDK – Object-Oriented API Reference

The Python SDK is designed to be driven through the object model rather than
issuing raw gRPC calls. Each object mirrors a domain entity on the server and
provides helper methods that traverse the hierarchy from **project → group →
product → version → resource**, using [Kref](kumiho/kref.py) URIs to address and
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

- `product_search(context_filter="", name_filter="", ptype_filter="")` returns
  a list of `Product` objects matching the provided context, name, or type
  filters.
- `resolve(kref)` maps a product, version, or resource Kref to a concrete
  resource location while respecting default-location semantics. This mirrors
  `Client.resolve` but avoids manual client access.
- `get_resources_by_location(location)` finds all `Resource` objects whose
  backing location matches the provided file path.

## Kref utility

`Kref` represents resource references as URI strings and includes helpers such
as `get_path()`, `get_group()`, `get_product_name()`, and `get_resource_name()`
to decompose paths. Use `Kref.to_pb()` when passing references back to the
client, and prefer constructing downstream objects via their Kref-aware helper
methods instead of manual string parsing.

## Projects

`Project` objects wrap server responses and expose group-centric helpers. Obtain
one via `kumiho.create_project`, `kumiho.get_project`, or iteration over
`kumiho.get_projects`. Key methods:

- `create_group(name, parent_path=None)`: creates a child group under the
  project root or a supplied path.
- `get_group(name, parent_path=None)`: returns an existing child group.
- `get_groups(parent_path=None)`: lists immediate child groups under the
  project.
- `delete(force=False)`: deprecates or deletes the project.

## Groups

`Group` encapsulates a hierarchical container. Start from a `Project` or call
`Group.get_child_groups()` to traverse downward. Core helpers:

- `create_group(name)`, `get_group(name)`, and `get_child_groups()` maintain the
  nested hierarchy without manual path concatenation.
- `create_product(product_name, product_type)` and `get_products(...)` manage
  products within the group.
- `set_metadata(metadata)` replaces all metadata; `set_attribute(key, value)`,
  `get_attribute(key)`, and `delete_attribute(key)` provide granular updates.
- `delete(force=False)` removes the group via the client.

## Products

A `Product` represents a versioned asset. Retrieve one via a `Group`, a
`Client` search helper, or by resolving a product Kref (`Client.get_product_by_kref`).
Notable operations:

- `create_version(metadata=None, number=0)`, `get_versions()`, and
  `get_latest_version()` manage the version lineage.
- `get_version(number)`, `get_version_by_tag(tag)`, and `get_version_by_time(time)`
  resolve a specific snapshot.
- `peek_next_version()` inspects the next auto-incremented version number.
- `set_metadata(metadata)` and `delete(force=False)` delegate updates to the
  client.

## Versions

`Version` instances expose resource and tagging workflows while automatically
refreshing tag lists when stale. Primary helpers:

- `create_resource(name, location)`, `get_resource(name)`, and `get_resources()`
  manage resources attached to the version.
- `tag(tag)`, `untag(tag)`, `has_tag(tag)`, and `was_tagged(tag)` apply and query
  tags; `set_metadata(metadata)` updates metadata.
- `get_locations()` returns resource locations; `get_product()` and `get_group()`
  climb back up the hierarchy.

## Resources

`Resource` models a file or artifact associated with a version. Access resources
through their parent `Version` helpers or via `Client.get_resource` when you
already have a version Kref. Helpers include:

- `name` property derived from the Kref (no manual parsing required).
- `set_metadata(metadata)` to update metadata.
- `delete(force=False)` to remove the resource.

## Links

`Link` represents relationships between versions. Create them via
`Client.create_link(source_version, target_version, link_type, metadata=None)`
and fetch them with `Client.get_links(kref, link_type_filter="", direction=0)`.
Use direction constants `kumiho.OUTGOING` (default), `kumiho.INCOMING`, or
`kumiho.BOTH` to control which links are returned. Call `Link.delete()` to
remove a relationship.

## Graph Traversal

The SDK provides powerful graph traversal methods on `Version` objects:

- `get_all_dependencies(max_depth=10, link_type_filter=None, limit=100)` finds
  all versions this version depends on (following outgoing links).
- `get_all_dependents(max_depth=10, link_type_filter=None, limit=100)` finds all
  versions that depend on this version (following incoming links).
- `find_path_to(target_version, link_type_filter=None, max_depth=10)` returns a
  `ShortestPathResult` with steps between the source and target.
- `analyze_impact(link_type_filter=None, max_depth=10, limit=100)` returns
  `ImpactedVersion` objects showing what would be affected by changes.

## Events

`kumiho.event_stream(routing_key_filter="", kref_filter="")` yields `Event`
objects from the server so you can react to changes. Use wildcard-capable
routing key and Kref filters to scope the feed.

## Kref resolution and resource lookup

The `Client.resolve(kref)` helper walks the hierarchy for you:

- A product Kref resolves to its latest version and default (or first) resource
  location.
- A version Kref resolves to the default or first resource location for that
  version.
- A resource Kref returns the resource’s location directly.

Prefer this resolver over manual string handling so Kref semantics stay
consistent.