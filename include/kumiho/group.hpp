/**
 * @file group.hpp
 * @brief Group entity for hierarchical organization of products.
 *
 * Groups form the folder structure within a project. They can contain
 * other groups (subgroups) and products, allowing you to organize assets
 * in a meaningful hierarchy.
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
class Product;
class Project;
class Collection;

/**
 * @brief A hierarchical container for organizing products in Kumiho.
 *
 * Groups form the folder structure within a project. They can contain
 * other groups (subgroups) and products, allowing you to organize assets
 * in a meaningful hierarchy.
 *
 * Groups are identified by their full path (e.g., "/project/characters/heroes")
 * and can store custom metadata.
 *
 * Example:
 * @code
 *   auto assets = project->createGroup("assets");
 *   auto models = assets->createGroup("models");
 *   auto textures = assets->createGroup("textures");
 *   
 *   // Create products
 *   auto chair = models->createProduct("chair", "model");
 *   
 *   // Navigate hierarchy
 *   auto parent = models->getParentGroup();  // Returns assets
 *   auto children = assets->getChildGroups();  // Returns [models, textures]
 * @endcode
 */
class Group {
public:
    /**
     * @brief Construct a Group from a protobuf response.
     * @param response The protobuf GroupResponse message.
     * @param client The client for making API calls.
     */
    Group(const ::kumiho::GroupResponse& response, Client* client);

    /**
     * @brief Get the group's full path.
     * @return The full path (e.g., "/project/assets/models").
     */
    std::string getPath() const;

    /**
     * @brief Get the group's Kref.
     * @return A Kref containing the group path.
     */
    Kref getKref() const;

    /**
     * @brief Get the group's name (last component of path).
     * @return The group name.
     */
    std::string getName() const;

    /**
     * @brief Get the group's type.
     * @return "root" for project-level, "sub" for nested groups.
     */
    std::string getType() const;

    /**
     * @brief Get the group's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the group was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the group.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the group creator.
     */
    std::string getUsername() const;

    /**
     * @brief Create a subgroup.
     * @param name The name of the new group.
     * @return The created Group.
     */
    std::shared_ptr<Group> createGroup(const std::string& name);

    /**
     * @brief Create a product in this group.
     *
     * @param name The product name.
     * @param ptype The product type (e.g., "model", "texture").
     * @return The created Product.
     * @throws ReservedProductTypeError if ptype is reserved (e.g., "collection").
     */
    std::shared_ptr<Product> createProduct(const std::string& name, const std::string& ptype);

    /**
     * @brief Get a product by name and type.
     * @param name The product name.
     * @param ptype The product type.
     * @return The Product.
     */
    std::shared_ptr<Product> getProduct(const std::string& name, const std::string& ptype);

    /**
     * @brief Get all products in this group.
     * @param name_filter Optional filter by product name (supports wildcards).
     * @param ptype_filter Optional filter by product type.
     * @return A list of Product objects.
     */
    std::vector<std::shared_ptr<Product>> getProducts(
        const std::string& name_filter = "",
        const std::string& ptype_filter = ""
    );

    /**
     * @brief Set or update metadata for this group.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Group.
     */
    std::shared_ptr<Group> setMetadata(const Metadata& metadata);

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
     * @brief Delete this group.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteGroup(bool force = false);

    /**
     * @brief Get the parent group.
     * @return The parent Group, or nullptr if this is a root group.
     */
    std::shared_ptr<Group> getParentGroup();

    /**
     * @brief Get child groups.
     * @return A list of child Group objects.
     */
    std::vector<std::shared_ptr<Group>> getChildGroups();

    /**
     * @brief Get the parent project.
     * @return The Project containing this group.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Create a collection in this group.
     * @param name The collection name.
     * @return The created Collection.
     */
    std::shared_ptr<Collection> createCollection(const std::string& name);

    /**
     * @brief Get a collection by name.
     * @param name The collection name.
     * @return The Collection.
     */
    std::shared_ptr<Collection> getCollection(const std::string& name);

private:
    ::kumiho::GroupResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
