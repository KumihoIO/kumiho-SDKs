/**
 * @file revision.hpp
 * @brief Revision entity representing iterations of an item.
 *
 * Revisions are immutable snapshots of an item at a point in time. Each
 * revision can have multiple artifacts (file references), tags for
 * categorization, and edges to other revisions for dependency tracking.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/edge.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Artifact;
class Item;
class Space;
class Project;

/**
 * @brief A specific iteration of an item in the Kumiho system.
 *
 * Revisions are snapshots of an item at a point in time. Each
 * revision can have multiple artifacts (file references), tags for
 * categorization, and edges to other revisions for dependency tracking.
 *
 * The revision's kref includes the revision number:
 * `kref://project/space/item.kind?r=1`
 *
 * Example:
 * @code
 *   auto v1 = item->createRevision({{"artist", "jane"}});
 *   
 *   // Add artifacts
 *   auto mesh = v1->createArtifact("mesh", "/assets/hero.fbx");
 *   auto rig = v1->createArtifact("rig", "/assets/hero_rig.fbx");
 *   
 *   // Set default artifact
 *   v1->setDefaultArtifact("mesh");
 *   
 *   // Tag the revision
 *   v1->tag("approved");
 *   
 *   // Check tags
 *   if (v1->hasTag("approved")) {
 *       std::cout << "Revision is approved!" << std::endl;
 *   }
 * @endcode
 */
class Revision {
public:
    /**
     * @brief Construct a Revision from a protobuf response.
     * @param response The protobuf RevisionResponse message.
     * @param client The client for making API calls.
     */
    Revision(const ::kumiho::RevisionResponse& response, Client* client);

    /**
     * @brief Get the revision's unique Kref.
     * @return The Kref URI for this revision.
     */
    Kref getKref() const;

    /**
     * @brief Get the parent item's Kref.
     * @return The Kref of the item containing this revision.
     */
    Kref getItemKref() const;

    /**
     * @brief Get the revision number.
     * @return The revision number (1-based).
     */
    int getRevisionNumber() const;

    /**
     * @brief Get the tags applied to this revision.
     * @return A list of tag strings.
     */
    std::vector<std::string> getTags() const;

    /**
     * @brief Get the revision's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the revision was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the revision.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the revision creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if this is the latest revision.
     * @return True if this is the latest revision of the item.
     */
    bool isLatest() const;

    /**
     * @brief Check if the revision is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Check if the revision is published.
     *
     * Published revisions are immutable—their metadata cannot be changed.
     *
     * @return True if published, false otherwise.
     */
    bool isPublished() const;

    /**
     * @brief Get the default artifact name.
     * @return The name of the default artifact, or nullopt if not set.
     */
    std::optional<std::string> getDefaultArtifact() const;

    /**
     * @brief Set the default artifact for this revision.
     * @param artifact_name The name of the artifact to set as default.
     */
    void setDefaultArtifact(const std::string& artifact_name);

    /**
     * @brief Create a new artifact for this revision.
     *
     * Artifacts are file references that point to actual assets on disk
     * or network storage. Kumiho tracks the path and metadata but does
     * not upload or copy the files.
     *
     * @param name The name of the artifact (e.g., "mesh", "textures").
     * @param location The file path or URI where the artifact is stored.
     * @return The created Artifact.
     */
    std::shared_ptr<Artifact> createArtifact(const std::string& name, const std::string& location);

    /**
     * @brief Get an artifact by name.
     * @param name The artifact name.
     * @return The Artifact.
     */
    std::shared_ptr<Artifact> getArtifact(const std::string& name);

    /**
     * @brief Get all artifacts for this revision.
     * @return A list of Artifact objects.
     */
    std::vector<std::shared_ptr<Artifact>> getArtifacts();

    /**
     * @brief Get all artifact locations.
     * @return A list of location strings.
     */
    std::vector<std::string> getLocations();

    /**
     * @brief Set or update metadata for this revision.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Revision.
     */
    std::shared_ptr<Revision> setMetadata(const Metadata& metadata);

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
     * @brief Add a tag to this revision.
     *
     * Tags are used to categorize revisions and mark their status.
     * Common tags include "latest", "published", "approved", etc.
     * 
     * The server records the timestamp when a tag is applied, enabling
     * time-based queries like "what was published on June 1st?"
     * Use Item::getRevisionByTagAndTime() for historical tag lookups.
     *
     * @param tag The tag to add.
     * 
     * Example:
     * @code
     *   revision->tag("approved");
     *   revision->tag("published");
     * @endcode
     */
    void tag(const std::string& tag);

    /**
     * @brief Remove a tag from this revision.
     * 
     * The server records when the tag was removed, preserving the history.
     * Use wasTagged() to check if a tag was ever applied, even after removal.
     *
     * @param tag The tag to remove.
     */
    void untag(const std::string& tag);

    /**
     * @brief Check if this revision currently has a tag.
     * @param tag The tag to check.
     * @return True if the revision currently has the tag.
     */
    bool hasTag(const std::string& tag);

    /**
     * @brief Check if this revision ever had a tag (including removed tags).
     * 
     * This checks the historical record. A tag that was applied and later
     * removed will still return true. Use this for auditing.
     *
     * @param tag The tag to check.
     * @return True if the revision ever had the tag.
     */
    bool wasTagged(const std::string& tag);

    /**
     * @brief Delete this revision.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteRevision(bool force = false);

    /**
     * @brief Get the parent item.
     * @return The Item containing this revision.
     */
    std::shared_ptr<Item> getItem();

    /**
     * @brief Get the parent space.
     * @return The Space containing this revision's item.
     */
    std::shared_ptr<Space> getSpace();

    /**
     * @brief Get the parent project.
     * @return The Project containing this revision.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Create an edge from this revision to another.
     * @param target The target revision's Kref.
     * @param edge_type The type of relationship (e.g., EdgeType::DEPENDS_ON).
     * @param metadata Optional metadata for the edge.
     * @return The created Edge.
     */
    std::shared_ptr<Edge> createEdge(
        const Kref& target,
        const std::string& edge_type,
        const Metadata& metadata = {}
    );

    /**
     * @brief Get edges from or to this revision.
     * @param edge_type_filter Filter by edge type (empty = all types).
     * @param direction The direction to query (default: OUTGOING).
     * @return A list of Edge objects.
     */
    std::vector<std::shared_ptr<Edge>> getEdges(
        const std::string& edge_type_filter = "",
        EdgeDirection direction = EdgeDirection::OUTGOING
    );

    /**
     * @brief Refresh this revision's data from the server.
     * @return The refreshed Revision.
     */
    std::shared_ptr<Revision> refresh();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     */
    void setDeprecated(bool deprecated);

    /**
     * @brief Publish this revision (adds published tag, makes immutable).
     * @return The updated Revision.
     */
    std::shared_ptr<Revision> publish();

    // --- Graph Traversal Methods ---

    /**
     * @brief Get all transitive dependencies of this revision.
     *
     * Traverses outgoing edges to find all revisions this revision
     * depends on, directly or indirectly.
     *
     * @param edge_type_filter Filter by edge types (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum number of results (default: 100).
     * @return TraversalResult containing discovered revisions.
     *
     * Example:
     * @code
     *   auto deps = revision->getAllDependencies({"DEPENDS_ON"}, 5);
     *   for (const auto& kref : deps.revision_krefs) {
     *       std::cout << "Depends on: " << kref << std::endl;
     *   }
     * @endcode
     */
    TraversalResult getAllDependencies(
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

    /**
     * @brief Get all revisions that transitively depend on this revision.
     *
     * Traverses incoming edges to find all revisions that depend on
     * this revision, directly or indirectly. Useful for impact analysis.
     *
     * @param edge_type_filter Filter by edge types.
     * @param max_depth Maximum traversal depth.
     * @param limit Maximum number of results.
     * @return TraversalResult containing dependent revisions.
     */
    TraversalResult getAllDependents(
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

    /**
     * @brief Find the shortest path from this revision to another.
     *
     * Uses graph traversal to find how two revisions are connected.
     *
     * @param target The target revision's Kref.
     * @param edge_type_filter Filter by edge types.
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
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        bool all_paths = false
    );

    /**
     * @brief Analyze the impact of changes to this revision.
     *
     * Returns all revisions that directly or indirectly depend on this
     * revision, sorted by impact depth (closest dependencies first).
     *
     * @param edge_type_filter Edge types to follow (empty = all).
     * @param max_depth Maximum traversal depth (default: 10).
     * @param limit Maximum results (default: 100).
     * @return ImpactAnalysisResult with impacted revisions.
     *
     * Example:
     * @code
     *   auto impact = texture->analyzeImpact({"DEPENDS_ON"});
     *   std::cout << impact.total_impacted << " revisions affected" << std::endl;
     * @endcode
     */
    ImpactAnalysisResult analyzeImpact(
        const std::vector<std::string>& edge_type_filter = {},
        int max_depth = 10,
        int limit = 100
    );

private:
    ::kumiho::RevisionResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
