/**
 * @file discovery.cpp
 * @brief Implementation of discovery and auto-configuration.
 */

#include "kumiho/discovery.hpp"
#include "kumiho/token_loader.hpp"
#include "kumiho/error.hpp"
#include "kumiho/client.hpp"

#include <fstream>
#include <sstream>
#include <cstdlib>
#include <ctime>
#include <regex>
#include <random>
#include <iomanip>
#include <array>

#ifdef _WIN32
#include <windows.h>
#include <wincrypt.h>
#pragma comment(lib, "advapi32.lib")
#else
#include <unistd.h>
#endif

// Simple JSON parsing (we avoid external dependencies)
// For production, consider using nlohmann/json or rapidjson

namespace kumiho {
namespace api {

namespace {

// Default cache key when no tenant hint is provided
const std::string DEFAULT_CACHE_KEY = "__default__";

// Get environment variable safely
std::string getEnvVar(const char* name, const std::string& defaultValue = "") {
    const char* value = std::getenv(name);
    return value ? value : defaultValue;
}

// Parse ISO8601 timestamp to time_point
std::chrono::system_clock::time_point parseIso8601(const std::string& timestamp) {
    if (timestamp.empty()) {
        throw DiscoveryError("Discovery payload missing required timestamp");
    }
    
    std::string text = timestamp;
    // Replace Z with +00:00
    if (!text.empty() && text.back() == 'Z') {
        text = text.substr(0, text.size() - 1);
    }
    
    // Parse using std::get_time
    std::tm tm = {};
    std::istringstream ss(text);
    ss >> std::get_time(&tm, "%Y-%m-%dT%H:%M:%S");
    
    if (ss.fail()) {
        throw DiscoveryError("Invalid ISO8601 timestamp: " + timestamp);
    }
    
    // Convert to time_point (assuming UTC)
    std::time_t t = 
#ifdef _WIN32
        _mkgmtime(&tm);
#else
        timegm(&tm);
#endif
    
    return std::chrono::system_clock::from_time_t(t);
}

// Format time_point to ISO8601 string
std::string toIso8601(const std::chrono::system_clock::time_point& tp) {
    std::time_t t = std::chrono::system_clock::to_time_t(tp);
    std::tm tm;
#ifdef _WIN32
    gmtime_s(&tm, &t);
#else
    gmtime_r(&t, &tm);
#endif
    char buf[32];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm);
    return buf;
}

// Simple JSON string extraction (handles basic cases)
std::string extractJsonString(const std::string& json, const std::string& key) {
    std::string pattern = "\"" + key + "\"\\s*:\\s*\"([^\"\\\\]*(\\\\.[^\"\\\\]*)*)\"";
    std::regex re(pattern);
    std::smatch match;
    if (std::regex_search(json, match, re)) {
        return match[1].str();
    }
    return "";
}

// Extract JSON integer
int extractJsonInt(const std::string& json, const std::string& key) {
    std::string pattern = "\"" + key + "\"\\s*:\\s*(-?\\d+)";
    std::regex re(pattern);
    std::smatch match;
    if (std::regex_search(json, match, re)) {
        return std::stoi(match[1].str());
    }
    return 0;
}

// Extract JSON object as substring
std::string extractJsonObject(const std::string& json, const std::string& key) {
    std::string pattern = "\"" + key + "\"\\s*:\\s*\\{";
    std::regex re(pattern);
    std::smatch match;
    if (std::regex_search(json, match, re)) {
        size_t start = match.position(0) + match.length(0) - 1;
        int depth = 1;
        size_t end = start + 1;
        while (end < json.size() && depth > 0) {
            if (json[end] == '{') depth++;
            else if (json[end] == '}') depth--;
            end++;
        }
        return json.substr(start, end - start);
    }
    return "";
}

// Extract JSON array of strings
std::vector<std::string> extractJsonStringArray(const std::string& json, const std::string& key) {
    std::vector<std::string> result;
    std::string pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]*)\\]";
    std::regex re(pattern);
    std::smatch match;
    if (std::regex_search(json, match, re)) {
        std::string arrayContent = match[1].str();
        std::regex strRe("\"([^\"\\\\]*(\\\\.[^\"\\\\]*)*)\"");
        std::sregex_iterator it(arrayContent.begin(), arrayContent.end(), strRe);
        std::sregex_iterator end;
        for (; it != end; ++it) {
            result.push_back((*it)[1].str());
        }
    }
    return result;
}

// Build the discovery endpoint URL
std::string buildDiscoveryUrl(const std::string& baseUrl) {
    std::string base = baseUrl;
    // Remove trailing slash
    while (!base.empty() && base.back() == '/') {
        base.pop_back();
    }
    
    if (base.find("/api/discovery/tenant") != std::string::npos) {
        return base;
    }
    if (base.find("/api/discovery") != std::string::npos) {
        return base + "/tenant";
    }
    if (base.find("/api") != std::string::npos) {
        return base + "/discovery/tenant";
    }
    return base + "/api/discovery/tenant";
}

// Ensure we have a Firebase token (not a control-plane token)
std::string ensureFirebaseToken(const std::string& candidate) {
    if (!isControlPlaneToken(candidate)) {
        return candidate;
    }
    
    auto firebase = loadFirebaseToken();
    if (firebase) {
        return *firebase;
    }
    
    throw DiscoveryError(
        "Control Plane JWT detected but no Firebase ID token is available. "
        "Run 'kumiho-auth login' to refresh credentials."
    );
}

} // anonymous namespace

// --- CacheControl implementation ---

bool CacheControl::isExpired() const {
    return std::chrono::system_clock::now() >= expires_at;
}

bool CacheControl::shouldRefresh() const {
    return std::chrono::system_clock::now() >= refresh_at;
}

// --- Encryption helpers ---

namespace {

// Simple SHA-256 implementation for key derivation (no external dependencies)
// This is a simplified version - production should use OpenSSL or similar
std::array<uint8_t, 32> simpleSha256(const std::string& input) {
    // Using a simple hash for key derivation
    // In production, use OpenSSL SHA256 or platform crypto API
    std::array<uint8_t, 32> result = {};
    
#ifdef _WIN32
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    
    if (CryptAcquireContext(&hProv, nullptr, nullptr, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {
        if (CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) {
            CryptHashData(hHash, reinterpret_cast<const BYTE*>(input.data()), 
                         static_cast<DWORD>(input.size()), 0);
            DWORD hashLen = 32;
            CryptGetHashParam(hHash, HP_HASHVAL, result.data(), &hashLen, 0);
            CryptDestroyHash(hHash);
        }
        CryptReleaseContext(hProv, 0);
    }
#else
    // Fallback: simple non-cryptographic hash for demo
    // Production should use OpenSSL: SHA256(input.data(), input.size(), result.data());
    std::hash<std::string> hasher;
    size_t h = hasher(input);
    for (size_t i = 0; i < 32; ++i) {
        result[i] = static_cast<uint8_t>((h >> (i % 8 * 8)) ^ (i * 0x9e3779b9));
        h = h * 0x5851F42D4C957F2D + i;
    }
#endif
    
    return result;
}

std::string getMachineId() {
#ifdef _WIN32
    // Windows: use Machine GUID from registry
    HKEY hKey;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, 
                      "SOFTWARE\\Microsoft\\Cryptography", 
                      0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        char value[256];
        DWORD valueLen = sizeof(value);
        if (RegQueryValueExA(hKey, "MachineGuid", nullptr, nullptr, 
                            reinterpret_cast<LPBYTE>(value), &valueLen) == ERROR_SUCCESS) {
            RegCloseKey(hKey);
            return std::string(value);
        }
        RegCloseKey(hKey);
    }
#else
    // Linux: try /etc/machine-id
    std::ifstream f("/etc/machine-id");
    if (f.is_open()) {
        std::string id;
        std::getline(f, id);
        if (!id.empty()) return id;
    }
    // Fallback: try /var/lib/dbus/machine-id
    f.open("/var/lib/dbus/machine-id");
    if (f.is_open()) {
        std::string id;
        std::getline(f, id);
        if (!id.empty()) return id;
    }
#endif
    
    // Fallback: generate and store a random ID
    auto idFile = getConfigDir() / ".machine_id";
    if (std::filesystem::exists(idFile)) {
        std::ifstream f(idFile);
        std::string id;
        std::getline(f, id);
        if (!id.empty()) return id;
    }
    
    // Generate new ID
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 15);
    std::ostringstream oss;
    for (int i = 0; i < 32; ++i) {
        oss << std::hex << dis(gen);
    }
    std::string newId = oss.str();
    
    // Store it
    std::filesystem::create_directories(idFile.parent_path());
    std::ofstream of(idFile);
    of << newId;
    
    return newId;
}

std::string base64Encode(const std::vector<uint8_t>& data) {
    static const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string result;
    result.reserve((data.size() + 2) / 3 * 4);
    
    for (size_t i = 0; i < data.size(); i += 3) {
        uint32_t n = static_cast<uint32_t>(data[i]) << 16;
        if (i + 1 < data.size()) n |= static_cast<uint32_t>(data[i + 1]) << 8;
        if (i + 2 < data.size()) n |= data[i + 2];
        
        result += chars[(n >> 18) & 0x3f];
        result += chars[(n >> 12) & 0x3f];
        result += (i + 1 < data.size()) ? chars[(n >> 6) & 0x3f] : '=';
        result += (i + 2 < data.size()) ? chars[n & 0x3f] : '=';
    }
    return result;
}

std::vector<uint8_t> base64Decode(const std::string& encoded) {
    static const int lookup[] = {
        -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
        -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
        -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,62,-1,-1,-1,63,
        52,53,54,55,56,57,58,59,60,61,-1,-1,-1,-1,-1,-1,
        -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,
        15,16,17,18,19,20,21,22,23,24,25,-1,-1,-1,-1,-1,
        -1,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
        41,42,43,44,45,46,47,48,49,50,51
    };
    
    std::vector<uint8_t> result;
    result.reserve(encoded.size() * 3 / 4);
    
    uint32_t val = 0;
    int bits = -8;
    for (char c : encoded) {
        if (c == '=') break;
        if (c < 0 || c >= 128 || lookup[c] < 0) continue;
        val = (val << 6) | lookup[c];
        bits += 6;
        if (bits >= 0) {
            result.push_back(static_cast<uint8_t>((val >> bits) & 0xff));
            bits -= 8;
        }
    }
    return result;
}

} // anonymous namespace

// --- DiscoveryCache implementation ---

DiscoveryCache::DiscoveryCache(const std::filesystem::path& path, bool encrypt)
    : path_(path.empty() ? getDefaultCachePath() : path), encrypt_(encrypt) {}

std::vector<uint8_t> DiscoveryCache::deriveKey() {
    std::string machineId = getMachineId();
    std::string userContext;
    
#ifdef _WIN32
    char username[256];
    DWORD size = sizeof(username);
    if (GetUserNameA(username, &size)) {
        userContext = username;
    }
#else
    userContext = std::to_string(getuid());
#endif
    
    std::string keyMaterial = "kumiho-discovery-cache-v1:" + machineId + ":" + userContext;
    auto hash = simpleSha256(keyMaterial);
    return std::vector<uint8_t>(hash.begin(), hash.end());
}

std::string DiscoveryCache::encryptContent(const std::string& plaintext) {
    auto key = deriveKey();
    
    // Generate random IV
    std::vector<uint8_t> iv(16);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dis(0, 255);
    for (auto& b : iv) b = static_cast<uint8_t>(dis(gen));
    
    // Generate key stream from key + IV
    std::string keyStreamInput(key.begin(), key.end());
    keyStreamInput.append(iv.begin(), iv.end());
    auto keyStream = simpleSha256(keyStreamInput);
    
    // Extend key stream for longer plaintexts
    std::vector<uint8_t> fullKeyStream(keyStream.begin(), keyStream.end());
    while (fullKeyStream.size() < plaintext.size()) {
        std::string ext(fullKeyStream.end() - 32, fullKeyStream.end());
        ext.insert(ext.begin(), key.begin(), key.end());
        auto more = simpleSha256(ext);
        fullKeyStream.insert(fullKeyStream.end(), more.begin(), more.end());
    }
    
    // XOR encrypt
    std::vector<uint8_t> ciphertext(plaintext.size());
    for (size_t i = 0; i < plaintext.size(); ++i) {
        ciphertext[i] = static_cast<uint8_t>(plaintext[i]) ^ fullKeyStream[i];
    }
    
    // Simple MAC (hash of key + iv + ciphertext)
    std::string macInput(key.begin(), key.end());
    macInput.append(iv.begin(), iv.end());
    macInput.append(ciphertext.begin(), ciphertext.end());
    auto mac = simpleSha256(macInput);
    
    // Combine: iv + ciphertext + mac[0:16]
    std::vector<uint8_t> result;
    result.insert(result.end(), iv.begin(), iv.end());
    result.insert(result.end(), ciphertext.begin(), ciphertext.end());
    result.insert(result.end(), mac.begin(), mac.begin() + 16);
    
    return "enc:v1:" + base64Encode(result);
}

std::string DiscoveryCache::decryptContent(const std::string& encrypted) {
    // Check for unencrypted legacy format
    if (encrypted.empty() || encrypted[0] == '{') {
        return encrypted;  // Return as-is for migration
    }
    
    if (encrypted.substr(0, 7) != "enc:v1:") {
        return "";  // Unknown format
    }
    
    try {
        auto raw = base64Decode(encrypted.substr(7));
        if (raw.size() < 32) return "";  // iv(16) + mac(16) minimum
        
        auto key = deriveKey();
        
        std::vector<uint8_t> iv(raw.begin(), raw.begin() + 16);
        std::vector<uint8_t> mac(raw.end() - 16, raw.end());
        std::vector<uint8_t> ciphertext(raw.begin() + 16, raw.end() - 16);
        
        // Verify MAC
        std::string macInput(key.begin(), key.end());
        macInput.append(iv.begin(), iv.end());
        macInput.append(ciphertext.begin(), ciphertext.end());
        auto expectedMac = simpleSha256(macInput);
        
        bool macValid = true;
        for (size_t i = 0; i < 16 && macValid; ++i) {
            if (mac[i] != expectedMac[i]) macValid = false;
        }
        if (!macValid) return "";  // Integrity check failed
        
        // Generate key stream
        std::string keyStreamInput(key.begin(), key.end());
        keyStreamInput.append(iv.begin(), iv.end());
        auto keyStream = simpleSha256(keyStreamInput);
        
        std::vector<uint8_t> fullKeyStream(keyStream.begin(), keyStream.end());
        while (fullKeyStream.size() < ciphertext.size()) {
            std::string ext(fullKeyStream.end() - 32, fullKeyStream.end());
            ext.insert(ext.begin(), key.begin(), key.end());
            auto more = simpleSha256(ext);
            fullKeyStream.insert(fullKeyStream.end(), more.begin(), more.end());
        }
        
        // XOR decrypt
        std::string plaintext;
        plaintext.reserve(ciphertext.size());
        for (size_t i = 0; i < ciphertext.size(); ++i) {
            plaintext += static_cast<char>(ciphertext[i] ^ fullKeyStream[i]);
        }
        
        return plaintext;
    } catch (...) {
        return "";
    }
}

std::optional<DiscoveryRecord> DiscoveryCache::load(const std::string& cache_key) {
    if (!std::filesystem::exists(path_)) {
        return std::nullopt;
    }
    
    try {
        std::ifstream file(path_);
        if (!file.is_open()) {
            return std::nullopt;
        }
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string rawContent = buffer.str();
        
        // Decrypt if needed
        std::string content = decryptContent(rawContent);
        if (content.empty()) {
            return std::nullopt;  // Decryption failed
        }
        
        // Find the entry for this cache_key
        std::string keyPattern = "\"" + cache_key + "\"\\s*:\\s*\\{";
        std::regex re(keyPattern);
        std::smatch match;
        if (!std::regex_search(content, match, re)) {
            return std::nullopt;
        }
        
        // Extract the nested object
        size_t start = match.position(0) + match.length(0) - 1;
        int depth = 1;
        size_t end = start + 1;
        while (end < content.size() && depth > 0) {
            if (content[end] == '{') depth++;
            else if (content[end] == '}') depth--;
            end++;
        }
        std::string entry = content.substr(start, end - start);
        
        // Parse the discovery record
        DiscoveryRecord record;
        record.tenant_id = extractJsonString(entry, "tenant_id");
        if (record.tenant_id.empty()) {
            return std::nullopt;
        }
        
        std::string tenantName = extractJsonString(entry, "tenant_name");
        if (!tenantName.empty()) {
            record.tenant_name = tenantName;
        }
        
        record.roles = extractJsonStringArray(entry, "roles");
        
        // Parse region
        std::string regionJson = extractJsonObject(entry, "region");
        if (regionJson.empty()) {
            return std::nullopt;
        }
        record.region.region_code = extractJsonString(regionJson, "region_code");
        record.region.server_url = extractJsonString(regionJson, "server_url");
        std::string authority = extractJsonString(regionJson, "grpc_authority");
        if (!authority.empty()) {
            record.region.grpc_authority = authority;
        }
        
        // Parse cache_control
        std::string cacheJson = extractJsonObject(entry, "cache_control");
        if (cacheJson.empty()) {
            return std::nullopt;
        }
        record.cache_control.issued_at = parseIso8601(extractJsonString(cacheJson, "issued_at"));
        record.cache_control.refresh_at = parseIso8601(extractJsonString(cacheJson, "refresh_at"));
        record.cache_control.expires_at = parseIso8601(extractJsonString(cacheJson, "expires_at"));
        record.cache_control.expires_in_seconds = extractJsonInt(cacheJson, "expires_in_seconds");
        record.cache_control.refresh_after_seconds = extractJsonInt(cacheJson, "refresh_after_seconds");
        
        return record;
        
    } catch (const std::exception& e) {
        // Cache read failed - return empty
        return std::nullopt;
    }
}

void DiscoveryCache::store(const std::string& cache_key, const DiscoveryRecord& record) {
    // Create parent directories
    std::filesystem::create_directories(path_.parent_path());
    
    // Read existing cache
    std::map<std::string, std::string> allData;
    if (std::filesystem::exists(path_)) {
        std::ifstream file(path_);
        if (file.is_open()) {
            std::stringstream buffer;
            buffer << file.rdbuf();
            // Note: Full JSON parsing would be needed for a complete implementation
            // For now, we simply overwrite the file
        }
    }
    
    // Build JSON for this record
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"" << cache_key << "\": {\n";
    oss << "    \"tenant_id\": \"" << record.tenant_id << "\",\n";
    if (record.tenant_name) {
        oss << "    \"tenant_name\": \"" << *record.tenant_name << "\",\n";
    }
    oss << "    \"roles\": [";
    for (size_t i = 0; i < record.roles.size(); ++i) {
        if (i > 0) oss << ", ";
        oss << "\"" << record.roles[i] << "\"";
    }
    oss << "],\n";
    oss << "    \"region\": {\n";
    oss << "      \"region_code\": \"" << record.region.region_code << "\",\n";
    oss << "      \"server_url\": \"" << record.region.server_url << "\"";
    if (record.region.grpc_authority) {
        oss << ",\n      \"grpc_authority\": \"" << *record.region.grpc_authority << "\"";
    }
    oss << "\n    },\n";
    oss << "    \"cache_control\": {\n";
    oss << "      \"issued_at\": \"" << toIso8601(record.cache_control.issued_at) << "\",\n";
    oss << "      \"refresh_at\": \"" << toIso8601(record.cache_control.refresh_at) << "\",\n";
    oss << "      \"expires_at\": \"" << toIso8601(record.cache_control.expires_at) << "\",\n";
    oss << "      \"expires_in_seconds\": " << record.cache_control.expires_in_seconds << ",\n";
    oss << "      \"refresh_after_seconds\": " << record.cache_control.refresh_after_seconds << "\n";
    oss << "    }\n";
    oss << "  }\n";
    oss << "}\n";
    
    std::string jsonContent = oss.str();
    
    // Encrypt if enabled
    std::string contentToWrite = encrypt_ ? encryptContent(jsonContent) : jsonContent;
    
    // Write to temp file and rename (atomic on most filesystems)
    auto tmpPath = path_;
    tmpPath.replace_extension(".tmp");
    
    std::ofstream file(tmpPath);
    if (!file.is_open()) {
        throw DiscoveryError("Failed to write discovery cache: " + tmpPath.string());
    }
    file << contentToWrite;
    file.close();
    
    // Rename with retry for Windows file locking
    for (int i = 0; i < 5; ++i) {
        try {
            std::filesystem::rename(tmpPath, path_);
            return;
        } catch (const std::filesystem::filesystem_error&) {
            if (i == 4) throw;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }
}

std::map<std::string, std::map<std::string, std::string>> DiscoveryCache::readAll() {
    // Simplified implementation - would need full JSON parsing for complete impl
    return {};
}

// --- DiscoveryManager implementation ---

DiscoveryManager::DiscoveryManager(
    const std::string& control_plane_url,
    const std::filesystem::path& cache_path,
    double timeout_seconds
)
    : base_url_(control_plane_url.empty() ? getDefaultControlPlaneUrl() : control_plane_url)
    , cache_(cache_path)
    , timeout_(timeout_seconds)
{}

DiscoveryRecord DiscoveryManager::resolve(
    const std::string& id_token,
    const std::optional<std::string>& tenant_hint,
    bool force_refresh
) {
    std::string cache_key = tenant_hint.value_or(DEFAULT_CACHE_KEY);
    
    auto fetchFresh = [&]() -> DiscoveryRecord {
        std::string firebase_token = ensureFirebaseToken(id_token);
        DiscoveryRecord fresh = fetchRemote(firebase_token, tenant_hint);
        cache_.store(cache_key, fresh);
        return fresh;
    };
    
    if (!force_refresh) {
        auto cached = cache_.load(cache_key);
        if (cached && !cached->cache_control.isExpired()) {
            if (cached->cache_control.shouldRefresh()) {
                // Try to refresh, but fall back to cache on failure
                try {
                    return fetchFresh();
                } catch (const DiscoveryError&) {
                    if (!cached->cache_control.isExpired()) {
                        return *cached;
                    }
                    throw;
                }
            }
            return *cached;
        }
    }
    
    return fetchFresh();
}

DiscoveryRecord DiscoveryManager::fetchRemote(
    const std::string& id_token,
    const std::optional<std::string>& tenant_hint
) {
    // Note: This implementation requires an HTTP client library.
    // For production use, integrate with libcurl, cpr, or similar.
    // For now, we throw an error indicating the functionality needs
    // an HTTP client implementation.
    
    // The Python implementation uses requests.post() to call:
    // POST {base_url}/api/discovery/tenant
    // Headers: Authorization: Bearer {id_token}, Content-Type: application/json
    // Body: {"tenant_hint": "..."} (optional)
    
    throw DiscoveryError(
        "Remote discovery not yet implemented in C++ SDK. "
        "Use direct endpoint connection with Client::createFromEnv() or "
        "provide explicit endpoint to Client constructor."
    );
}

// --- Convenience functions ---

std::string getDefaultControlPlaneUrl() {
    return getEnvVar("KUMIHO_CONTROL_PLANE_URL", "https://kumiho.io");
}

std::filesystem::path getDefaultCachePath() {
    std::string envPath = getEnvVar("KUMIHO_DISCOVERY_CACHE_FILE");
    if (!envPath.empty()) {
        return envPath;
    }
    return getConfigDir() / "discovery-cache.json";
}

std::shared_ptr<Client> clientFromDiscovery(
    const std::optional<std::string>& id_token,
    const std::optional<std::string>& tenant_hint,
    const std::string& control_plane_url,
    const std::string& cache_path,
    bool force_refresh
) {
    // Get token
    std::string token;
    if (id_token) {
        token = *id_token;
    } else {
        auto loaded = loadBearerToken();
        if (!loaded) {
            throw AuthenticationError(
                "A bearer token is required. Set KUMIHO_AUTH_TOKEN or run kumiho-auth login."
            );
        }
        token = *loaded;
    }
    
    // Resolve discovery
    DiscoveryManager manager(
        control_plane_url,
        cache_path.empty() ? std::filesystem::path{} : std::filesystem::path{cache_path},
        10.0
    );
    
    DiscoveryRecord record = manager.resolve(token, tenant_hint, force_refresh);
    
    // Build target endpoint
    std::string target = record.region.grpc_authority.value_or(record.region.server_url);
    
    // Create channel with credentials
    // Note: Full implementation would use grpc::SslCredentials with the token
    // For now, create using the resolved endpoint
    
    auto channelCreds = grpc::SslCredentials(grpc::SslCredentialsOptions());
    
    grpc::ChannelArguments args;
    if (record.region.grpc_authority) {
        args.SetString(GRPC_SSL_TARGET_NAME_OVERRIDE_ARG, *record.region.grpc_authority);
    }
    
    // Add tenant ID as default metadata
    // Note: gRPC doesn't support default metadata on channel; would need interceptor
    
    auto channel = grpc::CreateCustomChannel(target, channelCreds, args);
    return std::make_shared<Client>(channel);
}

} // namespace api
} // namespace kumiho
