# Kumiho C++ SDK

Modern C++ client library for the Kumiho asset management and versioning platform.

[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://isocpp.org/std/the-standard)
[![gRPC](https://img.shields.io/badge/gRPC-1.50+-green.svg)](https://grpc.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Features

- **Full API Parity**: Complete feature parity with the Python Kumiho SDK
- **Modern C++17**: Uses `std::optional`, `std::string_view`, structured bindings
- **gRPC Backend**: High-performance communication with Kumiho servers
- **Type-Safe**: Strong typing with compile-time checks
- **Graph Traversal**: Dependency tracking and impact analysis
- **Streaming Events**: Real-time change notifications
- **Discovery Service**: Automatic endpoint resolution

## Terminology

| New Term       | Description                          |
|----------------|--------------------------------------|
| **Space**      | Hierarchical container/namespace     |
| **Item**       | Asset/entity in the graph            |
| **Revision**   | Specific state of an item            |
| **Artifact**   | File/location attached to a revision |
| **Edge**       | Relationship between revisions       |
| **Bundle**     | Curated set of items                 |
| **Kind**       | Category/classification of an item   |

> **Note**: All old method names and types are still supported as backwards-compatible aliases.

## Quick Start

### Prerequisites

- C++17 compatible compiler (MSVC 2019+, GCC 8+, Clang 8+)
- CMake 3.10+
- vcpkg (recommended for dependency management)
- gRPC and Protobuf

### Installation via vcpkg

```bash
# Install dependencies
vcpkg install grpc protobuf gtest

# Clone and build
git clone https://github.com/kumihoclouds/kumiho-cpp.git
cd kumiho-cpp
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=[vcpkg root]/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
```

### Basic Usage

```cpp
#include <kumiho/kumiho.hpp>
#include <iostream>

using namespace kumiho::api;

int main() {
    // Connect to server
    auto client = Client::createFromEnv();
    
    // Create a project
    auto project = client->createProject("my-project", "My first project");
    std::cout << "Created project: " << project->getName() << std::endl;
    
    // Create a space hierarchy
    auto assets = project->createSpace("assets");
    auto characters = assets->createSpace("characters");
    
    // Create an item with revision
    auto hero = characters->createItem("hero", "model");
    auto v1 = hero->createRevision({{"author", "artist1"}});
    
    // Add an artifact
    v1->createArtifact("main_mesh", "/path/to/hero.obj");
    
    std::cout << "Created revision " << v1->getNumber() << std::endl;
    
    return 0;
}
```

## Core Concepts

### Kref (Kumiho Reference)

Krefs are URI-style identifiers for all entities:

```cpp
// Parse a Kref
Kref kref("kref://my-project/assets/hero.model?r=1");

std::cout << "Project: " << kref.getProject() << std::endl;    // my-project
std::cout << "Space: " << kref.getSpace() << std::endl;        // assets
std::cout << "Item: " << kref.getItemName() << std::endl;      // hero
std::cout << "Kind: " << kref.getKind() << std::endl;          // model
std::cout << "Revision: " << *kref.getRevision() << std::endl; // 1

// Check validity
if (kref.isValid()) {
    // Use the kref
}

// Convert to string
std::string uri = kref.uri();
```

### Entity Hierarchy

```
Project
├── Space (can be nested)
│   ├── Space
│   │   └── Item.kind
│   │       ├── Revision 1
│   │       │   └── Artifact
│   │       └── Revision 2
│   └── Item.kind
└── Bundle (curated item collections)
```

### Edges and Dependencies

```cpp
// Create revisions
auto modelR1 = model.createRevision({});
auto rigR1 = rig.createRevision({});

// Create a dependency edge
auto edge = modelR1.createEdge(rigR1.kref(), EdgeType::DEPENDS_ON);

// Query edges
auto outgoing = modelR1.getEdges(EdgeDirection::OUTGOING);
auto incoming = rigR1.getEdges(EdgeDirection::INCOMING);

// Traverse the graph
auto deps = modelR1.getAllDependencies({}, 5, 100);
for (const auto& kref : deps.revision_krefs) {
    std::cout << "Depends on: " << kref << std::endl;
}

// Find shortest path
auto path = modelR1.findPathTo(targetKref, {}, 10, false);
if (path.path_exists) {
    std::cout << "Path length: " << path.path_length << std::endl;
}

// Impact analysis
auto impact = rigR1.analyzeImpact({}, 5, 100);
for (const auto& impacted : impact.impacted_revisions) {
    std::cout << "Would impact: " << impacted.revision_kref << std::endl;
}
```

### Bundles

```cpp
// Create a bundle
auto bundle = project.createBundle("my_bundle");

// Add members
bundle.addMember(item1);
bundle.addMember(item2);

// List members
for (const auto& member : bundle.getMembers()) {
    std::cout << "Member: " << member.item_kref.uri() << std::endl;
}

// View history
for (const auto& entry : bundle.getHistory()) {
    std::cout << entry.action << " at " << entry.created_at << std::endl;
}
```

### Event Streaming

```cpp
// Subscribe to events
client->subscribeEvents("my-project", [](const Event& event) {
    std::cout << "Event: " << event.eventType() << std::endl;
    std::cout << "Entity: " << event.entityKref().toString() << std::endl;
    return true;  // Continue listening
});

// Or use EventStream for manual control
auto stream = client->openEventStream("my-project");
while (true) {
    auto event = stream->next();
    if (!event) break;
    // Process event
}
```

### Time-Based Revision Queries

One of Kumiho's most powerful features is **time-based revision lookup**. This enables
reproducible builds, historical debugging, and auditing by answering questions like:
"What was the published revision of this asset on June 1st?"

#### Why Time-Based Queries Matter

In production pipelines, you often need to:

1. **Reproduce past renders**: Re-render a shot exactly as it was delivered months ago
2. **Debug regressions**: Compare current assets against a known-good state from a specific date
3. **Audit changes**: Understand what revision was used when a decision was made
4. **Compliance**: Prove what asset revisions were in use at a particular milestone

#### Supported Time Formats

The `time` parameter accepts multiple formats:

| Format | Example | Precision |
|--------|---------|-----------|
| **YYYYMMDDHHMM** | `"202406011330"` | Minute-level |
| **ISO 8601** | `"2024-06-01T13:30:00Z"` | Second-level |
| **std::chrono** | `system_clock::time_point` | Sub-second |

#### Using Time-Based Methods

```cpp
#include <chrono>

// Get revision by tag
auto published = item->getRevisionByTag("published");

// Get revision by time (YYYYMMDDHHMM format)
auto historyRev = item->getRevisionByTime("202406011330");

// Using ISO 8601 format for sub-second precision
auto historyRev2 = item->getRevisionByTime("2024-06-01T13:30:45Z");

// Using std::chrono (C++ datetime)
auto june_1 = std::chrono::system_clock::from_time_t(1717243200);  // June 1, 2024
auto historyRev3 = item->getRevisionByTime(june_1);

// Get revision by BOTH tag and time
// "What was the published revision on June 1st?"
auto publishedAtTime = item->getRevisionByTagAndTime("published", "202406011330");
if (publishedAtTime) {
    std::cout << "On June 1, published revision was r" 
              << publishedAtTime->getRevisionNumber() << std::endl;
}

// Using std::chrono with tag
auto publishedAtTime2 = item->getRevisionByTagAndTime("published", june_1);
```

#### Time-Based Kref URIs

You can also use time-based queries directly in Kref URIs:

```cpp
// Get published revision at a specific time
auto revision = client->resolveKref(
    "kref://my-project/chars/hero.model",
    "published",      // tag
    "202406011330"    // time (YYYYMMDDHHMM or ISO 8601)
);

// Using ISO 8601 format
auto revision2 = client->resolveKref(
    "kref://my-project/chars/hero.model",
    "published",
    "2024-06-01T13:30:00Z"
);

// Resolve to artifact location at that point in time
auto location = client->resolve("kref://my-project/chars/hero.model?t=published&time=202406011330");
```

**Kref time query parameters:**
| Parameter | Description |
|-----------|-------------|
| `t=<tag>` | Find revision with this tag (e.g., `t=published`, `t=approved`) |
| `time=<YYYYMMDDHHMM>` | Point in time to query (e.g., `time=202406011330`) |

#### Practical Examples

**Reproduce a past delivery:**
```cpp
// Find all assets as they were for the Q2 delivery
std::string delivery_time = "202406302359";  // June 30, 2024 23:59

for (const auto& item : space->getItems()) {
    auto rev = item->getRevisionByTagAndTime("published", delivery_time);
    if (rev) {
        std::cout << item->getName() << ": r" << rev->getRevisionNumber() << std::endl;
        for (const auto& artifact : rev->getArtifacts()) {
            std::cout << "  -> " << artifact->getLocation() << std::endl;
        }
    }
}
```

**Compare current vs historical:**
```cpp
// What changed between two milestones?
auto alpha_rev = item->getRevisionByTagAndTime("published", "202403010000");
auto beta_rev = item->getRevisionByTagAndTime("published", "202406010000");

if (alpha_rev && beta_rev && alpha_rev->getRevisionNumber() != beta_rev->getRevisionNumber()) {
    std::cout << "Asset changed from r" << alpha_rev->getRevisionNumber() 
              << " to r" << beta_rev->getRevisionNumber() << std::endl;
}
```

#### Tags and Time

The `published` tag is especially important for time-based queries because:

1. **Immutability**: Published revisions cannot be modified or deleted
2. **Stability**: Downstream consumers can rely on published revisions not changing
3. **Audit trail**: Tag history is preserved, so you can query what was published when

Common tags for time-based queries:
- `published`: Approved for downstream consumption
- `approved`: Supervisor-approved revisions
- `delivered`: Revisions sent to clients
- `milestone-alpha`, `milestone-beta`: Project milestone snapshots

### Tenant Usage

```cpp
// Check tenant resource usage
auto usage = client->getTenantUsage();

std::cout << "Nodes: " << usage.node_count << "/" << usage.node_limit << std::endl;
std::cout << "Usage: " << usage.usagePercent() << "%" << std::endl;

if (usage.isNearLimit()) {
    std::cout << "Warning: Approaching node limit!" << std::endl;
}
```

### Discovery & Auto-Configuration

```cpp
#include <kumiho/discovery.hpp>
#include <kumiho/token_loader.hpp>

// Auto-discover endpoint from Firebase token
auto firebaseToken = loadFirebaseToken();  // From env or file
if (firebaseToken) {
    auto client = clientFromDiscovery(*firebaseToken);
    // Client is now configured for the correct region
}

// Or load bearer token directly
auto bearerToken = loadBearerToken();  // From KUMIHO_AUTH_TOKEN env
```

## API Reference

### Client

| Method | Description |
|--------|-------------|
| `createProject(name, description)` | Create a new project |
| `getProjects()` | List all projects |
| `getProject(name)` | Get project by name |
| `deleteProject(id, force)` | Delete a project |
| `getRevision(kref)` | Get revision by Kref |
| `getItem(kref)` | Get item by Kref |
| `resolveKref(kref, tag, time)` | Resolve Kref with optional tag/time |
| `resolve(kref)` | Resolve Kref to artifact location |
| `getTenantUsage()` | Get tenant usage stats |
| `subscribeEvents(project, callback)` | Subscribe to events |

### Project

| Method | Description |
|--------|-------------|
| `createSpace(name)` | Create a child space |
| `getSpace(path)` | Get space by path |
| `getSpaces(recursive)` | List spaces |
| `createBundle(name)` | Create a bundle |
| `setPublic(allow)` | Set public access |
| `update(description)` | Update project |
| `delete(force)` | Delete project |

### Space

| Method | Description |
|--------|-------------|
| `createSpace(name)` | Create nested space |
| `createItem(name, kind)` | Create an item |
| `getItems()` | List items |
| `getItem(name, kind)` | Get item |

### Item

| Method | Description |
|--------|-------------|
| `createRevision(metadata)` | Create new revision |
| `getRevisions()` | List all revisions |
| `getRevision(number)` | Get revision by number |
| `getRevisionByTag(tag)` | Get revision by tag |
| `getRevisionByTime(time)` | Get revision by timestamp (YYYYMMDDHHMM) |
| `getRevisionByTagAndTime(tag, time)` | Get revision by tag and timestamp |
| `getLatestRevision()` | Get latest revision |
| `peekNextRevision()` | Peek at next revision number |

### Revision

| Method | Description |
|--------|-------------|
| `createArtifact(name, path, meta)` | Add artifact |
| `getArtifacts()` | List artifacts |
| `createEdge(target, type)` | Create edge |
| `getEdges(direction)` | Get edges |
| `addTag(tag)` | Add tag |
| `removeTag(tag)` | Remove tag |
| `updateMetadata(meta)` | Update metadata |
| `getAllDependencies(...)` | Traverse dependencies |
| `analyzeImpact(...)` | Impact analysis |

## Building from Source

### Windows (Visual Studio 2022)

```powershell
# Configure
cmake -B build -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake

# Build
cmake --build build --config Release

# Run tests
cd build
ctest -C Release --output-on-failure
```

### Linux/macOS

```bash
# Configure
cmake -B build \
    -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
    -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build

# Run tests
cd build && ctest --output-on-failure
```

### Running Integration Tests

```bash
# Enable integration tests
export KUMIHO_INTEGRATION_TEST=1
export KUMIHO_SERVER_URL=localhost:50051

# Run all tests
ctest --output-on-failure

# Run specific test suite
./kumiho_integration_tests
```

## Project Structure

```
kumiho-cpp/
├── include/kumiho/       # Public headers
│   ├── kumiho.hpp        # Main include
│   ├── client.hpp        # Client class
│   ├── project.hpp       # Project class
│   ├── space.hpp         # Space class (formerly group.hpp)
│   ├── item.hpp          # Item class (formerly product.hpp)
│   ├── revision.hpp      # Revision class (formerly version.hpp)
│   ├── artifact.hpp      # Artifact class (formerly resource.hpp)
│   ├── edge.hpp          # Edge class (formerly link.hpp)
│   ├── bundle.hpp        # Bundle class (formerly collection.hpp)
│   ├── kref.hpp          # Kref URI handling
│   ├── event.hpp         # Event streaming
│   ├── discovery.hpp     # Auto-discovery
│   ├── token_loader.hpp  # Token utilities
│   ├── types.hpp         # Common types
│   ├── base.hpp          # Base classes
│   └── error.hpp         # Exception types
├── src/                  # Implementation
├── tests/                # Unit tests
│   └── integration/      # Integration tests
├── proto/                # Protobuf definitions
├── docs/                 # Documentation
├── CMakeLists.txt        # Build configuration
└── vcpkg.json           # vcpkg manifest
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `KUMIHO_AUTH_TOKEN` | Bearer token for authentication |
| `KUMIHO_FIREBASE_ID_TOKEN` | Firebase ID token |
| `KUMIHO_CONTROL_PLANE_URL` | Control plane URL override |
| `KUMIHO_USE_CONTROL_PLANE_TOKEN` | Use control plane token |
| `KUMIHO_CONFIG_DIR` | Config directory override |
| `KUMIHO_INTEGRATION_TEST` | Enable integration tests |
| `KUMIHO_SERVER_URL` | Server URL for tests |

## Error Handling

```cpp
#include <kumiho/error.hpp>

try {
    auto project = client->getProject("non-existent");
} catch (const NotFoundError& e) {
    std::cerr << "Project not found: " << e.what() << std::endl;
} catch (const AuthenticationError& e) {
    std::cerr << "Auth failed: " << e.what() << std::endl;
} catch (const KumihoError& e) {
    std::cerr << "Kumiho error: " << e.what() << std::endl;
}
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Links

- [Kumiho Clouds](https://kumiho.io)
- [API Documentation](https://docs.kumiho.io/cpp)
- [Python SDK](https://github.com/kumihoclouds/kumiho-python)
- [Issue Tracker](https://github.com/kumihoclouds/kumiho-cpp/issues)
