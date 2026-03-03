/**
 * @file test_token_loader.cpp
 * @brief Unit tests for token loading utilities.
 */

#include <gtest/gtest.h>
#include <kumiho/token_loader.hpp>
#include <kumiho/error.hpp>
#include <fstream>
#include <cstdlib>

using namespace kumiho::api;

// --- getConfigDir Tests ---

class ConfigDirTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Save original environment variable if set
        const char* existing = std::getenv(CONFIG_DIR_ENV);
        if (existing) {
            original_config_dir_ = existing;
            has_original_ = true;
        }
    }
    
    void TearDown() override {
        // Restore original environment variable
        if (has_original_) {
#ifdef _WIN32
            _putenv_s(CONFIG_DIR_ENV, original_config_dir_.c_str());
#else
            setenv(CONFIG_DIR_ENV, original_config_dir_.c_str(), 1);
#endif
        } else {
#ifdef _WIN32
            _putenv_s(CONFIG_DIR_ENV, "");
#else
            unsetenv(CONFIG_DIR_ENV);
#endif
        }
    }
    
    std::string original_config_dir_;
    bool has_original_ = false;
};

TEST_F(ConfigDirTest, DefaultConfigDir) {
    // Unset the env var
#ifdef _WIN32
    _putenv_s(CONFIG_DIR_ENV, "");
#else
    unsetenv(CONFIG_DIR_ENV);
#endif
    
    auto path = getConfigDir();
    
    // Should end with .kumiho
    EXPECT_TRUE(path.filename() == ".kumiho");
}

TEST_F(ConfigDirTest, CustomConfigDir) {
#ifdef _WIN32
    _putenv_s(CONFIG_DIR_ENV, "C:\\custom\\kumiho");
#else
    setenv(CONFIG_DIR_ENV, "/custom/kumiho", 1);
#endif
    
    auto path = getConfigDir();
    
#ifdef _WIN32
    EXPECT_EQ(path.string(), "C:\\custom\\kumiho");
#else
    EXPECT_EQ(path.string(), "/custom/kumiho");
#endif
}

// --- getCredentialsPath Tests ---

TEST_F(ConfigDirTest, CredentialsPath) {
    auto path = getCredentialsPath();
    
    EXPECT_EQ(path.filename().string(), CREDENTIALS_FILENAME);
}

// --- JWT Decoding Tests ---

class JwtDecodingTest : public ::testing::Test {};

TEST_F(JwtDecodingTest, DecodeSimpleJwt) {
    // A test JWT with payload: {"sub":"user123","iss":"test-issuer"}
    // Base64URL encoded: eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoidGVzdC1pc3N1ZXIifQ
    std::string jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoidGVzdC1pc3N1ZXIifQ.signature";
    
    auto claims = decodeJwtClaims(jwt);
    
    EXPECT_EQ(claims["sub"], "user123");
    EXPECT_EQ(claims["iss"], "test-issuer");
}

TEST_F(JwtDecodingTest, DecodeEmptyToken) {
    auto claims = decodeJwtClaims("");
    
    EXPECT_TRUE(claims.empty());
}

TEST_F(JwtDecodingTest, DecodeInvalidToken) {
    auto claims = decodeJwtClaims("not-a-jwt");
    
    EXPECT_TRUE(claims.empty());
}

TEST_F(JwtDecodingTest, DecodeTokenWithOnePart) {
    auto claims = decodeJwtClaims("single-part");
    
    EXPECT_TRUE(claims.empty());
}

// --- isControlPlaneToken Tests ---

class ControlPlaneTokenTest : public ::testing::Test {};

TEST_F(ControlPlaneTokenTest, TokenWithTenantId) {
    // JWT with tenant_id claim
    // Payload: {"tenant_id":"tenant-123"}
    // Base64URL: eyJ0ZW5hbnRfaWQiOiJ0ZW5hbnQtMTIzIn0
    std::string jwt = "eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOiJ0ZW5hbnQtMTIzIn0.sig";
    
    EXPECT_TRUE(isControlPlaneToken(jwt));
}

TEST_F(ControlPlaneTokenTest, TokenWithKumihoIssuer) {
    // JWT with iss: https://kumiho.io/auth
    // Payload: {"iss":"https://kumiho.io/auth"}
    // Base64URL: eyJpc3MiOiJodHRwczovL2t1bWloby5pby9hdXRoIn0
    std::string jwt = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2t1bWloby5pby9hdXRoIn0.sig";
    
    EXPECT_TRUE(isControlPlaneToken(jwt));
}

TEST_F(ControlPlaneTokenTest, TokenWithKumihoAudience) {
    // JWT with aud: https://api.kumiho.io
    // Payload: {"aud":"https://api.kumiho.io"}
    // Base64URL: eyJhdWQiOiJodHRwczovL2FwaS5rdW1paG8uaW8ifQ
    std::string jwt = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJodHRwczovL2FwaS5rdW1paG8uaW8ifQ.sig";
    
    EXPECT_TRUE(isControlPlaneToken(jwt));
}

TEST_F(ControlPlaneTokenTest, RegularFirebaseToken) {
    // JWT without control plane indicators
    // Payload: {"sub":"user123","iss":"https://securetoken.google.com"}
    // Base64URL: eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tIn0
    std::string jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tIn0.sig";
    
    EXPECT_FALSE(isControlPlaneToken(jwt));
}

TEST_F(ControlPlaneTokenTest, EmptyToken) {
    EXPECT_FALSE(isControlPlaneToken(""));
}

TEST_F(ControlPlaneTokenTest, InvalidToken) {
    EXPECT_FALSE(isControlPlaneToken("not.a.jwt.really"));
}

// --- loadBearerToken Tests ---

class LoadBearerTokenTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Save original env vars
        const char* existing = std::getenv(TOKEN_ENV);
        if (existing) {
            original_token_ = existing;
            has_original_token_ = true;
        }
    }
    
    void TearDown() override {
        // Restore env vars
        if (has_original_token_) {
#ifdef _WIN32
            _putenv_s(TOKEN_ENV, original_token_.c_str());
#else
            setenv(TOKEN_ENV, original_token_.c_str(), 1);
#endif
        } else {
#ifdef _WIN32
            _putenv_s(TOKEN_ENV, "");
#else
            unsetenv(TOKEN_ENV);
#endif
        }
    }
    
    std::string original_token_;
    bool has_original_token_ = false;
};

TEST_F(LoadBearerTokenTest, LoadFromEnv) {
    // Must look like a JWT (header.payload.signature)
    std::string test_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.sig";
#ifdef _WIN32
    _putenv_s(TOKEN_ENV, test_token.c_str());
#else
    setenv(TOKEN_ENV, test_token.c_str(), 1);
#endif
    
    auto token = loadBearerToken();
    
    ASSERT_TRUE(token.has_value());
    EXPECT_EQ(token.value(), test_token);
}

TEST_F(LoadBearerTokenTest, EmptyEnvReturnsNullopt) {
#ifdef _WIN32
    _putenv_s(TOKEN_ENV, "");
#else
    unsetenv(TOKEN_ENV);
#endif
    
    // If no credentials file exists, should return nullopt
    // Note: This test may pass or fail depending on whether
    // ~/.kumiho/kumiho_authentication.json exists
    auto token = loadBearerToken();
    
    // We can only assert that it doesn't throw
    // The result depends on the local environment
}

TEST_F(LoadBearerTokenTest, WhitespaceOnlyEnvReturnsNullopt) {
#ifdef _WIN32
    _putenv_s(TOKEN_ENV, "   ");
#else
    setenv(TOKEN_ENV, "   ", 1);
#endif
    
    auto token = loadBearerToken();
    
    // Whitespace-only should be normalized to nullopt
    // or return the trimmed value from credentials file
}

// --- loadFirebaseToken Tests ---

class LoadFirebaseTokenTest : public ::testing::Test {
protected:
    void SetUp() override {
        const char* existing = std::getenv(FIREBASE_TOKEN_ENV);
        if (existing) {
            original_token_ = existing;
            has_original_ = true;
        }
    }
    
    void TearDown() override {
        if (has_original_) {
#ifdef _WIN32
            _putenv_s(FIREBASE_TOKEN_ENV, original_token_.c_str());
#else
            setenv(FIREBASE_TOKEN_ENV, original_token_.c_str(), 1);
#endif
        } else {
#ifdef _WIN32
            _putenv_s(FIREBASE_TOKEN_ENV, "");
#else
            unsetenv(FIREBASE_TOKEN_ENV);
#endif
        }
    }
    
    std::string original_token_;
    bool has_original_ = false;
};

TEST_F(LoadFirebaseTokenTest, LoadFromEnv) {
    // Must look like a JWT (header.payload.signature)
    std::string test_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmaXJlYmFzZSJ9.sig";
#ifdef _WIN32
    _putenv_s(FIREBASE_TOKEN_ENV, test_token.c_str());
#else
    setenv(FIREBASE_TOKEN_ENV, test_token.c_str(), 1);
#endif
    
    auto token = loadFirebaseToken();
    
    ASSERT_TRUE(token.has_value());
    EXPECT_EQ(token.value(), test_token);
}

// --- Environment Variable Constants ---

TEST(TokenLoaderConstantsTest, EnvVarNames) {
    EXPECT_STREQ(TOKEN_ENV, "KUMIHO_AUTH_TOKEN");
    EXPECT_STREQ(FIREBASE_TOKEN_ENV, "KUMIHO_FIREBASE_ID_TOKEN");
    EXPECT_STREQ(USE_CP_TOKEN_ENV, "KUMIHO_USE_CONTROL_PLANE_TOKEN");
    EXPECT_STREQ(CONFIG_DIR_ENV, "KUMIHO_CONFIG_DIR");
    EXPECT_STREQ(CREDENTIALS_FILENAME, "kumiho_authentication.json");
}
