# Core Concepts

This guide explains the core concepts of Kumiho Cloud and how they relate to the Python SDK.

## Graph-Native Architecture

Kumiho Cloud is built on a **graph database (Neo4j)**, which means relationships between assets are first-class citizens. Unlike traditional file-based systems, Kumiho tracks:

- **Dependencies**: What assets does this asset depend on?
- **Lineage**: What was this asset created from?
- **Usage**: Where is this asset used?

```
┌───────────────────────────────────────────────────────┐
│                         PROJECT                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │                        SPACE                    │  │
│  │  ┌─────────┐      ┌─────────┐     ┌─────────┐   │  │
│  │  │  ITEM   │────▶│  ITEM   │────▶│  ITEM   │   │  │
│  │  └────┬────┘      └────┬────┘     └────┬────┘   │  │
│  │       │                │               │        │  │
│  │  ┌────▼────┐      ┌────▼────┐     ┌────▼────┐   │  │
│  │  │REVISION │      │REVISION │     │REVISION │   │  │
│  │  │   v1    │      │   v1    │     │   v1    │   │  │
│  │  └────┬────┘      └────┬────┘     └────┬────┘   │  │
│  │       │                │               │        │  │
│  │  ┌────▼────┐      ┌────▼────┐     ┌────▼────┐   │  │
│  │  │ARTIFACT │      │ARTIFACT │     │ARTIFACT │   │  │
│  │  └─────────┘      └─────────┘     └─────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

## Entity Hierarchy

### Project

A **Project** is the top-level container representing a production, show, or workspace. Each project is isolated within a tenant's graph database.

```python
project = kumiho.create_project(
    name="sci-fi-short",
    description="Sci-fi short film VFX assets"
)
```

**Key attributes:**
- `name`: URL-safe identifier (used in Kref URIs)
- `description`: Human-readable description
- `kref`: Reference URI (`kref://sci-fi-short`)

### Space

A **Space** organizes assets within a project. Common groupings include:
- By type: `characters`, `environments`, `props`
- By episode: `ep01`, `ep02`
- By department: `modeling`, `animation`, `lighting`

```python
space = project.create_space("characters")
```

**Key attributes:**
- `name`: URL-safe identifier
- `path`: Full path in the hierarchy (e.g., `/sci-fi-short/characters`)
- `metadata`: Custom key-value metadata

### Item

An **Item** represents a single creative asset or AI artifact. Items have a kind that indicates what type of asset they are.

```python
item = space.create_item(
    item_name="hero-robot",
    kind="model"
)
```

**Common item kinds:**
- `model`: 3D models
- `texture`: Textures and materials
- `animation`: Animation data
- `rig`: Character rigs
- `composite`: Compositing setups
- `ai_model`: Trained AI models
- `dataset`: Training datasets
- `prompt`: AI prompts

**Key attributes:**
- `name`: URL-safe identifier
- `kind`: Category of the asset
- `kref`: Reference URI (`kref://sci-fi-short/characters/hero-robot.model`)

### Revision

A **Revision** represents a specific iteration of an item. Revisions are immutable once published.

```python
# Simple revision creation
revision = item.create_revision()

# Revision with metadata
revision = item.create_revision(
    metadata={
        "artist": "jane",
        "render_engine": "arnold",
        "notes": "Added facial rigging for dialogue"
    }
)
```

**Key attributes:**
- `number`: Auto-incrementing revision number
- `metadata`: Custom key-value metadata
- `kref`: Reference URI (`kref://sci-fi-short/characters/hero-robot.model?v=3`)
- `tags`: List of tags (e.g., "latest", "published", "approved")

### Artifact

An **Artifact** is a file reference attached to a revision. Artifacts store metadata about files without uploading the actual data—files stay on your local/NAS storage.

```python
artifact = revision.create_artifact(
    name="hero_robot_v3.fbx",
    location="smb://studio-nas/projects/scifi/hero_robot_v3.fbx"
)

# Add metadata after creation
artifact.set_metadata({
    "size": "52428800",
    "checksum": "sha256:a1b2c3...",
    "format": "fbx"
})
```

**Key attributes:**
- `name`: Artifact identifier within the revision
- `location`: URI pointing to the actual file
- `metadata`: Custom key-value metadata

### Edge

An **Edge** represents a relationship between revisions. Edges enable lineage tracking.

```python
import kumiho

# Get the target revision
texture = kumiho.get_revision("kref://sci-fi-short/textures/metal.texture?v=2")

# Create edge with optional metadata
edge = revision.create_edge(
    target_revision=texture,
    edge_type=kumiho.DEPENDS_ON,
    metadata={"usage": "body material"}
)
```

**Edge types:**
- `kumiho.DEPENDS_ON`: This revision depends on the target
- `kumiho.DERIVED_FROM`: This revision was derived from the target
- `kumiho.REFERENCED`: This revision references the target
- `kumiho.CONTAINS`: This revision contains the target

**Querying edges by direction:**

```python
# Get outgoing edges (default) - edges FROM this revision
outgoing = revision.get_edges(direction=kumiho.OUTGOING)

# Get incoming edges - edges TO this revision
incoming = revision.get_edges(direction=kumiho.INCOMING)

# Get all edges in both directions
all_edges = revision.get_edges(direction=kumiho.BOTH)
```

### Graph Traversal

Kumiho provides powerful graph traversal methods for dependency analysis:

```python
# Find all dependencies (what this revision depends on)
deps = revision.get_all_dependencies(max_depth=5)
for kref in deps.revision_krefs:
    print(f"Depends on: {kref.uri}")

# Find all dependents (what depends on this revision)
dependents = revision.get_all_dependents(max_depth=5)
for kref in dependents.revision_krefs:
    print(f"Depended on by: {kref.uri}")

# Find shortest path between revisions
path = source_revision.find_path_to(target_revision)
if path:
    print(f"Path length: {path.total_depth}")
    for step in path.steps:
        print(f"  -> {step.revision_kref.uri} via {step.edge_type}")

# Analyze impact of changes (what would be affected)
impact = revision.analyze_impact()
for impacted in impact:
    print(f"Would affect: {impacted.revision_kref.uri} at depth {impacted.impact_depth}")
```

### Bundle

A **Bundle** is a special item kind that aggregates other items. Bundles are useful for grouping related assets together (e.g., a character bundle with model, textures, and rig) with full revision-based audit trail of membership changes.

```python
# Create a bundle via Project or Space
bundle = project.create_bundle("release-bundle")

# Or from a space
assets = project.get_space("assets")
char_bundle = assets.create_bundle("character-bundle")

# Add items to the bundle
hero_model = assets.get_item("hero", "model")
hero_rig = assets.get_item("hero", "rig")
bundle.add_member(hero_model)
bundle.add_member(hero_rig)

# Get current members
members = bundle.get_members()
for member in members:
    print(f"  {member.item_kref}")

# View change history (audit trail)
history = bundle.get_history()
for entry in history:
    print(f"v{entry.revision_number}: {entry.action} {entry.member_item_kref}")
```

**Key characteristics:**
- Bundles use the reserved item kind `"bundle"` 
- Cannot be created via `create_item()` (use `create_bundle()`)
- Each membership change (add/remove) creates a new bundle revision
- Full audit trail: who added/removed what item and when
- Can query members at any specific revision in history

## Metadata

All node types support custom metadata as key-value string pairs. Metadata can be set during creation (where supported) or updated afterward.

### Setting Metadata

```python
# During revision creation
revision = item.create_revision(metadata={
    "artist": "jane",
    "render_engine": "arnold",
    "frame_range": "1-100"
})

# During edge creation
edge = revision.create_edge(
    target_revision=texture,
    edge_type=kumiho.DEPENDS_ON,
    metadata={"channel": "diffuse"}
)

# Update metadata after creation (all node types)
space.set_metadata({"department": "modeling"})
item.set_metadata({"status": "approved"})
revision.set_metadata({"published_by": "supervisor"})
artifact.set_metadata({"checksum": "sha256:..."})
```

### Granular Attribute Operations

For updating individual metadata fields without replacing the entire map:

```python
# Set a single attribute
space.set_attribute("department", "modeling")
revision.set_attribute("status", "approved")

# Get a single attribute
dept = space.get_attribute("department")  # Returns "modeling" or None

# Delete a single attribute
space.delete_attribute("old_field")
```

This is more efficient than `set_metadata()` when you only need to change one field.

### Common Metadata Patterns

| Node Type | Common Keys |
|-----------|-------------|
| Space | `department`, `supervisor`, `deadline` |
| Item | `status`, `priority`, `assigned_to` |
| Revision | `artist`, `render_engine`, `notes`, `software_version` |
| Artifact | `size`, `checksum`, `format`, `resolution` |
| Edge | `usage`, `channel`, `relationship_notes` |

## Kref URI Scheme

Kumiho uses **Kref URIs** as universal identifiers for all entities:

```
kref://project/space/item.kind?v=revision&r=artifact
```

| URI | Resolves To |
|-----|-------------|
| `kref://my-project` | Project |
| `kref://my-project/chars` | Space |
| `kref://my-project/chars/human` | Sub-Space(s) |
| `kref://my-project/chars/human/hero.model` | Item (latest revision) |
| `kref://my-project/chars/human/hero.model?r=2` | Specific revision |
| `kref://my-project/chars/human/hero.model?r=2&a=mesh` | Specific artifact |
| `kref://my-project/chars/human/hero.model?t=published` | Latest published revision |
| `kref://my-project/chars/human/hero.model?t=published&a=mesh` | Latest published revision with specific artifact|
| `kref://my-project/chars/human/hero.model?t=published&time=202406011330&a=mesh` | Published revision at specific time with specific artifact|

## Time-Based Revision Queries

One of Kumiho's most powerful features is **time-based revision lookup**. This enables
reproducible builds, historical debugging, and auditing by answering questions like:
"What was the published version of this asset on June 1st?"

### Why Time-Based Queries Matter

In production pipelines, you often need to:

1. **Reproduce past renders**: Re-render a shot exactly as it was delivered months ago
2. **Debug regressions**: Compare current assets against a known-good state from a specific date
3. **Audit changes**: Understand what version was used when a decision was made
4. **Compliance**: Prove what asset versions were in use at a particular milestone

Without time-based queries, you'd need to manually track revision numbers for every
asset at every milestone—an error-prone and tedious process.

### Using `get_revision_by_time`

The SDK provides `get_revision_by_time()` to find the revision that was tagged with
a specific tag at a given point in time:

```python
from datetime import datetime, timezone

# Get the "published" revision as of June 1st, 2024
june_1 = datetime(2024, 6, 1, tzinfo=timezone.utc)
revision = item.get_revision_by_time(
    time=june_1,
    tag="published"
)

print(f"On {june_1}, published revision was r{revision.number}")
```

The `time` parameter accepts multiple formats:
- **datetime object**: `datetime(2024, 6, 1, 13, 30, 45, tzinfo=timezone.utc)` - full precision
- **ISO 8601 string**: `"2024-06-01T13:30:45+00:00"` or `"2024-06-01T13:30:45Z"` - full precision  
- **YYYYMMDDHHMM string**: `"202406011330"` - minute-level precision (rounded to end of minute)

For historical auditing where events may happen within the same minute, use datetime
objects or ISO strings for sub-second precision.

This is especially useful for the `published` tag, which marks revisions as immutable
and approved for downstream consumption.

### Time-Based Kref URIs

You can also use time-based queries directly in Kref URIs with the `t=` (tag) and
`time=` parameters:

```python
# Get published revision at a specific time via Kref
# Format: YYYYMMDDHHMM (e.g., 202406011330 = June 1, 2024 at 13:30)
kref = "kref://my-project/chars/hero.model?t=published&time=202406011330"
revision = kumiho.get_revision(kref)

# Resolve to artifact location at that point in time
location = kumiho.resolve(kref)
```

**Kref time query parameters:**
| Parameter | Description |
|-----------|-------------|
| `t=<tag>` | Find revision with this tag (e.g., `t=published`, `t=approved`) |
| `time=<YYYYMMDDHHMM>` | Point in time to query (e.g., `time=202406011330`) |

When both `t=` and `time=` are provided, Kumiho finds the revision that:
1. Had the specified tag at the given time
2. Was the most recent such revision before or at that time

### Practical Examples

**Reproduce a past delivery:**
```python
# Find all assets as they were for the Q2 delivery
delivery_date = datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc)

for item in space.get_items():
    rev = item.get_revision_by_time(time=delivery_date, tag="published")
    if rev:
        print(f"{item.name}: r{rev.number}")
        for artifact in rev.get_artifacts():
            print(f"  -> {artifact.location}")
```

**Compare current vs historical:**
```python
# What changed between two milestones?
alpha_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
beta_date = datetime(2024, 6, 1, tzinfo=timezone.utc)

alpha_rev = item.get_revision_by_time(time=alpha_date, tag="published")
beta_rev = item.get_revision_by_time(time=beta_date, tag="published")

if alpha_rev.number != beta_rev.number:
    print(f"Asset changed from r{alpha_rev.number} to r{beta_rev.number}")
```

**Pipeline integration with timestamps:**
```python
# In a render farm job, record the exact time for reproducibility
import json
from datetime import datetime, timezone

render_manifest = {
    "render_time": datetime.now(timezone.utc).isoformat(),
    "assets": []
}

for item_kref in required_assets:
    item = kumiho.get_item(item_kref)
    rev = item.get_revision_by_tag("published")
    render_manifest["assets"].append({
        "kref": rev.kref,
        "revision": rev.number
    })

# Later, reproduce using the recorded timestamp
with open("render_manifest.json") as f:
    manifest = json.load(f)
    
render_time = datetime.fromisoformat(manifest["render_time"])
# Convert to YYYYMMDDHHMM format for kref
time_str = render_time.strftime("%Y%m%d%H%M")
for asset in manifest["assets"]:
    # Get exactly what was published at render time
    kref = f"{asset['kref'].split('?')[0]}?t=published&time={time_str}"
    revision = kumiho.get_revision(kref)
```

### Tags and Time

The `published` tag is especially important for time-based queries because:

1. **Immutability**: Published revisions cannot be modified or deleted
2. **Stability**: Downstream consumers can rely on published revisions not changing
3. **Audit trail**: Tag history is preserved, so you can query what was published when

Other common tags for time-based queries:
- `approved`: Supervisor-approved versions
- `delivered`: Versions sent to clients
- `milestone-alpha`, `milestone-beta`: Project milestone snapshots

## BYO Storage Philosophy

Kumiho follows a **"Bring Your Own Storage"** philosophy:

1. **Files stay local**: Original files remain on your NAS, local disk, or on-prem storage
2. **Metadata in cloud**: Only paths, hashes, and relationships are stored in the cloud
3. **No vendor lock-in**: You can always access your files directly

```python
# Artifact location is just a URI - files aren't uploaded
artifact = revision.create_artifact(
    name="hero.fbx",
    location="file:///mnt/studio/projects/hero.fbx"  # File stays here
)
```

**Supported URI schemes:**
- `file://`: Local filesystem
- `smb://`: Windows/Samba shares
- `nfs://`: NFS mounts
- `s3://`: Amazon S3 (for hybrid setups)
- `gs://`: Google Cloud Storage (for hybrid setups)

## Multi-Tenant Architecture

Kumiho Cloud is a multi-tenant SaaS:

- **Tenant**: A studio or organization with their own isolated data
- **Region**: Geographic location of the data (e.g., `us-central`, `eu-west`)
- **Control Plane**: Global service for authentication and routing
- **Data Plane**: Regional servers with Neo4j databases

The SDK handles tenant resolution automatically:

```python
# SDK automatically routes to the correct region
kumiho.connect()  # Uses cached credentials and tenant info
```

## Event Streaming

Kumiho supports real-time event streaming for reactive workflows:

```python
# Stream events from a project
for event in project.stream_events():
    if event.event_type == "revision.created":
        print(f"New revision: {event.payload}")
```

**Event types:**
- `revision.created`: New revision was published
- `edge.created`: New relationship was created
- `artifact.added`: Artifact was added to a revision

## Next Steps

- Try the [Getting Started](getting-started.md) tutorial
- Explore the [API Reference](api/kumiho.rst)
- Learn about [Authentication](authentication.md)
