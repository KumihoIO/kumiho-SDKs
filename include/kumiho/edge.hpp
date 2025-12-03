/**
 * @file edge.hpp
 * @brief Edge entity for tracking relationships between revisions.
 *
 * Edges represent directed relationships between revisions in the Kumiho
 * graph database. They enable dependency tracking, lineage visualization,
 * and impact analysis.
 */

#pragma once

#include <string>
#include <map>
#include <optional>
#include <regex>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/error.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declaration
class Client;

/**
 * @brief Standard edge types for Kumiho relationships.
 *
 * These constants define the semantic meaning of relationships between
 * revisions. All edge types use UPPERCASE format as required by the
 * Neo4j graph database.
 *
 * Example:
 * @code
 *   revision->createEdge(texture, EdgeType::DEPENDS_ON);
 * @endcode
 */
struct EdgeType {
    /** @brief Indicates ownership or grouping relationship. */
    static constexpr const char* BELONGS_TO = "BELONGS_TO";
    
    /** @brief Indicates the source was generated/created from target. */
    static constexpr const char* CREATED_FROM = "CREATED_FROM";
    
    /** @brief Indicates a soft reference relationship. */
    static constexpr const char* REFERENCED = "REFERENCED";
    
    /** @brief Indicates the source requires target to function. */
    static constexpr const char* DEPENDS_ON = "DEPENDS_ON";
    
    /** @brief Indicates the source was derived or modified from target. */
    static constexpr const char* DERIVED_FROM = "DERIVED_FROM";
    
    /** @brief Indicates the source contains or includes target. */
    static constexpr const char* CONTAINS = "CONTAINS";
};

/**
 * @brief Direction constants for edge traversal queries.
 *
 * When querying edges, specify which direction to traverse:
 * outgoing edges (from source), incoming edges (to target), or both.
 *
 * Example:
 * @code
 *   // Get dependencies (what this revision depends on)
 *   auto deps = revision->getEdges(EdgeType::DEPENDS_ON, EdgeDirection::OUTGOING);
 *   
 *   // Get dependents (what depends on this revision)
 *   auto dependents = revision->getEdges(EdgeType::DEPENDS_ON, EdgeDirection::INCOMING);
 * @endcode
 */
enum class EdgeDirection : int {
    /** @brief Edges where the queried revision is the source. */
    OUTGOING = 0,
    
    /** @brief Edges where the queried revision is the target. */
    INCOMING = 1,
    
    /** @brief Edges in either direction. */
    BOTH = 2
};

/**
 * @brief Validate an edge type for security and correctness.
 *
 * Edge types must:
 * - Start with an uppercase letter
 * - Contain only uppercase letters, digits, and underscores
 * - Be 1-50 characters long
 *
 * @param edge_type The edge type to validate.
 * @throws EdgeTypeValidationError if the edge type is invalid.
 *
 * Example:
 * @code
 *   validateEdgeType("DEPENDS_ON");  // OK
 *   validateEdgeType("depends_on");  // Throws error
 * @endcode
 */
inline void validateEdgeType(const std::string& edge_type) {
    static const std::regex pattern("^[A-Z][A-Z0-9_]{0,49}$");
    if (!std::regex_match(edge_type, pattern)) {
        throw EdgeTypeValidationError(
            "Invalid edge_type '" + edge_type + "'. Must start with uppercase letter, "
            "contain only uppercase letters, digits, underscores, and be 1-50 chars."
        );
    }
}

/**
 * @brief Check if an edge type is valid without throwing exceptions.
 *
 * @param edge_type The edge type to validate.
 * @return True if the edge type is valid, false otherwise.
 */
inline bool isValidEdgeType(const std::string& edge_type) {
    try {
        validateEdgeType(edge_type);
        return true;
    } catch (const EdgeTypeValidationError&) {
        return false;
    }
}

/**
 * @brief A relationship between two revisions in the Kumiho system.
 *
 * Edges represent semantic relationships between revisions, enabling
 * dependency tracking, lineage visualization, and impact analysis.
 * They are directional (source -> target) and typed.
 *
 * Common use cases:
 * - Track which textures a model uses (DEPENDS_ON)
 * - Record that a LOD was created from a high-poly model (DERIVED_FROM)
 * - Link a render to the scene file that created it (CREATED_FROM)
 *
 * Example:
 * @code
 *   auto edges = revision->getEdges(EdgeType::DEPENDS_ON);
 *   for (const auto& edge : edges) {
 *       std::cout << edge->getSourceKref().uri() 
 *                 << " depends on " 
 *                 << edge->getTargetKref().uri() << std::endl;
 *   }
 * @endcode
 */
class Edge {
public:
    /**
     * @brief Construct an Edge from a protobuf message.
     * @param edge The protobuf Edge message.
     * @param client The client for making API calls.
     */
    Edge(const ::kumiho::Edge& edge, Client* client);

    /**
     * @brief Get the source revision's Kref.
     * @return The Kref of the source revision.
     */
    Kref getSourceKref() const;

    /**
     * @brief Get the target revision's Kref.
     * @return The Kref of the target revision.
     */
    Kref getTargetKref() const;

    /**
     * @brief Get the edge type.
     * @return The edge type string (e.g., "DEPENDS_ON").
     */
    std::string getEdgeType() const;

    /**
     * @brief Get the edge's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the edge was created, or empty.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the edge.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the edge creator.
     */
    std::string getUsername() const;

    /**
     * @brief Delete this edge.
     */
    void deleteEdge();

private:
    ::kumiho::Edge edge_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
