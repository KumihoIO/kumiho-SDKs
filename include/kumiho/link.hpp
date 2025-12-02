/**
 * @file link.hpp
 * @brief Link entity for tracking relationships between versions.
 *
 * Links represent directed relationships between versions in the Kumiho
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
 * @brief Standard link types for Kumiho relationships.
 *
 * These constants define the semantic meaning of relationships between
 * versions. All link types use UPPERCASE format as required by the
 * Neo4j graph database.
 *
 * Example:
 * @code
 *   version->createLink(texture, LinkType::DEPENDS_ON);
 * @endcode
 */
struct LinkType {
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
 * @brief Direction constants for link traversal queries.
 *
 * When querying links, specify which direction to traverse:
 * outgoing links (from source), incoming links (to target), or both.
 *
 * Example:
 * @code
 *   // Get dependencies (what this version depends on)
 *   auto deps = version->getLinks(LinkType::DEPENDS_ON, LinkDirection::OUTGOING);
 *   
 *   // Get dependents (what depends on this version)
 *   auto dependents = version->getLinks(LinkType::DEPENDS_ON, LinkDirection::INCOMING);
 * @endcode
 */
enum class LinkDirection : int {
    /** @brief Links where the queried version is the source. */
    OUTGOING = 0,
    
    /** @brief Links where the queried version is the target. */
    INCOMING = 1,
    
    /** @brief Links in either direction. */
    BOTH = 2
};

/**
 * @brief Validate a link type for security and correctness.
 *
 * Link types must:
 * - Start with an uppercase letter
 * - Contain only uppercase letters, digits, and underscores
 * - Be 1-50 characters long
 *
 * @param link_type The link type to validate.
 * @throws LinkTypeValidationError if the link type is invalid.
 *
 * Example:
 * @code
 *   validateLinkType("DEPENDS_ON");  // OK
 *   validateLinkType("depends_on");  // Throws error
 * @endcode
 */
inline void validateLinkType(const std::string& link_type) {
    static const std::regex pattern("^[A-Z][A-Z0-9_]{0,49}$");
    if (!std::regex_match(link_type, pattern)) {
        throw LinkTypeValidationError(
            "Invalid link_type '" + link_type + "'. Must start with uppercase letter, "
            "contain only uppercase letters, digits, underscores, and be 1-50 chars."
        );
    }
}

/**
 * @brief Check if a link type is valid without throwing exceptions.
 *
 * @param link_type The link type to validate.
 * @return True if the link type is valid, false otherwise.
 */
inline bool isValidLinkType(const std::string& link_type) {
    try {
        validateLinkType(link_type);
        return true;
    } catch (const LinkTypeValidationError&) {
        return false;
    }
}

/**
 * @brief A relationship between two versions in the Kumiho system.
 *
 * Links represent semantic relationships between versions, enabling
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
 *   auto links = version->getLinks(LinkType::DEPENDS_ON);
 *   for (const auto& link : links) {
 *       std::cout << link->getSourceKref().uri() 
 *                 << " depends on " 
 *                 << link->getTargetKref().uri() << std::endl;
 *   }
 * @endcode
 */
class Link {
public:
    /**
     * @brief Construct a Link from a protobuf message.
     * @param link The protobuf Link message.
     * @param client The client for making API calls.
     */
    Link(const ::kumiho::Link& link, Client* client);

    /**
     * @brief Get the source version's Kref.
     * @return The Kref of the source version.
     */
    Kref getSourceKref() const;

    /**
     * @brief Get the target version's Kref.
     * @return The Kref of the target version.
     */
    Kref getTargetKref() const;

    /**
     * @brief Get the link type.
     * @return The link type string (e.g., "DEPENDS_ON").
     */
    std::string getLinkType() const;

    /**
     * @brief Get the link's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the link was created, or empty.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the link.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the link creator.
     */
    std::string getUsername() const;

    /**
     * @brief Delete this link.
     *
     * Removes the relationship between the source and target versions.
     */
    void deleteLink();

private:
    ::kumiho::Link link_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
