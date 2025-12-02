/**
 * @file product.cpp
 * @brief Implementation of Product class.
 */

#include "kumiho/product.hpp"
#include "kumiho/client.hpp"
#include "kumiho/version.hpp"
#include "kumiho/group.hpp"
#include "kumiho/project.hpp"
#include "kumiho/error.hpp"
#include <algorithm>

namespace kumiho {
namespace api {

Product::Product(const ::kumiho::ProductResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Product::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Product::getName() const {
    return response_.name();
}

std::string Product::getProductName() const {
    return response_.product_name();
}

std::string Product::getProductType() const {
    return response_.product_type();
}

Metadata Product::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Product::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Product::getAuthor() const {
    return response_.author();
}

std::string Product::getUsername() const {
    return response_.username();
}

bool Product::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Version> Product::createVersion(const Metadata& metadata) {
    return client_->createVersion(getKref(), metadata);
}

std::shared_ptr<Version> Product::getVersion(int version_number) {
    std::string kref_uri = getKref().uri() + "?v=" + std::to_string(version_number);
    return client_->getVersion(kref_uri);
}

std::vector<std::shared_ptr<Version>> Product::getVersions() {
    return client_->getVersions(getKref());
}

std::shared_ptr<Version> Product::getVersionByTag(const std::string& tag) {
    return client_->resolveKref(getKref().uri(), tag, "");
}

std::shared_ptr<Version> Product::getVersionByTime(const std::string& time) {
    return client_->resolveKref(getKref().uri(), "", time);
}

std::shared_ptr<Version> Product::getLatestVersion() {
    auto versions = getVersions();
    if (versions.empty()) {
        return nullptr;
    }
    
    // Find versions marked as latest
    for (const auto& version : versions) {
        if (version->isLatest()) {
            return version;
        }
    }
    
    // Fallback to highest version number
    return *std::max_element(versions.begin(), versions.end(),
        [](const std::shared_ptr<Version>& a, const std::shared_ptr<Version>& b) {
            return a->getVersionNumber() < b->getVersionNumber();
        });
}

int Product::peekNextVersion() {
    return client_->peekNextVersion(getKref());
}

std::shared_ptr<Product> Product::setMetadata(const Metadata& metadata) {
    return client_->updateProductMetadata(getKref(), metadata);
}

std::optional<std::string> Product::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Product::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Product::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Product::deleteProduct(bool force) {
    client_->deleteProduct(getKref(), force);
}

std::shared_ptr<Group> Product::getGroup() {
    std::string group_path = "/" + getKref().getGroup();
    return client_->getGroup(group_path);
}

std::shared_ptr<Project> Product::getProject() {
    return getGroup()->getProject();
}

void Product::setDeprecated(bool deprecated) {
    client_->setProductDeprecated(getKref(), deprecated);
}

std::shared_ptr<Product> Product::refresh() {
    return client_->getProductByKref(getKref().uri());
}

} // namespace api
} // namespace kumiho
