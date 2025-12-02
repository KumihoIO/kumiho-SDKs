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
class Group;
class Product;
class Version;
class Resource;
class Link;
class Collection;
class Event;
class EventStream;

/**
 * @brief Metadata type used throughout Kumiho.
 * 
 * Metadata is a key-value store of string pairs attached to most entities.
 */
using Metadata = std::map<std::string, std::string>;

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
 * @brief Reserved product types that cannot be created manually.
 * 
 * Use dedicated methods (e.g., createCollection) for these types.
 */
inline const std::vector<std::string> RESERVED_PRODUCT_TYPES = {"collection"};

/**
 * @brief Check if a product type is reserved.
 * @param ptype The product type to check.
 * @return True if the type is reserved, false otherwise.
 */
inline bool isReservedProductType(const std::string& ptype) {
    for (const auto& reserved : RESERVED_PRODUCT_TYPES) {
        if (ptype == reserved) return true;
    }
    return false;
}

// Forward declaration for Kref
class Kref;

/**
 * @brief A single step in a graph traversal path.
 *
 * Represents one hop in a path between versions, including
 * the version reached and the relationship type used.
 */
struct PathStep {
    /** @brief The version's Kref at this step. */
    std::string version_kref;
    
    /** @brief The link type used to reach this node (e.g., "DEPENDS_ON"). */
    std::string link_type;
    
    /** @brief Distance from the origin (0 = origin). */
    int depth;
};

/**
 * @brief A complete path between two versions.
 *
 * Contains the sequence of steps from a source to a target version.
 */
struct VersionPath {
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
 * Contains all discovered versions and optionally the paths to reach them.
 */
struct TraversalResult {
    /** @brief Full paths to each discovered version (if include_path=true). */
    std::vector<VersionPath> paths;
    
    /** @brief Flat list of all discovered version Krefs. */
    std::vector<std::string> version_krefs;
    
    /** @brief All links traversed during the operation. */
    std::vector<std::shared_ptr<Link>> links;
    
    /** @brief Total number of nodes found. */
    int total_count = 0;
    
    /** @brief True if results were limited/truncated. */
    bool truncated = false;
};

/**
 * @brief Result of a shortest path query.
 *
 * Contains one or more shortest paths between two versions.
 */
struct ShortestPathResult {
    /** @brief One or more shortest paths found. */
    std::vector<VersionPath> paths;
    
    /** @brief True if any path was found. */
    bool path_exists;
    
    /** @brief Length of the shortest path(s). */
    int path_length;
    
    /** @brief Get the first path, or nullptr if none found. */
    const VersionPath* first_path() const {
        return paths.empty() ? nullptr : &paths[0];
    }
};

/**
 * @brief A version that would be impacted by changes.
 *
 * Used in impact analysis to identify downstream dependencies.
 */
struct ImpactedVersion {
    /** @brief The impacted version's Kref. */
    std::string version_kref;
    
    /** @brief The product's Kref. */
    std::string product_kref;
    
    /** @brief How many hops away from the source. */
    int impact_depth;
    
    /** @brief Link types in the impact chain. */
    std::vector<std::string> impact_path_types;
};

/**
 * @brief Result of an impact analysis operation.
 *
 * Contains all versions that would be affected by changes to a source version.
 */
struct ImpactAnalysisResult {
    /** @brief All versions that would be impacted. */
    std::vector<ImpactedVersion> impacted_versions;
    
    /** @brief Total number of impacted versions. */
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
