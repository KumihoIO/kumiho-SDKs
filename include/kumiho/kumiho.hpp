/**
 * @file kumiho.hpp
 * @brief Main include header for the Kumiho C++ SDK.
 *
 * This is the primary header to include when using the Kumiho SDK.
 * It includes all public headers and provides convenience aliases.
 *
 * @example
 * @code
 *   #include <kumiho/kumiho.hpp>
 *   
 *   int main() {
 *       auto client = kumiho::api::Client::createFromEnv();
 *       auto project = client->createProject("my-project");
 *       auto group = project->createGroup("assets");
 *       auto product = group->createProduct("hero", "model");
 *       auto version = product->createVersion({{"artist", "jane"}});
 *       version->createResource("mesh", "/assets/hero.fbx");
 *       version->tag("approved");
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
#include "kumiho/group.hpp"
#include "kumiho/product.hpp"
#include "kumiho/version.hpp"
#include "kumiho/resource.hpp"
#include "kumiho/link.hpp"
#include "kumiho/collection.hpp"
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

// Convenience aliases for commonly used types

/** @brief Alias for LinkType::DEPENDS_ON */
constexpr const char* DEPENDS_ON = LinkType::DEPENDS_ON;

/** @brief Alias for LinkType::DERIVED_FROM */
constexpr const char* DERIVED_FROM = LinkType::DERIVED_FROM;

/** @brief Alias for LinkType::CREATED_FROM */
constexpr const char* CREATED_FROM = LinkType::CREATED_FROM;

/** @brief Alias for LinkType::REFERENCED */
constexpr const char* REFERENCED = LinkType::REFERENCED;

/** @brief Alias for LinkType::CONTAINS */
constexpr const char* CONTAINS = LinkType::CONTAINS;

/** @brief Alias for LinkType::BELONGS_TO */
constexpr const char* BELONGS_TO = LinkType::BELONGS_TO;

/** @brief Alias for LinkDirection::OUTGOING */
constexpr LinkDirection OUTGOING = LinkDirection::OUTGOING;

/** @brief Alias for LinkDirection::INCOMING */
constexpr LinkDirection INCOMING = LinkDirection::INCOMING;

/** @brief Alias for LinkDirection::BOTH */
constexpr LinkDirection BOTH = LinkDirection::BOTH;

} // namespace api
} // namespace kumiho
