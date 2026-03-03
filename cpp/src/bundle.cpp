/**
 * @file bundle.cpp
 * @brief Implementation of Bundle class.
 */

#include "kumiho/bundle.hpp"
#include "kumiho/client.hpp"
#include "kumiho/error.hpp"

namespace kumiho {
namespace api {

Bundle::Bundle(const ::kumiho::ItemResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Bundle::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Bundle::getName() const {
    return response_.item_name();
}

Metadata Bundle::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Bundle::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Bundle::getAuthor() const {
    return response_.author();
}

std::string Bundle::getUsername() const {
    return response_.username();
}

bool Bundle::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Bundle> Bundle::addMember(const std::shared_ptr<Item>& item) {
    return addMember(item->getKref());
}

std::shared_ptr<Bundle> Bundle::addMember(const Kref& item_kref) {
    client_->addBundleMember(getKref(), item_kref);
    // Return refreshed bundle
    // TODO: Implement proper refresh
    return std::make_shared<Bundle>(response_, client_);
}

std::shared_ptr<Bundle> Bundle::removeMember(const std::shared_ptr<Item>& item) {
    return removeMember(item->getKref());
}

std::shared_ptr<Bundle> Bundle::removeMember(const Kref& item_kref) {
    client_->removeBundleMember(getKref(), item_kref);
    // Return refreshed bundle
    return std::make_shared<Bundle>(response_, client_);
}

std::vector<BundleMember> Bundle::getMembers() {
    return client_->getBundleMembers(getKref());
}

std::vector<BundleRevisionHistory> Bundle::getHistory() {
    return client_->getBundleHistory(getKref());
}

void Bundle::deleteBundle(bool force) {
    Kref kref = getKref();
    client_->deleteItem(kref, force);
}

} // namespace api
} // namespace kumiho
