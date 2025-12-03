/**
 * @file kref.hpp
 * @brief Kref (Kumiho Reference) URI parser and utilities.
 *
 * Kref is the URI-based unique identifier system for Kumiho objects.
 * Format: kref://project/space/item.kind?r=1&a=artifact
 *
 * Terminology:
 * - Space: A hierarchical container/namespace
 * - Item: An asset/entity in the graph
 * - Revision: A specific state of an item
 * - Artifact: A file/location attached to a revision
 * - Kind: The category of an item
 */

#pragma once

#include <string>
#include <optional>
#include <regex>
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

/**
 * @brief A Kumiho Reference URI that uniquely identifies any object.
 *
 * Kref URIs follow the format:
 * - Project: `kref://project-name`
 * - Space: `kref://project/space/subspace`
 * - Item: `kref://project/space/item.kind`
 * - Revision: `kref://project/space/item.kind?r=1`
 * - Artifact: `kref://project/space/item.kind?r=1&a=artifact`
 *
 * Legacy format with `kumiho://` prefix is also supported.
 *
 * Example:
 * @code
 *   Kref kref("kref://my-project/assets/hero.model?r=1");
 *   std::cout << kref.getProject();   // "my-project"
 *   std::cout << kref.getSpace();     // "assets"
 *   std::cout << kref.getItemName();  // "hero"
 *   std::cout << kref.getKind();      // "model"
 *   std::cout << kref.getRevision();  // 1
 * @endcode
 */
class Kref : public std::string {
public:
    /**
     * @brief Construct a Kref from a URI string.
     * @param uri The Kref URI string.
     */
    explicit Kref(const std::string& uri = "");

    /**
     * @brief Get the full URI string.
     * @return The complete Kref URI.
     */
    const std::string& uri() const { return *this; }

    /**
     * @brief Get the path component (everything after scheme, before query).
     * @return The path portion of the URI.
     */
    std::string getPath() const;

    /**
     * @brief Get the project name (first path component).
     * @return The project name.
     */
    std::string getProject() const;

    /**
     * @brief Get the space path (path between project and item).
     * @return The space path, or empty if this is a project-level kref.
     */
    std::string getSpace() const;
    
    // Backwards compatibility alias
    std::string getGroup() const { return getSpace(); }

    /**
     * @brief Get the base item name (without kind).
     * @return The item name, or empty if this is a space-level kref.
     */
    std::string getItemName() const;
    
    // Backwards compatibility alias
    std::string getProductName() const { return getItemName(); }

    /**
     * @brief Get the item kind.
     * @return The item kind (e.g., "model", "texture"), or empty.
     */
    std::string getKind() const;
    
    // Backwards compatibility alias
    std::string getType() const { return getKind(); }

    /**
     * @brief Get the full item name including kind.
     * @return The full item name (e.g., "hero.model"), or empty.
     */
    std::string getFullItemName() const;
    
    // Backwards compatibility alias
    std::string getFullProductName() const { return getFullItemName(); }

    /**
     * @brief Get the revision number if present.
     * @return The revision number, or std::nullopt if not specified.
     */
    std::optional<int> getRevision() const;
    
    // Backwards compatibility alias
    std::optional<int> getVersion() const { return getRevision(); }

    /**
     * @brief Get the artifact name if present.
     * @return The artifact name, or empty if not specified.
     */
    std::string getArtifactName() const;
    
    // Backwards compatibility alias
    std::string getResourceName() const { return getArtifactName(); }

    /**
     * @brief Get the tag query parameter if present.
     * @return The tag value, or empty if not specified.
     */
    std::string getTag() const;

    /**
     * @brief Get the time query parameter if present.
     * @return The time value, or empty if not specified.
     */
    std::string getTime() const;

    /**
     * @brief Convert to protobuf Kref message.
     * @return A protobuf Kref with this URI.
     */
    ::kumiho::Kref toPb() const;

    /**
     * @brief Check if this is a valid Kref.
     * @return True if the URI is non-empty and has valid format.
     */
    bool isValid() const;

    /**
     * @brief Equality comparison with another Kref.
     */
    bool operator==(const Kref& other) const {
        return static_cast<const std::string&>(*this) == static_cast<const std::string&>(other);
    }

    /**
     * @brief Equality comparison with a string.
     */
    bool operator==(const std::string& other) const {
        return static_cast<const std::string&>(*this) == other;
    }

private:
    /**
     * @brief Extract a query parameter value.
     * @param param The parameter name (e.g., "v", "r", "t").
     * @return The parameter value, or empty if not found.
     */
    std::string getQueryParam(const std::string& param) const;
};

/**
 * @brief Validate a Kref URI string.
 *
 * Validates that the string is a properly formatted Kref URI.
 * Does not check if the referenced entity exists.
 *
 * @param kref_uri The URI string to validate.
 * @throws KrefValidationError if the format is invalid.
 */
void validateKref(const std::string& kref_uri);

/**
 * @brief Check if a string is a valid Kref URI.
 *
 * Non-throwing version of validateKref().
 *
 * @param kref_uri The URI string to check.
 * @return True if valid, false otherwise.
 */
bool isValidKref(const std::string& kref_uri);

} // namespace api
} // namespace kumiho
