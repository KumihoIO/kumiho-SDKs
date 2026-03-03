/**
 * @file version.cpp
 * @brief Implementation of Version class.
 */

#include "kumiho/version.hpp"
#include "kumiho/client.hpp"
#include "kumiho/resource.hpp"
#include "kumiho/product.hpp"
#include "kumiho/group.hpp"
#include "kumiho/project.hpp"
#include "kumiho/link.hpp"
#include "kumiho/error.hpp"
#include <algorithm>

namespace kumiho {
namespace api {

Version::Version(const ::kumiho::VersionResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Version::getKref() const {
    return Kref(response_.kref().uri());
}

Kref Version::getProductKref() const {
    return Kref(response_.product_kref().uri());
}

int Version::getVersionNumber() const {
    return response_.number();
}

std::vector<std::string> Version::getTags() const {
    return {response_.tags().begin(), response_.tags().end()};
}

Metadata Version::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Version::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Version::getAuthor() const {
    return response_.author();
}

std::string Version::getUsername() const {
    return response_.username();
}

bool Version::isLatest() const {
    return response_.latest();
}

bool Version::isDeprecated() const {
    return response_.deprecated();
}

bool Version::isPublished() const {
    return response_.published();
}

std::optional<std::string> Version::getDefaultResource() const {
    if (!response_.default_resource().empty()) {
        return response_.default_resource();
    }
    return std::nullopt;
}

void Version::setDefaultResource(const std::string& resource_name) {
    client_->setDefaultResource(getKref(), resource_name);
}

std::shared_ptr<Resource> Version::createResource(const std::string& name, const std::string& location) {
    return client_->createResource(getKref(), name, location);
}

std::shared_ptr<Resource> Version::getResource(const std::string& name) {
    return client_->getResource(getKref(), name);
}

std::vector<std::shared_ptr<Resource>> Version::getResources() {
    return client_->getResources(getKref());
}

std::vector<std::string> Version::getLocations() {
    auto resources = getResources();
    std::vector<std::string> locations;
    locations.reserve(resources.size());
    for (const auto& res : resources) {
        locations.push_back(res->getLocation());
    }
    return locations;
}

std::shared_ptr<Version> Version::setMetadata(const Metadata& metadata) {
    return client_->updateVersionMetadata(getKref(), metadata);
}

std::optional<std::string> Version::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Version::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Version::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Version::tag(const std::string& tag) {
    client_->tagVersion(getKref(), tag);
}

void Version::untag(const std::string& tag) {
    client_->untagVersion(getKref(), tag);
}

bool Version::hasTag(const std::string& tag) {
    return client_->hasTag(getKref(), tag);
}

bool Version::wasTagged(const std::string& tag) {
    return client_->wasTagged(getKref(), tag);
}

void Version::deleteVersion(bool force) {
    client_->deleteVersion(getKref(), force);
}

std::shared_ptr<Product> Version::getProduct() {
    return client_->getProductByKref(getProductKref().uri());
}

std::shared_ptr<Group> Version::getGroup() {
    std::string group_path = "/" + getProductKref().getGroup();
    return client_->getGroup(group_path);
}

std::shared_ptr<Project> Version::getProject() {
    return getGroup()->getProject();
}

std::shared_ptr<Link> Version::createLink(
    const Kref& target,
    const std::string& link_type,
    const Metadata& metadata
) {
    validateLinkType(link_type);
    return client_->createLink(getKref(), target, link_type, metadata);
}

std::vector<std::shared_ptr<Link>> Version::getLinks(
    const std::string& link_type_filter,
    LinkDirection direction
) {
    // TODO: Add direction parameter to client method
    return client_->getLinks(getKref(), link_type_filter);
}

std::shared_ptr<Version> Version::refresh() {
    return client_->getVersion(getKref().uri());
}

void Version::setDeprecated(bool deprecated) {
    client_->setVersionDeprecated(getKref(), deprecated);
}

std::shared_ptr<Version> Version::publish() {
    tag(PUBLISHED_TAG);
    return refresh();
}

// --- Graph Traversal Methods ---

TraversalResult Version::getAllDependencies(
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    int limit
) {
    return client_->traverseLinks(
        getKref(),
        static_cast<int>(LinkDirection::OUTGOING),
        link_type_filter,
        max_depth,
        limit,
        false  // include_path
    );
}

TraversalResult Version::getAllDependents(
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    int limit
) {
    return client_->traverseLinks(
        getKref(),
        static_cast<int>(LinkDirection::INCOMING),
        link_type_filter,
        max_depth,
        limit,
        false  // include_path
    );
}

ShortestPathResult Version::findPathTo(
    const Kref& target,
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    bool all_paths
) {
    return client_->findShortestPath(
        getKref(),
        target,
        link_type_filter,
        max_depth,
        all_paths
    );
}

ImpactAnalysisResult Version::analyzeImpact(
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    int limit
) {
    return client_->analyzeImpact(
        getKref(),
        link_type_filter,
        max_depth,
        limit
    );
}

} // namespace api
} // namespace kumiho
