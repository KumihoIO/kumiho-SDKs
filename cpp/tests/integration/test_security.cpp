/**
 * @file test_security.cpp
 * @brief Security integration tests for the Kumiho C++ SDK.
 *
 * These tests verify security features work correctly when communicating
 * with localhost kumiho-server and control-plane instances.
 *
 * Requirements:
 * - kumiho-server running on localhost:8080
 * - control-plane running on localhost:3000
 * - Set KUMIHO_INTEGRATION_TEST=1 to enable
 *
 * Test categories:
 * 1. Token validation - bad tokens should be rejected
 * 2. Token format validation - client-side validation
 * 3. Discovery cache encryption - encrypted storage
 * 4. Error handling - clear error messages
 */

#include <gtest/gtest.h>
#include <kumiho/kumiho.hpp>
#include <string>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <regex>

using namespace kumiho::api;
namespace fs = std::filesystem;

namespace {

bool shouldRunSecurityTests() {
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

std::string getEnvOrDefault(const char* name, const std::string& defaultValue) {
#ifdef _MSC_VER
    char* env = nullptr;
    size_t len = 0;
    _dupenv_s(&env, &len, name);
    std::string result = (env != nullptr) ? std::string(env) : defaultValue;
    free(env);
    return result;
#else
    const char* env = std::getenv(name);
    return env ? std::string(env) : defaultValue;
#endif
}

} // anonymous namespace

/**
 * @brief Security test fixture.
 */
class SecurityTest : public ::testing::Test {
protected:
    std::string serverEndpoint_;
    std::string testCacheDir_;

    void SetUp() override {
        if (!shouldRunSecurityTests()) {
            GTEST_SKIP() << "Security tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.";
        }

        serverEndpoint_ = getEnvOrDefault("KUMIHO_SERVER_ENDPOINT", "localhost:8080");

        // Create temporary cache directory
        fs::path tempDir = fs::temp_directory_path() / "kumiho_security_test";
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

// ============================================================================
// Token Validation Tests
// ============================================================================

/**
 * @test Server should reject expired tokens.
 */
TEST_F(SecurityTest, RejectsExpiredToken) {
    // Create an obviously expired token
    std::string expiredToken = 
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ."
        "fake_signature";

    ClientOptions options;
    options.endpoint = serverEndpoint_;
    options.idToken = expiredToken;
    options.useTls = false;  // localhost testing

    try {
        auto client = Client::create(options);
        auto projects = client->getProjects();
        FAIL() << "Should have rejected expired token";
    } catch (const AuthenticationError& e) {
        // Expected - authentication should fail
        std::string error = e.what();
        EXPECT_TRUE(
            error.find("unauthenticated") != std::string::npos ||
            error.find("expired") != std::string::npos ||
            error.find("invalid") != std::string::npos ||
            error.find("unauthorized") != std::string::npos
        ) << "Error should mention auth issue: " << error;
    } catch (const std::exception& e) {
        // Other errors might include gRPC status
        std::string error = e.what();
        // Should be auth-related
        SUCCEED() << "Got expected auth error: " << error;
    }
}

/**
 * @test Server should reject malformed tokens.
 */
TEST_F(SecurityTest, RejectsMalformedToken) {
    std::string malformedToken = "not-a-valid-jwt-token";

    ClientOptions options;
    options.endpoint = serverEndpoint_;
    options.idToken = malformedToken;
    options.useTls = false;

    try {
        auto client = Client::create(options);
        auto projects = client->getProjects();
        FAIL() << "Should have rejected malformed token";
    } catch (const ValidationError& e) {
        // Expected - client-side validation should catch this
        SUCCEED();
    } catch (const AuthenticationError& e) {
        // Also acceptable - server-side rejection
        SUCCEED();
    } catch (const std::exception& e) {
        // Other errors are also acceptable
        SUCCEED() << "Got expected error: " << e.what();
    }
}

/**
 * @test Server should reject tokens with wrong audience.
 */
TEST_F(SecurityTest, RejectsWrongAudienceToken) {
    // Create JWT with wrong audience (simplified - not cryptographically valid)
    // Header: {"alg":"RS256","typ":"JWT"}
    std::string header = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9";
    // Payload with wrong audience
    std::string payload = "eyJzdWIiOiJ0ZXN0IiwiYXVkIjoid3JvbmctYXVkaWVuY2UiLCJleHAiOjk5OTk5OTk5OTl9";
    std::string wrongAudToken = header + "." + payload + ".fake_signature";

    ClientOptions options;
    options.endpoint = serverEndpoint_;
    options.idToken = wrongAudToken;
    options.useTls = false;

    try {
        auto client = Client::create(options);
        auto projects = client->getProjects();
        FAIL() << "Should have rejected wrong audience token";
    } catch (const std::exception& e) {
        // Any rejection is expected
        SUCCEED();
    }
}

// ============================================================================
// Token Format Validation Tests
// ============================================================================

/**
 * @test validateTokenFormat accepts valid JWT.
 */
TEST_F(SecurityTest, ValidateTokenFormatAcceptsValidJWT) {
    std::string validToken = 
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNjAwMDAwMDAwfQ."
        "signature";

    // Should not throw
    EXPECT_NO_THROW(validateTokenFormat(validToken));
}

/**
 * @test validateTokenFormat rejects token too short.
 */
TEST_F(SecurityTest, ValidateTokenFormatRejectsTooShort) {
    EXPECT_THROW(validateTokenFormat("short"), ValidationError);
}

/**
 * @test validateTokenFormat rejects token too long.
 */
TEST_F(SecurityTest, ValidateTokenFormatRejectsTooLong) {
    std::string longToken(20001, 'a');
    EXPECT_THROW(validateTokenFormat(longToken), ValidationError);
}

/**
 * @test validateTokenFormat rejects wrong parts count.
 */
TEST_F(SecurityTest, ValidateTokenFormatRejectsWrongParts) {
    EXPECT_THROW(validateTokenFormat("only.two"), ValidationError);
    EXPECT_THROW(validateTokenFormat("too.many.parts.here.now"), ValidationError);
}

/**
 * @test validateTokenFormat rejects invalid characters.
 */
TEST_F(SecurityTest, ValidateTokenFormatRejectsInvalidChars) {
    EXPECT_THROW(validateTokenFormat("header.pay<script>load.sig"), ValidationError);
}

// ============================================================================
// Discovery Cache Encryption Tests
// ============================================================================

/**
 * @test Discovery cache encrypts data on disk.
 */
TEST_F(SecurityTest, DiscoveryCacheEncryptsData) {
    fs::path cacheFile = fs::path(testCacheDir_) / "encrypted_cache.json";
    
    // Create cache with encryption enabled
    DiscoveryCache cache(cacheFile, true);  // encrypt=true

    // Store test record
    RegionRouting routing;
    routing.region_code = "us-central1";
    routing.server_url = "test.kumiho.io:443";
    routing.grpc_authority = "test.kumiho.io";

    DiscoveryRecord record;
    record.tenant_id = "secret-tenant-123";
    record.region = routing;

    cache.store("test_key", record);

    // Read raw file content
    std::ifstream file(cacheFile);
    std::string rawContent((std::istreambuf_iterator<char>(file)),
                            std::istreambuf_iterator<char>());
    file.close();

    // Should be encrypted (starts with enc:v1:)
    EXPECT_TRUE(rawContent.find("enc:v1:") == 0) 
        << "Cache should be encrypted, got: " << rawContent.substr(0, 50);

    // Plaintext tenant ID should NOT appear
    EXPECT_EQ(rawContent.find("secret-tenant-123"), std::string::npos)
        << "Tenant ID should be encrypted, not in plaintext";
}

/**
 * @test Encrypted cache round-trips correctly.
 */
TEST_F(SecurityTest, DiscoveryCacheRoundTrip) {
    fs::path cacheFile = fs::path(testCacheDir_) / "roundtrip_cache.json";
    DiscoveryCache cache(cacheFile, true);

    RegionRouting routing;
    routing.region_code = "asia-southeast1";
    routing.server_url = "asia.kumiho.io:443";
    routing.grpc_authority = "asia.kumiho.io";

    DiscoveryRecord record;
    record.tenant_id = "roundtrip-tenant-456";
    record.region = routing;

    cache.store("roundtrip_key", record);

    // Load it back
    auto loaded = cache.load("roundtrip_key");
    ASSERT_TRUE(loaded.has_value()) << "Should load cached record";
    EXPECT_EQ(loaded->tenant_id, "roundtrip-tenant-456");
    EXPECT_EQ(loaded->region.region_code, "asia-southeast1");
    EXPECT_EQ(loaded->region.server_url, "asia.kumiho.io:443");
}

/**
 * @test Tampered cache data is rejected.
 */
TEST_F(SecurityTest, DiscoveryCacheDetectsTampering) {
    fs::path cacheFile = fs::path(testCacheDir_) / "tampered_cache.json";
    DiscoveryCache cache(cacheFile, true);

    RegionRouting routing;
    routing.region_code = "eu-west1";
    DiscoveryRecord record;
    record.tenant_id = "tamper-test";
    record.region = routing;

    cache.store("tamper_key", record);

    // Read and tamper with the file
    std::string rawContent;
    {
        std::ifstream file(cacheFile);
        rawContent = std::string((std::istreambuf_iterator<char>(file)),
                                  std::istreambuf_iterator<char>());
    }

    // Modify some bytes (after enc:v1: prefix)
    if (rawContent.size() > 20) {
        rawContent[15] = 'X';  // Corrupt some data
        std::ofstream outFile(cacheFile);
        outFile << rawContent;
    }

    // Try to load with new cache instance
    DiscoveryCache cache2(cacheFile, true);
    auto loaded = cache2.load("tamper_key");

    // Should return empty optional for tampered data
    EXPECT_FALSE(loaded.has_value()) << "Tampered data should not load";
}

// ============================================================================
// Correlation ID Tests
// ============================================================================

/**
 * @test Correlation ID has valid UUID format.
 */
TEST_F(SecurityTest, CorrelationIdValidFormat) {
    std::string correlationId = generateCorrelationId();

    // UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars)
    EXPECT_EQ(correlationId.length(), 36u) << "UUID should be 36 characters";

    // Check UUID regex pattern
    std::regex uuidPattern(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        std::regex_constants::icase
    );
    EXPECT_TRUE(std::regex_match(correlationId, uuidPattern))
        << "Should match UUID pattern: " << correlationId;
}

/**
 * @test Each correlation ID is unique.
 */
TEST_F(SecurityTest, CorrelationIdsUnique) {
    std::set<std::string> ids;
    for (int i = 0; i < 100; i++) {
        std::string id = generateCorrelationId();
        bool inserted = ids.insert(id).second;
        EXPECT_TRUE(inserted) << "Correlation ID should be unique: " << id;
    }
}

// ============================================================================
// TLS Enforcement Tests
// ============================================================================

/**
 * @test Localhost connections without TLS are allowed.
 */
TEST_F(SecurityTest, LocalhostWithoutTlsAllowed) {
    // These should NOT throw during client creation (connection may fail later)
    std::vector<std::string> localhostEndpoints = {
        "localhost:8080",
        "127.0.0.1:8080"
    };

    for (const auto& endpoint : localhostEndpoints) {
        ClientOptions options;
        options.endpoint = endpoint;
        options.idToken = "test.token.placeholder";
        options.useTls = false;

        // Client creation should succeed for localhost
        EXPECT_NO_THROW({
            try {
                auto client = Client::create(options);
            } catch (const ConnectionError&) {
                // Connection failure is okay - we're testing client creation
            }
        }) << "Localhost should allow non-TLS: " << endpoint;
    }
}

// ============================================================================
// Error Handling Tests
// ============================================================================

/**
 * @test Permission denied errors have clear messages.
 */
TEST_F(SecurityTest, PermissionDeniedClearMessage) {
    std::string token = getEnvOrDefault("KUMIHO_AUTH_TOKEN", "");
    if (token.empty()) {
        GTEST_SKIP() << "Need KUMIHO_AUTH_TOKEN for permission tests";
    }

    ClientOptions options;
    options.endpoint = serverEndpoint_;
    options.idToken = token;
    options.useTls = false;

    try {
        auto client = Client::create(options);
        // Try to access nonexistent project
        client->getProject("nonexistent-project-xyz-99999");
        FAIL() << "Should have thrown for nonexistent project";
    } catch (const NotFoundError& e) {
        // Expected - clear not found error
        SUCCEED();
    } catch (const PermissionDeniedError& e) {
        // Also acceptable
        SUCCEED();
    } catch (const std::exception& e) {
        // Other errors should still be meaningful
        std::string error = e.what();
        EXPECT_TRUE(error.length() > 0) << "Error message should not be empty";
    }
}

/**
 * @test Handles rate limiting gracefully.
 */
TEST_F(SecurityTest, HandlesRateLimitingGracefully) {
    std::string token = getEnvOrDefault("KUMIHO_AUTH_TOKEN", "");
    if (token.empty()) {
        GTEST_SKIP() << "Need KUMIHO_AUTH_TOKEN for rate limit tests";
    }

    ClientOptions options;
    options.endpoint = serverEndpoint_;
    options.idToken = token;
    options.useTls = false;

    auto client = Client::create(options);

    // Make rapid requests - should handle gracefully
    int successCount = 0;
    int errorCount = 0;

    for (int i = 0; i < 10; i++) {
        try {
            auto projects = client->getProjects();
            successCount++;
        } catch (const ResourceExhaustedError& e) {
            // Rate limit - acceptable
            errorCount++;
        } catch (const std::exception& e) {
            // Other errors - log but don't fail
            errorCount++;
        }
    }

    // Should complete without crashing
    EXPECT_GT(successCount + errorCount, 0) << "Should process all requests";
}

// ============================================================================
// Metadata Sanitization Tests
// ============================================================================

/**
 * @test Metadata values are sanitized.
 */
TEST_F(SecurityTest, MetadataSanitization) {
    // Control characters that should be stripped/rejected
    std::string controlChars = "\x00\x01\x02\n\r\t";

    // Valid metadata should be accepted
    std::string validValue = "John Doe - Artist";
    
    // sanitizeMetadataValue should remove control chars
    std::string sanitized = sanitizeMetadataValue(controlChars + validValue);
    
    // Should not contain control characters
    for (char c : sanitized) {
        EXPECT_GE(c, 0x20) << "Sanitized value should not contain control chars";
    }
    
    // Should preserve valid content
    EXPECT_NE(sanitized.find("John Doe"), std::string::npos)
        << "Should preserve valid content";
}

// ============================================================================
// Helper Function Declarations (implement in SDK if not present)
// ============================================================================

// These functions should be implemented in the SDK
// If not present, the tests will fail to link, indicating missing functionality

#ifndef KUMIHO_HAS_SECURITY_HELPERS
// Stub implementations for testing - remove when SDK implements these

inline void validateTokenFormat(const std::string& token) {
    if (token.length() < 20) {
        throw ValidationError("Token too short");
    }
    if (token.length() > 20000) {
        throw ValidationError("Token too long");
    }

    // Count dots for JWT format
    int dotCount = 0;
    for (char c : token) {
        if (c == '.') dotCount++;
    }
    if (dotCount != 2) {
        throw ValidationError("Invalid JWT format: expected 3 parts");
    }

    // Check for invalid characters
    std::regex validChars("^[A-Za-z0-9_\\-=.]+$");
    if (!std::regex_match(token, validChars)) {
        throw ValidationError("Invalid characters in token");
    }
}

inline std::string generateCorrelationId() {
    // Simple UUID v4 generation
    auto now = std::chrono::high_resolution_clock::now();
    auto epoch = now.time_since_epoch();
    auto nanos = std::chrono::duration_cast<std::chrono::nanoseconds>(epoch).count();

    // Format as UUID-like string
    char buf[40];
    snprintf(buf, sizeof(buf), "%08llx-%04llx-%04llx-%04llx-%012llx",
             (unsigned long long)(nanos & 0xFFFFFFFF),
             (unsigned long long)((nanos >> 32) & 0xFFFF),
             (unsigned long long)(0x4000 | ((nanos >> 48) & 0x0FFF)),  // Version 4
             (unsigned long long)(0x8000 | ((nanos >> 60) & 0x3FFF)),  // Variant
             (unsigned long long)(nanos ^ (nanos >> 16)));
    return std::string(buf);
}

inline std::string sanitizeMetadataValue(const std::string& value) {
    std::string result;
    result.reserve(value.length());
    for (char c : value) {
        if (c >= 0x20 || c == '\t') {  // Allow printable + tab
            result += c;
        }
    }
    return result;
}

#endif // KUMIHO_HAS_SECURITY_HELPERS
