/**
 * @file group.cpp
 * @brief Implementation of Group class.
 */

#include "kumiho/group.hpp"
#include "kumiho/client.hpp"
#include "kumiho/product.hpp"
#include "kumiho/project.hpp"
#include "kumiho/collection.hpp"
#include "kumiho/error.hpp"
#include <sstream>

namespace kumiho {
namespace api {

Group::Group(const ::kumiho::GroupResponse& response, Client* client)
    : response_(response), client_(client) {}

std::string Group::getPath() const {
    return response_.path();
}

Kref Group::getKref() const {
    return Kref("kref://" + response_.path().substr(1)); // Remove leading /
}

std::string Group::getName() const {
    return response_.name();
}

std::string Group::getType() const {
    return response_.type();
}

Metadata Group::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Group::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Group::getAuthor() const {
    return response_.author();
}

std::string Group::getUsername() const {
    return response_.username();
}

std::shared_ptr<Group> Group::createGroup(const std::string& name) {
    return client_->createGroup(response_.path(), name);
}

std::shared_ptr<Product> Group::createProduct(const std::string& name, const std::string& ptype) {
    if (isReservedProductType(ptype)) {
        throw ReservedProductTypeError(
            "Product type '" + ptype + "' is reserved. Use createCollection() instead."
        );
    }
    return client_->createProduct(response_.path(), name, ptype);
}

std::shared_ptr<Product> Group::getProduct(const std::string& name, const std::string& ptype) {
    return client_->getProduct(response_.path(), name, ptype);
}

std::vector<std::shared_ptr<Product>> Group::getProducts(
    const std::string& name_filter,
    const std::string& ptype_filter
) {
    return client_->productSearch(response_.path(), name_filter, ptype_filter);
}

std::shared_ptr<Group> Group::setMetadata(const Metadata& metadata) {
    return client_->updateGroupMetadata(getKref(), metadata);
}

std::optional<std::string> Group::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Group::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Group::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Group::deleteGroup(bool force) {
    client_->deleteGroup(response_.path(), force);
}

std::shared_ptr<Group> Group::getParentGroup() {
    std::string path = response_.path();
    if (path == "/") {
        return nullptr;
    }
    
    // Split path and remove empty strings
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string part;
    while (std::getline(ss, part, '/')) {
        if (!part.empty()) {
            parts.push_back(part);
        }
    }
    
    if (parts.size() <= 1) {
        return nullptr;  // This is a root-level group
    }
    
    // Remove the last component to get parent path
    parts.pop_back();
    
    std::string parent_path;
    if (parts.empty()) {
        parent_path = "/";
    } else {
        parent_path = "/";
        for (size_t i = 0; i < parts.size(); ++i) {
            if (i > 0) parent_path += "/";
            parent_path += parts[i];
        }
    }
    
    return client_->getGroup(parent_path);
}

std::vector<std::shared_ptr<Group>> Group::getChildGroups() {
    return client_->getChildGroups(response_.path());
}

std::shared_ptr<Project> Group::getProject() {
    // Extract project name from path
    std::string path = response_.path();
    size_t first_slash = path.find('/', 1);  // Skip leading /
    std::string project_name;
    if (first_slash == std::string::npos) {
        project_name = path.substr(1);  // Entire path minus leading /
    } else {
        project_name = path.substr(1, first_slash - 1);
    }
    return client_->getProject(project_name);
}

std::shared_ptr<Collection> Group::createCollection(const std::string& name) {
    return client_->createCollection(response_.path(), name);
}

std::shared_ptr<Collection> Group::getCollection(const std::string& name) {
    return client_->getCollection(response_.path(), name);
}

} // namespace api
} // namespace kumiho
