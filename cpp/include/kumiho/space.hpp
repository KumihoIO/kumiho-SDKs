/**
 * @file space.hpp
 * @brief Space entity for hierarchical organization of items.
 *
 * Spaces form the folder structure within a project. They can contain
 * other spaces (sub-spaces) and items, allowing you to organize assets
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
class Item;
class Project;
class Bundle;

/**
 * @brief A hierarchical container for organizing items in Kumiho.
 *
 * Spaces form the folder structure within a project. They can contain
 * other spaces (sub-spaces) and items, allowing you to organize assets
 * in a meaningful hierarchy.
 *
 * Spaces are identified by their full path (e.g., "/project/characters/heroes")
 * and can store custom metadata.
 *
 * Example:
 * @code
 *   auto assets = project->createSpace("assets");
 *   auto models = assets->createSpace("models");
 *   auto textures = assets->createSpace("textures");
 *   
 *   // Create items
 *   auto chair = models->createItem("chair", "model");
 *   
 *   // Navigate hierarchy
 *   auto parent = models->getParentSpace();  // Returns assets
 *   auto children = assets->getChildSpaces();  // Returns [models, textures]
 * @endcode
 */
class Space {
public:
    /**
     * @brief Construct a Space from a protobuf response.
     * @param response The protobuf SpaceResponse message.
     * @param client The client for making API calls.
     */
    Space(const ::kumiho::SpaceResponse& response, Client* client);

    /**
     * @brief Get the space's full path.
     * @return The full path (e.g., "/project/assets/models").
     */
    std::string getPath() const;

    /**
     * @brief Get the space's Kref.
     * @return A Kref containing the space path.
     */
    Kref getKref() const;

    /**
     * @brief Get the space's name (last component of path).
     * @return The space name.
     */
    std::string getName() const;

    /**
     * @brief Get the space's type.
     * @return "root" for project-level, "sub" for nested spaces.
     */
    std::string getType() const;

    /**
     * @brief Get the space's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the space was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the space.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the space creator.
     */
    std::string getUsername() const;

    /**
     * @brief Create a sub-space.
     * @param name The name of the new space.
     * @return The created Space.
     */
    std::shared_ptr<Space> createSpace(const std::string& name);

    /**
     * @brief Create an item in this space.
     *
     * @param name The item name.
     * @param kind The item kind (e.g., "model", "texture").
     * @return The created Item.
     * @throws ReservedKindError if kind is reserved (e.g., "bundle").
     */
    std::shared_ptr<Item> createItem(const std::string& name, const std::string& kind);

    /**
     * @brief Get an item by name and kind.
     * @param name The item name.
     * @param kind The item kind.
     * @return The Item.
     */
    std::shared_ptr<Item> getItem(const std::string& name, const std::string& kind);

    /**
     * @brief Get all items in this space.
     * @param name_filter Optional filter by item name (supports wildcards).
     * @param kind_filter Optional filter by item kind.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @param include_deprecated Whether to include deprecated items.
     * @return A PagedList of Item objects.
     */
    PagedList<std::shared_ptr<Item>> getItems(
        const std::string& name_filter = "",
        const std::string& kind_filter = "",
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt,
        bool include_deprecated = false
    );

    /**
     * @brief Set or update metadata for this space.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Space.
     */
    std::shared_ptr<Space> setMetadata(const Metadata& metadata);

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
     * @brief Delete this space.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteSpace(bool force = false);

    /**
     * @brief Get the parent space.
     * @return The parent Space, or nullptr if this is a root space.
     */
    std::shared_ptr<Space> getParentSpace();

    /**
     * @brief Get child spaces.
     * @return A list of child Space objects.
     */
    std::vector<std::shared_ptr<Space>> getChildSpaces();

    /**
     * @brief Get the parent project.
     * @return The Project containing this space.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Create a bundle in this space.
     * @param name The bundle name.
     * @return The created Bundle.
     */
    std::shared_ptr<Bundle> createBundle(const std::string& name);

    /**
     * @brief Get a bundle by name.
     * @param name The bundle name.
     * @return The Bundle.
     */
    std::shared_ptr<Bundle> getBundle(const std::string& name);

private:
    ::kumiho::SpaceResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
