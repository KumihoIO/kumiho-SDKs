/**
 * @file space.cpp
 * @brief Implementation of Space class.
 */

#include "kumiho/space.hpp"
#include "kumiho/client.hpp"
#include "kumiho/item.hpp"
#include "kumiho/project.hpp"
#include "kumiho/bundle.hpp"
#include "kumiho/error.hpp"
#include <sstream>

namespace kumiho {
namespace api {

Space::Space(const ::kumiho::SpaceResponse& response, Client* client)
    : response_(response), client_(client) {}

std::string Space::getPath() const {
    return response_.path();
}

Kref Space::getKref() const {
    return Kref("kref://" + response_.path().substr(1)); // Remove leading /
}

std::string Space::getName() const {
    return response_.name();
}

std::string Space::getType() const {
    return response_.type();
}

Metadata Space::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Space::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Space::getAuthor() const {
    return response_.author();
}

std::string Space::getUsername() const {
    return response_.username();
}

std::shared_ptr<Space> Space::createSpace(const std::string& name) {
    return client_->createSpace(response_.path(), name);
}

std::shared_ptr<Item> Space::createItem(const std::string& name, const std::string& kind) {
    if (isReservedKind(kind)) {
        throw ReservedKindError(
            "Kind '" + kind + "' is reserved. Use createBundle() instead."
        );
    }
    return client_->createItem(response_.path(), name, kind);
}

std::shared_ptr<Item> Space::getItem(const std::string& name, const std::string& kind) {
    return client_->getItem(response_.path(), name, kind);
}

PagedList<std::shared_ptr<Item>> Space::getItems(
    const std::string& name_filter,
    const std::string& kind_filter,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor,
    bool include_deprecated
) {
    // Note: Space::getItems uses itemSearch internally in Python SDK too, 
    // but here we should probably use getItems on client if it existed, 
    // or itemSearch with context.
    // The original code used client_->itemSearch(response_.path(), ...)
    return client_->itemSearch(response_.path(), name_filter, kind_filter, page_size, cursor, include_deprecated);
}

std::shared_ptr<Space> Space::setMetadata(const Metadata& metadata) {
    return client_->updateSpaceMetadata(getKref(), metadata);
}

std::optional<std::string> Space::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Space::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Space::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Space::deleteSpace(bool force) {
    client_->deleteSpace(response_.path(), force);
}

std::shared_ptr<Space> Space::getParentSpace() {
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
        return nullptr;  // This is a root-level space
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
    
    return client_->getSpace(parent_path);
}

std::vector<std::shared_ptr<Space>> Space::getChildSpaces() {
    return client_->getChildSpaces(response_.path());
}

std::shared_ptr<Project> Space::getProject() {
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

std::shared_ptr<Bundle> Space::createBundle(const std::string& name) {
    return client_->createBundle(response_.path(), name);
}

std::shared_ptr<Bundle> Space::getBundle(const std::string& name) {
    return client_->getBundle(response_.path(), name);
}

} // namespace api
} // namespace kumiho
