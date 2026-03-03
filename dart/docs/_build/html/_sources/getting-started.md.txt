# Getting Started

This guide will help you get started with the Kumiho Dart SDK.

## Installation

Add the SDK to your `pubspec.yaml`. Until the package is published to pub.dev, use the Git repository directly:

```yaml
dependencies:
  kumiho:
    git:
      url: https://github.com/kumihoclouds/kumiho-dart.git
```

Then fetch dependencies:

```bash
dart pub get
```

## Authentication

Before using the SDK, you need to authenticate with Kumiho Cloud.

### Using the CLI

The easiest way to authenticate is using the Kumiho CLI:

```bash
kumiho-auth login
```

This will:
1. Prompt for your Kumiho Cloud email and password
2. Cache your credentials in `~/.kumiho/kumiho_authentication.json`
3. Automatically exchange for a Control Plane JWT

### Programmatic Authentication

You can also provide a token directly when constructing the client:

```dart
final client = KumihoClient(
  host: 'localhost',
  port: 50051,
  token: 'your-control-plane-jwt',
);
```

Or use environment variables:

```bash
export KUMIHO_AUTH_TOKEN="your-control-plane-jwt"
```

```dart
// SDK reads from environment automatically
final client = KumihoClient(
  host: 'localhost',
  port: 50051,
);
```

## Basic Concepts

### Projects

Projects are the top-level containers for organizing your assets:

```dart
final client = KumihoClient(host: 'localhost', port: 50051);

// Create a new project
final project = await client.createProject(
  'my-project',
  description: 'My VFX Project',
);

// Get an existing project
final existingProject = await client.getProject('my-project');
```

### Spaces

Spaces organize assets within a project (e.g., by type, department, or episode):

```dart
// Create a space
final space = await client.createSpace('/my-project', 'characters');

// Create nested spaces
final subspace = await client.createSpace('/my-project/characters', 'heroes');

// List spaces in a project
final spaces = await client.getSpaces('my-project');
```

### Items

Items represent individual assets with their metadata:

```dart
// Create an item in a space
final item = await client.createItem(
  '/my-project/characters',
  'hero',
  'model',
);

// Search for items
final results = await client.searchItems(
  contextFilter: 'my-project/*',
  kindFilter: 'model',
);
```

### Revisions

Revisions track versions of items:

```dart
// Create a revision
final revision = await client.createRevision(item.kref);

// Get all revisions for an item
final revisions = await client.getItemRevisions(item.kref);
```

### Artifacts

Artifacts are file references attached to revisions:

```dart
// Add artifacts to a revision
await client.createArtifact(
  revision.kref,
  'mesh',
  '/path/to/hero.fbx',
);

await client.createArtifact(
  revision.kref,
  'textures',
  's3://bucket/hero/textures.tar',
);
```

## Why Kumiho?

- **Graph-native modeling** that tracks relationships between revisions and bundles
- **BYO-storage philosophy** — store file references as artifacts while keeping your own storage layer
- **Fluent, high-level Dart models** layered on top of the generated gRPC stubs
- **Flutter compatible** — works seamlessly in Flutter desktop and mobile apps

## Next Steps

- Learn about [Core Concepts](concepts.md) in depth
- Explore [Authentication](authentication.md) options
- Check out the [Usage Guide](usage_guide.rst) for advanced patterns
