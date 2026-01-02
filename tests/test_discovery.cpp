/**
 * @file test_discovery.cpp
 * @brief Unit tests for discovery and caching functionality.
 */

#include <gtest/gtest.h>
#include <kumiho/discovery.hpp>
#include <kumiho/error.hpp>
#include <fstream>
#include <chrono>
#include <thread>

using namespace kumiho::api;

// --- CacheControl Tests ---

class CacheControlTest : public ::testing::Test {};

TEST_F(CacheControlTest, IsExpired) {
    CacheControl cc;
    auto now = std::chrono::system_clock::now();
    
    // Expired 1 hour ago
    cc.expires_at = now - std::chrono::hours(1);
    EXPECT_TRUE(cc.isExpired());
    
    // Expires in 1 hour
    cc.expires_at = now + std::chrono::hours(1);
    EXPECT_FALSE(cc.isExpired());
}

TEST_F(CacheControlTest, ShouldRefresh) {
    CacheControl cc;
    auto now = std::chrono::system_clock::now();
    
    // Refresh time passed 1 minute ago
    cc.refresh_at = now - std::chrono::minutes(1);
    EXPECT_TRUE(cc.shouldRefresh());
    
    // Refresh in 1 hour
    cc.refresh_at = now + std::chrono::hours(1);
    EXPECT_FALSE(cc.shouldRefresh());
}

TEST_F(CacheControlTest, ExpiredButNotRefresh) {
    CacheControl cc;
    auto now = std::chrono::system_clock::now();
    
    // Not yet refresh time, but also not expired
    cc.refresh_at = now + std::chrono::hours(1);
    cc.expires_at = now + std::chrono::hours(2);
    
    EXPECT_FALSE(cc.shouldRefresh());
    EXPECT_FALSE(cc.isExpired());
}

TEST_F(CacheControlTest, ShouldRefreshButNotExpired) {
    CacheControl cc;
    auto now = std::chrono::system_clock::now();
    
    // Past refresh time, but not expired
    cc.refresh_at = now - std::chrono::minutes(10);
    cc.expires_at = now + std::chrono::hours(1);
    
    EXPECT_TRUE(cc.shouldRefresh());
    EXPECT_FALSE(cc.isExpired());
}

// --- RegionRouting Tests ---

class RegionRoutingTest : public ::testing::Test {};

TEST_F(RegionRoutingTest, BasicConstruction) {
    RegionRouting rr;
    rr.region_code = "us-central1";
    rr.server_url = "grpc.kumiho.io:443";
    rr.grpc_authority = "grpc.kumiho.io";
    
    EXPECT_EQ(rr.region_code, "us-central1");
    EXPECT_EQ(rr.server_url, "grpc.kumiho.io:443");
    ASSERT_TRUE(rr.grpc_authority.has_value());
    EXPECT_EQ(rr.grpc_authority.value(), "grpc.kumiho.io");
}

TEST_F(RegionRoutingTest, WithoutAuthority) {
    RegionRouting rr;
    rr.region_code = "asia-northeast3";
    rr.server_url = "grpc-kr.kumiho.io:443";
    
    EXPECT_EQ(rr.region_code, "asia-northeast3");
    EXPECT_EQ(rr.server_url, "grpc-kr.kumiho.io:443");
    EXPECT_FALSE(rr.grpc_authority.has_value());
}

// --- DiscoveryRecord Tests ---

class DiscoveryRecordTest : public ::testing::Test {};

TEST_F(DiscoveryRecordTest, BasicConstruction) {
    DiscoveryRecord record;
    record.tenant_id = "tenant-123";
    record.tenant_name = "Test Tenant";
    record.roles = {"admin", "editor"};
    record.region.region_code = "us-central1";
    record.region.server_url = "grpc.kumiho.io:443";
    
    EXPECT_EQ(record.tenant_id, "tenant-123");
    ASSERT_TRUE(record.tenant_name.has_value());
    EXPECT_EQ(record.tenant_name.value(), "Test Tenant");
    EXPECT_EQ(record.roles.size(), 2);
    EXPECT_EQ(record.roles[0], "admin");
    EXPECT_EQ(record.roles[1], "editor");
}

TEST_F(DiscoveryRecordTest, WithoutOptionalFields) {
    DiscoveryRecord record;
    record.tenant_id = "tenant-456";
    record.region.region_code = "asia-northeast3";
    record.region.server_url = "grpc-kr.kumiho.io:443";
    
    EXPECT_EQ(record.tenant_id, "tenant-456");
    EXPECT_FALSE(record.tenant_name.has_value());
    EXPECT_TRUE(record.roles.empty());
    EXPECT_FALSE(record.guardrails.has_value());
}

// --- DiscoveryCache Tests ---

class DiscoveryCacheTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create a temp directory for test cache files
        test_cache_path_ = std::filesystem::temp_directory_path() / "kumiho_test_cache.json";
        
        // Clean up any existing test file
        if (std::filesystem::exists(test_cache_path_)) {
            std::filesystem::remove(test_cache_path_);
        }
    }
    
    void TearDown() override {
        // Clean up test file
        if (std::filesystem::exists(test_cache_path_)) {
            std::filesystem::remove(test_cache_path_);
        }
        
        auto tmp_path = test_cache_path_;
        tmp_path.replace_extension(".tmp");
        if (std::filesystem::exists(tmp_path)) {
            std::filesystem::remove(tmp_path);
        }
    }
    
    std::filesystem::path test_cache_path_;
};

TEST_F(DiscoveryCacheTest, LoadFromEmptyCache) {
    DiscoveryCache cache(test_cache_path_);
    
    auto record = cache.load("test-key");
    
    EXPECT_FALSE(record.has_value());
}

TEST_F(DiscoveryCacheTest, StoreAndLoad) {
    DiscoveryCache cache(test_cache_path_);
    
    // Create a record
    DiscoveryRecord record;
    record.tenant_id = "test-tenant";
    record.tenant_name = "Test Tenant Name";
    record.roles = {"viewer"};
    record.region.region_code = "us-central1";
    record.region.server_url = "grpc.test.kumiho.io:443";
    record.region.grpc_authority = "grpc.test.kumiho.io";
    
    auto now = std::chrono::system_clock::now();
    record.cache_control.issued_at = now;
    record.cache_control.refresh_at = now + std::chrono::hours(1);
    record.cache_control.expires_at = now + std::chrono::hours(24);
    record.cache_control.expires_in_seconds = 86400;
    record.cache_control.refresh_after_seconds = 3600;
    
    // Store
    cache.store("my-cache-key", record);
    
    // Load
    auto loaded = cache.load("my-cache-key");
    
    ASSERT_TRUE(loaded.has_value());
    EXPECT_EQ(loaded->tenant_id, "test-tenant");
    EXPECT_EQ(loaded->region.region_code, "us-central1");
    EXPECT_EQ(loaded->region.server_url, "grpc.test.kumiho.io:443");
}

TEST_F(DiscoveryCacheTest, LoadMissingKey) {
    DiscoveryCache cache(test_cache_path_);
    
    // Store under one key
    DiscoveryRecord record;
    record.tenant_id = "tenant-a";
    record.region.region_code = "us-central1";
    record.region.server_url = "grpc.kumiho.io:443";
    
    auto now = std::chrono::system_clock::now();
    record.cache_control.issued_at = now;
    record.cache_control.refresh_at = now + std::chrono::hours(1);
    record.cache_control.expires_at = now + std::chrono::hours(24);
    
    cache.store("key-a", record);
    
    // Try to load different key
    auto loaded = cache.load("key-b");
    
    EXPECT_FALSE(loaded.has_value());
}

TEST_F(DiscoveryCacheTest, GetPath) {
    DiscoveryCache cache(test_cache_path_);
    
    EXPECT_EQ(cache.getPath(), test_cache_path_);
}

// --- DiscoveryManager Tests ---

class DiscoveryManagerTest : public ::testing::Test {};

TEST_F(DiscoveryManagerTest, DefaultConstruction) {
    DiscoveryManager manager;
    
    // Should not throw
    // Note: Actually calling resolve() would require network access
    // or mocking HTTP calls
}

TEST_F(DiscoveryManagerTest, CustomUrl) {
    DiscoveryManager manager("https://custom.kumiho.io");
    
    // Should not throw
}

TEST_F(DiscoveryManagerTest, ResolveWithoutTokenThrows) {
    DiscoveryManager manager;
    
    // Remote fetch is stubbed, so this will throw DiscoveryError
    EXPECT_THROW(manager.resolve("fake-token"), DiscoveryError);
}

// --- Convenience Function Tests ---

class DiscoveryFunctionsTest : public ::testing::Test {};

TEST_F(DiscoveryFunctionsTest, GetDefaultControlPlaneUrl) {
    // Save and clear env var
    std::string original;
    const char* existing = std::getenv("KUMIHO_CONTROL_PLANE_URL");
    if (existing) {
        original = existing;
    }
#ifdef _WIN32
    _putenv_s("KUMIHO_CONTROL_PLANE_URL", "");
#else
    unsetenv("KUMIHO_CONTROL_PLANE_URL");
#endif
    
    std::string url = getDefaultControlPlaneUrl();
    
    EXPECT_EQ(url, "https://control.kumiho.cloud");
    
    // Restore
    if (!original.empty()) {
#ifdef _WIN32
        _putenv_s("KUMIHO_CONTROL_PLANE_URL", original.c_str());
#else
        setenv("KUMIHO_CONTROL_PLANE_URL", original.c_str(), 1);
#endif
    }
}

TEST_F(DiscoveryFunctionsTest, GetDefaultControlPlaneUrlCustom) {
#ifdef _WIN32
    _putenv_s("KUMIHO_CONTROL_PLANE_URL", "https://staging.kumiho.io");
#else
    setenv("KUMIHO_CONTROL_PLANE_URL", "https://staging.kumiho.io", 1);
#endif
    
    std::string url = getDefaultControlPlaneUrl();
    
    EXPECT_EQ(url, "https://staging.kumiho.io");
    
    // Cleanup
#ifdef _WIN32
    _putenv_s("KUMIHO_CONTROL_PLANE_URL", "");
#else
    unsetenv("KUMIHO_CONTROL_PLANE_URL");
#endif
}

TEST_F(DiscoveryFunctionsTest, GetDefaultCachePath) {
    // Clear env var
#ifdef _WIN32
    _putenv_s("KUMIHO_DISCOVERY_CACHE_FILE", "");
#else
    unsetenv("KUMIHO_DISCOVERY_CACHE_FILE");
#endif
    
    auto path = getDefaultCachePath();
    
    // Should end with discovery-cache.json
    EXPECT_EQ(path.filename().string(), "discovery-cache.json");
}

TEST_F(DiscoveryFunctionsTest, ClientFromDiscoveryWithoutTokenThrows) {
    // Clear auth env vars
#ifdef _WIN32
    _putenv_s("KUMIHO_AUTH_TOKEN", "");
#else
    unsetenv("KUMIHO_AUTH_TOKEN");
#endif
    
    // If no token is available (no credentials file), should throw AuthenticationError
    // If token is available but discovery fails, should throw DiscoveryError
    // Either way, it should throw
    EXPECT_THROW(clientFromDiscovery(), std::exception);
}
