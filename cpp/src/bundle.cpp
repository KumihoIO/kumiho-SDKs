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

BundleMemberResult Bundle::addMember(const std::shared_ptr<Item>& item, const Metadata& metadata) {
    return addMember(item->getKref(), metadata);
}

BundleMemberResult Bundle::addMember(const Kref& item_kref, const Metadata& metadata) {
    return client_->addBundleMember(getKref(), item_kref, metadata);
}

BundleMemberResult Bundle::removeMember(const std::shared_ptr<Item>& item, const Metadata& metadata) {
    return removeMember(item->getKref(), metadata);
}

BundleMemberResult Bundle::removeMember(const Kref& item_kref, const Metadata& metadata) {
    return client_->removeBundleMember(getKref(), item_kref, metadata);
}

std::vector<BundleMember> Bundle::getMembers(int revision_number) {
    return client_->getBundleMembers(getKref(), revision_number);
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
