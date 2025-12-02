/**
 * @file link.cpp
 * @brief Implementation of Link class.
 */

#include "kumiho/link.hpp"
#include "kumiho/client.hpp"

namespace kumiho {
namespace api {

Link::Link(const ::kumiho::Link& link, Client* client)
    : link_(link), client_(client) {}

Kref Link::getSourceKref() const {
    return Kref(link_.source_kref().uri());
}

Kref Link::getTargetKref() const {
    return Kref(link_.target_kref().uri());
}

std::string Link::getLinkType() const {
    return link_.link_type();
}

Metadata Link::getMetadata() const {
    return {link_.metadata().begin(), link_.metadata().end()};
}

std::optional<std::string> Link::getCreatedAt() const {
    if (!link_.created_at().empty()) {
        return link_.created_at();
    }
    return std::nullopt;
}

std::string Link::getAuthor() const {
    return link_.author();
}

std::string Link::getUsername() const {
    return link_.username();
}

void Link::deleteLink() {
    client_->deleteLink(getSourceKref(), getTargetKref(), getLinkType());
}

} // namespace api
} // namespace kumiho
