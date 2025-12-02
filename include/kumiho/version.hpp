/**
 * @file version.hpp
 * @brief Version entity representing iterations of a product.
 *
 * Versions are immutable snapshots of a product at a point in time. Each
 * version can have multiple resources (file references), tags for
 * categorization, and links to other versions for dependency tracking.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/link.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Resource;
class Product;
class Group;
class Project;

/**
 * @brief A specific iteration of a product in the Kumiho system.
 *
 * Versions are snapshots of a product at a point in time. Each
 * version can have multiple resources (file references), tags for
 * categorization, and links to other versions for dependency tracking.
 *
 * The version's kref includes the version number:
 * `kref://project/group/product.type?v=1`
 *
 * Example:
 * @code
 *   auto v1 = product->createVersion({{"artist", "jane"}});
 *   
 *   // Add resources
 *   auto mesh = v1->createResource("mesh", "/assets/hero.fbx");
 *   auto rig = v1->createResource("rig", "/assets/hero_rig.fbx");
 *   
 *   // Set default resource
 *   v1->setDefaultResource("mesh");
 *   
 *   // Tag the version
 *   v1->tag("approved");
 *   
 *   // Check tags
 *   if (v1->hasTag("approved")) {
 *       std::cout << "Version is approved!" << std::endl;
 *   }
 * @endcode
 */
class Version {
public:
    /**
     * @brief Construct a Version from a protobuf response.
     * @param response The protobuf VersionResponse message.
     * @param client The client for making API calls.
     */
    Version(const ::kumiho::VersionResponse& response, Client* client);

    /**
     * @brief Get the version's unique Kref.
     * @return The Kref URI for this version.
     */
    Kref getKref() const;

    /**
     * @brief Get the parent product's Kref.
     * @return The Kref of the product containing this version.
     */
    Kref getProductKref() const;

    /**
     * @brief Get the version number.
     * @return The version number (1-based).
     */
    int getVersionNumber() const;

    /**
     * @brief Get the tags applied to this version.
     * @return A list of tag strings.
     */
    std::vector<std::string> getTags() const;

    /**
     * @brief Get the version's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the version was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the version.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the version creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if this is the latest version.
     * @return True if this is the latest version of the product.
     */
    bool isLatest() const;

    /**
     * @brief Check if the version is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Check if the version is published.
     *
     * Published versions are immutable—their metadata cannot be changed.
     *
     * @return True if published, false otherwise.
     */
    bool isPublished() const;

    /**
     * @brief Get the default resource name.
     * @return The name of the default resource, or nullopt if not set.
     */
    std::optional<std::string> getDefaultResource() const;

    /**
     * @brief Set the default resource for this version.
     * @param resource_name The name of the resource to set as default.
     */
    void setDefaultResource(const std::string& resource_name);

    /**
     * @brief Create a new resource for this version.
     *
     * Resources are file references that point to actual assets on disk
     * or network storage. Kumiho tracks the path and metadata but does
     * not upload or copy the files.
     *
     * @param name The name of the resource (e.g., "mesh", "textures").
     * @param location The file path or URI where the resource is stored.
     * @return The created Resource.
     */
    std::shared_ptr<Resource> createResource(const std::string& name, const std::string& location);

    /**
     * @brief Get a resource by name.
     * @param name The resource name.
     * @return The Resource.
     */
    std::shared_ptr<Resource> getResource(const std::string& name);

    /**
     * @brief Get all resources for this version.
     * @return A list of Resource objects.
     */
    std::vector<std::shared_ptr<Resource>> getResources();

    /**
     * @brief Get all resource locations.
     * @return A list of location strings.
     */
    std::vector<std::string> getLocations();

    /**
     * @brief Set or update metadata for this version.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Version.
     */
    std::shared_ptr<Version> setMetadata(const Metadata& metadata);

    /**
     * @brief Get a single metadata attribute.
     * @param key The attribute key to retrieve.
     * @return The attribute value, or nullopt if not found.
     */
    std::optional<std::string> getAttribute(const std::string& key);

    /**
     * @brief Set a single metadata attribute.
     * @param key The attribute key to set.
     * @param value The attribute value.
     * @return True if the attribute was set successfully.
     */
    bool setAttribute(const std::string& key, const std::string& value);

    /**
     * @brief Delete a single metadata attribute.
     * @param key The attribute key to delete.
     * @return True if the attribute was deleted successfully.
     */
    bool deleteAttribute(const std::string& key);

    /**
     * @brief Add a tag to this version.
     * @param tag The tag to add.
     */
    void tag(const std::string& tag);

    /**
     * @brief Remove a tag from this version.
     * @param tag The tag to remove.
     */
    void untag(const std::string& tag);

    /**
     * @brief Check if this version currently has a tag.
     * @param tag The tag to check.
     * @return True if the version has the tag.
     */
    bool hasTag(const std::string& tag);

    /**
     * @brief Check if this version ever had a tag (including removed).
     * @param tag The tag to check.
     * @return True if the version ever had the tag.
     */
    bool wasTagged(const std::string& tag);

    /**
     * @brief Delete this version.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteVersion(bool force = false);

    /**
     * @brief Get the parent product.
     * @return The Product containing this version.
     */
    std::shared_ptr<Product> getProduct();

    /**
     * @brief Get the parent group.
     * @return The Group containing this version's product.
     */
    std::shared_ptr<Group> getGroup();

    /**
     * @brief Get the parent project.
     * @return The Project containing this version.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Create a link from this version to another.
     * @param target The target version's Kref.
     * @param link_type The type of relationship (e.g., LinkType::DEPENDS_ON).
     * @param metadata Optional metadata for the link.
     * @return The created Link.
     */
    std::shared_ptr<Link> createLink(
        const Kref& target,
        const std::string& link_type,
        const Metadata& metadata = {}
    );

    /**
     * @brief Get links from or to this version.
     * @param link_type_filter Filter by link type (empty = all types).
     * @param direction The direction to query (default: OUTGOING).
     * @return A list of Link objects.
     */
    std::vector<std::shared_ptr<Link>> getLinks(
        const std::string& link_type_filter = "",
        LinkDirection direction = LinkDirection::OUTGOING
    );

    /**
     * @brief Refresh this version's data from the server.
     * @return The refreshed Version.
     */
    std::shared_ptr<Version> refresh();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     */
    void setDeprecated(bool deprecated);

    /**
     * @brief Publish this version (adds published tag, makes immutable).
     * @return The updated Version.
     */
    std::shared_ptr<Version> publish();

    // --- Graph Traversal Methods ---

    /**
     * @brief Get all transitive dependencies of this version.
     *
     * Traverses outgoing links to find all versions this version
     * depends on, directly or indirectly.
     *
     * @param link_type_filter Filter by link types (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum number of results (default: 100).
     * @return TraversalResult containing discovered versions.
     *
     * Example:
     * @code
     *   auto deps = version->getAllDependencies({"DEPENDS_ON"}, 5);
     *   for (const auto& kref : deps.version_krefs) {
     *       std::cout << "Depends on: " << kref << std::endl;
     *   }
     * @endcode
     */
    TraversalResult getAllDependencies(
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

    /**
     * @brief Get all versions that transitively depend on this version.
     *
     * Traverses incoming links to find all versions that depend on
     * this version, directly or indirectly. Useful for impact analysis.
     *
     * @param link_type_filter Filter by link types.
     * @param max_depth Maximum traversal depth.
     * @param limit Maximum number of results.
     * @return TraversalResult containing dependent versions.
     */
    TraversalResult getAllDependents(
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

    /**
     * @brief Find the shortest path from this version to another.
     *
     * Uses graph traversal to find how two versions are connected.
     *
     * @param target The target version's Kref.
     * @param link_type_filter Filter by link types.
     * @param max_depth Maximum path length to search.
     * @param all_paths If true, returns all shortest paths.
     * @return ShortestPathResult containing the path(s).
     *
     * Example:
     * @code
     *   auto result = model->findPathTo(texture->getKref());
     *   if (result.path_exists) {
     *       std::cout << "Path length: " << result.path_length << std::endl;
     *   }
     * @endcode
     */
    ShortestPathResult findPathTo(
        const Kref& target,
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        bool all_paths = false
    );

    /**
     * @brief Analyze the impact of changes to this version.
     *
     * Returns all versions that directly or indirectly depend on this
     * version, sorted by impact depth (closest dependencies first).
     *
     * @param link_type_filter Link types to follow (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum results (default: 100).
     * @return ImpactAnalysisResult with impacted versions.
     *
     * Example:
     * @code
     *   auto impact = texture->analyzeImpact({"DEPENDS_ON"});
     *   std::cout << impact.total_impacted << " versions affected" << std::endl;
     * @endcode
     */
    ImpactAnalysisResult analyzeImpact(
        const std::vector<std::string>& link_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

private:
    ::kumiho::VersionResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
