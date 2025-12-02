/**
 * @file token_loader.cpp
 * @brief Implementation of token loading utilities.
 */

#include "kumiho/token_loader.hpp"
#include "kumiho/error.hpp"

#include <fstream>
#include <sstream>
#include <cstdlib>
#include <regex>
#include <algorithm>

// Base64 decoding for JWT parsing
#ifdef _WIN32
#include <windows.h>
#include <wincrypt.h>
#pragma comment(lib, "crypt32.lib")
#else
// Use a simple base64 decoder for non-Windows platforms
#endif

namespace kumiho {
namespace api {

namespace {

// Get environment variable safely
std::string getEnvVar(const char* name) {
    const char* value = std::getenv(name);
    return value ? value : "";
}

// Normalize a string (trim whitespace)
std::optional<std::string> normalize(const std::string& value) {
    std::string trimmed = value;
    // Trim left
    trimmed.erase(trimmed.begin(), std::find_if(trimmed.begin(), trimmed.end(), [](int ch) {
        return !std::isspace(ch);
    }));
    // Trim right
    trimmed.erase(std::find_if(trimmed.rbegin(), trimmed.rend(), [](int ch) {
        return !std::isspace(ch);
    }).base(), trimmed.end());
    
    if (trimmed.empty()) {
        return std::nullopt;
    }
    return trimmed;
}

// Check if environment flag is set to truthy value
bool envFlag(const char* name) {
    std::string value = getEnvVar(name);
    if (value.empty()) return false;
    
    // Normalize to lowercase
    std::transform(value.begin(), value.end(), value.begin(), ::tolower);
    
    // Trim
    value.erase(0, value.find_first_not_of(" \t\r\n"));
    value.erase(value.find_last_not_of(" \t\r\n") + 1);
    
    return value == "1" || value == "true" || value == "yes";
}

// Read credentials from JSON file
struct CredentialsData {
    std::optional<std::string> control_plane_token;
    std::optional<std::string> id_token;
};

CredentialsData readCredentials() {
    CredentialsData data;
    
    auto path = getCredentialsPath();
    if (!std::filesystem::exists(path)) {
        return data;
    }
    
    try {
        std::ifstream file(path);
        if (!file.is_open()) {
            return data;
        }
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string content = buffer.str();
        
        // Simple JSON extraction
        std::regex cpTokenRe("\"control_plane_token\"\\s*:\\s*\"([^\"\\\\]*(\\\\.[^\"\\\\]*)*)\"");
        std::regex idTokenRe("\"id_token\"\\s*:\\s*\"([^\"\\\\]*(\\\\.[^\"\\\\]*)*)\"");
        
        std::smatch match;
        if (std::regex_search(content, match, cpTokenRe)) {
            data.control_plane_token = normalize(match[1].str());
        }
        if (std::regex_search(content, match, idTokenRe)) {
            data.id_token = normalize(match[1].str());
        }
        
    } catch (const std::exception&) {
        // Ignore errors reading credentials
    }
    
    return data;
}

// Base64 URL decode (JWT uses URL-safe base64)
std::string base64UrlDecode(const std::string& input) {
    std::string base64 = input;
    
    // Replace URL-safe characters
    std::replace(base64.begin(), base64.end(), '-', '+');
    std::replace(base64.begin(), base64.end(), '_', '/');
    
    // Add padding
    while (base64.size() % 4 != 0) {
        base64 += '=';
    }
    
#ifdef _WIN32
    DWORD decodedLen = 0;
    if (!CryptStringToBinaryA(base64.c_str(), (DWORD)base64.size(), CRYPT_STRING_BASE64,
                              nullptr, &decodedLen, nullptr, nullptr)) {
        return "";
    }
    
    std::string decoded(decodedLen, '\0');
    if (!CryptStringToBinaryA(base64.c_str(), (DWORD)base64.size(), CRYPT_STRING_BASE64,
                              reinterpret_cast<BYTE*>(&decoded[0]), &decodedLen, nullptr, nullptr)) {
        return "";
    }
    decoded.resize(decodedLen);
    return decoded;
#else
    // Simple base64 decoder for non-Windows
    static const std::string base64_chars = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789+/";
    
    std::string decoded;
    int val = 0, valb = -8;
    for (unsigned char c : base64) {
        if (c == '=') break;
        size_t pos = base64_chars.find(c);
        if (pos == std::string::npos) continue;
        val = (val << 6) + (int)pos;
        valb += 6;
        if (valb >= 0) {
            decoded.push_back(char((val >> valb) & 0xFF));
            valb -= 8;
        }
    }
    return decoded;
#endif
}

} // anonymous namespace

// --- Public API ---

std::filesystem::path getConfigDir() {
    std::string envDir = getEnvVar(CONFIG_DIR_ENV);
    if (!envDir.empty()) {
        return std::filesystem::path(envDir);
    }
    
    // Get home directory
#ifdef _WIN32
    std::string home = getEnvVar("USERPROFILE");
    if (home.empty()) {
        std::string drive = getEnvVar("HOMEDRIVE");
        std::string path = getEnvVar("HOMEPATH");
        home = drive + path;
    }
#else
    std::string home = getEnvVar("HOME");
#endif
    
    if (home.empty()) {
        throw AuthenticationError("Cannot determine home directory");
    }
    
    return std::filesystem::path(home) / ".kumiho";
}

std::filesystem::path getCredentialsPath() {
    return getConfigDir() / CREDENTIALS_FILENAME;
}

std::optional<std::string> loadBearerToken() {
    // 1. Check environment variable
    std::string envToken = getEnvVar(TOKEN_ENV);
    auto normalized = normalize(envToken);
    if (normalized) {
        return normalized;
    }
    
    // 2. Read from credentials file
    auto creds = readCredentials();
    bool preferControlPlane = envFlag(USE_CP_TOKEN_ENV);
    
    if (preferControlPlane && creds.control_plane_token) {
        return creds.control_plane_token;
    }
    if (creds.id_token) {
        return creds.id_token;
    }
    if (creds.control_plane_token) {
        return creds.control_plane_token;
    }
    
    return std::nullopt;
}

std::optional<std::string> loadFirebaseToken() {
    // 1. Check environment variable
    std::string envToken = getEnvVar(FIREBASE_TOKEN_ENV);
    auto normalized = normalize(envToken);
    if (normalized) {
        return normalized;
    }
    
    // 2. Read id_token from credentials file
    auto creds = readCredentials();
    return creds.id_token;
}

std::map<std::string, std::string> decodeJwtClaims(const std::string& token) {
    std::map<std::string, std::string> claims;
    
    // Split by dots
    std::vector<std::string> parts;
    std::stringstream ss(token);
    std::string part;
    while (std::getline(ss, part, '.')) {
        parts.push_back(part);
    }
    
    if (parts.size() < 2) {
        return claims;
    }
    
    // Decode the payload (second part)
    std::string payload = base64UrlDecode(parts[1]);
    if (payload.empty()) {
        return claims;
    }
    
    // Simple JSON extraction for string values
    std::regex stringRe("\"([^\"]+)\"\\s*:\\s*\"([^\"\\\\]*(\\\\.[^\"\\\\]*)*)\"");
    std::sregex_iterator it(payload.begin(), payload.end(), stringRe);
    std::sregex_iterator end;
    
    for (; it != end; ++it) {
        std::string key = (*it)[1].str();
        std::string value = (*it)[2].str();
        claims[key] = value;
    }
    
    return claims;
}

bool isControlPlaneToken(const std::string& token) {
    auto claims = decodeJwtClaims(token);
    if (claims.empty()) {
        return false;
    }
    
    // Check for tenant_id claim
    if (claims.find("tenant_id") != claims.end()) {
        return true;
    }
    
    // Check issuer
    auto issIt = claims.find("iss");
    if (issIt != claims.end()) {
        if (issIt->second.find("https://kumiho.io") == 0) {
            return true;
        }
    }
    
    // Check audience
    auto audIt = claims.find("aud");
    if (audIt != claims.end()) {
        if (audIt->second.find("https://api.kumiho.io") == 0) {
            return true;
        }
    }
    
    return false;
}

} // namespace api
} // namespace kumiho
