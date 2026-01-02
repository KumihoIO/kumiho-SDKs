/**
 * @file project.hpp
 * @brief Project entity - the top-level container for assets.
 *
 * Projects are the root of the Kumiho hierarchy. Each project has its own
 * namespace for groups and products, and manages access control and settings
 * independently.
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

// Forward declarations - use new terminology (aliases defined in types.hpp)
class Client;
class Space;
class Bundle;

/**
 * @brief A Kumiho project—the top-level container for assets.
 *
 * Projects are the root of the Kumiho hierarchy. Each project has its own
 * namespace for spaces and items, and manages access control and settings
 * independently.
 *
 * Projects support both public and private access modes, allowing you to
 * share assets publicly or restrict them to authenticated users.
 *
 * Example:
 * @code
 *   auto project = client->createProject("film-2024", "Feature film VFX assets");
 *   
 *   // Create space structure
 *   auto chars = project->createSpace("characters");
 *   auto envs = project->createSpace("environments");
 *   
 *   // List all spaces recursively
 *   for (const auto& space : project->getSpaces(true)) {
 *       std::cout << space->getPath() << std::endl;
 *   }
 *   
 *   // Enable public access
 *   project->setPublic(true);
 * @endcode
 */
class Project {
public:
    /**
     * @brief Construct a Project from a protobuf response.
     * @param response The protobuf ProjectResponse message.
     * @param client The client for making API calls.
     */
    Project(const ::kumiho::ProjectResponse& response, Client* client);

    /**
     * @brief Get the project's unique ID.
     * @return The project UUID.
     */
    std::string getProjectId() const;

    /**
     * @brief Get the project's URL-safe name.
     * @return The project name (e.g., "film-2024").
     */
    std::string getName() const;

    /**
     * @brief Get the project's Kref.
     * @return A Kref for this project.
     */
    Kref getKref() const;

    /**
     * @brief Get the project's description.
     * @return The human-readable description.
     */
    std::string getDescription() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the project was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the last update timestamp.
     * @return ISO timestamp of the last update, or nullopt.
     */
    std::optional<std::string> getUpdatedAt() const;

    /**
     * @brief Check if the project is deprecated.
     * @return True if deprecated (soft-deleted), false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Check if public access is allowed.
     * @return True if anonymous read access is enabled.
     */
    bool isPublic() const;

    /**
     * @brief Create a space in this project.
     * @param name The space name.
     * @return The created Space.
     */
    std::shared_ptr<Space> createSpace(const std::string& name);

    /**
     * @brief Get a space by path.
     * @param path The space path relative to the project (e.g., "assets/models").
     * @return The Space.
     */
    std::shared_ptr<Space> getSpace(const std::string& path);

    /**
     * @brief Get all spaces in this project.
     * @param recursive If true, include all descendant spaces.
     * @return A list of Space objects.
     */
    std::vector<std::shared_ptr<Space>> getSpaces(bool recursive = false);

    /**
     * @brief Search for items within this project.
     * @param name_filter Filter by item name. Supports wildcards.
     * @param kind_filter Filter by item kind.
     * @param page_size Optional page size for pagination.
     * @param cursor Optional cursor for pagination.
     * @return A PagedList of Item objects.
     */
    PagedList<std::shared_ptr<Item>> getItems(
        const std::string& name_filter = "",
        const std::string& kind_filter = "",
        std::optional<int32_t> page_size = std::nullopt,
        std::optional<std::string> cursor = std::nullopt
    );

    /**
     * @brief Create a bundle in this project.
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

    /**
     * @brief Set public access mode.
     * @param allow True to enable public access, false to restrict.
     * @return The updated Project.
     */
    std::shared_ptr<Project> setPublic(bool allow);

    /**
     * @brief Alias for setPublic() using the allow_public terminology.
     * @param allow_public True to enable public access, false to restrict.
     * @return The updated Project.
     */
    std::shared_ptr<Project> setAllowPublic(bool allow_public);

    /**
     * @brief Update the project's description.
     * @param description The new description.
     * @return The updated Project.
     */
    std::shared_ptr<Project> update(const std::string& description);

    /**
     * @brief Delete this project.
     * @param force If true, permanently delete. If false, soft delete (deprecate).
     */
    void deleteProject(bool force = false);

private:
    ::kumiho::ProjectResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
