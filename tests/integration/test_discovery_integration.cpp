/**
 * @file test_discovery_integration.cpp
 * @brief Integration tests for discovery and automatic configuration.
 *
 * These tests verify the discovery service and automatic endpoint resolution.
 * Requires network access to the control plane.
 *
 * Set KUMIHO_INTEGRATION_TEST=1 to enable these tests.
 * Control plane URL defaults to http://localhost:3000.
 */

#include <gtest/gtest.h>
#include <kumiho/kumiho.hpp>
#include <string>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <algorithm>

using namespace kumiho::api;
namespace fs = std::filesystem;

namespace {

bool shouldRunIntegrationTests() {
#ifdef _MSC_VER
    char* env = nullptr;
    size_t len = 0;
    _dupenv_s(&env, &len, "KUMIHO_INTEGRATION_TEST");
    bool result = (env != nullptr && std::string(env) == "1");
    free(env);
    return result;
#else
    const char* env = std::getenv("KUMIHO_INTEGRATION_TEST");
    return env != nullptr && std::string(env) == "1";
#endif
}

} // anonymous namespace

/**
 * @brief Integration test fixture for discovery tests.
 */
class DiscoveryIntegrationTest : public ::testing::Test {
protected:
    std::string testCacheDir_;

    void SetUp() override {
        if (!shouldRunIntegrationTests()) {
            GTEST_SKIP() << "Integration tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.";
        }

        // Create temporary cache directory for tests
        fs::path tempDir = fs::temp_directory_path() / "kumiho_cpp_test_cache";
        testCacheDir_ = tempDir.string();
        fs::create_directories(testCacheDir_);
    }

    void TearDown() override {
        // Clean up test cache directory
        if (!testCacheDir_.empty()) {
            try {
                fs::remove_all(testCacheDir_);
            } catch (...) {
                // Ignore cleanup errors
            }
        }
    }
};

/**
 * @test Discovery cache file operations.
 */
TEST_F(DiscoveryIntegrationTest, DiscoveryCacheOperations) {
    // DiscoveryCache expects a file path, not a directory
    fs::path cacheFile = fs::path(testCacheDir_) / "discovery_cache.json";
    DiscoveryCache cache(cacheFile);

    // Create a test record
    RegionRouting routing;
    routing.region_code = "us-central1";
    routing.server_url = "test-server.kumiho.io:443";
    routing.grpc_authority = "test-server.kumiho.io";

    DiscoveryRecord record;
    record.tenant_id = "test-tenant-123";
    record.region = routing;

    // Store the record
    cache.store("test_cache_key", record);

    // Verify file was created (cache stores all entries in the cache file path)
    EXPECT_TRUE(fs::exists(cacheFile)) << "Cache file should exist at: " << cacheFile.string();

    // Load the record back
    auto loaded = cache.load("test_cache_key");
    ASSERT_TRUE(loaded.has_value()) << "Should be able to load cached record";
    EXPECT_EQ(loaded->tenant_id, "test-tenant-123");
    EXPECT_EQ(loaded->region.region_code, "us-central1");
    EXPECT_EQ(loaded->region.server_url, "test-server.kumiho.io:443");
}

/**
 * @test Discovery manager initialization.
 */
TEST_F(DiscoveryIntegrationTest, DiscoveryManagerInit) {
    DiscoveryManager manager;
    // Default state should be valid - construction should not throw
    std::cout << "DiscoveryManager initialized successfully" << std::endl;
    SUCCEED();
}

/**
 * @test Discovery manager with custom URL.
 */
TEST_F(DiscoveryIntegrationTest, DiscoveryManagerCustomUrl) {
    DiscoveryManager manager("http://localhost:3000", testCacheDir_);
    // Should be initialized without error
    std::cout << "DiscoveryManager with custom URL initialized successfully" << std::endl;
    SUCCEED();
}

/**
 * @test Control plane token detection.
 */
TEST_F(DiscoveryIntegrationTest, ControlPlaneTokenDetection) {
    // Create a mock JWT with tenant_id claim
    // JWT format: header.payload.signature (base64 encoded)
    // Payload: {"tenant_id": "test-tenant", "iss": "kumiho"}
    std::string cpToken = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
                          "eyJ0ZW5hbnRfaWQiOiJ0ZXN0LXRlbmFudCIsImlzcyI6Imt1bWlobyJ9."
                          "signature";

    EXPECT_TRUE(isControlPlaneToken(cpToken)) << "Token with tenant_id should be detected as control plane token";

    // Regular Firebase token (no tenant_id) - payload: {"sub": "user123", "iss": "firebase"}
    std::string fbToken = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
                          "eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoiZmlyZWJhc2UifQ."
                          "signature";

    EXPECT_FALSE(isControlPlaneToken(fbToken)) << "Token without tenant_id should not be control plane token";
}

/**
 * @test Config directory paths.
 */
TEST_F(DiscoveryIntegrationTest, ConfigDirectoryPaths) {
    fs::path configDir = getConfigDir();
    EXPECT_FALSE(configDir.empty()) << "Config directory should not be empty";

    // Should contain kumiho in the path
    std::string configDirStr = configDir.string();
    std::string configDirLower = configDirStr;
    std::transform(configDirLower.begin(), configDirLower.end(),
                   configDirLower.begin(), ::tolower);
    EXPECT_TRUE(configDirLower.find("kumiho") != std::string::npos)
        << "Config directory should contain 'kumiho': " << configDirStr;

    fs::path credPath = getCredentialsPath();
    EXPECT_FALSE(credPath.empty()) << "Credentials path should not be empty";
    std::string credPathStr = credPath.string();
    std::string credPathLower = credPathStr;
    std::transform(credPathLower.begin(), credPathLower.end(),
                   credPathLower.begin(), ::tolower);
    EXPECT_TRUE(credPathLower.find("kumiho") != std::string::npos)
        << "Credentials path should contain 'kumiho': " << credPathStr;

    std::cout << "Config dir: " << configDirStr << std::endl;
    std::cout << "Credentials path: " << credPathStr << std::endl;
}

/**
 * @test Token loading from environment.
 */
TEST_F(DiscoveryIntegrationTest, TokenLoadingFromEnv) {
    // Check if any tokens are available
    auto bearerToken = loadBearerToken();
    auto firebaseToken = loadFirebaseToken();

    std::cout << "Bearer token available: " << (bearerToken.has_value() ? "yes" : "no") << std::endl;
    std::cout << "Firebase token available: " << (firebaseToken.has_value() ? "yes" : "no") << std::endl;

    // At least validate that the functions don't crash
    SUCCEED();
}

/**
 * @test Default control plane URL.
 */
TEST_F(DiscoveryIntegrationTest, DefaultControlPlaneUrl) {
    auto url = getDefaultControlPlaneUrl();
    EXPECT_FALSE(url.empty()) << "Default control plane URL should not be empty";
    EXPECT_TRUE(url.find("http") == 0) << "URL should start with http: " << url;
    std::cout << "Default control plane URL: " << url << std::endl;
}
