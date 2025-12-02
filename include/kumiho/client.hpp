/**
 * @file client.hpp
 * @brief Low-level gRPC client for the Kumiho Cloud service.
 *
 * This module provides the Client class that handles all gRPC communication
 * with Kumiho Cloud servers. It manages connection establishment, authentication,
 * and all gRPC method calls.
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
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Project;
class Group;
class Product;
class Version;
class Resource;
class Link;
class Collection;
class Event;
class EventStream;
struct CollectionMember;
struct CollectionVersionHistory;

/**
 * @brief The main client for interacting with Kumiho Cloud services.
 *
 * The Client class provides methods for all Kumiho operations including
 * creating and managing projects, groups, products, versions, resources,
 * and links.
 *
 * Example:
 * @code
 *   // Create from environment variables
 *   auto client = Client::createFromEnv();
 *   
 *   // Create a project
 *   auto project = client->createProject("my-project", "My VFX assets");
 *   
 *   // Create groups and products
 *   auto group = client->createGroup("/" + project->getName(), "assets");
 *   auto product = group->createProduct("hero", "model");
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

    // --- Group Operations ---

    /**
     * @brief Create a new group.
     * @param parent_path The path of the parent (project or group).
     * @param name The group name.
     * @return The created Group.
     */
    std::shared_ptr<Group> createGroup(const std::string& parent_path, const std::string& name);

    /**
     * @brief Get a group by path.
     * @param path The full group path.
     * @return The Group.
     */
    std::shared_ptr<Group> getGroup(const std::string& path);

    /**
     * @brief Get child groups of a parent.
     * @param parent_path The parent path (empty for root).
     * @return A list of Group objects.
     */
    std::vector<std::shared_ptr<Group>> getChildGroups(const std::string& parent_path = "");

    /**
     * @brief Update group metadata.
     * @param kref The group's Kref.
     * @param metadata The metadata to set.
     * @return The updated Group.
     */
    std::shared_ptr<Group> updateGroupMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete a group.
     * @param path The group path.
     * @param force If true, permanently delete.
     */
    void deleteGroup(const std::string& path, bool force = false);

    // --- Product Operations ---

    /**
     * @brief Create a new product.
     * @param parent_path The parent group path.
     * @param name The product name.
     * @param ptype The product type.
     * @return The created Product.
     * @throws ReservedProductTypeError if ptype is reserved.
     */
    std::shared_ptr<Product> createProduct(const std::string& parent_path, const std::string& name, const std::string& ptype);

    /**
     * @brief Get a product by parent path, name, and type.
     * @param parent_path The parent group path.
     * @param name The product name.
     * @param ptype The product type.
     * @return The Product.
     */
    std::shared_ptr<Product> getProduct(const std::string& parent_path, const std::string& name, const std::string& ptype);

    /**
     * @brief Get a product by Kref.
     * @param kref_uri The product's Kref URI.
     * @return The Product.
     */
    std::shared_ptr<Product> getProductByKref(const std::string& kref_uri);

    /**
     * @brief Search for products.
     * @param context_filter Filter by context (project/group path).
     * @param name_filter Filter by product name.
     * @param ptype_filter Filter by product type.
     * @return A list of matching Product objects.
     */
    std::vector<std::shared_ptr<Product>> productSearch(
        const std::string& context_filter = "",
        const std::string& name_filter = "",
        const std::string& ptype_filter = ""
    );

    /**
     * @brief Update product metadata.
     * @param kref The product's Kref.
     * @param metadata The metadata to set.
     * @return The updated Product.
     */
    std::shared_ptr<Product> updateProductMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete a product.
     * @param kref The product's Kref.
     * @param force If true, permanently delete.
     */
    void deleteProduct(const Kref& kref, bool force = false);

    /**
     * @brief Set product deprecated status.
     * @param kref The product's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setProductDeprecated(const Kref& kref, bool deprecated);

    // --- Version Operations ---

    /**
     * @brief Create a new version.
     * @param product_kref The parent product's Kref.
     * @param metadata Optional metadata.
     * @param number Optional specific version number (0 for auto).
     * @return The created Version.
     */
    std::shared_ptr<Version> createVersion(const Kref& product_kref, const Metadata& metadata = {}, int number = 0);

    /**
     * @brief Get a version by Kref.
     * @param kref_uri The version's Kref URI.
     * @return The Version.
     */
    std::shared_ptr<Version> getVersion(const std::string& kref_uri);

    /**
     * @brief Resolve a Kref to a version.
     * @param kref_uri The Kref URI.
     * @param tag Optional tag to resolve.
     * @param time Optional time in YYYYMMDDHHMM format.
     * @return The Version, or nullptr if not found.
     */
    std::shared_ptr<Version> resolveKref(const std::string& kref_uri, const std::string& tag = "", const std::string& time = "");

    /**
     * @brief Resolve a Kref to a location.
     * @param kref_uri The Kref URI.
     * @return The resolved location, or nullopt.
     */
    std::optional<std::string> resolve(const std::string& kref_uri);

    /**
     * @brief Get all versions of a product.
     * @param product_kref The product's Kref.
     * @return A list of Version objects.
     */
    std::vector<std::shared_ptr<Version>> getVersions(const Kref& product_kref);

    /**
     * @brief Peek at the next version number.
     * @param product_kref The product's Kref.
     * @return The next version number.
     */
    int peekNextVersion(const Kref& product_kref);

    /**
     * @brief Update version metadata.
     * @param kref The version's Kref.
     * @param metadata The metadata to set.
     * @return The updated Version.
     */
    std::shared_ptr<Version> updateVersionMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Add a tag to a version.
     * @param kref The version's Kref.
     * @param tag The tag to add.
     */
    void tagVersion(const Kref& kref, const std::string& tag);

    /**
     * @brief Remove a tag from a version.
     * @param kref The version's Kref.
     * @param tag The tag to remove.
     */
    void untagVersion(const Kref& kref, const std::string& tag);

    /**
     * @brief Check if a version has a tag.
     * @param kref The version's Kref.
     * @param tag The tag to check.
     * @return True if the version has the tag.
     */
    bool hasTag(const Kref& kref, const std::string& tag);

    /**
     * @brief Check if a version ever had a tag.
     * @param kref The version's Kref.
     * @param tag The tag to check.
     * @return True if the version ever had the tag.
     */
    bool wasTagged(const Kref& kref, const std::string& tag);

    /**
     * @brief Set version deprecated status.
     * @param kref The version's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setVersionDeprecated(const Kref& kref, bool deprecated);

    /**
     * @brief Delete a version.
     * @param kref The version's Kref.
     * @param force If true, permanently delete.
     */
    void deleteVersion(const Kref& kref, bool force = false);

    // --- Resource Operations ---

    /**
     * @brief Create a new resource.
     * @param version_kref The parent version's Kref.
     * @param name The resource name.
     * @param location The file path or URI.
     * @return The created Resource.
     */
    std::shared_ptr<Resource> createResource(const Kref& version_kref, const std::string& name, const std::string& location);

    /**
     * @brief Get a resource by version and name.
     * @param version_kref The version's Kref.
     * @param name The resource name.
     * @return The Resource.
     */
    std::shared_ptr<Resource> getResource(const Kref& version_kref, const std::string& name);

    /**
     * @brief Get all resources for a version.
     * @param version_kref The version's Kref.
     * @return A list of Resource objects.
     */
    std::vector<std::shared_ptr<Resource>> getResources(const Kref& version_kref);

    /**
     * @brief Get resources by location.
     * @param location The file location to search.
     * @return A list of matching Resource objects.
     */
    std::vector<std::shared_ptr<Resource>> getResourcesByLocation(const std::string& location);

    /**
     * @brief Set the default resource for a version.
     * @param version_kref The version's Kref.
     * @param resource_name The resource name to set as default.
     */
    void setDefaultResource(const Kref& version_kref, const std::string& resource_name);

    /**
     * @brief Update resource metadata.
     * @param kref The resource's Kref.
     * @param metadata The metadata to set.
     * @return The updated Resource.
     */
    std::shared_ptr<Resource> updateResourceMetadata(const Kref& kref, const Metadata& metadata);

    /**
     * @brief Delete a resource.
     * @param kref The resource's Kref.
     * @param force If true, permanently delete.
     */
    void deleteResource(const Kref& kref, bool force = false);

    /**
     * @brief Set resource deprecated status.
     * @param kref The resource's Kref.
     * @param deprecated True to deprecate, false to restore.
     */
    void setResourceDeprecated(const Kref& kref, bool deprecated);

    // --- Link Operations ---

    /**
     * @brief Create a link between versions.
     * @param source_kref The source version's Kref.
     * @param target_kref The target version's Kref.
     * @param link_type The link type (e.g., "DEPENDS_ON").
     * @param metadata Optional link metadata.
     * @return The created Link.
     */
    std::shared_ptr<Link> createLink(
        const Kref& source_kref,
        const Kref& target_kref,
        const std::string& link_type,
        const Metadata& metadata = {}
    );

    /**
     * @brief Get links for a version.
     * @param kref The version's Kref.
     * @param link_type_filter Filter by link type (empty = all).
     * @return A list of Link objects.
     */
    std::vector<std::shared_ptr<Link>> getLinks(const Kref& kref, const std::string& link_type_filter = "");

    /**
     * @brief Delete a link.
     * @param source_kref The source version's Kref.
     * @param target_kref The target version's Kref.
     * @param link_type The link type.
     */
    void deleteLink(const Kref& source_kref, const Kref& target_kref, const std::string& link_type);

    // --- Graph Traversal Operations ---

    /**
     * @brief Traverse links from a starting version.
     *
     * Performs a breadth-first traversal of the version graph following
     * links in the specified direction.
     *
     * @param origin_kref The starting version's Kref.
     * @param direction The direction to traverse (OUTGOING or INCOMING).
     * @param link_type_filter Filter by link types (empty = all types).
     * @param max_depth Maximum traversal depth (default: 10, max: 20).
     * @param limit Maximum number of results (default: 100, max: 1000).
     * @param include_path Whether to include full path info.
     * @return TraversalResult containing discovered versions.
     */
    TraversalResult traverseLinks(
        const Kref& origin_kref,
        int direction,
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        int limit = 100,
        bool include_path = false
    );

    /**
     * @brief Find the shortest path between two versions.
     *
     * Uses graph traversal to find how two versions are connected.
     *
     * @param source_kref The source version's Kref.
     * @param target_kref The target version's Kref.
     * @param link_type_filter Filter by link types (empty = all).
     * @param max_depth Maximum path length to search (default: 10).
     * @param all_shortest If true, return all shortest paths.
     * @return ShortestPathResult containing the path(s).
     */
    ShortestPathResult findShortestPath(
        const Kref& source_kref,
        const Kref& target_kref,
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        bool all_shortest = false
    );

    /**
     * @brief Analyze the impact of changes to a version.
     *
     * Returns all versions that directly or indirectly depend on
     * the specified version, sorted by impact depth.
     *
     * @param version_kref The version to analyze.
     * @param link_type_filter Link types to follow (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum results (default: 100).
     * @return ImpactAnalysisResult with impacted versions.
     */
    ImpactAnalysisResult analyzeImpact(
        const Kref& version_kref,
        const std::vector<std::string>& link_type_filter = {},
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

    // --- Collection Operations ---

    /**
     * @brief Create a collection.
     * @param parent_path The parent group path.
     * @param name The collection name.
     * @return The created Collection.
     */
    std::shared_ptr<Collection> createCollection(const std::string& parent_path, const std::string& name);

    /**
     * @brief Create a collection using a parent Kref.
     * @param parent_kref The parent's Kref.
     * @param name The collection name.
     * @return The created Collection.
     */
    std::shared_ptr<Collection> createCollection(const Kref& parent_kref, const std::string& name);

    /**
     * @brief Get a collection by parent path and name.
     * @param parent_path The parent group path.
     * @param name The collection name.
     * @return The Collection.
     */
    std::shared_ptr<Collection> getCollection(const std::string& parent_path, const std::string& name);

    /**
     * @brief Add a member to a collection.
     * @param collection_kref The collection's Kref.
     * @param product_kref The product to add.
     */
    void addCollectionMember(const Kref& collection_kref, const Kref& product_kref);

    /**
     * @brief Remove a member from a collection.
     * @param collection_kref The collection's Kref.
     * @param product_kref The product to remove.
     */
    void removeCollectionMember(const Kref& collection_kref, const Kref& product_kref);

    /**
     * @brief Get collection members.
     * @param collection_kref The collection's Kref.
     * @return A list of CollectionMember objects.
     */
    std::vector<CollectionMember> getCollectionMembers(const Kref& collection_kref);

    /**
     * @brief Get collection history.
     * @param collection_kref The collection's Kref.
     * @return A list of CollectionVersionHistory objects.
     */
    std::vector<CollectionVersionHistory> getCollectionHistory(const Kref& collection_kref);

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
 * @brief Create nested groups from a path.
 *
 * Creates intermediate groups if they don't exist.
 *
 * @param client The client to use.
 * @param path The full path of groups to create (e.g., "project/seq/shot").
 * @return The final Group in the path.
 */
std::shared_ptr<Group> createGroup(std::shared_ptr<Client> client, const std::string& path);

/**
 * @brief Get the current username from environment.
 * @return The username, or "unknown" if not found.
 */
std::string getCurrentUser();

} // namespace api
} // namespace kumiho
