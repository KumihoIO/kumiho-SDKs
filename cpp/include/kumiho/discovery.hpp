/**
 * @file discovery.hpp
 * @brief Discovery and auto-configuration for the Kumiho C++ SDK.
 *
 * This header provides classes and functions for bootstrapping a Client via
 * the control-plane discovery endpoint. It handles caching of discovery payloads,
 * respects cache-control metadata, and automatically refreshes routing info.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <map>
#include <chrono>
#include <filesystem>

namespace kumiho {
namespace api {

// Forward declarations
class Client;

// --- Self-hosted Community Edition (CE) discovery ---
//
// These constants form a cross-component contract shared with the Python SDK,
// kumiho-server (config/apply_deployment_defaults), and the installer scripts.
// The names and the default port MUST NOT change.

/** @brief Env var holding an explicit loopback CE endpoint (e.g. "127.0.0.1:9190"). */
constexpr const char* kLocalCeEndpointEnv = "KUMIHO_LOCAL_SERVER_ENDPOINT";

/** @brief Env var holding an explicit loopback CE port. */
constexpr const char* kLocalCePortEnv = "KUMIHO_LOCAL_SERVER_PORT";

/** @brief Env var overriding the CE liveness-probe timeout in seconds. */
constexpr const char* kLocalCeTimeoutEnv = "KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS";

/** @brief Default loopback port for a self-hosted CE server. */
constexpr int kDefaultLocalCePort = 9190;

/**
 * @brief Region routing information from discovery.
 *
 * Contains the endpoint and optional gRPC authority override for a region.
 */
struct RegionRouting {
    /** @brief The region code (e.g., "us-central1", "asia-northeast3"). */
    std::string region_code;
    
    /** @brief The gRPC server URL (e.g., "grpc.kumiho.io:443"). */
    std::string server_url;
    
    /** @brief Optional gRPC authority override for TLS verification. */
    std::optional<std::string> grpc_authority;
};

/**
 * @brief Cache control metadata from the discovery response.
 *
 * Tracks when the cache was issued, when it should be refreshed,
 * and when it expires.
 */
struct CacheControl {
    /** @brief When the cache entry was issued. */
    std::chrono::system_clock::time_point issued_at;
    
    /** @brief When the cache should be proactively refreshed. */
    std::chrono::system_clock::time_point refresh_at;
    
    /** @brief When the cache entry expires and must be refreshed. */
    std::chrono::system_clock::time_point expires_at;
    
    /** @brief Total seconds until expiration. */
    int expires_in_seconds;
    
    /** @brief Seconds until refresh should occur. */
    int refresh_after_seconds;

    /**
     * @brief Check if the cache entry has expired.
     * @return True if expired, false otherwise.
     */
    bool isExpired() const;

    /**
     * @brief Check if the cache entry should be proactively refreshed.
     * @return True if refresh is recommended, false otherwise.
     */
    bool shouldRefresh() const;
};

/**
 * @brief A complete discovery record from the control plane.
 *
 * Contains tenant information, role assignments, region routing,
 * and cache control metadata.
 */
struct DiscoveryRecord {
    /** @brief The tenant's unique identifier. */
    std::string tenant_id;
    
    /** @brief The tenant's display name (optional). */
    std::optional<std::string> tenant_name;
    
    /** @brief List of role assignments for the user. */
    std::vector<std::string> roles;
    
    /** @brief Optional guardrails/limits for the tenant. */
    std::optional<std::map<std::string, std::string>> guardrails;
    
    /** @brief Region routing information. */
    RegionRouting region;
    
    /** @brief Cache control metadata. */
    CacheControl cache_control;
};

/**
 * @brief Encrypted JSON file cache for discovery records.
 *
 * Stores discovery records in an encrypted JSON file, keyed by tenant hint.
 * The default location is ~/.kumiho/discovery-cache.json.
 * 
 * Cache data is encrypted at rest using a machine-specific key derived from
 * hardware identifiers, providing defense-in-depth protection for tenant metadata.
 */
class DiscoveryCache {
public:
    /**
     * @brief Construct a cache with the default or specified path.
     * @param path Optional path to the cache file.
     * @param encrypt Whether to encrypt cache data (default: true).
     */
    explicit DiscoveryCache(const std::filesystem::path& path = {}, bool encrypt = true);

    /**
     * @brief Load a cached discovery record.
     * @param cache_key The cache key (tenant hint or "__default__").
     * @return The cached record, or nullopt if not found or invalid.
     */
    std::optional<DiscoveryRecord> load(const std::string& cache_key);

    /**
     * @brief Store a discovery record in the cache.
     * @param cache_key The cache key.
     * @param record The record to store.
     */
    void store(const std::string& cache_key, const DiscoveryRecord& record);

    /**
     * @brief Get the cache file path.
     * @return The filesystem path to the cache file.
     */
    const std::filesystem::path& getPath() const { return path_; }

private:
    std::filesystem::path path_;
    bool encrypt_;
    
    std::map<std::string, std::map<std::string, std::string>> readAll();
    
    /**
     * @brief Encrypt cache content for storage.
     * @param plaintext The JSON content to encrypt.
     * @return The encrypted content with "enc:v1:" prefix.
     */
    std::string encryptContent(const std::string& plaintext);
    
    /**
     * @brief Decrypt cache content from storage.
     * @param encrypted The encrypted content.
     * @return The decrypted JSON, or empty string if decryption fails.
     */
    std::string decryptContent(const std::string& encrypted);
    
    /**
     * @brief Get machine-specific encryption key.
     * @return 32-byte key derived from machine ID.
     */
    std::vector<uint8_t> deriveKey();
};

/**
 * @brief Manager for discovery endpoint interactions.
 *
 * Coordinates cache usage and remote discovery calls to the control plane.
 */
class DiscoveryManager {
public:
    /**
     * @brief Construct a discovery manager.
    * @param control_plane_url The control plane base URL (default: https://control.kumiho.cloud).
     * @param cache_path Optional path to the cache file.
     * @param timeout_seconds Request timeout in seconds (default: 10).
     */
    explicit DiscoveryManager(
        const std::string& control_plane_url = "",
        const std::filesystem::path& cache_path = {},
        double timeout_seconds = 10.0
    );

    /**
     * @brief Resolve tenant routing via discovery.
     *
     * Uses the cache when available and valid, or fetches fresh data
     * from the control plane discovery endpoint.
     *
     * @param id_token The Firebase ID token for authentication.
     * @param tenant_hint Optional tenant ID hint for multi-tenant users.
     * @param force_refresh Force a fresh fetch even if cache is valid.
     * @return The resolved discovery record.
     * @throws DiscoveryError if the endpoint cannot be reached.
     */
    DiscoveryRecord resolve(
        const std::string& id_token,
        const std::optional<std::string>& tenant_hint = std::nullopt,
        bool force_refresh = false
    );

private:
    std::string base_url_;
    DiscoveryCache cache_;
    double timeout_;

    DiscoveryRecord fetchRemote(
        const std::string& id_token,
        const std::optional<std::string>& tenant_hint
    );
};

// --- Convenience Functions ---

/**
 * @brief Get the default control plane URL.
 *
 * Returns the value of KUMIHO_CONTROL_PLANE_URL environment variable,
 * or "https://control.kumiho.cloud" if not set.
 *
 * @return The control plane URL.
 */
std::string getDefaultControlPlaneUrl();

/**
 * @brief Get the default discovery cache path.
 *
 * Returns the value of KUMIHO_DISCOVERY_CACHE_FILE environment variable,
 * or ~/.kumiho/discovery-cache.json if not set.
 *
 * @return The cache file path.
 */
std::filesystem::path getDefaultCachePath();

/**
 * @brief Create a Client configured via the discovery endpoint.
 *
 * This is the recommended way to create a Client for production use.
 * It automatically discovers the correct data plane endpoint based on
 * the user's tenant and region.
 *
 * @param id_token Optional ID token (defaults to loaded bearer token).
 * @param tenant_hint Optional tenant ID hint.
 * @param control_plane_url Optional control plane URL override.
 * @param cache_path Optional cache file path override.
 * @param force_refresh Force refresh of cached discovery data.
 * @return A shared pointer to the configured Client.
 * @throws DiscoveryError if discovery fails.
 * @throws AuthenticationError if no token is available.
 *
 * @example
 * @code
 *   // Simple usage (uses cached credentials)
 *   auto client = kumiho::api::clientFromDiscovery();
 *   
 *   // With explicit token
 *   auto client = kumiho::api::clientFromDiscovery("your-id-token");
 *   
 *   // Force refresh for testing
 *   auto client = kumiho::api::clientFromDiscovery(
 *       std::nullopt, std::nullopt, "", "", true
 *   );
 * @endcode
 */
std::shared_ptr<Client> clientFromDiscovery(
    const std::optional<std::string>& id_token = std::nullopt,
    const std::optional<std::string>& tenant_hint = std::nullopt,
    const std::string& control_plane_url = "",
    const std::string& cache_path = "",
    bool force_refresh = false
);

/**
 * @brief Resolve a loopback gRPC target for a self-hosted CE server, if present.
 *
 * Probes loopback candidates (derived from KUMIHO_LOCAL_SERVER_ENDPOINT,
 * KUMIHO_LOCAL_SERVER_PORT, or the default 127.0.0.1:9190) by issuing an HTTP
 * GET to `http://<target>/api/_live`. A candidate matches only when the probe
 * returns HTTP status < 400 and a JSON body with `deployment_mode` exactly
 * equal to `"self_hosted_ce"`.
 *
 * Only loopback hosts (localhost, 127.0.0.0/8, ::1) are accepted; non-loopback
 * targets are rejected as a hard security invariant.
 *
 * @param timeout Optional probe timeout in seconds. When omitted, falls back to
 *                KUMIHO_LOCAL_DISCOVERY_TIMEOUT_SECONDS (min 0.05) or 0.5.
 * @return The first probe-passing loopback target, or std::nullopt if none.
 * @throws DiscoveryError if an explicit env var points to a non-loopback host
 *         or an invalid port.
 */
std::optional<std::string> resolveLocalCeEndpoint(
    std::optional<double> timeout = std::nullopt
);

/**
 * @brief Create a tokenless Client for a loopback self-hosted CE server.
 *
 * Builds an insecure gRPC channel to the resolved loopback target with no auth
 * token loaded, discovery disabled, and auto-login disabled. Returns nullptr
 * (does NOT throw) when no CE server is detected.
 *
 * This must never run when the caller already has an explicit endpoint or a
 * resolved token — see Client::createFromEnv for the gating logic.
 *
 * @param timeout Optional probe timeout in seconds (see resolveLocalCeEndpoint).
 * @return A shared pointer to the configured Client, or nullptr if no CE server.
 */
std::shared_ptr<Client> clientFromLocalCe(
    std::optional<double> timeout = std::nullopt
);

} // namespace api
} // namespace kumiho
