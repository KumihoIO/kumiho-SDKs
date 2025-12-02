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

// Forward declarations
class Client;
class Group;
class Collection;

/**
 * @brief A Kumiho project—the top-level container for assets.
 *
 * Projects are the root of the Kumiho hierarchy. Each project has its own
 * namespace for groups and products, and manages access control and settings
 * independently.
 *
 * Projects support both public and private access modes, allowing you to
 * share assets publicly or restrict them to authenticated users.
 *
 * Example:
 * @code
 *   auto project = client->createProject("film-2024", "Feature film VFX assets");
 *   
 *   // Create group structure
 *   auto chars = project->createGroup("characters");
 *   auto envs = project->createGroup("environments");
 *   
 *   // List all groups recursively
 *   for (const auto& group : project->getGroups(true)) {
 *       std::cout << group->getPath() << std::endl;
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
     * @brief Create a group in this project.
     * @param name The group name.
     * @return The created Group.
     */
    std::shared_ptr<Group> createGroup(const std::string& name);

    /**
     * @brief Get a group by path.
     * @param path The group path relative to the project (e.g., "assets/models").
     * @return The Group.
     */
    std::shared_ptr<Group> getGroup(const std::string& path);

    /**
     * @brief Get all groups in this project.
     * @param recursive If true, include all descendant groups.
     * @return A list of Group objects.
     */
    std::vector<std::shared_ptr<Group>> getGroups(bool recursive = false);

    /**
     * @brief Create a collection in this project.
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

    /**
     * @brief Set public access mode.
     * @param allow True to enable public access, false to restrict.
     * @return The updated Project.
     */
    std::shared_ptr<Project> setPublic(bool allow);

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
