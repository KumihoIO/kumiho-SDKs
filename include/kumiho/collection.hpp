/**
 * @file collection.hpp
 * @brief Collection entity for aggregating products.
 *
 * Collections are special products that aggregate other products. They
 * maintain an audit trail of membership changes through versioning.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho/product.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;

/**
 * @brief A product that is a member of a collection.
 *
 * Represents the membership relationship between a product and a collection,
 * including metadata about when and by whom the product was added.
 */
struct CollectionMember {
    /** @brief The kref of the member product. */
    Kref product_kref;
    
    /** @brief ISO timestamp when the product was added. */
    std::string added_at;
    
    /** @brief UUID of the user who added the product. */
    std::string added_by;
    
    /** @brief Display name of the user who added the product. */
    std::string added_by_username;
    
    /** @brief The collection version when this product was added. */
    int added_in_version;
};

/**
 * @brief A historical change to a collection's membership.
 *
 * Each entry captures a single add or remove operation, providing
 * an immutable audit trail of all membership changes.
 */
struct CollectionVersionHistory {
    /** @brief The collection version number for this change. */
    int version_number;
    
    /** @brief The action performed: "CREATED", "ADDED", or "REMOVED". */
    std::string action;
    
    /** @brief The product that was added/removed (null for CREATED). */
    std::optional<Kref> member_product_kref;
    
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
 * @brief A product that aggregates other products.
 *
 * Collections are special products (with type "collection") that can
 * contain references to other products. Each membership change creates
 * a new version, providing an immutable audit trail.
 *
 * Note: The "collection" product type is reserved and cannot be created
 * via createProduct(). Use createCollection() instead.
 *
 * Example:
 * @code
 *   // Create a collection
 *   auto bundle = project->createCollection("asset-bundle");
 *   
 *   // Add products
 *   auto hero_model = client->getProduct("kref://project/models/hero.model");
 *   bundle->addMember(hero_model);
 *   
 *   // Get all members
 *   for (const auto& member : bundle->getMembers()) {
 *       std::cout << "Product: " << member.product_kref.uri() << std::endl;
 *   }
 *   
 *   // View audit history
 *   for (const auto& entry : bundle->getHistory()) {
 *       std::cout << "v" << entry.version_number << ": " 
 *                 << entry.action << std::endl;
 *   }
 * @endcode
 */
class Collection {
public:
    /**
     * @brief Construct a Collection from a protobuf response.
     * @param response The protobuf ProductResponse message.
     * @param client The client for making API calls.
     */
    Collection(const ::kumiho::ProductResponse& response, Client* client);

    /**
     * @brief Get the collection's unique Kref.
     * @return The Kref URI for this collection.
     */
    Kref getKref() const;

    /**
     * @brief Get the collection name.
     * @return The collection name (without type).
     */
    std::string getName() const;

    /**
     * @brief Get the collection's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the collection was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the collection.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the collection creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the collection is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Add a product to this collection.
     *
     * Creates a new version of the collection with the membership change.
     *
     * @param product The product to add.
     * @return The updated Collection.
     */
    std::shared_ptr<Collection> addMember(const std::shared_ptr<Product>& product);

    /**
     * @brief Add a product to this collection by Kref.
     * @param product_kref The kref of the product to add.
     * @return The updated Collection.
     */
    std::shared_ptr<Collection> addMember(const Kref& product_kref);

    /**
     * @brief Remove a product from this collection.
     *
     * Creates a new version of the collection with the membership change.
     *
     * @param product The product to remove.
     * @return The updated Collection.
     */
    std::shared_ptr<Collection> removeMember(const std::shared_ptr<Product>& product);

    /**
     * @brief Remove a product from this collection by Kref.
     * @param product_kref The kref of the product to remove.
     * @return The updated Collection.
     */
    std::shared_ptr<Collection> removeMember(const Kref& product_kref);

    /**
     * @brief Get all current members of this collection.
     * @return A list of CollectionMember objects.
     */
    std::vector<CollectionMember> getMembers();

    /**
     * @brief Get the membership change history.
     *
     * Returns all historical changes to the collection's membership,
     * providing an immutable audit trail.
     *
     * @return A list of CollectionVersionHistory objects.
     */
    std::vector<CollectionVersionHistory> getHistory();

    /**
     * @brief Delete this collection.
     * @param force If true, permanently delete. If false, soft delete.
     */
    void deleteCollection(bool force = false);

private:
    ::kumiho::ProductResponse response_;
    Client* client_;
};

} // namespace api
} // namespace kumiho
