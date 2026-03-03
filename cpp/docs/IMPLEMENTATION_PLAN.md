# Kumiho C++ SDK Implementation Plan

**Goal:** Modernize kumiho-cpp to achieve feature parity with kumiho-python while adopting modular design patterns.

**Reference:** kumiho-python v0.3.0

---

## Current State Assessment

### Existing Code Quality: ⭐⭐⭐☆☆ (3/5)

| Aspect | Status | Notes |
|--------|--------|-------|
| gRPC Integration | ✅ Good | Proper channel/stub management |
| Memory Management | ✅ Good | Consistent shared_ptr usage |
| TLS/SSL Support | ✅ Good | CA bundles, authority override |
| Endpoint Parsing | ✅ Good | Handles multiple URI formats |
| Error Handling | ⚠️ Basic | Only std::runtime_error |
| Code Organization | ❌ Poor | Single header + single cpp file |
| Documentation | ⚠️ Basic | Some doxygen comments |
| Testing | ❌ Missing | Only example file |

### Architecture Problem

**Current (Monolithic):**
```
include/
  kumiho.h           # 242 lines - ALL classes in one header
client/
  kumiho.cpp         # 1431 lines - ALL implementations in one file
```

**Target (Modular - Matching Python):**
```
include/kumiho/
  kumiho.hpp         # Main include (forwards + convenience)
  client.hpp         # Client class
  project.hpp        # Project entity
  group.hpp          # Group entity  
  product.hpp        # Product entity
  version.hpp        # Version entity
  resource.hpp       # Resource entity
  link.hpp           # Link entity + LinkType + LinkDirection
  collection.hpp     # Collection entity
  kref.hpp           # Kref URI parser
  event.hpp          # Event + EventStream
  discovery.hpp      # Discovery + auto-configure
  error.hpp          # Exception hierarchy
  types.hpp          # Common typedefs, constants
src/
  client.cpp
  project.cpp
  group.cpp
  product.cpp
  version.cpp
  resource.cpp
  link.cpp
  collection.cpp
  kref.cpp
  event.cpp
  discovery.cpp
```

---

## Implementation Checklist

### Phase 1: Project Structure & Modularization ✅ COMPLETE
> Refactor existing code into modular files without changing functionality

- [x] **1.1** Create new directory structure
  - [x] Create `include/kumiho/` directory
  - [x] Create `src/` directory (rename from `client/`)
  - [x] Update `CMakeLists.txt` for new structure

- [x] **1.2** Extract `kref.hpp` / `kref.cpp`
  - [x] Move `Kref` class to separate files
  - [x] Add `KrefValidationError` exception
  - [x] Add `validate_kref()` and `is_valid_kref()` functions
  - [x] Match Python's parsing logic exactly

- [x] **1.3** Extract `error.hpp`
  - [x] Create `KumihoError` base exception
  - [x] Create `RpcError` for gRPC failures
  - [x] Create `NotFoundError` for NOT_FOUND status
  - [x] Create `ProjectLimitError` for RESOURCE_EXHAUSTED
  - [x] Create `ValidationError` for input validation
  - [x] Create `DiscoveryError` for discovery failures

- [x] **1.4** Extract `types.hpp`
  - [x] Define common type aliases
  - [x] Define constants (LATEST_TAG, PUBLISHED_TAG)
  - [x] Define `Metadata` = `std::map<std::string, std::string>`

- [x] **1.5** Extract entity headers (Group, Product, Version, Resource, Link)
  - [x] Move each class to its own header
  - [x] Create corresponding `.cpp` files
  - [x] Add forward declarations to avoid circular includes

- [x] **1.6** Extract `client.hpp` / `client.cpp`
  - [x] Keep Client class with all gRPC methods
  - [x] Add proper includes for all entity types

- [x] **1.7** Create main `kumiho.hpp` umbrella header
  - [x] Include all public headers
  - [x] Add namespace aliases for convenience
  - [x] Match Python's `__init__.py` exports

- [x] **1.8** Update build system
  - [x] Update `CMakeLists.txt` with all new source files
  - [x] Ensure library builds correctly
  - [x] Update tests to use new includes
  - [x] All targets build: `kumiho.lib`, examples, tests

**Files Created:**
- `include/kumiho/types.hpp`, `error.hpp`, `kref.hpp`, `link.hpp`, `event.hpp`
- `include/kumiho/group.hpp`, `product.hpp`, `version.hpp`, `resource.hpp`
- `include/kumiho/project.hpp`, `collection.hpp`, `client.hpp`, `kumiho.hpp`
- `src/client.cpp`, `kref.cpp`, `link.cpp`, `event.cpp`
- `src/group.cpp`, `product.cpp`, `version.cpp`, `resource.cpp`
- `src/project.cpp`, `collection.cpp`

---

### Phase 2: Add Missing Entities ✅ COMPLETE
> Implement Project and Collection classes

- [x] **2.1** Implement `project.hpp` / `project.cpp`
  - [x] `Project` class with attributes:
    - [x] `project_id: std::string`
    - [x] `name: std::string`
    - [x] `description: std::string`
    - [x] `created_at: std::optional<std::string>`
    - [x] `updated_at: std::optional<std::string>`
    - [x] `deprecated: bool`
    - [x] `allow_public: bool`
  - [x] Methods:
    - [x] `createGroup(name) -> Group`
    - [x] `getGroup(path) -> Group`
    - [x] `getGroups(recursive=false) -> vector<Group>`
    - [x] `createCollection(name) -> Collection`
    - [x] `getCollection(name) -> Collection`
    - [x] `setPublic(allow) -> Project`
    - [x] `update(description) -> Project`
    - [x] `delete(force=false) -> void`

- [x] **2.2** Add Project methods to Client
  - [x] `createProject(name, description) -> Project`
  - [x] `getProjects() -> vector<Project>`
  - [x] `getProject(name) -> optional<Project>`
  - [x] `deleteProject(project_id, force) -> void`
  - [x] `updateProject(project_id, ...) -> Project`

- [x] **2.3** Implement `collection.hpp` / `collection.cpp`
  - [x] `Collection` class (extends Product pattern)
  - [x] `CollectionMember` struct:
    - [x] `product_kref: Kref`
    - [x] `added_at: std::string`
    - [x] `added_by: std::string`
    - [x] `added_by_username: std::string`
    - [x] `added_in_version: int`
  - [x] `CollectionVersionHistory` struct:
    - [x] `version_number: int`
    - [x] `action: std::string` (CREATED/ADDED/REMOVED)
    - [x] `member_product_kref: std::optional<Kref>`
    - [x] `author: std::string`
    - [x] `username: std::string`
    - [x] `created_at: std::string`
    - [x] `metadata: Metadata`
  - [x] Methods:
    - [x] `addMember(product) -> Collection`
    - [x] `removeMember(product) -> Collection`
    - [x] `getMembers() -> vector<CollectionMember>`
    - [x] `getHistory() -> vector<CollectionVersionHistory>`

- [x] **2.4** Add Collection client methods
  - [x] `createCollection(parent_path, name) -> Collection`
  - [x] `createCollection(parent_kref, name) -> Collection` (overload)
  - [x] `getCollection(parent_path, name) -> Collection`
  - [x] `addCollectionMember(collection_kref, product_kref) -> void`
  - [x] `removeCollectionMember(collection_kref, product_kref) -> void`
  - [x] `getCollectionMembers(collection_kref) -> vector<CollectionMember>`
  - [x] `getCollectionHistory(collection_kref) -> vector<CollectionVersionHistory>`

- [x] **2.5** Add reserved product type validation
  - [x] Define `RESERVED_PRODUCT_TYPES` constant in `types.hpp`
  - [x] Create `ReservedProductTypeError` exception in `error.hpp`
  - [x] Add validation in `Client::createProduct()` and `Group::createProduct()`

---

### Phase 3: Add Missing Methods to Existing Entities
> Bring existing classes to full parity with Python

- [x] **3.1** Group enhancements
  - [x] `getProject() -> Project` (navigate to parent project)
  - [x] `getProducts(name_filter, ptype_filter) -> vector<Product>` (with filters)
  - [x] `createCollection(name) -> Collection`
  - [x] `getCollection(name) -> Collection`

- [x] **3.2** Product enhancements
  - [x] `setDeprecated(deprecated) -> Product`
  - [x] `getProject() -> Project`
  - [x] `refresh() -> Product` (reload from server)

- [x] **3.3** Version enhancements
  - [x] `refresh() -> Version` (reload from server)
  - [x] `setDeprecated(deprecated) -> Version`
  - [x] `publish() -> Version` (add published tag, make immutable)
  - [x] `isPublished() -> bool` (check published tag)
  - [x] `getProject() -> Project`
  - [x] `createLink(target, link_type, metadata) -> Link`
  - [x] `getLinks(link_type_filter, direction) -> vector<Link>`
  - [x] `deleteLink(target, link_type) -> void`

- [x] **3.4** Resource enhancements
  - [x] `getVersion() -> Version`
  - [x] `getProduct() -> Product`
  - [x] `getGroup() -> Group`
  - [x] `getProject() -> Project`
  - [x] `setDefault() -> void` (set as default resource)
  - [x] `setDeprecated(deprecated) -> Resource`

- [x] **3.5** Link enhancements
  - [x] Add `LinkDirection` enum (OUTGOING=0, INCOMING=1, BOTH=2)
  - [x] Add `LinkType` class with constants:
    - [x] `BELONGS_TO`
    - [x] `CREATED_FROM`
    - [x] `REFERENCED`
    - [x] `DEPENDS_ON`
    - [x] `DERIVED_FROM`
    - [x] `CONTAINS`
  - [x] Add `validateLinkType()` function
  - [x] Add `LinkTypeValidationError` exception
  - [x] `created_at: std::optional<std::string>`
  - [x] `author: std::string`
  - [x] `username: std::string`
  - [x] `deleteLink() -> void`

---

### Phase 4: Graph Traversal & Advanced Features ✅
> Add graph traversal capabilities matching Python

- [x] **4.1** Add traversal types (in `types.hpp`)
  - [x] `PathStep` struct:
    - [x] `version_kref: std::string`
    - [x] `link_type: std::string`
    - [x] `depth: int`
  - [x] `VersionPath` struct:
    - [x] `steps: vector<PathStep>`
    - [x] `total_depth: int`
  - [x] `TraversalResult` struct:
    - [x] `paths: vector<VersionPath>`
    - [x] `version_krefs: vector<string>`
    - [x] `links: vector<shared_ptr<Link>>`
    - [x] `total_count: int`
    - [x] `truncated: bool`
  - [x] `ShortestPathResult` struct:
    - [x] `paths: vector<VersionPath>`
    - [x] `path_exists: bool`
    - [x] `path_length: int`
    - [x] `first_path() -> const VersionPath*`
  - [x] `ImpactedVersion` struct:
    - [x] `version_kref: std::string`
    - [x] `product_kref: std::string`
    - [x] `impact_depth: int`
    - [x] `impact_path_types: vector<string>`
  - [x] `ImpactAnalysisResult` struct:
    - [x] `impacted_versions: vector<ImpactedVersion>`
    - [x] `total_impacted: int`
    - [x] `truncated: bool`

- [x] **4.2** Add Client graph methods
  - [x] `traverseLinks(origin_kref, direction, link_type_filter, max_depth, limit, include_path) -> TraversalResult`
  - [x] `findShortestPath(source, target, link_type_filter, max_depth, all_shortest) -> ShortestPathResult`
  - [x] `analyzeImpact(version_kref, link_type_filter, max_depth, limit) -> ImpactAnalysisResult`

- [x] **4.3** Add Version graph convenience methods
  - [x] `getAllDependencies(link_type_filter, max_depth, limit) -> TraversalResult`
  - [x] `getAllDependents(link_type_filter, max_depth, limit) -> TraversalResult`
  - [x] `findPathTo(target, link_type_filter, max_depth, all_paths) -> ShortestPathResult`
  - [x] `analyzeImpact(link_type_filter, max_depth, limit) -> ImpactAnalysisResult`

---

### Phase 5: Attributes System ✅
> Add dynamic key-value attribute support

- [x] **5.1** Add attribute methods to Client
  - [x] `getAttribute(kref, key) -> optional<string>`
  - [x] `setAttribute(kref, key, value) -> bool`
  - [x] `deleteAttribute(kref, key) -> bool`

- [x] **5.2** Add attribute methods to entities
  - [x] `Product::getAttribute(key) -> optional<string>`
  - [x] `Product::setAttribute(key, value) -> bool`
  - [x] `Product::deleteAttribute(key) -> bool`
  - [x] `Version::getAttribute(key) -> optional<string>`
  - [x] `Version::setAttribute(key, value) -> bool`
  - [x] `Version::deleteAttribute(key) -> bool`
  - [x] `Resource::getAttribute(key) -> optional<string>`
  - [x] `Resource::setAttribute(key, value) -> bool`
  - [x] `Resource::deleteAttribute(key) -> bool`
  - [x] `Group::getAttribute(key) -> optional<string>`
  - [x] `Group::setAttribute(key, value) -> bool`
  - [x] `Group::deleteAttribute(key) -> bool`

---

### Phase 6: Discovery & Authentication ✅
> Add automatic endpoint discovery and auth token loading

- [x] **6.1** Implement `discovery.hpp` / `discovery.cpp`
  - [x] `DiscoveryRecord` struct:
    - [x] `tenant_id: std::string`
    - [x] `region: RegionRouting`
  - [x] `RegionRouting` struct:
    - [x] `region_code: std::string`
    - [x] `server_url: std::string`
    - [x] `grpc_authority: std::optional<std::string>`
  - [x] `CacheControl` struct with `isExpired()`, `shouldRefresh()`
  - [x] `DiscoveryCache` class:
    - [x] `load(cache_key) -> optional<DiscoveryRecord>`
    - [x] `store(cache_key, record) -> void`
  - [x] `DiscoveryManager` class:
    - [x] `resolve(id_token, tenant_hint, force_refresh) -> DiscoveryRecord`
    - [x] Local JSON caching support
  - [x] `DiscoveryError` exception (already in error.hpp)

- [x] **6.2** Add token loading (`token_loader.hpp` / `token_loader.cpp`)
  - [x] `loadBearerToken() -> optional<string>`
  - [x] `loadFirebaseToken() -> optional<string>`
  - [x] `isControlPlaneToken(token) -> bool`
  - [x] `decodeJwtClaims(token) -> map<string, string>`
  - [x] `getConfigDir() -> path` (returns `~/.kumiho/`)
  - [x] `getCredentialsPath() -> path`
  - [x] Support `KUMIHO_AUTH_TOKEN` env var override
  - [x] Support `KUMIHO_FIREBASE_ID_TOKEN` env var
  - [x] Support `KUMIHO_USE_CONTROL_PLANE_TOKEN` flag

- [x] **6.3** Add auto-configure function
  - [x] `clientFromDiscovery(id_token, tenant_hint, ...) -> shared_ptr<Client>`
  - [x] `getDefaultControlPlaneUrl() -> string`
  - [x] `getDefaultCachePath() -> path`

**Files Created:**
- `include/kumiho/discovery.hpp` - Discovery types and DiscoveryManager
- `include/kumiho/token_loader.hpp` - Token loading utilities
- `src/discovery.cpp` - Discovery implementation
- `src/token_loader.cpp` - Token loader implementation

**Note:** Remote HTTP discovery endpoint calls are stubbed (requires HTTP client library like libcurl). 
Local cache operations are fully functional.

---

### Phase 7: Tenant & Usage APIs ✅
> Add tenant-level operations

- [x] **7.1** Add tenant usage methods
  - [x] `TenantUsage` struct in `types.hpp`:
    - [x] `node_count: int64_t`
    - [x] `node_limit: int64_t`
    - [x] `tenant_id: std::string`
    - [x] `usagePercent() -> double` (helper method)
    - [x] `isNearLimit() -> bool` (>80% usage)
    - [x] `isAtLimit() -> bool` (100% usage)
  - [x] `Client::getTenantUsage() -> TenantUsage`

---

### Phase 8: Testing & Documentation ✅
> Add comprehensive test suite and documentation

- [x] **8.1** Unit tests
  - [x] `tests/test_kref.cpp` - Kref parsing tests (26 tests)
  - [x] `tests/test_types.cpp` - Types and struct tests (20 tests)
  - [x] `tests/test_token_loader.cpp` - Token loading tests (18 tests)
  - [x] `tests/test_discovery.cpp` - Discovery caching tests (19 tests)
  - [x] `tests/test_api.cpp` - API client mock tests (existing)
  - [x] `tests/test_streaming.cpp` - Streaming tests (existing)

- [x] **8.2** Integration tests
  - [x] `tests/integration/test_workflow.cpp` - Full workflow tests (6 tests)
    - ClientConnection, FullEntityHierarchy, LinkingWorkflow
    - MetadataUpdateWorkflow, VersionTaggingWorkflow, TenantUsageQuery
  - [x] `tests/integration/test_discovery_integration.cpp` - Discovery tests (7 tests)
    - DiscoveryCacheOperations, DiscoveryManagerInit, DiscoveryManagerCustomUrl
    - ControlPlaneTokenDetection, ConfigDirectoryPaths, TokenLoadingFromEnv, DefaultControlPlaneUrl
  - [x] Integration test structure with environment variable control
  - [x] Full integration tests verified against local servers (localhost:8080 data plane, localhost:3000 control plane)

- [x] **8.3** Documentation
  - [x] Doxygen-style documentation in headers
  - [x] Usage examples in README.md
  - [x] Doxyfile configuration for API reference generation
  - [ ] Migration guide from old API (future)

- [x] **8.4** CMake improvements
  - [x] Add test targets (6 unit test + 2 integration test executables)
  - [x] GTest integration
  - [x] Add install target with proper include directories
  - [x] Add find_package support (`cmake/kumiho-config.cmake.in`)
  - [x] vcpkg manifest (`vcpkg.json`)

**Test Coverage:**
- Total: 83+ unit tests across 6 unit test executables
- Integration tests: 13 tests across 2 executables (6 workflow + 7 discovery)
- All unit tests pass on Windows/MSVC
- All integration tests pass against local servers (requires KUMIHO_INTEGRATION_TEST=1)

---

## File Mapping: Python → C++

| Python Module | C++ Header | C++ Source |
|---------------|------------|------------|
| `__init__.py` | `kumiho.hpp` | - |
| `client.py` | `client.hpp` | `client.cpp` |
| `project.py` | `project.hpp` | `project.cpp` |
| `group.py` | `group.hpp` | `group.cpp` |
| `product.py` | `product.hpp` | `product.cpp` |
| `version.py` | `version.hpp` | `version.cpp` |
| `resource.py` | `resource.hpp` | `resource.cpp` |
| `link.py` | `link.hpp` | `link.cpp` |
| `collection.py` | `collection.hpp` | `collection.cpp` |
| `kref.py` | `kref.hpp` | `kref.cpp` |
| `event.py` | `event.hpp` | `event.cpp` |
| `discovery.py` | `discovery.hpp` | `discovery.cpp` |
| `base.py` | `base.hpp` | - |
| `_token_loader.py` | `token_loader.hpp` | `token_loader.cpp` |

---

## Priority Order

1. **Phase 1** (Foundation) - ✅ COMPLETE
2. **Phase 2** (Project/Collection) - ✅ COMPLETE
3. **Phase 3** (Method parity) - ✅ COMPLETE
4. **Phase 4** (Graph traversal) - ✅ COMPLETE
5. **Phase 5** (Attributes) - ✅ COMPLETE
6. **Phase 6** (Discovery) - ✅ COMPLETE
7. **Phase 7** (Tenant) - ✅ COMPLETE
8. **Phase 8** (Testing) - ✅ COMPLETE

---

## Estimated Effort

| Phase | Effort | Dependencies | Status |
|-------|--------|--------------|--------|
| Phase 1 | 4-6 hours | None | ✅ Complete |
| Phase 2 | 3-4 hours | Phase 1 | ✅ Complete |
| Phase 3 | 3-4 hours | Phase 1 | ✅ Complete |
| Phase 4 | 2-3 hours | Phase 3 | ✅ Complete |
| Phase 5 | 1-2 hours | Phase 1 | ✅ Complete |
| Phase 6 | 3-4 hours | Phase 1 | ✅ Complete |
| Phase 7 | 1 hour | Phase 1 | ✅ Complete |
| Phase 8 | 4-6 hours | All | ✅ Complete |

**Total: ~22-30 hours - ALL PHASES COMPLETE**

---

## Notes

- Use C++17 features (std::optional, std::string_view where appropriate)
- Consider C++20 concepts for type constraints if available
- Follow Google C++ Style Guide for consistency
- Use `#pragma once` for header guards
- Namespace: `kumiho::api` (keep existing)
- All public methods should have doxygen comments
