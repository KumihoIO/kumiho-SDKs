/**
 * @file resource.cpp
 * @brief Implementation of Resource class.
 */

#include "kumiho/resource.hpp"
#include "kumiho/client.hpp"
#include "kumiho/version.hpp"
#include "kumiho/product.hpp"
#include "kumiho/group.hpp"
#include "kumiho/project.hpp"
#include "kumiho/error.hpp"

namespace kumiho {
namespace api {

Resource::Resource(const ::kumiho::ResourceResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Resource::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Resource::getName() const {
    return response_.name();
}

std::string Resource::getLocation() const {
    return response_.location();
}

Kref Resource::getVersionKref() const {
    return Kref(response_.version_kref().uri());
}

Kref Resource::getProductKref() const {
    return Kref(response_.product_kref().uri());
}

Metadata Resource::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Resource::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Resource::getAuthor() const {
    return response_.author();
}

std::string Resource::getUsername() const {
    return response_.username();
}

bool Resource::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Resource> Resource::setMetadata(const Metadata& metadata) {
    return client_->updateResourceMetadata(getKref(), metadata);
}

std::optional<std::string> Resource::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Resource::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Resource::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Resource::deleteResource(bool force) {
    client_->deleteResource(getKref(), force);
}

std::shared_ptr<Version> Resource::getVersion() {
    return client_->getVersion(getVersionKref().uri());
}

std::shared_ptr<Product> Resource::getProduct() {
    return client_->getProductByKref(getProductKref().uri());
}

std::shared_ptr<Group> Resource::getGroup() {
    std::string group_path = "/" + getProductKref().getGroup();
    return client_->getGroup(group_path);
}

std::shared_ptr<Project> Resource::getProject() {
    return getGroup()->getProject();
}

void Resource::setDefault() {
    client_->setDefaultResource(getVersionKref(), getName());
}

std::shared_ptr<Resource> Resource::setDeprecated(bool deprecated) {
    client_->setResourceDeprecated(getKref(), deprecated);
    // Refresh and return updated resource
    return client_->getResource(getVersionKref(), getName());
}

} // namespace api
} // namespace kumiho
