/**
 * @file bundle.hpp
 * @brief Bundle entity for aggregating items.
 *
 * Bundles are special items that aggregate other items. They
 * maintain an audit trail of membership changes through revisioning.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/item.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;

/**
 * @brief An item that is a member of a bundle.
 *
 * Represents the membership relationship between an item and a bundle,
 * including metadata about when and by whom the item was added.
 */
struct BundleMember {
    /** @brief The kref of the member item. */
    Kref item_kref;
    
    /** @brief ISO timestamp when the item was added. */
    std::string added_at;
    
    /** @brief UUID of the user who added the item. */
    std::string added_by;
    
    /** @brief Display name of the user who added the item. */
    std::string added_by_username;
    
    /** @brief The bundle revision when this item was added. */
    int added_in_revision;
};

/**
 * @brief A historical change to a bundle's membership.
 *
 * Each entry captures a single add or remove operation, providing
 * an immutable audit trail of all membership changes.
 */
struct BundleRevisionHistory {
    /** @brief The bundle revision number for this change. */
    int revision_number;
    
    /** @brief The action performed: "CREATED", "ADDED", or "REMOVED". */
    std::string action;
    
    /** @brief The item that was added/removed (null for CREATED). */
    std::optional<Kref> member_item_kref;
    
    /** @brief UUID of the user who made the change. */
    std::string author;
    
    /** @brief Display name of the user who made the change. */
    std::string username;
    
    /** @brief ISO timestamp of the change. */
    std::string created_at;
    
    /** @brief Immutable metadata captured at the time of change. */
    Metadata metadata;
};

/**
 * @brief An item that aggregates other items.
 *
 * Bundles are special items (with kind "bundle") that can
 * contain references to other items. Each membership change creates
 * a new revision, providing an immutable audit trail.
 *
 * Note: The "bundle" item kind is reserved and cannot be created
 * via createItem(). Use createBundle() instead.
 *
 * Example:
 * @code
 *   // Create a bundle
 *   auto bundle = project->createBundle("asset-bundle");
 *   
 *   // Add items
 *   auto hero_model = client->getItem("kref://project/models/hero.model");
 *   bundle->addMember(hero_model);
 *   
 *   // Get all members
 *   for (const auto& member : bundle->getMembers()) {
 *       std::cout << "Item: " << member.item_kref.uri() << std::endl;
 *   }
 *   
 *   // View audit history
 *   for (const auto& entry : bundle->getHistory()) {
 *       std::cout << "v" << entry.revision_number << ": " 
 *                 << entry.action << std::endl;
 *   }
 * @endcode
 */
class Bundle {
public:
    /**
     * @brief Construct a Bundle from a protobuf response.
     * @param response The protobuf ItemResponse message.
     * @param client The client for making API calls.
     */
    Bundle(const ::kumiho::ItemResponse& response, Client* client);

    /**
     * @brief Get the bundle's unique Kref.
     * @return The Kref URI for this bundle.
     */
    Kref getKref() const;

    /**
     * @brief Get the bundle name.
     * @return The bundle name (without kind).
     */
    std::string getName() const;

    /**
     * @brief Get the bundle's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the bundle was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the bundle.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the bundle creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the bundle is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Add an item to this bundle.
     *
     * Creates a new revision of the bundle with the membership change.
     *
     * @param item The item to add.
     * @return The updated Bundle.
     */
    std::shared_ptr<Bundle> addMember(const std::shared_ptr<Item>& item);

    /**
     * @brief Add an item to this bundle by Kref.
     * @param item_kref The kref of the item to add.
     * @return The updated Bundle.
     */
    std::shared_ptr<Bundle> addMember(const Kref& item_kref);

    /**
     * @brief Remove an item from this bundle.
     *
     * Creates a new revision of the bundle with the membership change.
     *
     * @param item The item to remove.
     * @return The updated Bundle.
     */
    std::shared_ptr<Bundle> removeMember(const std::shared_ptr<Item>& item);

    /**
     * @brief Remove an item from this bundle by Kref.
     * @param item_kref The kref of the item to remove.
     * @return The updated Bundle.
     */
    std::shared_ptr<Bundle> removeMember(const Kref& item_kref);

    /**
     * @brief Get all current members of this bundle.
     * @return A list of BundleMember objects.
     */
    std::vector<BundleMember> getMembers();

    /**
     * @brief Get the membership change history.
     *
     * Returns all historical changes to the bundle's membership,
     * providing an immutable audit trail.
     *
     * @return A list of BundleRevisionHistory objects.
     */
    std::vector<BundleRevisionHistory> getHistory();

    /**
     * @brief Delete this bundle.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteBundle(bool force = false);

private:
    ::kumiho::ItemResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
