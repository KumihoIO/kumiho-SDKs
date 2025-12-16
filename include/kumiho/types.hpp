/**
 * @file types.hpp
 * @brief Common type definitions and constants for the Kumiho C++ SDK.
 *
 * This header defines type aliases, constants, and common enumerations used
 * throughout the Kumiho library.
 */

#pragma once

#include <map>
#include <string>
#include <vector>
#include <optional>
#include <memory>

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Project;
class Space;
class Item;
class Revision;
class Artifact;
class Edge;
class Bundle;
class Event;
class EventStream;

/**
 * @brief Metadata type used throughout Kumiho.
 * 
 * Metadata is a key-value store of string pairs attached to most entities.
 */
using Metadata = std::map<std::string, std::string>;

/**
 * @brief A list that also contains pagination information.
 * 
 * @tparam T The type of items in the list.
 */
template <typename T>
struct PagedList {
    std::vector<T> items;
    std::optional<std::string> next_cursor;
    std::optional<int32_t> total_count;
};

/**
 * @brief Standard tag name for the latest version.
 * 
 * This tag automatically moves to the newest version of a product.
 */
constexpr const char* LATEST_TAG = "latest";

/**
 * @brief Standard tag name for published versions.
 * 
 * Published versions are immutable - their metadata cannot be changed.
 */
constexpr const char* PUBLISHED_TAG = "published";

/**
 * @brief Reserved item kinds that cannot be created manually.
 * 
 * Use dedicated methods (e.g., createBundle) for these kinds.
 */
inline const std::vector<std::string> RESERVED_KINDS = {"bundle"};

/**
 * @brief Check if an item kind is reserved.
 * @param kind The item kind to check.
 * @return True if the kind is reserved, false otherwise.
 */
inline bool isReservedKind(const std::string& kind) {
    for (const auto& reserved : RESERVED_KINDS) {
        if (kind == reserved) return true;
    }
    return false;
}

// Forward declaration for Kref
class Kref;

/**
 * @brief A single step in a graph traversal path.
 *
 * Represents one hop in a path between revisions, including
 * the revision reached and the relationship type used.
 */
struct PathStep {
    /** @brief The revision's Kref at this step. */
    std::string revision_kref;
    
    /** @brief The edge type used to reach this node (e.g., "DEPENDS_ON"). */
    std::string edge_type;
    
    /** @brief Distance from the origin (0 = origin). */
    int depth;
};

/**
 * @brief A complete path between two revisions.
 *
 * Contains the sequence of steps from a source to a target revision.
 */
struct RevisionPath {
    /** @brief The sequence of steps in the path. */
    std::vector<PathStep> steps;
    
    /** @brief Total depth/length of the path. */
    int total_depth = 0;
    
    /** @brief Check if the path is empty. */
    bool empty() const { return steps.empty(); }
};

/**
 * @brief Result of a graph traversal operation.
 *
 * Contains all discovered revisions and optionally the paths to reach them.
 */
struct TraversalResult {
    /** @brief Full paths to each discovered revision (if include_path=true). */
    std::vector<RevisionPath> paths;
    
    /** @brief Flat list of all discovered revision Krefs. */
    std::vector<std::string> revision_krefs;
    
    /** @brief All edges traversed during the operation. */
    std::vector<std::shared_ptr<Edge>> edges;
    
    /** @brief Total number of nodes found. */
    int total_count = 0;
    
    /** @brief True if results were limited/truncated. */
    bool truncated = false;
};

/**
 * @brief Result of a shortest path query.
 *
 * Contains one or more shortest paths between two revisions.
 */
struct ShortestPathResult {
    /** @brief One or more shortest paths found. */
    std::vector<RevisionPath> paths;
    
    /** @brief True if any path was found. */
    bool path_exists;
    
    /** @brief Length of the shortest path(s). */
    int path_length;
    
    /** @brief Get the first path, or nullptr if none found. */
    const RevisionPath* first_path() const {
        return paths.empty() ? nullptr : &paths[0];
    }
};

/**
 * @brief A revision that would be impacted by changes.
 *
 * Used in impact analysis to identify downstream dependencies.
 */
struct ImpactedRevision {
    /** @brief The impacted revision's Kref. */
    std::string revision_kref;
    
    /** @brief The item's Kref. */
    std::string item_kref;
    
    /** @brief How many hops away from the source. */
    int impact_depth;
    
    /** @brief Edge types in the impact chain. */
    std::vector<std::string> impact_path_types;
};

/**
 * @brief Result of an impact analysis operation.
 *
 * Contains all revisions that would be affected by changes to a source revision.
 */
struct ImpactAnalysisResult {
    /** @brief All revisions that would be impacted. */
    std::vector<ImpactedRevision> impacted_revisions;
    
    /** @brief Total number of impacted revisions. */
    int total_impacted = 0;
    
    /** @brief True if results were limited/truncated. */
    bool truncated = false;
};

/**
 * @brief Tenant usage and limits information.
 *
 * Contains the current resource usage and quota limits for the tenant.
 */
struct TenantUsage {
    /** @brief Current number of nodes (entities) in the tenant. */
    int64_t node_count = 0;
    
    /** @brief Maximum allowed nodes for the tenant's plan. */
    int64_t node_limit = 0;
    
    /** @brief The tenant's unique identifier. */
    std::string tenant_id;
    
    /** @brief Calculate usage percentage. */
    double usagePercent() const {
        if (node_limit <= 0) return 0.0;
        return static_cast<double>(node_count) / node_limit * 100.0;
    }
    
    /** @brief Check if tenant is near the limit (>80% usage). */
    bool isNearLimit() const {
        return usagePercent() >= 80.0;
    }
    
    /** @brief Check if tenant has reached the limit. */
    bool isAtLimit() const {
        return node_count >= node_limit;
    }
};

} // namespace api
} // namespace kumiho
