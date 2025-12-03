/**
 * @file edge.cpp
 * @brief Implementation of Edge class.
 */

#include "kumiho/edge.hpp"
#include "kumiho/client.hpp"

namespace kumiho {
namespace api {

Edge::Edge(const ::kumiho::Edge& edge, Client* client)
    : edge_(edge), client_(client) {}

Kref Edge::getSourceKref() const {
    return Kref(edge_.source_kref().uri());
}

Kref Edge::getTargetKref() const {
    return Kref(edge_.target_kref().uri());
}

std::string Edge::getEdgeType() const {
    return edge_.edge_type();
}

Metadata Edge::getMetadata() const {
    return {edge_.metadata().begin(), edge_.metadata().end()};
}

std::optional<std::string> Edge::getCreatedAt() const {
    if (!edge_.created_at().empty()) {
        return edge_.created_at();
    }
    return std::nullopt;
}

std::string Edge::getAuthor() const {
    return edge_.author();
}

std::string Edge::getUsername() const {
    return edge_.username();
}

void Edge::deleteEdge() {
    client_->deleteEdge(getSourceKref(), getTargetKref(), getEdgeType());
}

} // namespace api
} // namespace kumiho
