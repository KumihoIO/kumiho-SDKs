/**
 * @file kref.hpp
 * @brief Kref (Kumiho Reference) URI parser and utilities.
 *
 * Kref is the URI-based unique identifier system for Kumiho objects.
 * Format: kref://project/group/product.type?v=1&r=resource
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
 * - Group: `kref://project/group/subgroup`
 * - Product: `kref://project/group/product.type`
 * - Version: `kref://project/group/product.type?v=1`
 * - Resource: `kref://project/group/product.type?v=1&r=resource`
 *
 * Legacy format with `kumiho://` prefix is also supported.
 *
 * Example:
 * @code
 *   Kref kref("kref://my-project/assets/hero.model?v=1");
 *   std::cout << kref.getProject();     // "my-project"
 *   std::cout << kref.getGroup();       // "assets"
 *   std::cout << kref.getProductName(); // "hero"
 *   std::cout << kref.getType();        // "model"
 *   std::cout << kref.getVersion();     // 1
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
     * @brief Get the group path (path between project and product).
     * @return The group path, or empty if this is a project-level kref.
     */
    std::string getGroup() const;

    /**
     * @brief Get the base product name (without type).
     * @return The product name, or empty if this is a group-level kref.
     */
    std::string getProductName() const;

    /**
     * @brief Get the product type.
     * @return The product type (e.g., "model", "texture"), or empty.
     */
    std::string getType() const;

    /**
     * @brief Get the full product name including type.
     * @return The full product name (e.g., "hero.model"), or empty.
     */
    std::string getFullProductName() const;

    /**
     * @brief Get the version number if present.
     * @return The version number, or std::nullopt if not specified.
     */
    std::optional<int> getVersion() const;

    /**
     * @brief Get the resource name if present.
     * @return The resource name, or empty if not specified.
     */
    std::string getResourceName() const;

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
