/**
 * @file item.cpp
 * @brief Implementation of Item class.
 */

#include "kumiho/item.hpp"
#include "kumiho/client.hpp"
#include "kumiho/revision.hpp"
#include "kumiho/space.hpp"
#include "kumiho/project.hpp"
#include "kumiho/error.hpp"
#include <algorithm>
#include <iomanip>
#include <sstream>

namespace kumiho {
namespace api {

namespace {
    /**
     * Convert a time_point to ISO 8601 string format.
     */
    std::string timePointToIso8601(std::chrono::system_clock::time_point tp) {
        auto time_t_val = std::chrono::system_clock::to_time_t(tp);
        std::tm tm_val;
#ifdef _WIN32
        gmtime_s(&tm_val, &time_t_val);
#else
        gmtime_r(&time_t_val, &tm_val);
#endif
        std::ostringstream oss;
        oss << std::put_time(&tm_val, "%Y-%m-%dT%H:%M:%S") << "Z";
        return oss.str();
    }
}  // namespace

Item::Item(const ::kumiho::ItemResponse& response, Client* client)
    : response_(response), client_(client) {}

Kref Item::getKref() const {
    return Kref(response_.kref().uri());
}

std::string Item::getName() const {
    return response_.name();
}

std::string Item::getItemName() const {
    return response_.item_name();
}

std::string Item::getKind() const {
    return response_.kind();
}

Metadata Item::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::optional<std::string> Item::getCreatedAt() const {
    if (!response_.created_at().empty()) {
        return response_.created_at();
    }
    return std::nullopt;
}

std::string Item::getAuthor() const {
    return response_.author();
}

std::string Item::getUsername() const {
    return response_.username();
}

bool Item::isDeprecated() const {
    return response_.deprecated();
}

std::shared_ptr<Revision> Item::createRevision(const Metadata& metadata) {
    return client_->createRevision(getKref(), metadata);
}

std::shared_ptr<Revision> Item::getRevision(int revision_number) {
    std::string kref_uri = getKref().uri() + "?r=" + std::to_string(revision_number);
    return client_->getRevision(kref_uri);
}

std::vector<std::shared_ptr<Revision>> Item::getRevisions() {
    return client_->getRevisions(getKref());
}

std::shared_ptr<Revision> Item::getRevisionByTag(const std::string& tag) {
    return client_->resolveKref(getKref().uri(), tag, "");
}

std::shared_ptr<Revision> Item::getRevisionByTime(const std::string& time) {
    return client_->resolveKref(getKref().uri(), "", time);
}

std::shared_ptr<Revision> Item::getRevisionByTime(std::chrono::system_clock::time_point time_point) {
    return client_->resolveKref(getKref().uri(), "", timePointToIso8601(time_point));
}

std::shared_ptr<Revision> Item::getRevisionByTagAndTime(const std::string& tag, const std::string& time) {
    return client_->resolveKref(getKref().uri(), tag, time);
}

std::shared_ptr<Revision> Item::getRevisionByTagAndTime(const std::string& tag, std::chrono::system_clock::time_point time_point) {
    return client_->resolveKref(getKref().uri(), tag, timePointToIso8601(time_point));
}

std::shared_ptr<Revision> Item::getLatestRevision() {
    auto revisions = getRevisions();
    if (revisions.empty()) {
        return nullptr;
    }
    
    // Find revisions marked as latest
    for (const auto& revision : revisions) {
        if (revision->isLatest()) {
            return revision;
        }
    }
    
    // Fallback to highest revision number
    return *std::max_element(revisions.begin(), revisions.end(),
        [](const std::shared_ptr<Revision>& a, const std::shared_ptr<Revision>& b) {
            return a->getRevisionNumber() < b->getRevisionNumber();
        });
}

int Item::peekNextRevision() {
    return client_->peekNextRevision(getKref());
}

std::shared_ptr<Item> Item::setMetadata(const Metadata& metadata) {
    return client_->updateItemMetadata(getKref(), metadata);
}

std::optional<std::string> Item::getAttribute(const std::string& key) {
    return client_->getAttribute(getKref(), key);
}

bool Item::setAttribute(const std::string& key, const std::string& value) {
    return client_->setAttribute(getKref(), key, value);
}

bool Item::deleteAttribute(const std::string& key) {
    return client_->deleteAttribute(getKref(), key);
}

void Item::deleteItem(bool force) {
    client_->deleteItem(getKref(), force);
}

std::shared_ptr<Space> Item::getSpace() {
    std::string project = getKref().getProject();
    std::string space = getKref().getSpace();
    std::string space_path = "/" + project;
    if (!space.empty()) {
        space_path += "/" + space;
    }
    return client_->getSpace(space_path);
}

std::shared_ptr<Project> Item::getProject() {
    return getSpace()->getProject();
}

void Item::setDeprecated(bool deprecated) {
    client_->setItemDeprecated(getKref(), deprecated);
}

std::shared_ptr<Item> Item::refresh() {
    return client_->getItemByKref(getKref().uri());
}

} // namespace api
} // namespace kumiho
