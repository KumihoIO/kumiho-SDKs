# Core Concepts

This guide explains the core concepts of Kumiho Cloud and how they relate to the Dart SDK.

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

```dart
final project = await client.createProject(
  'sci-fi-short',
  description: 'Sci-fi short film VFX assets',
);
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

```dart
final space = await client.createSpace('/sci-fi-short', 'characters');
```

**Key attributes:**
- `name`: URL-safe identifier
- `path`: Full path in the hierarchy (e.g., `/sci-fi-short/characters`)
- `metadata`: Custom key-value metadata

### Item

An **Item** represents a single creative asset or AI artifact. Items have a kind that indicates what type of asset they are.

```dart
final item = await client.createItem(
  '/sci-fi-short/characters',
  'hero-robot',
  'model',
);
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

```dart
// Create a revision
final revision = await client.createRevision(item.kref);

// Create a revision with metadata
final revision = await client.createRevision(
  item.kref,
  metadata: {'artist': 'john', 'status': 'wip'},
);
```

**Key attributes:**
- `revisionNumber`: Sequential version number
- `metadata`: Custom key-value metadata
- `tags`: Applied tags (e.g., `latest`, `published`, `approved`)
- `kref`: Reference URI (`kref://sci-fi-short/characters/hero-robot.model?r=1`)

### Artifact

An **Artifact** is a file reference attached to a revision. Kumiho follows a BYO-storage philosophy — files stay on your storage, only paths are tracked.

```dart
await client.createArtifact(
  revision.kref,
  'mesh',
  '/mnt/assets/hero-robot.fbx',
);

await client.createArtifact(
  revision.kref,
  'textures',
  's3://bucket/hero-robot/textures.tar',
);
```

**Key attributes:**
- `name`: Artifact identifier
- `location`: File path or URI (file://, s3://, smb://, etc.)
- `kref`: Reference URI

### Bundle

A **Bundle** groups related items or revisions together, useful for releases or delivery packages.

```dart
final bundle = await client.createBundle(
  '/sci-fi-short',
  'release-v1',
  metadata: {'channel': 'beta'},
);

await client.addBundleMember(bundle.kref, item.kref);
await client.addBundleMember(bundle.kref, rigRevision.kref);
```

## Kref URIs

Every object in Kumiho is addressable by a URI-style **Kref** (Kumiho Reference):

| Entity | Format | Example |
|--------|--------|---------|
| Project | `kref://project` | `kref://sci-fi-short` |
| Space | `kref://project/space` | `kref://sci-fi-short/characters` |
| Item | `kref://project/space/item.kind` | `kref://sci-fi-short/characters/hero.model` |
| Revision | `kref://project/space/item.kind?r=N` | `kref://sci-fi-short/characters/hero.model?r=1` |
| Artifact | `kref://project/space/item.kind?r=N&a=name` | `kref://sci-fi-short/characters/hero.model?r=1&a=mesh` |

## Edges (Relationships)

Edges represent relationships between revisions. Common edge types include:

| Edge Type | Description |
|-----------|-------------|
| `DEPENDS_ON` | Asset requires another asset to function |
| `DERIVED_FROM` | Asset was created from another asset |
| `REFERENCED` | Asset references another asset |
| `CONTAINS` | Asset contains another asset |
| `CREATED_FROM` | Asset was created using another asset |

```dart
// Create a dependency relationship
await client.createEdge(
  modelRevision.kref,
  textureRevision.kref,
  EdgeType.dependsOn,
);

// Analyze impact of changes
final impact = await client.analyzeImpact(textureRevision.kref);
```

## BYO Storage Philosophy

Kumiho does **not** store your files. Instead, it tracks references (artifacts) to files that remain on your storage:

- Local filesystems: `file:///path/to/file.fbx`
- Network shares: `smb://server/share/file.fbx`
- Cloud storage: `s3://bucket/path/file.fbx`

This approach provides:
- **No egress costs**: Files never leave your infrastructure
- **Flexibility**: Use any storage that works for your pipeline
- **Control**: Keep your data on your own storage solutions

## Multi-Tenant Architecture

Kumiho Cloud is a multi-tenant SaaS platform:

- Each organization is a **tenant**
- Tenants are isolated in separate Neo4j databases
- Regional deployment ensures data locality
- The SDK automatically discovers your tenant's region

```dart
// SDK handles tenant discovery automatically
final client = KumihoClient(host: 'api.kumiho.io', port: 443);
final tenantInfo = await client.getTenant();
print('Connected to tenant: ${tenantInfo.name}');
```
