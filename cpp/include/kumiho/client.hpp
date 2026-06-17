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
#include <utility>
#include <grpcpp/grpcpp.h>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/edge.hpp"  // for EdgeDirection used in getEdges()
#include "kumiho/error.hpp"
#include "kumiho/bundle.hpp"  // For BundleMember, BundleRevisionHistory in inline functions
#include "kumiho/event.hpp"   // For EventCapabilities return type
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
 * @brief A single full-text search hit (item + relevance score).
 *
 * Mirrors the protobuf SearchResult. Search always returns Items, even when
 * the match was on revision/artifact metadata.
 */
struct SearchResult {
    /** @brief The matched item. */
    std::shared_ptr<Item> item;
    /** @brief Relevance score (higher = better match). */
    double score = 0.0;
    /** @brief Where the match was found: "item", "revision", "artifact". */
    std::vector<std::string> matched_in;
};

/**
 * @brief A revision scored against a query (server-side embeddings/fulltext).
 *
 * Mirrors the protobuf ScoredRevision returned by scoreRevisions().
 */
struct ScoredRevision {
    /** @brief The scored revision's kref. */
    Kref kref;
    /** @brief Relevance score (0.0 - 1.0). */
    double score = 0.0;
    /** @brief How the score was computed: "vector", "fulltext", or "hybrid". */
    std::string score_method;
};

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
     * @return The StatusResponse returned by the server.
     */
    StatusResponse deleteProject(const std::string& project_id, bool force = false);

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
     * @param recursive Whether to fetch all descendant spaces recursively.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @return A list of Space objects.
     */
    std::vector<std::shared_ptr<Space>> getChildSpaces(
        const std::string& parent_path = "",
        bool recursive = false,
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt
    );

    /**
     * @brief Get child spaces of a parent with pagination metadata surfaced.
     *
     * Sibling of getChildSpaces() that returns a PagedList carrying the
     * response's next_cursor and total_count. Mirrors the Python behavior
     * of returning a PagedList when pagination is supplied.
     *
     * @param parent_path The parent path (empty for root).
     * @param recursive Whether to fetch all descendant spaces recursively.
     * @param page_size Page size for pagination (0 = server default).
     * @param cursor Cursor for pagination (empty = first page).
     * @return A PagedList of Space objects.
     */
    PagedList<std::shared_ptr<Space>> getChildSpacesPaged(
        const std::string& parent_path = "",
        bool recursive = false,
        int32_t page_size = 0,
        const std::string& cursor = ""
    );

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
     * @return The StatusResponse returned by the server.
     */
    StatusResponse deleteSpace(const std::string& path, bool force = false);

    // --- Item Operations ---

    /**
     * @brief Create a new item.
     * @param parent_path The parent space path.
     * @param name The item name.
     * @param kind The item kind (type).
     * @param metadata Optional metadata to set on the created item.
     * @return The created Item.
     * @throws ReservedKindError if kind is reserved.
     */
    std::shared_ptr<Item> createItem(const std::string& parent_path, const std::string& name, const std::string& kind, const Metadata& metadata = {});

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
     * @brief Get the item that contains a specific revision.
     * @param revision_kref The revision's Kref URI.
     * @return The Item that contains the revision.
     */
    std::shared_ptr<Item> getItemFromRevision(const std::string& revision_kref);

    /**
     * @brief Get items within a space with optional filtering.
     *
     * Calls the GetItems RPC (mirrors Python Client.get_items). Unlike
     * itemSearch(), this lists items under a specific parent space.
     *
     * @param parent_path The path of the parent space.
     * @param item_name_filter Optional filter for item names.
     * @param kind_filter Optional filter for item kinds.
     * @param include_deprecated Whether to include deprecated items.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @return A list of Item objects matching the filters.
     */
    std::vector<std::shared_ptr<Item>> getItems(
        const std::string& parent_path,
        const std::string& item_name_filter = "",
        const std::string& kind_filter = "",
        bool include_deprecated = false,
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt
    );

    /**
     * @brief Search for items.
     * @param context_filter Filter by context (project/space path).
     * @param name_filter Filter by item name.
     * @param kind_filter Filter by item kind.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @param include_deprecated Whether to include deprecated items.
     * @return A PagedList of matching Item objects.
     */
    PagedList<std::shared_ptr<Item>> itemSearch(
        const std::string& context_filter = "",
        const std::string& name_filter = "",
        const std::string& kind_filter = "",
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt,
        bool include_deprecated = false
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
     * @param embedding_text Optional override for the text used to generate the
     *        server-side embedding. When empty the server auto-generates from
     *        concatenated metadata.
     * @return The created Revision.
     */
    std::shared_ptr<Revision> createRevision(const Kref& item_kref, const Metadata& metadata = {}, int number = 0, const std::string& embedding_text = "");

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
     * @brief Full-text fuzzy search across items.
     * @param query Search terms (supports fuzzy matching).
     * @param context_filter Restrict to a kref prefix (e.g., "myproject/assets").
     * @param kind_filter Exact kind match (e.g., "model").
     * @param include_deprecated Include soft-deleted items.
     * @param include_revision_metadata Also search revision tags/metadata.
     * @param include_artifact_metadata Also search artifact names/metadata.
     * @param page_size Optional results per page (1-1000, default 100).
     * @param cursor Optional pagination cursor.
     * @param min_score Minimum relevance score 0.0-1.0.
     * @return A list of SearchResult ordered by relevance.
     */
    std::vector<SearchResult> search(
        const std::string& query,
        const std::string& context_filter = "",
        const std::string& kind_filter = "",
        bool include_deprecated = false,
        bool include_revision_metadata = false,
        bool include_artifact_metadata = false,
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt,
        double min_score = 0.0
    );

    /**
     * @brief Score specific revisions against a query (server-side embeddings).
     * @param query The query string to score against.
     * @param revision_krefs Revision kref URIs to score (max 100).
     * @param score_fields When non-empty, re-embed from only these metadata fields.
     * @return ScoredRevision entries ordered by score descending.
     */
    std::vector<ScoredRevision> scoreRevisions(
        const std::string& query,
        const std::vector<std::string>& revision_krefs,
        const std::vector<std::string>& score_fields = {}
    );

    /**
     * @brief Batch fetch multiple revisions in a single call.
     * @param revision_krefs Revision kref URIs to fetch directly.
     * @param item_krefs Item kref URIs to resolve with the given tag.
     * @param tag Tag to resolve when using item_krefs (default "latest").
     * @param allow_partial If true, return partial results for not-found krefs.
     * @return A pair of (found revisions, not-found kref URIs).
     */
    std::pair<std::vector<std::shared_ptr<Revision>>, std::vector<std::string>>
    batchGetRevisions(
        const std::vector<std::string>& revision_krefs = {},
        const std::vector<std::string>& item_krefs = {},
        const std::string& tag = "latest",
        bool allow_partial = true
    );

    /**
     * @brief Get the latest revision of an item.
     *
     * Resolves the item kref to its latest revision (mirrors Python
     * Client.get_latest_revision).
     *
     * @param item_kref The item's Kref.
     * @return The latest Revision, or nullptr if the item has no revisions.
     */
    std::shared_ptr<Revision> getLatestRevision(const Kref& item_kref);

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
     * @param metadata Optional key-value metadata for the artifact.
     * @return The created Artifact.
     */
    std::shared_ptr<Artifact> createArtifact(const Kref& revision_kref, const std::string& name, const std::string& location, const Metadata& metadata = {});

    /**
     * @brief Get an artifact by revision and name.
     * @param revision_kref The revision's Kref.
     * @param name The artifact name.
     * @return The Artifact.
     */
    std::shared_ptr<Artifact> getArtifact(const Kref& revision_kref, const std::string& name);

    /**
     * @brief Get an artifact by its Kref URI.
     *
     * If the Kref contains an artifact name (`&a=`), that artifact is fetched
     * directly. Otherwise the Kref is treated as an item/revision reference and
     * the revision's default artifact is returned.
     *
     * @param kref_uri The artifact's Kref URI.
     * @return The Artifact.
     * @throws ValidationError if no artifact name is present and no default
     *         artifact is set on the revision.
     */
    std::shared_ptr<Artifact> getArtifactByKref(const std::string& kref_uri);

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
     * @param direction Direction of edges to retrieve (OUTGOING, INCOMING, or BOTH).
     * @return A list of Edge objects.
     */
    std::vector<std::shared_ptr<Edge>> getEdges(
        const Kref& kref,
        const std::string& edge_type_filter = "",
        EdgeDirection direction = EdgeDirection::OUTGOING
    );

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
     * @param metadata Optional key-value metadata for the bundle.
     * @return The created Bundle.
     */
    std::shared_ptr<Bundle> createBundle(const std::string& parent_path, const std::string& name, const Metadata& metadata = {});

    /**
     * @brief Create a bundle using a parent Kref.
     * @param parent_kref The parent's Kref.
     * @param name The bundle name.
     * @param metadata Optional key-value metadata for the bundle.
     * @return The created Bundle.
     */
    std::shared_ptr<Bundle> createBundle(const Kref& parent_kref, const std::string& name, const Metadata& metadata = {});

    /**
     * @brief Get a bundle by parent path and name.
     * @param parent_path The parent space path.
     * @param name The bundle name.
     * @return The Bundle.
     */
    std::shared_ptr<Bundle> getBundle(const std::string& parent_path, const std::string& name);

    /**
     * @brief Get a bundle by its Kref URI.
     *
     * Retrieves the item and verifies it is a bundle (kind == "bundle").
     *
     * @param kref_uri The bundle's Kref URI.
     * @return The Bundle.
     * @throws ValidationError if the item exists but is not a bundle.
     */
    std::shared_ptr<Bundle> getBundleByKref(const std::string& kref_uri);

    /**
     * @brief Add a member to a bundle.
     *
     * Creates a new bundle revision (mirrors Python add_bundle_member).
     *
     * @param bundle_kref The bundle's Kref.
     * @param item_kref The item to add.
     * @param metadata Optional key-value metadata to store in the revision.
     * @return A BundleMemberResult with success, message, and new_revision.
     */
    BundleMemberResult addBundleMember(const Kref& bundle_kref, const Kref& item_kref, const Metadata& metadata = {});

    /**
     * @brief Remove a member from a bundle.
     *
     * Creates a new bundle revision (mirrors Python remove_bundle_member).
     *
     * @param bundle_kref The bundle's Kref.
     * @param item_kref The item to remove.
     * @param metadata Optional key-value metadata to store in the revision.
     * @return A BundleMemberResult with success, message, and new_revision.
     */
    BundleMemberResult removeBundleMember(const Kref& bundle_kref, const Kref& item_kref, const Metadata& metadata = {});

    /**
     * @brief Get bundle members.
     * @param bundle_kref The bundle's Kref.
     * @param revision_number Optional revision to query (0 = latest revision).
     * @return A list of BundleMember objects.
     */
    std::vector<BundleMember> getBundleMembers(const Kref& bundle_kref, int revision_number = 0);

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
    std::shared_ptr<EventStream> eventStream(
        const std::string& routing_key_filter = "",
        const std::string& kref_filter = "",
        const std::string& cursor = "",
        const std::string& consumer_group = "",
        bool from_beginning = false,
        double timeout_seconds = 0.0
    );

    /**
     * @brief Get event streaming capabilities for the current tenant tier.
     *
     * Returns the capabilities available based on the authenticated tenant's
     * subscription tier (replay, cursor resume, consumer groups, retention and
     * buffer limits).
     *
     * @return An EventCapabilities struct describing the tier's capabilities.
     */
    EventCapabilities getEventCapabilities();

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

    /**
     * @brief Set the tenant id sent as the x-tenant-id metadata header.
     *
     * Used by discovery-built clients to route requests to the resolved
     * tenant. When set, every RPC includes x-tenant-id.
     * @param tenant_id The tenant id, or empty to disable.
     */
    void setTenantId(const std::string& tenant_id);

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
    std::string tenant_id_;   // Tenant id for x-tenant-id routing (discovery)

    /**
     * @brief Configure a ClientContext with authentication metadata.
     *
     * Adds a correlation id and (when set) the bearer token. For unary RPCs a
     * default per-RPC deadline is applied (KUMIHO_RPC_TIMEOUT_SECONDS, default
     * 30s); streaming RPCs opt out by passing with_deadline = false.
     *
     * @param context The context to configure.
     * @param with_deadline Whether to set a default per-RPC deadline.
     */
    void configureContext(grpc::ClientContext& context, bool with_deadline = true) const;
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

/**
 * @brief Apply standard gRPC keepalive settings to channel arguments.
 *
 * Configures HTTP/2 keepalive pings so long-lived channels (including event
 * streams) survive idle NAT/proxy timeouts and detect dead connections:
 * - GRPC_ARG_KEEPALIVE_TIME_MS = 30000
 * - GRPC_ARG_KEEPALIVE_TIMEOUT_MS = 10000
 * - GRPC_ARG_KEEPALIVE_PERMIT_WITHOUT_CALLS = 1
 * - GRPC_ARG_HTTP2_MIN_SENT_PING_INTERVAL_WITHOUT_DATA_MS = 10000
 * - GRPC_ARG_HTTP2_MAX_PINGS_WITHOUT_DATA = 3
 *
 * Applied uniformly in createFromEnv, clientFromDiscovery, and the CE channel.
 *
 * @param args The channel arguments to mutate.
 */
void applyKeepaliveArgs(grpc::ChannelArguments& args);

} // namespace api
} // namespace kumiho
