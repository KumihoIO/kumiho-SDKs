/**
 * @file product.hpp
 * @brief Product entity representing versioned assets.
 *
 * Products represent assets that can have multiple versions, such as 3D models,
 * textures, workflows, or any other type of creative content. Each product
 * belongs to a group and is identified by a combination of name and type.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Version;
class Group;
class Project;

/**
 * @brief A versioned asset in the Kumiho system.
 *
 * Products represent assets that can have multiple versions. Each product
 * belongs to a group and is identified by a combination of name and type.
 *
 * The product's kref (Kumiho Reference) is a URI that uniquely identifies it:
 * `kref://project/group/product.type`
 *
 * Example:
 * @code
 *   auto product = group->createProduct("hero", "model");
 *   
 *   // Create versions
 *   auto v1 = product->createVersion();
 *   auto v2 = product->createVersion({{"notes", "Updated mesh"}});
 *   
 *   // Get specific version
 *   auto v1 = product->getVersion(1);
 *   auto latest = product->getLatestVersion();
 *   
 *   // Get version by tag
 *   auto approved = product->getVersionByTag("approved");
 * @endcode
 */
class Product {
public:
    /**
     * @brief Construct a Product from a protobuf response.
     * @param response The protobuf ProductResponse message.
     * @param client The client for making API calls.
     */
    Product(const ::kumiho::ProductResponse& response, Client* client);

    /**
     * @brief Get the product's unique Kref.
     * @return The Kref URI for this product.
     */
    Kref getKref() const;

    /**
     * @brief Get the full name including type.
     * @return The full product name (e.g., "hero.model").
     */
    std::string getName() const;

    /**
     * @brief Get the base product name.
     * @return The product name without type (e.g., "hero").
     */
    std::string getProductName() const;

    /**
     * @brief Get the product type.
     * @return The product type (e.g., "model", "texture").
     */
    std::string getProductType() const;

    /**
     * @brief Get the product's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the product was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the product.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the product creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the product is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Create a new version of this product.
     *
     * Versions are automatically numbered sequentially. Each version starts
     * with the "latest" tag, which moves to the newest version.
     *
     * @param metadata Optional metadata for the version.
     * @return The created Version.
     */
    std::shared_ptr<Version> createVersion(const Metadata& metadata = {});

    /**
     * @brief Get a specific version by number.
     * @param version_number The version number (1-based).
     * @return The Version.
     */
    std::shared_ptr<Version> getVersion(int version_number);

    /**
     * @brief Get all versions of this product.
     * @return A list of Version objects, ordered by version number.
     */
    std::vector<std::shared_ptr<Version>> getVersions();

    /**
     * @brief Get a version by tag.
     * @param tag The tag to search for.
     * @return The Version, or nullptr if not found.
     */
    std::shared_ptr<Version> getVersionByTag(const std::string& tag);

    /**
     * @brief Get a version by creation time.
     * @param time The time in YYYYMMDDHHMM format.
     * @return The Version, or nullptr if not found.
     */
    std::shared_ptr<Version> getVersionByTime(const std::string& time);

    /**
     * @brief Get the latest version.
     * @return The latest Version, or nullptr if no versions exist.
     */
    std::shared_ptr<Version> getLatestVersion();

    /**
     * @brief Peek at the next version number.
     * @return The next version number that would be assigned.
     */
    int peekNextVersion();

    /**
     * @brief Set or update metadata for this product.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Product.
     */
    std::shared_ptr<Product> setMetadata(const Metadata& metadata);

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
     * @brief Delete this product.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteProduct(bool force = false);

    /**
     * @brief Get the parent group.
     * @return The Group containing this product.
     */
    std::shared_ptr<Group> getGroup();

    /**
     * @brief Get the parent project.
     * @return The Project containing this product.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     */
    void setDeprecated(bool deprecated);

    /**
     * @brief Refresh this product's data from the server.
     * @return The refreshed Product.
     */
    std::shared_ptr<Product> refresh();

private:
    ::kumiho::ProductResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
