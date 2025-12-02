/**
 * @file collection.cpp
 * @brief Implementation of Collection class.
 */

#include "kumiho/collection.hpp"
#include "kumiho/client.hpp"
#include "kumiho/error.hpp"

namespace kumiho {
namespace api {

Collection::Collection(const ::kumiho::ProductResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Collection::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Collection::getName() const {
    return response_.product_name();
}

Metadata Collection::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Collection::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Collection::getAuthor() const {
    return response_.author();
}

std::string Collection::getUsername() const {
    return response_.username();
}

bool Collection::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Collection> Collection::addMember(const std::shared_ptr<Product>& product) {
    return addMember(product->getKref());
}

std::shared_ptr<Collection> Collection::addMember(const Kref& product_kref) {
    client_->addCollectionMember(getKref(), product_kref);
    // Return refreshed collection
    // TODO: Implement proper refresh
    return std::make_shared<Collection>(response_, client_);
}

std::shared_ptr<Collection> Collection::removeMember(const std::shared_ptr<Product>& product) {
    return removeMember(product->getKref());
}

std::shared_ptr<Collection> Collection::removeMember(const Kref& product_kref) {
    client_->removeCollectionMember(getKref(), product_kref);
    // Return refreshed collection
    return std::make_shared<Collection>(response_, client_);
}

std::vector<CollectionMember> Collection::getMembers() {
    return client_->getCollectionMembers(getKref());
}

std::vector<CollectionVersionHistory> Collection::getHistory() {
    return client_->getCollectionHistory(getKref());
}

void Collection::deleteCollection(bool force) {
    Kref kref = getKref();
    client_->deleteProduct(kref, force);
}

} // namespace api
} // namespace kumiho
