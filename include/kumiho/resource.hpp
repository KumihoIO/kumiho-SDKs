/**
 * @file resource.hpp
 * @brief Resource entity representing file references within versions.
 *
 * Resources are the leaf nodes of the Kumiho hierarchy. They point to
 * actual files on local disk, network storage, or cloud URIs. Kumiho
 * tracks the path and metadata but does not upload or modify the files.
 */

#pragma once

#include <string>
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
class Product;
class Group;
class Project;

/**
 * @brief A file reference within a version in the Kumiho system.
 *
 * Resources point to actual files on local disk, network storage, or
 * cloud URIs. Kumiho tracks the path and metadata but does not upload
 * or modify the files.
 *
 * The resource's kref includes both version and resource name:
 * `kref://project/group/product.type?v=1&r=resource_name`
 *
 * Example:
 * @code
 *   auto mesh = version->createResource("mesh", "/assets/hero.fbx");
 *   auto textures = version->createResource("textures", "smb://server/tex/hero/");
 *   
 *   // Set metadata
 *   mesh->setMetadata({{"triangles", "2.5M"}, {"format", "FBX 2020"}});
 *   
 *   // Set as default resource
 *   mesh->setDefault();
 * @endcode
 */
class Resource {
public:
    /**
     * @brief Construct a Resource from a protobuf response.
     * @param response The protobuf ResourceResponse message.
     * @param client The client for making API calls.
     */
    Resource(const ::kumiho::ResourceResponse& response, Client* client);

    /**
     * @brief Get the resource's unique Kref.
     * @return The Kref URI for this resource.
     */
    Kref getKref() const;

    /**
     * @brief Get the resource name.
     * @return The name of this resource (e.g., "mesh", "textures").
     */
    std::string getName() const;

    /**
     * @brief Get the file location.
     * @return The file path or URI where the resource is stored.
     */
    std::string getLocation() const;

    /**
     * @brief Get the parent version's Kref.
     * @return The Kref of the version containing this resource.
     */
    Kref getVersionKref() const;

    /**
     * @brief Get the parent product's Kref.
     * @return The Kref of the product containing this resource.
     */
    Kref getProductKref() const;

    /**
     * @brief Get the resource's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the resource was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the resource.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the resource creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the resource is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Set or update metadata for this resource.
     *
     * Metadata is merged with existing metadata—existing keys are
     * overwritten and new keys are added.
     *
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Resource.
     */
    std::shared_ptr<Resource> setMetadata(const Metadata& metadata);

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
     * @brief Delete this resource.
     * @param force If true, permanently delete. If false, soft delete (deprecate).
     */
    void deleteResource(bool force = false);

    /**
     * @brief Get the parent version.
     * @return The Version containing this resource.
     */
    std::shared_ptr<Version> getVersion();

    /**
     * @brief Get the parent product.
     * @return The Product containing this resource.
     */
    std::shared_ptr<Product> getProduct();

    /**
     * @brief Get the parent group.
     * @return The Group containing this resource's product.
     */
    std::shared_ptr<Group> getGroup();

    /**
     * @brief Get the parent project.
     * @return The Project containing this resource.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Set this resource as the default for its version.
     *
     * When resolving a version without specifying a resource name,
     * the default resource's location is returned.
     */
    void setDefault();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     * @return The updated Resource.
     */
    std::shared_ptr<Resource> setDeprecated(bool deprecated);

private:
    ::kumiho::ResourceResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
