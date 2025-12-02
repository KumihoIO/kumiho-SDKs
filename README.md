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
    auto client = std::make_shared<Client>("localhost:50051");
    
    // Create a project
    auto project = client->createProject("my-project", "My first project");
    std::cout << "Created project: " << project.name() << std::endl;
    
    // Create a group hierarchy
    auto assets = project.createGroup("assets");
    auto characters = assets.createGroup("characters");
    
    // Create a product with version
    auto hero = characters.createProduct("hero", "model");
    auto v1 = hero.createVersion({{"author", "artist1"}});
    
    // Add a resource
    v1.addResource("main_mesh", "geometry", "/path/to/hero.obj", {
        {"format", "obj"},
        {"vertices", "50000"}
    });
    
    std::cout << "Created version " << v1.versionNumber() << std::endl;
    
    return 0;
}
```

## Core Concepts

### Kref (Kumiho Reference)

Krefs are URI-style identifiers for all entities:

```cpp
// Parse a Kref
Kref kref("kref://my-project/assets/hero.model/v1");

std::cout << "Project: " << kref.getProject() << std::endl;     // my-project
std::cout << "Group: " << kref.getGroup() << std::endl;         // assets
std::cout << "Product: " << kref.getProductName() << std::endl; // hero
std::cout << "Type: " << kref.getType() << std::endl;           // model
std::cout << "Version: " << kref.getVersion() << std::endl;     // 1

// Check validity
if (kref.isValid()) {
    // Use the kref
}

// Convert to string
std::string uri = kref.toString();
```

### Entity Hierarchy

```
Project
├── Group (can be nested)
│   ├── Group
│   │   └── Product.type
│   │       ├── Version 1
│   │       │   └── Resource
│   │       └── Version 2
│   └── Product.type
└── Collection (special product type)
```

### Linking and Dependencies

```cpp
// Create versions
auto modelV1 = model.createVersion({});
auto rigV1 = rig.createVersion({});

// Create a dependency link
auto link = modelV1.createLink(rigV1.kref(), "DEPENDS_ON");

// Query links
auto outgoing = modelV1.getLinks(LinkDirection::OUTGOING);
auto incoming = rigV1.getLinks(LinkDirection::INCOMING);

// Traverse the graph
auto deps = modelV1.getAllDependencies({}, 5, 100);
for (const auto& kref : deps.version_krefs) {
    std::cout << "Depends on: " << kref << std::endl;
}

// Find shortest path
auto path = modelV1.findPathTo(targetKref, {}, 10, false);
if (path.path_exists) {
    std::cout << "Path length: " << path.path_length << std::endl;
}

// Impact analysis
auto impact = rigV1.analyzeImpact({}, 5, 100);
for (const auto& impacted : impact.impacted_versions) {
    std::cout << "Would impact: " << impacted.version_kref << std::endl;
}
```

### Collections

```cpp
// Create a collection
auto collection = project.createCollection("my_collection");

// Add members
collection.addMember(product1);
collection.addMember(product2);

// List members
for (const auto& member : collection.getMembers()) {
    std::cout << "Member: " << member.product_kref.toString() << std::endl;
}

// View history
for (const auto& entry : collection.getHistory()) {
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
| `getVersion(kref)` | Get version by Kref |
| `getProduct(kref)` | Get product by Kref |
| `getTenantUsage()` | Get tenant usage stats |
| `subscribeEvents(project, callback)` | Subscribe to events |

### Project

| Method | Description |
|--------|-------------|
| `createGroup(name)` | Create a child group |
| `getGroup(path)` | Get group by path |
| `getGroups(recursive)` | List groups |
| `createCollection(name)` | Create a collection |
| `setPublic(allow)` | Set public access |
| `update(description)` | Update project |
| `delete(force)` | Delete project |

### Group

| Method | Description |
|--------|-------------|
| `createGroup(name)` | Create nested group |
| `createProduct(name, type)` | Create a product |
| `getProducts()` | List products |
| `getProduct(name, type)` | Get product |

### Product

| Method | Description |
|--------|-------------|
| `createVersion(metadata)` | Create new version |
| `getVersions()` | List all versions |
| `getVersion(number)` | Get version by number |
| `getVersionByTag(tag)` | Get version by tag |
| `getLatestVersion()` | Get latest version |

### Version

| Method | Description |
|--------|-------------|
| `addResource(name, type, path, meta)` | Add resource |
| `getResources()` | List resources |
| `createLink(target, type)` | Create link |
| `getLinks(direction)` | Get links |
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
│   ├── group.hpp         # Group class
│   ├── product.hpp       # Product class
│   ├── version.hpp       # Version class
│   ├── resource.hpp      # Resource class
│   ├── link.hpp          # Link class
│   ├── collection.hpp    # Collection class
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
