/**
 * @file item.hpp
 * @brief Item entity representing versioned assets.
 *
 * Items represent assets that can have multiple revisions, such as 3D models,
 * textures, workflows, or any other type of creative content. Each item
 * belongs to a space and is identified by a combination of name and kind.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <chrono>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Revision;
class Space;
class Project;

/**
 * @brief A versioned asset in the Kumiho system.
 *
 * Items represent assets that can have multiple revisions. Each item
 * belongs to a space and is identified by a combination of name and kind.
 *
 * The item's kref (Kumiho Reference) is a URI that uniquely identifies it:
 * `kref://project/space/item.kind`
 *
 * Example:
 * @code
 *   auto item = space->createItem("hero", "model");
 *   
 *   // Create revisions
 *   auto v1 = item->createRevision();
 *   auto v2 = item->createRevision({{"notes", "Updated mesh"}});
 *   
 *   // Get specific revision
 *   auto v1 = item->getRevision(1);
 *   auto latest = item->getLatestRevision();
 *   
 *   // Get revision by tag
 *   auto approved = item->getRevisionByTag("approved");
 * @endcode
 */
class Item {
public:
    /**
     * @brief Construct an Item from a protobuf response.
     * @param response The protobuf ItemResponse message.
     * @param client The client for making API calls.
     */
    Item(const ::kumiho::ItemResponse& response, Client* client);

    /**
     * @brief Get the item's unique Kref.
     * @return The Kref URI for this item.
     */
    Kref getKref() const;

    /**
     * @brief Get the full name including kind.
     * @return The full item name (e.g., "hero.model").
     */
    std::string getName() const;

    /**
     * @brief Get the base item name.
     * @return The item name without kind (e.g., "hero").
     */
    std::string getItemName() const;

    /**
     * @brief Get the item kind.
     * @return The item kind (e.g., "model", "texture").
     */
    std::string getKind() const;

    /**
     * @brief Get the item's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the item was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the item.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the item creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the item is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Create a new revision of this item.
     *
     * Revisions are automatically numbered sequentially. Each revision starts
     * with the "latest" tag, which moves to the newest revision.
     *
     * @param metadata Optional metadata for the revision.
     * @return The created Revision.
     */
    std::shared_ptr<Revision> createRevision(const Metadata& metadata = {});

    /**
     * @brief Get a specific revision by number.
     * @param revision_number The revision number (1-based).
     * @return The Revision.
     */
    std::shared_ptr<Revision> getRevision(int revision_number);

    /**
     * @brief Get all revisions of this item.
     * @return A list of Revision objects, ordered by revision number.
     */
    std::vector<std::shared_ptr<Revision>> getRevisions();

    /**
     * @brief Get a revision by tag.
     * @param tag The tag to search for.
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> getRevisionByTag(const std::string& tag);

    /**
     * @brief Get a revision by creation time.
     * 
     * @param time The time in one of these formats:
     *             - YYYYMMDDHHMM (e.g., "202406011330")
     *             - ISO 8601 (e.g., "2024-06-01T13:30:00Z")
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> getRevisionByTime(const std::string& time);

    /**
     * @brief Get a revision by creation time using std::chrono.
     * 
     * @param time_point The time as a std::chrono::system_clock::time_point.
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> getRevisionByTime(std::chrono::system_clock::time_point time_point);

    /**
     * @brief Get a revision by both tag and time.
     *
     * This finds the revision that had the specified tag at the specified time.
     * Useful for reconstructing historical states and reproducible builds.
     * 
     * Example:
     * @code
     *   // Get the "published" revision as of June 1st, 2024
     *   auto rev = item->getRevisionByTagAndTime("published", "202406010000");
     *   
     *   // Using ISO 8601 format
     *   auto rev = item->getRevisionByTagAndTime("published", "2024-06-01T00:00:00Z");
     * @endcode
     *
     * @param tag The tag to search for (e.g., "published", "approved").
     * @param time The time in YYYYMMDDHHMM or ISO 8601 format.
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> getRevisionByTagAndTime(const std::string& tag, const std::string& time);

    /**
     * @brief Get a revision by both tag and time using std::chrono.
     *
     * @param tag The tag to search for.
     * @param time_point The time as a std::chrono::system_clock::time_point.
     * @return The Revision, or nullptr if not found.
     */
    std::shared_ptr<Revision> getRevisionByTagAndTime(const std::string& tag, std::chrono::system_clock::time_point time_point);

    /**
     * @brief Get the latest revision.
     * @return The latest Revision, or nullptr if no revisions exist.
     */
    std::shared_ptr<Revision> getLatestRevision();

    /**
     * @brief Peek at the next revision number.
     * @return The next revision number that would be assigned.
     */
    int peekNextRevision();

    /**
     * @brief Set or update metadata for this item.
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Item.
     */
    std::shared_ptr<Item> setMetadata(const Metadata& metadata);

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
     * @brief Delete this item.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteItem(bool force = false);

    /**
     * @brief Get the parent space.
     * @return The Space containing this item.
     */
    std::shared_ptr<Space> getSpace();

    /**
     * @brief Get the parent project.
     * @return The Project containing this item.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     */
    void setDeprecated(bool deprecated);

    /**
     * @brief Refresh this item's data from the server.
     * @return The refreshed Item.
     */
    std::shared_ptr<Item> refresh();

private:
    ::kumiho::ItemResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
