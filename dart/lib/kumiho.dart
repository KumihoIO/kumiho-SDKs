// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Kumiho Dart SDK - A graph-native creative and AI asset management client.
///
/// This library provides a Dart client for the Kumiho Cloud gRPC service.
/// Kumiho tracks revisions, relationships, and lineage of creative assets
/// without uploading files to the cloud (BYO Storage philosophy).
///
/// ## Getting Started
///
/// ```dart
/// import 'package:kumiho/kumiho.dart';
///
/// void main() async {
///   // Token is auto-loaded from env var or ~/.kumiho/kumiho_authentication.json
///   final client = KumihoClient(
///     host: 'localhost',
///     port: 50051,
///   );
///
///   try {
///     // Create a project
///     final project = await client.newProject('my-project');
///
///     // Create a space using fluent API
///     final space = await project.createSpace('models');
///
///     // Create an item
///     final item = await space.createItem('hero', 'model');
///
///     // Create a revision
///     final revision = await item.createRevision();
///
///     // Add an artifact
///     await revision.createArtifact('mesh', '/path/to/hero.fbx');
///
///   } finally {
///     await client.shutdownAsync();
///   }
/// }
/// ```
///
/// ## Authentication
///
/// The SDK supports multiple authentication methods:
///
/// 1. **Explicit token**: Pass `token` parameter to constructor
/// 2. **Environment variable**: Set `KUMIHO_AUTH_TOKEN`
/// 3. **Credentials file**: Use `kumiho-cli login` to cache credentials
///    at `~/.kumiho/kumiho_authentication.json`
///
/// ### Auto-Refresh (Opt-in)
///
/// Set `KUMIHO_ENABLE_AUTO_REFRESH=true` to enable automatic token refresh
/// when credentials expire. The SDK will use the stored refresh token.
///
/// ### Environment Variables
///
/// | Variable | Description |
/// |----------|-------------|
/// | `KUMIHO_AUTH_TOKEN` | Primary auth token (overrides file) |
/// | `KUMIHO_CONFIG_DIR` | Custom config directory |
/// | `KUMIHO_USE_CONTROL_PLANE_TOKEN` | Prefer CP token (true/false) |
/// | `KUMIHO_ENABLE_AUTO_REFRESH` | Enable token auto-refresh (true/false) |
/// | `KUMIHO_AUTH_TOKEN_GRACE_SECONDS` | Grace period before expiry (default: 300) |
/// | `KUMIHO_CONTROL_PLANE_URL` | Control Plane base URL (preferred) |
///
/// ## Key Concepts
///
/// - **Project**: Top-level container for all assets and spaces
/// - **Space**: Hierarchical folder structure within a project
/// - **Item**: A versioned asset (model, texture, workflow, etc.)
/// - **Revision**: A specific iteration of an item with artifacts
/// - **Artifact**: A file reference (path/URI) within a revision
/// - **Edge**: A relationship between revisions (dependencies, references)
/// - **Bundle**: A special item that aggregates other items
/// - **Kref**: A URI-based unique identifier for any Kumiho object
library kumiho;

import 'package:grpc/grpc_connection_interface.dart';

import 'src/api/artifact_api.dart';
import 'src/api/attribute_api.dart';
import 'src/api/bundle_api.dart';
import 'src/kref.dart';
import 'src/models/base.dart' show KumihoError;
import 'src/api/edge_api.dart';
import 'src/api/event_api.dart';
import 'src/api/item_api.dart';
import 'src/api/project_api.dart';
import 'src/api/revision_api.dart';
import 'src/api/space_api.dart';
import 'src/api/tenant_api.dart';
import 'src/base_client.dart';

// Import models for high-level API
import 'src/models/project.dart' as models;
import 'src/models/space.dart' as models;
import 'src/models/item.dart' as models;
import 'src/models/revision.dart' as models;
import 'src/models/artifact.dart' as models;

// Export all public APIs
export 'src/kref.dart';
export 'src/api/edge_api.dart' show EdgeType;
export 'src/generated/kumiho.pb.dart' hide Kref, Edge;
export 'src/generated/kumiho.pbenum.dart';
export 'src/generated/kumiho.pbgrpc.dart' hide Kref, Edge;

// Discovery bootstrap
export 'discovery.dart';

// Export model classes (Edge from models replaces protobuf Edge)
export 'src/models/base.dart';
export 'src/models/project.dart';
export 'src/models/space.dart';
export 'src/models/item.dart';
export 'src/models/revision.dart';
export 'src/models/artifact.dart';
export 'src/models/edge.dart';
export 'src/models/bundle.dart';
export 'src/models/paged_list.dart';

/// High-level Dart client for the Kumiho Cloud service.
///
/// This client provides access to all Kumiho gRPC endpoints for managing
/// projects, spaces, items, revisions, artifacts, edges, and bundles.
///
/// ## Authentication
///
/// Pass a Firebase ID token to the [token] parameter for authentication.
/// The token is automatically injected as a Bearer token in all requests.
///
/// ```dart
/// final client = KumihoClient(
///   host: 'us-central.kumiho.cloud',
///   port: 443,
///   token: firebaseIdToken,
///   secure: true,
/// );
/// ```
///
/// ## Connection Options
///
/// For local development (insecure):
/// ```dart
/// final client = KumihoClient(host: 'localhost', port: 50051);
/// ```
///
/// For production (TLS):
/// ```dart
/// final client = KumihoClient(
///   host: 'api.kumiho.cloud',
///   port: 443,
///   secure: true,
///   token: authToken,
/// );
/// ```
///
/// For custom channel:
/// ```dart
/// final client = KumihoClient(channel: existingChannel);
/// ```
class KumihoClient extends KumihoClientBase
    with
        ProjectApi,
        SpaceApi,
        ItemApi,
        RevisionApi,
        ArtifactApi,
        EdgeApi,
        BundleApi,
        EventApi,
        TenantApi,
        AttributeApi {
  /// Creates a new Kumiho client.
  ///
  /// Either provide an existing [channel], or specify [host] and [port]
  /// to create a new channel.
  ///
  /// [token] is the authentication token (Firebase ID token).
  /// [tenantId] is the tenant ID for anonymous public access (passed as x-tenant-id header).
  /// [secure] enables TLS when `true` (required for production).
  /// [options] allows custom channel configuration.
  KumihoClient({
    String host = 'localhost',
    int port = 8080,
    String? token,
    String? tenantId,
    ClientChannelBase? channel,
    ChannelOptions? options,
    bool secure = false,
  }) : super(
          clientChannel: channel,
          host: host,
          port: port,
          token: token,
          tenantId: tenantId,
          options: options,
          secure: secure,
        );

// ============================================================
// High-Level Model API
// ============================================================
// These helpers intentionally wrap protobuf responses in rich model
// objects so consumers rarely need to touch the generated gRPC stubs.
// The fluent API mirrors the Python SDK, making it easy to script
// common asset-management workflows without wrestling with wire types.

  /// Creates a new project and returns a [Project] model.
  ///
  /// ```dart
  /// final project = await client.newProject('film-2024', description: 'VFX assets');
  /// final chars = await project.createSpace('characters');
  /// ```
  Future<models.Project> newProject(
    String name, {
    String description = '',
  }) async {
    final response = await createProject(name, description: description);
    return models.Project(response, this);
  }

  /// Gets a project by name and returns a [Project] model.
  ///
  /// ```dart
  /// final project = await client.project('film-2024');
  /// final spaces = await project.getSpaces();
  /// ```
  Future<models.Project> project(String name) async {
    final projectList = await getProjects();
    final pb = projectList.firstWhere(
      (p) => p.name == name,
      orElse: () => throw KumihoError('Project not found: $name'),
    );
    return models.Project(pb, this);
  }

  /// Gets all projects and returns [Project] models.
  ///
  /// ```dart
  /// final projects = await client.projects();
  /// for (final p in projects) {
  ///   print(p.name);
  /// }
  /// ```
  Future<List<models.Project>> projects() async {
    final projectList = await getProjects();
    return projectList.map((p) => models.Project(p, this)).toList();
  }

  /// Gets a space by path and returns a [Space] model.
  ///
  /// ```dart
  /// final space = await client.space('/film-2024/characters');
  /// final items = await space.getItems();
  /// ```
  Future<models.Space> space(String path) async {
    final response = await getSpace(path);
    return models.Space(response, this);
  }

  /// Gets an item by kref and returns an [Item] model.
  ///
  /// ```dart
  /// final item = await client.item('kref://film-2024/models/hero.model');
  /// final latest = await item.getLatestRevision();
  /// ```
  Future<models.Item> item(String krefUri) async {
    final response = await getItemByKref(krefUri);
    return models.Item(response, this);
  }

  /// Gets a revision by kref and returns a [Revision] model.
  ///
  /// ```dart
  /// final revision = await client.revision('kref://film-2024/models/hero.model?r=1');
  /// final artifacts = await revision.getArtifacts();
  /// ```
  Future<models.Revision> revision(String krefUri) async {
    final response = await getRevision(krefUri);
    return models.Revision(response, this);
  }

  /// Gets an artifact by kref and returns an [Artifact] model.
  ///
  /// The kref must include artifact name: `kref://project/space/item.kind?r=N&a=NAME`
  ///
  /// ```dart
  /// final artifact = await client.artifact('kref://film-2024/models/hero.model?r=1&a=mesh');
  /// print(artifact.location);
  /// ```
  Future<models.Artifact> artifact(String krefUri) async {
    // Parse kref to extract revision and artifact name
    final kref = Kref(krefUri);
    final artifactName = kref.artifactName;
    if (artifactName == null) {
      throw KumihoError('Artifact kref must include artifact name: $krefUri');
    }
    final revisionKref = kref.revisionKref;
    if (revisionKref == null) {
      throw KumihoError('Artifact kref must include revision: $krefUri');
    }
    final response = await getArtifact(revisionKref.uri, artifactName);
    return models.Artifact(response, this);
  }

  /// Searches for items and returns [Item] models.
  ///
  /// ```dart
  /// final items = await client.searchItems(
  ///   contextFilter: 'film-2024/*',
  ///   kindFilter: 'model',
  /// );
  /// ```
  Future<List<models.Item>> searchItems({
    String contextFilter = '',
    String kindFilter = '',
    String nameFilter = '',
  }) async {
    final itemList = await itemSearch(contextFilter, nameFilter, kindFilter);
    return itemList.map((i) => models.Item(i, this)).toList();
  }
}

/// Backwards-compatible alias for older imports.
@Deprecated('Use KumihoClient instead')
typedef KumihoApiClient = KumihoClient;

