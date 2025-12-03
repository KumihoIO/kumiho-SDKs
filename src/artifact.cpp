/**
 * @file artifact.cpp
 * @brief Implementation of Artifact class.
 */

#include "kumiho/artifact.hpp"
#include "kumiho/client.hpp"
#include "kumiho/revision.hpp"
#include "kumiho/item.hpp"
#include "kumiho/space.hpp"
#include "kumiho/project.hpp"
#include "kumiho/error.hpp"

namespace kumiho {
namespace api {

Artifact::Artifact(const ::kumiho::ArtifactResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Artifact::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Artifact::getName() const {
    return response_.name();
}

std::string Artifact::getLocation() const {
    return response_.location();
}

Kref Artifact::getRevisionKref() const {
    return Kref(response_.revision_kref().uri());
}

Kref Artifact::getItemKref() const {
    return Kref(response_.item_kref().uri());
}

Metadata Artifact::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Artifact::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Artifact::getAuthor() const {
    return response_.author();
}

std::string Artifact::getUsername() const {
    return response_.username();
}

bool Artifact::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Artifact> Artifact::setMetadata(const Metadata& metadata) {
    return client_->updateArtifactMetadata(getKref(), metadata);
}

std::optional<std::string> Artifact::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Artifact::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Artifact::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Artifact::deleteArtifact(bool force) {
    client_->deleteArtifact(getKref(), force);
}

std::shared_ptr<Revision> Artifact::getRevision() {
    return client_->getRevision(getRevisionKref().uri());
}

std::shared_ptr<Item> Artifact::getItem() {
    return client_->getItemByKref(getItemKref().uri());
}

std::shared_ptr<Space> Artifact::getSpace() {
    std::string space_path = "/" + getItemKref().getSpace();
    return client_->getSpace(space_path);
}

std::shared_ptr<Project> Artifact::getProject() {
    return getSpace()->getProject();
}

void Artifact::setDefault() {
    client_->setDefaultArtifact(getRevisionKref(), getName());
}

std::shared_ptr<Artifact> Artifact::setDeprecated(bool deprecated) {
    client_->setArtifactDeprecated(getKref(), deprecated);
    // Refresh and return updated artifact
    return client_->getArtifact(getRevisionKref(), getName());
}

// Backwards compatibility aliases
Kref Artifact::getVersionKref() const {
    return getRevisionKref();
}

Kref Artifact::getProductKref() const {
    return getItemKref();
}

void Artifact::deleteResource(bool force) {
    deleteArtifact(force);
}

std::shared_ptr<Revision> Artifact::getVersion() {
    return getRevision();
}

std::shared_ptr<Item> Artifact::getProduct() {
    return getItem();
}

std::shared_ptr<Space> Artifact::getGroup() {
    return getSpace();
}

} // namespace api
} // namespace kumiho
