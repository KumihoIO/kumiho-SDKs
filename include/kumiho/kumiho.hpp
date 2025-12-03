/**
 * @file kumiho.hpp
 * @brief Main include header for the Kumiho C++ SDK.
 *
 * This is the primary header to include when using the Kumiho SDK.
 * It includes all public headers.
 *
 * Terminology:
 * - Space: A hierarchical container/namespace
 * - Item: An asset/entity in the graph
 * - Revision: A specific state of an item
 * - Artifact: A file/location attached to a revision
 * - Edge: A relationship between revisions
 * - Bundle: A curated set of items
 *
 * @example
 * @code
 *   #include <kumiho/kumiho.hpp>
 *   
 *   int main() {
 *       auto client = kumiho::api::Client::createFromEnv();
 *       auto project = client->createProject("my-project");
 *       auto space = project->createSpace("assets");
 *       auto item = space->createItem("hero", "model");
 *       auto revision = item->createRevision({{"artist", "jane"}});
 *       revision->createArtifact("mesh", "/assets/hero.fbx");
 *       revision->tag("approved");
 *       return 0;
 *   }
 * @endcode
 */

#pragma once

// Core types and utilities
#include "kumiho/types.hpp"
#include "kumiho/error.hpp"
#include "kumiho/kref.hpp"

// Entity classes
#include "kumiho/project.hpp"
#include "kumiho/space.hpp"
#include "kumiho/item.hpp"
#include "kumiho/revision.hpp"
#include "kumiho/artifact.hpp"
#include "kumiho/edge.hpp"
#include "kumiho/bundle.hpp"
#include "kumiho/event.hpp"

// Discovery and authentication
#include "kumiho/token_loader.hpp"
#include "kumiho/discovery.hpp"

// Client
#include "kumiho/client.hpp"

/**
 * @namespace kumiho
 * @brief Root namespace for the Kumiho SDK.
 */
namespace kumiho {

/**
 * @namespace kumiho::api
 * @brief Public API namespace containing all Kumiho classes and functions.
 */
namespace api {

// Convenience aliases for commonly used edge types

/** @brief Alias for EdgeType::DEPENDS_ON */
constexpr const char* DEPENDS_ON = EdgeType::DEPENDS_ON;

/** @brief Alias for EdgeType::DERIVED_FROM */
constexpr const char* DERIVED_FROM = EdgeType::DERIVED_FROM;

/** @brief Alias for EdgeType::CREATED_FROM */
constexpr const char* CREATED_FROM = EdgeType::CREATED_FROM;

/** @brief Alias for EdgeType::REFERENCED */
constexpr const char* REFERENCED = EdgeType::REFERENCED;

/** @brief Alias for EdgeType::CONTAINS */
constexpr const char* CONTAINS = EdgeType::CONTAINS;

/** @brief Alias for EdgeType::BELONGS_TO */
constexpr const char* BELONGS_TO = EdgeType::BELONGS_TO;

/** @brief Alias for EdgeDirection::OUTGOING */
constexpr EdgeDirection OUTGOING = EdgeDirection::OUTGOING;

/** @brief Alias for EdgeDirection::INCOMING */
constexpr EdgeDirection INCOMING = EdgeDirection::INCOMING;

/** @brief Alias for EdgeDirection::BOTH */
constexpr EdgeDirection BOTH = EdgeDirection::BOTH;

} // namespace api
} // namespace kumiho
