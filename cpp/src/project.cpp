/**
 * @file project.cpp
 * @brief Implementation of Project class.
 */

#include "kumiho/project.hpp"
#include "kumiho/client.hpp"
#include "kumiho/space.hpp"
#include "kumiho/bundle.hpp"
#include "kumiho/error.hpp"

namespace kumiho {
namespace api {

Project::Project(const ::kumiho::ProjectResponse& response, Client* client)
    : response_(response), client_(client) {}

std::string Project::getProjectId() const {
    return response_.project_id();
}

std::string Project::getName() const {
    return response_.name();
}

Kref Project::getKref() const {
    return Kref("kref://" + response_.name());
}

std::string Project::getDescription() const {
    return response_.description();
}

std::optional<std::string> Project::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::optional<std::string> Project::getUpdatedAt() const {
    if (!response_.updated_at().empty()) {
        return response_.updated_at();
    }
    return std::nullopt;
}

bool Project::isDeprecated() const {
    return response_.deprecated();
}

bool Project::isPublic() const {
    return response_.allow_public();
}

std::shared_ptr<Space> Project::createSpace(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->createSpace(parent_path, name);
}

std::shared_ptr<Space> Project::getSpace(const std::string& path) {
    std::string full_path = "/" + response_.name() + "/" + path;
    return client_->getSpace(full_path);
}

std::vector<std::shared_ptr<Space>> Project::getSpaces(bool recursive) {
    std::string parent_path = "/" + response_.name();
    // TODO: Add recursive parameter support
    return client_->getChildSpaces(parent_path);
}

PagedList<std::shared_ptr<Item>> Project::getItems(
    const std::string& name_filter,
    const std::string& kind_filter,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor
) {
    return client_->itemSearch(response_.name(), name_filter, kind_filter, page_size, cursor);
}

std::shared_ptr<Bundle> Project::createBundle(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->createBundle(parent_path, name);
}

std::shared_ptr<Bundle> Project::getBundle(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->getBundle(parent_path, name);
}

std::shared_ptr<Project> Project::setPublic(bool allow) {
    return client_->updateProject(response_.project_id(), allow, std::nullopt);
}

std::shared_ptr<Project> Project::setAllowPublic(bool allow_public) {
    return setPublic(allow_public);
}

std::shared_ptr<Project> Project::update(const std::string& description) {
    return client_->updateProject(response_.project_id(), std::nullopt, description);
}

void Project::deleteProject(bool force) {
    client_->deleteProject(response_.project_id(), force);
}

} // namespace api
} // namespace kumiho
