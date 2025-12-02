/**
 * @file project.cpp
 * @brief Implementation of Project class.
 */

#include "kumiho/project.hpp"
#include "kumiho/client.hpp"
#include "kumiho/group.hpp"
#include "kumiho/collection.hpp"
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

std::shared_ptr<Group> Project::createGroup(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->createGroup(parent_path, name);
}

std::shared_ptr<Group> Project::getGroup(const std::string& path) {
    std::string full_path = "/" + response_.name() + "/" + path;
    return client_->getGroup(full_path);
}

std::vector<std::shared_ptr<Group>> Project::getGroups(bool recursive) {
    std::string parent_path = "/" + response_.name();
    // TODO: Add recursive parameter support
    return client_->getChildGroups(parent_path);
}

std::shared_ptr<Collection> Project::createCollection(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->createCollection(parent_path, name);
}

std::shared_ptr<Collection> Project::getCollection(const std::string& name) {
    std::string parent_path = "/" + response_.name();
    return client_->getCollection(parent_path, name);
}

std::shared_ptr<Project> Project::setPublic(bool allow) {
    return client_->updateProject(response_.project_id(), allow, std::nullopt);
}

std::shared_ptr<Project> Project::update(const std::string& description) {
    return client_->updateProject(response_.project_id(), std::nullopt, description);
}

void Project::deleteProject(bool force) {
    client_->deleteProject(response_.project_id(), force);
}

} // namespace api
} // namespace kumiho
