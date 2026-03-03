/**
 * @file token_loader.hpp
 * @brief Token loading utilities for the Kumiho C++ SDK.
 *
 * This header provides functions for locating and loading bearer tokens
 * used for authentication with Kumiho Cloud services.
 */

#pragma once

#include <string>
#include <optional>
#include <map>
#include <filesystem>

namespace kumiho {
namespace api {

// --- Environment Variable Names ---

/** @brief Environment variable for auth token override. */
constexpr const char* TOKEN_ENV = "KUMIHO_AUTH_TOKEN";

/** @brief Environment variable for Firebase ID token override. */
constexpr const char* FIREBASE_TOKEN_ENV = "KUMIHO_FIREBASE_ID_TOKEN";

/** @brief Environment variable to prefer control plane token. */
constexpr const char* USE_CP_TOKEN_ENV = "KUMIHO_USE_CONTROL_PLANE_TOKEN";

/** @brief Environment variable for config directory override. */
constexpr const char* CONFIG_DIR_ENV = "KUMIHO_CONFIG_DIR";

/** @brief Credentials filename. */
constexpr const char* CREDENTIALS_FILENAME = "kumiho_authentication.json";

// --- Path Functions ---

/**
 * @brief Get the Kumiho configuration directory.
 *
 * Returns the value of KUMIHO_CONFIG_DIR if set, otherwise returns
 * the user's home directory plus .kumiho (e.g., ~/.kumiho on Unix,
 * C:\Users\<user>\.kumiho on Windows).
 *
 * @return The path to the configuration directory.
 */
std::filesystem::path getConfigDir();

/**
 * @brief Get the path to the credentials file.
 *
 * @return The path to kumiho_authentication.json.
 */
std::filesystem::path getCredentialsPath();

// --- Token Loading Functions ---

/**
 * @brief Load the preferred bearer token for gRPC calls.
 *
 * Token resolution order:
 * 1. KUMIHO_AUTH_TOKEN environment variable
 * 2. Firebase ID token from credentials file (if KUMIHO_USE_CONTROL_PLANE_TOKEN not set)
 * 3. Control plane token from credentials file
 *
 * @return The bearer token, or nullopt if no token is available.
 * @throws ValidationError if a token is found but has invalid JWT format.
 */
std::optional<std::string> loadBearerToken();

/**
 * @brief Load the Firebase ID token for control-plane interactions.
 *
 * Token resolution order:
 * 1. KUMIHO_FIREBASE_ID_TOKEN environment variable
 * 2. id_token field from credentials file
 *
 * @return The Firebase ID token, or nullopt if not available.
 * @throws ValidationError if a token is found but has invalid JWT format.
 */
std::optional<std::string> loadFirebaseToken();

/**
 * @brief Validate that a token has valid JWT structure.
 *
 * Checks that the token has exactly 3 non-empty parts separated by dots.
 * This catches common errors like using API keys instead of JWTs.
 *
 * @param token The token string to validate.
 * @param source Description of the token source (for error messages).
 * @return The validated token string.
 * @throws ValidationError if the token format is invalid.
 */
std::string validateTokenFormat(const std::string& token, const std::string& source = "token");

/**
 * @brief Check if a JWT token is a control-plane token.
 *
 * Control plane tokens have specific claims that identify them:
 * - tenant_id claim
 * - iss starting with "https://kumiho.io"
 * - aud starting with "https://api.kumiho.io"
 *
 * @param token The JWT token string.
 * @return True if this is a control-plane token.
 */
bool isControlPlaneToken(const std::string& token);

/**
 * @brief Decode JWT claims from a token.
 *
 * Extracts the payload section from a JWT and returns the claims
 * as a string map. Only works for simple string claims.
 *
 * @param token The JWT token string.
 * @return A map of claim names to values.
 */
std::map<std::string, std::string> decodeJwtClaims(const std::string& token);

} // namespace api
} // namespace kumiho
