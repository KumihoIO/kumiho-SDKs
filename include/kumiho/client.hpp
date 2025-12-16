/**
 * @file client.hpp
 * @brief Low-level gRPC client for the Kumiho Cloud service.
 *
 * This module provides the Client class that handles all gRPC communication
 * with Kumiho Cloud servers. It manages connection establishment, authentication,
 * and all gRPC method calls.
 *
 * Terminology:
 * - Space: A hierarchical container/namespace
 * - Item: An asset/entity in the graph
 * - Revision: A specific state of an item
 * - Artifact: A file/location attached to a revision
 * - Edge: A relationship between revisions
 * - Bundle: A curated set of items
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <grpcpp/grpcpp.h>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/error.hpp"
#include "kumiho/bundle.hpp"  // For BundleMember, BundleRevisionHistory in inline functions
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
// Note: Bundle, BundleMember, BundleRevisionHistory are defined in bundle.hpp (included above)
class Project;
class Space;
class Item;
class Revision;
class Artifact;
class Edge;
class Event;
class EventStream;

/**
 * @brief The main client for interacting with Kumiho Cloud services.
 *
 * The Client class provides methods for all Kumiho operations including
 * creating and managing projects, spaces, items, revisions, artifacts,
 * and edges.
 *
 * Example:
 * @code
 *   // Create from environment variables
 *   auto client = Client::createFromEnv();
 *   
 *   // Create a project
 *   auto project = client->createProject("my-project", "My VFX assets");
 *   
 *   // Create spaces and items
 *   auto space = client->createSpace("/" + project->getName(), "assets");
 *   auto item = space->createItem("hero", "model");
 * @endcode
 */
class Client {
public:
    /**
     * @brief Construct a Client with a gRPC channel.
     * @param channel The gRPC channel to use.
     */
    explicit Client(std::shared_ptr<grpc::Channel> channel);

    /**
     * @brief Construct a Client with a pre-existing stub.
     * @param stub The gRPC stub to use.
     */
    explicit Client(std::shared_ptr<kumiho::KumihoService::StubInterface> stub);

    /**
     * @brief Create a Client from environment variables.
     *
     * Resolves the server endpoint using:
     * 1. KUMIHO_SERVER_ENDPOINT (preferred)
     * 2. KUMIHO_SERVER_ADDRESS (legacy)
     * 3. localhost:50051 (default)
     *
     * @return A shared pointer to the created Client.
     */
    static std::shared_ptr<Client> createFromEnv();

    // --- Project Operations ---

    /**
     * @brief Create a new project.
     * @param name The URL-safe project name.
     * @param description Optional description.
     * @return The created Project.
     * @throws ProjectLimitError if the project limit is reached.
     */
    std::shared_ptr<Project> createProject(const std::string& name, const std::string& description = "");

    /**
     * @brief Get all projects.
     * @return A list of Project objects.
     */
    std::vector<std::shared_ptr<Project>> getProjects();

    /**
     * @brief Get a project by name.
     * @param name The project name.
     * @return The Project, or nullptr if not found.
     */
    std::shared_ptr<Project> getProject(const std::string& name);

    /**
     * @brief Delete a project.
     * @param project_id The project UUID.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteProject(const std::string& project_id, bool force = false);

    /**
     * @brief Update a project.
     * @param project_id The project UUID.
     * @param allow_public Optional: set public access mode.
     * @param description Optional: new description.
     * @return The updated Project.
     */
    std::shared_ptr<Project> updateProject(
        const std::string& project_id,
        std::optional<bool> allow_public = std::nullopt,
        std::optional<std::string> description = std::nullopt
    );

    // --- Space Operations ---

    /**
     * @brief Create a new space.
     * @param parent_path The path of the parent (project or space).
     * @param name The space name.
     * @return The created Space.
     */
    std::shared_ptr<Space> createSpace(const std::string& parent_path, const std::string& name);

    /**
     * @brief Get a space by path.
     * @param path The full space path.
     * @return The Space.
     */
    std::shared_ptr<Space> getSpace(const std::string& path);

    /**
     * @brief Get child spaces of a parent.
     * @param parent_path The parent path (empty for root).
     * @return A list of Space objects.
     */
    std::vector<std::shared_ptr<Space>> getChildSpaces(const std::string& parent_path = "");

    /**
     * @brief Update space metadata.
     * @param kref The space's Kref.
     * @param metadata The metadata to set.
     * @return The updated Space.
     */
    std::shared_ptr<Space> updateSpaceMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete a space.
     * @param path The space path.
     * @param force If true, permanently delete.
     */
    void deleteSpace(const std::string& path, bool force = false);

    // --- Item Operations ---

    /**
     * @brief Create a new item.
     * @param parent_path The parent space path.
     * @param name The item name.
     * @param kind The item kind (type).
     * @return The created Item.
     * @throws ReservedKindError if kind is reserved.
     */
    std::shared_ptr<Item> createItem(const std::string& parent_path, const std::string& name, const std::string& kind);

    /**
     * @brief Get an item by parent path, name, and kind.
     * @param parent_path The parent space path.
     * @param name The item name.
     * @param kind The item kind.
     * @return The Item.
     */
    std::shared_ptr<Item> getItem(const std::string& parent_path, const std::string& name, const std::string& kind);

    /**
     * @brief Get an item by Kref.
     * @param kref_uri The item's Kref URI.
     * @return The Item.
     */
    std::shared_ptr<Item> getItemByKref(const std::string& kref_uri);

    /**
     * @brief Search for items.
     * @param context_filter Filter by context (project/space path).
     * @param name_filter Filter by item name.
     * @param kind_filter Filter by item kind.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @return A PagedList of matching Item objects.
     */
    PagedList<std::shared_ptr<Item>> itemSearch(
        const std::string& context_filter = "",
        const std::string& name_filter = "",
        const std::string& kind_filter = "",
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt
    );

    /**
     * @brief Update item metadata.
     * @param kref The item's Kref.
     * @param metadata The metadata to set.
     * @return The updated Item.
     */
    std::shared_ptr<Item> updateItemMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete an item.
     * @param kref The item's Kref.
     * @param force If true, permanently delete.
     */
    void deleteItem(const Kref& kref, bool force = false);

    /**
     * @brief Set item deprecated status.
     * @param kref The item's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setItemDeprecated(const Kref& kref, bool deprecated);

    // --- Revision Operations ---

    /**
     * @brief Create a new revision.
     * @param item_kref The parent item's Kref.
     * @param metadata Optional metadata.
     * @param number Optional specific revision number (0 for auto).
     * @return The created Revision.
     */
    std::shared_ptr<Revision> createRevision(const Kref& item_kref, const Metadata& metadata = {}, int number = 0);

    /**
     * @brief Get a revision by Kref.
     * @param kref_uri The revision's Kref URI.
     * @return The Revision.
     */
    std::shared_ptr<Revision> getRevision(const std::string& kref_uri);

    /**
     * @brief Resolve a Kref to a revision.
     * @param kref_uri The Kref URI.
     * @param tag Optional tag to resolve (e.g., "published", "approved").
     * @param time Optional time in YYYYMMDDHHMM format (e.g., "202406011330")
     *             or ISO 8601 format (e.g., "2024-06-01T13:30:00Z").
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> resolveKref(const std::string& kref_uri, const std::string& tag = "", const std::string& time = "");

    /**
     * @brief Resolve a Kref to a location.
     * @param kref_uri The Kref URI.
     * @return The resolved location, or nullopt.
     */
    std::optional<std::string> resolve(const std::string& kref_uri);

    /**
     * @brief Get all revisions of an item.
     * @param item_kref The item's Kref.
     * @return A list of Revision objects.
     */
    std::vector<std::shared_ptr<Revision>> getRevisions(const Kref& item_kref);

    /**
     * @brief Peek at the next revision number.
     * @param item_kref The item's Kref.
     * @return The next revision number.
     */
    int peekNextRevision(const Kref& item_kref);

    /**
     * @brief Update revision metadata.
     * @param kref The revision's Kref.
     * @param metadata The metadata to set.
     * @return The updated Revision.
     */
    std::shared_ptr<Revision> updateRevisionMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Add a tag to a revision.
     * @param kref The revision's Kref.
     * @param tag The tag to add.
     */
    void tagRevision(const Kref& kref, const std::string& tag);

    /**
     * @brief Remove a tag from a revision.
     * @param kref The revision's Kref.
     * @param tag The tag to remove.
     */
    void untagRevision(const Kref& kref, const std::string& tag);

    /**
     * @brief Check if a revision has a tag.
     * @param kref The revision's Kref.
     * @param tag The tag to check.
     * @return True if the revision has the tag.
     */
    bool hasTag(const Kref& kref, const std::string& tag);

    /**
     * @brief Check if a revision ever had a tag.
     * @param kref The revision's Kref.
     * @param tag The tag to check.
     * @return True if the revision ever had the tag.
     */
    bool wasTagged(const Kref& kref, const std::string& tag);

    /**
     * @brief Set revision deprecated status.
     * @param kref The revision's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setRevisionDeprecated(const Kref& kref, bool deprecated);

    /**
     * @brief Delete a revision.
     * @param kref The revision's Kref.
     * @param force If true, permanently delete.
     */
    void deleteRevision(const Kref& kref, bool force = false);

    // --- Artifact Operations ---

    /**
     * @brief Create a new artifact.
     * @param revision_kref The parent revision's Kref.
     * @param name The artifact name.
     * @param location The file path or URI.
     * @return The created Artifact.
     */
    std::shared_ptr<Artifact> createArtifact(const Kref& revision_kref, const std::string& name, const std::string& location);

    /**
     * @brief Get an artifact by revision and name.
     * @param revision_kref The revision's Kref.
     * @param name The artifact name.
     * @return The Artifact.
     */
    std::shared_ptr<Artifact> getArtifact(const Kref& revision_kref, const std::string& name);

    /**
     * @brief Get all artifacts for a revision.
     * @param revision_kref The revision's Kref.
     * @return A list of Artifact objects.
     */
    std::vector<std::shared_ptr<Artifact>> getArtifacts(const Kref& revision_kref);

    /**
     * @brief Get artifacts by location.
     * @param location The file location to search.
     * @return A list of matching Artifact objects.
     */
    std::vector<std::shared_ptr<Artifact>> getArtifactsByLocation(const std::string& location);

    /**
     * @brief Set the default artifact for a revision.
     * @param revision_kref The revision's Kref.
     * @param artifact_name The artifact name to set as default.
     */
    void setDefaultArtifact(const Kref& revision_kref, const std::string& artifact_name);

    /**
     * @brief Update artifact metadata.
     * @param kref The artifact's Kref.
     * @param metadata The metadata to set.
     * @return The updated Artifact.
     */
    std::shared_ptr<Artifact> updateArtifactMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete an artifact.
     * @param kref The artifact's Kref.
     * @param force If true, permanently delete.
     */
    void deleteArtifact(const Kref& kref, bool force = false);

    /**
     * @brief Set artifact deprecated status.
     * @param kref The artifact's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setArtifactDeprecated(const Kref& kref, bool deprecated);

    // --- Edge Operations ---

    /**
     * @brief Create an edge between revisions.
     * @param source_kref The source revision's Kref.
     * @param target_kref The target revision's Kref.
     * @param edge_type The edge type (e.g., "DEPENDS_ON").
     * @param metadata Optional edge metadata.
     * @return The created Edge.
     */
    std::shared_ptr<Edge> createEdge(
        const Kref& source_kref,
        const Kref& target_kref,
        const std::string& edge_type,
        const Metadata& metadata = {}
    );

    /**
     * @brief Get edges for a revision.
     * @param kref The revision's Kref.
     * @param edge_type_filter Filter by edge type (empty = all).
     * @return A list of Edge objects.
     */
    std::vector<std::shared_ptr<Edge>> getEdges(const Kref& kref, const std::string& edge_type_filter = "");

    /**
     * @brief Delete an edge.
     * @param source_kref The source revision's Kref.
     * @param target_kref The target revision's Kref.
     * @param edge_type The edge type.
     */
    void deleteEdge(const Kref& source_kref, const Kref& target_kref, const std::string& edge_type);

    // --- Graph Traversal Operations ---

    /**
     * @brief Traverse edges from a starting revision.
     *
     * Performs a breadth-first traversal of the revision graph following
     * edges in the specified direction.
     *
     * @param origin_kref The starting revision's Kref.
     * @param direction The direction to traverse (OUTGOING or INCOMING).
     * @param edge_type_filter Filter by edge types (empty = all types).
     * @param max_depth Maximum traversal depth (default: 10, max: 20).
     * @param limit Maximum number of results (default: 100, max: 1000).
     * @param include_path Whether to include full path info.
     * @return TraversalResult containing discovered revisions.
     */
    TraversalResult traverseEdges(
        const Kref& origin_kref,
        int direction,
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        int limit = 100,
        bool include_path = false
    );

    /**
     * @brief Find the shortest path between two revisions.
     *
     * Uses graph traversal to find how two revisions are connected.
     *
     * @param source_kref The source revision's Kref.
     * @param target_kref The target revision's Kref.
     * @param edge_type_filter Filter by edge types (empty = all).
     * @param max_depth Maximum path length to search (default: 10).
     * @param all_shortest If true, return all shortest paths.
     * @return ShortestPathResult containing the path(s).
     */
    ShortestPathResult findShortestPath(
        const Kref& source_kref,
        const Kref& target_kref,
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        bool all_shortest = false
    );

    /**
     * @brief Analyze the impact of changes to a revision.
     *
     * Returns all revisions that directly or indirectly depend on
     * the specified revision, sorted by impact depth.
     *
     * @param revision_kref The revision to analyze.
     * @param edge_type_filter Edge types to follow (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum results (default: 100).
     * @return ImpactAnalysisResult with impacted revisions.
     */
    ImpactAnalysisResult analyzeImpact(
        const Kref& revision_kref,
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

    // --- Attribute Operations ---

    /**
     * @brief Get a single metadata attribute.
     *
     * Retrieves a specific attribute value from any entity (product,
     * version, resource, group).
     *
     * @param kref The entity's Kref.
     * @param key The attribute key to retrieve.
     * @return The attribute value, or nullopt if not found.
     */
    std::optional<std::string> getAttribute(const Kref& kref, const std::string& key);

    /**
     * @brief Set a single metadata attribute.
     *
     * Creates or updates a specific attribute on any entity. This is
     * more efficient than setMetadata when updating a single value.
     *
     * @param kref The entity's Kref.
     * @param key The attribute key to set.
     * @param value The attribute value.
     * @return True if the attribute was set successfully.
     */
    bool setAttribute(const Kref& kref, const std::string& key, const std::string& value);

    /**
     * @brief Delete a single metadata attribute.
     *
     * Removes a specific attribute from any entity.
     *
     * @param kref The entity's Kref.
     * @param key The attribute key to delete.
     * @return True if the attribute was deleted successfully.
     */
    bool deleteAttribute(const Kref& kref, const std::string& key);

    // --- Bundle Operations ---

    /**
     * @brief Create a bundle.
     * @param parent_path The parent space path.
     * @param name The bundle name.
     * @return The created Bundle.
     */
    std::shared_ptr<Bundle> createBundle(const std::string& parent_path, const std::string& name);

    /**
     * @brief Create a bundle using a parent Kref.
     * @param parent_kref The parent's Kref.
     * @param name The bundle name.
     * @return The created Bundle.
     */
    std::shared_ptr<Bundle> createBundle(const Kref& parent_kref, const std::string& name);

    /**
     * @brief Get a bundle by parent path and name.
     * @param parent_path The parent space path.
     * @param name The bundle name.
     * @return The Bundle.
     */
    std::shared_ptr<Bundle> getBundle(const std::string& parent_path, const std::string& name);

    /**
     * @brief Add a member to a bundle.
     * @param bundle_kref The bundle's Kref.
     * @param item_kref The item to add.
     */
    void addBundleMember(const Kref& bundle_kref, const Kref& item_kref);

    /**
     * @brief Remove a member from a bundle.
     * @param bundle_kref The bundle's Kref.
     * @param item_kref The item to remove.
     */
    void removeBundleMember(const Kref& bundle_kref, const Kref& item_kref);

    /**
     * @brief Get bundle members.
     * @param bundle_kref The bundle's Kref.
     * @return A list of BundleMember objects.
     */
    std::vector<BundleMember> getBundleMembers(const Kref& bundle_kref);

    /**
     * @brief Get bundle history.
     * @param bundle_kref The bundle's Kref.
     * @return A list of BundleRevisionHistory objects.
     */
    std::vector<BundleRevisionHistory> getBundleHistory(const Kref& bundle_kref);

    // --- Tenant Operations ---

    /**
     * @brief Get the current tenant's usage and limits.
     *
     * Returns information about the tenant's resource consumption
     * and quota limits.
     *
     * @return A TenantUsage struct with node_count, node_limit, and tenant_id.
     */
    TenantUsage getTenantUsage();

    // --- Event Streaming ---

    /**
     * @brief Subscribe to event stream.
     * @param routing_key_filter Filter by routing key pattern.
     * @param kref_filter Filter by Kref pattern.
     * @return An EventStream for receiving events.
     */
    std::shared_ptr<EventStream> eventStream(const std::string& routing_key_filter = "", const std::string& kref_filter = "");

    // --- Authentication ---

    /**
     * @brief Set the authentication token for gRPC calls.
     * @param token The bearer token to use for authorization.
     */
    void setAuthToken(const std::string& token);

    /**
     * @brief Get the current authentication token.
     * @return The current token, or empty string if not set.
     */
    const std::string& getAuthToken() const { return auth_token_; }

    // --- Utility ---

    /**
     * @brief Get the raw gRPC stub.
     * @return Pointer to the stub interface.
     */
    kumiho::KumihoService::StubInterface* getStub() { return stub_.get(); }

private:
    std::shared_ptr<kumiho::KumihoService::StubInterface> stub_;
    std::shared_ptr<grpc::ClientContext> context_; // For event stream
    std::string auth_token_;  // Bearer token for authentication

    /**
     * @brief Configure a ClientContext with authentication metadata.
     * @param context The context to configure.
     */
    void configureContext(grpc::ClientContext& context) const;
};

// --- Convenience Functions ---

/**
 * @brief Create nested spaces from a path.
 *
 * Creates intermediate spaces if they don't exist.
 *
 * @param client The client to use.
 * @param path The full path of spaces to create (e.g., "project/seq/shot").
 * @return The final Space in the path.
 */
std::shared_ptr<Space> createSpace(std::shared_ptr<Client> client, const std::string& path);

// Backwards compatibility alias
inline std::shared_ptr<Space> createGroup(std::shared_ptr<Client> client, const std::string& path) {
    return createSpace(client, path);
}

/**
 * @brief Get the current username from environment.
 * @return The username, or "unknown" if not found.
 */
std::string getCurrentUser();

} // namespace api
} // namespace kumiho
