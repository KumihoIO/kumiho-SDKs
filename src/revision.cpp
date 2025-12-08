/**
 * @file revision.cpp
 * @brief Implementation of Revision class.
 */

#include "kumiho/revision.hpp"
#include "kumiho/client.hpp"
#include "kumiho/artifact.hpp"
#include "kumiho/item.hpp"
#include "kumiho/space.hpp"
#include "kumiho/project.hpp"
#include "kumiho/edge.hpp"
#include "kumiho/error.hpp"
#include <algorithm>

namespace kumiho {
namespace api {

Revision::Revision(const ::kumiho::RevisionResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Revision::getKref() const {
    return Kref(response_.kref().uri());
}

Kref Revision::getItemKref() const {
    return Kref(response_.item_kref().uri());
}

int Revision::getRevisionNumber() const {
    return response_.number();
}

std::vector<std::string> Revision::getTags() const {
    return {response_.tags().begin(), response_.tags().end()};
}

Metadata Revision::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Revision::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Revision::getAuthor() const {
    return response_.author();
}

std::string Revision::getUsername() const {
    return response_.username();
}

bool Revision::isLatest() const {
    return response_.latest();
}

bool Revision::isDeprecated() const {
    return response_.deprecated();
}

bool Revision::isPublished() const {
    return response_.published();
}

std::optional<std::string> Revision::getDefaultArtifact() const {
    if (!response_.default_artifact().empty()) {
        return response_.default_artifact();
    }
    return std::nullopt;
}

void Revision::setDefaultArtifact(const std::string& artifact_name) {
    client_->setDefaultArtifact(getKref(), artifact_name);
}

std::shared_ptr<Artifact> Revision::createArtifact(const std::string& name, const std::string& location) {
    return client_->createArtifact(getKref(), name, location);
}

std::shared_ptr<Artifact> Revision::getArtifact(const std::string& name) {
    return client_->getArtifact(getKref(), name);
}

std::vector<std::shared_ptr<Artifact>> Revision::getArtifacts() {
    return client_->getArtifacts(getKref());
}

std::vector<std::string> Revision::getLocations() {
    auto artifacts = getArtifacts();
    std::vector<std::string> locations;
    locations.reserve(artifacts.size());
    for (const auto& artifact : artifacts) {
        locations.push_back(artifact->getLocation());
    }
    return locations;
}

std::shared_ptr<Revision> Revision::setMetadata(const Metadata& metadata) {
    return client_->updateRevisionMetadata(getKref(), metadata);
}

std::optional<std::string> Revision::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Revision::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Revision::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Revision::tag(const std::string& tag) {
    client_->tagRevision(getKref(), tag);
}

void Revision::untag(const std::string& tag) {
    client_->untagRevision(getKref(), tag);
}

bool Revision::hasTag(const std::string& tag) {
    return client_->hasTag(getKref(), tag);
}

bool Revision::wasTagged(const std::string& tag) {
    return client_->wasTagged(getKref(), tag);
}

void Revision::deleteRevision(bool force) {
    client_->deleteRevision(getKref(), force);
}

std::shared_ptr<Item> Revision::getItem() {
    return client_->getItemByKref(getItemKref().uri());
}

std::shared_ptr<Space> Revision::getSpace() {
    std::string project = getItemKref().getProject();
    std::string space = getItemKref().getSpace();
    std::string space_path = "/" + project;
    if (!space.empty()) {
        space_path += "/" + space;
    }
    return client_->getSpace(space_path);
}

std::shared_ptr<Project> Revision::getProject() {
    return getSpace()->getProject();
}

std::shared_ptr<Edge> Revision::createEdge(
    const Kref& target,
    const std::string& edge_type,
    const Metadata& metadata
) {
    validateEdgeType(edge_type);
    return client_->createEdge(getKref(), target, edge_type, metadata);
}

std::vector<std::shared_ptr<Edge>> Revision::getEdges(
    const std::string& edge_type_filter,
    EdgeDirection direction
) {
    // TODO: Add direction parameter to client method
    return client_->getEdges(getKref(), edge_type_filter);
}

std::shared_ptr<Revision> Revision::refresh() {
    return client_->getRevision(getKref().uri());
}

void Revision::setDeprecated(bool deprecated) {
    client_->setRevisionDeprecated(getKref(), deprecated);
}

std::shared_ptr<Revision> Revision::publish() {
    tag(PUBLISHED_TAG);
    return refresh();
}

// --- Graph Traversal Methods ---

TraversalResult Revision::getAllDependencies(
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    int limit
) {
    return client_->traverseEdges(
        getKref(),
        static_cast<int>(EdgeDirection::OUTGOING),
        edge_type_filter,
        max_depth,
        limit,
        false  // include_path
    );
}

TraversalResult Revision::getAllDependents(
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    int limit
) {
    return client_->traverseEdges(
        getKref(),
        static_cast<int>(EdgeDirection::INCOMING),
        edge_type_filter,
        max_depth,
        limit,
        false  // include_path
    );
}

ShortestPathResult Revision::findPathTo(
    const Kref& target,
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    bool all_paths
) {
    return client_->findShortestPath(
        getKref(),
        target,
        edge_type_filter,
        max_depth,
        all_paths
    );
}

ImpactAnalysisResult Revision::analyzeImpact(
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    int limit
) {
    return client_->analyzeImpact(
        getKref(),
        edge_type_filter,
        max_depth,
        limit
    );
}

} // namespace api
} // namespace kumiho
