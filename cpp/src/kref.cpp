/**
 * @file kref.cpp
 * @brief Implementation of Kref URI parsing and validation.
 *
 * Terminology (with backwards compatibility):
 * - Space (formerly Group): A hierarchical container/namespace
 * - Item (formerly Product): An asset/entity in the graph
 * - Revision (formerly Version): A specific state of an item
 * - Artifact (formerly Resource): A file/location attached to a revision
 * - Kind (formerly Type): The category of an item
 */

#include "kumiho/kref.hpp"
#include "kumiho/error.hpp"
#include <sstream>
#include <cctype>

namespace kumiho {
namespace api {

Kref::Kref(const std::string& uri) : std::string(uri) {}

std::string Kref::getPath() const {
    // Find scheme separator
    size_t start = find("://");
    if (start == std::string::npos) return *this;
    start += 3;
    
    // Find query string start
    size_t end = find('?', start);
    return substr(start, end - start);
}

std::string Kref::getProject() const {
    std::string path = getPath();
    size_t pos = path.find('/');
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(0, pos);
}

std::string Kref::getSpace() const {
    std::string path = getPath();
    
    // Find first slash (after project)
    size_t first_slash = path.find('/');
    if (first_slash == std::string::npos) {
        return "";  // Project-level kref
    }
    
    // Find last slash (before item.kind)
    size_t last_slash = path.rfind('/');
    if (last_slash == first_slash) {
        // Only one slash: project/item.kind
        // Check if it's an item (has dot) or a space
        std::string remainder = path.substr(first_slash + 1);
        if (remainder.find('.') != std::string::npos) {
            return "";  // It's an item, no space path
        }
        return remainder;  // It's a space
    }
    
    // Multiple slashes: extract space path
    return path.substr(first_slash + 1, last_slash - first_slash - 1);
}

std::string Kref::getItemName() const {
    std::string full = getFullItemName();
    size_t dot = full.find('.');
    if (dot == std::string::npos) {
        return "";
    }
    return full.substr(0, dot);
}

std::string Kref::getKind() const {
    std::string full = getFullItemName();
    size_t dot = full.find('.');
    if (dot == std::string::npos) {
        return "";
    }
    return full.substr(dot + 1);
}

std::string Kref::getFullItemName() const {
    std::string path = getPath();
    
    // Find the last component
    size_t last_slash = path.rfind('/');
    std::string last_component;
    if (last_slash == std::string::npos) {
        last_component = path;
    } else {
        last_component = path.substr(last_slash + 1);
    }
    
    // Check if it's an item (contains dot)
    if (last_component.find('.') != std::string::npos) {
        return last_component;
    }
    
    return "";  // Not an item kref
}

std::optional<int> Kref::getRevision() const {
    std::string r = getQueryParam("r");
    if (r.empty()) {
        return std::nullopt;
    }
    try {
        return std::stoi(r);
    } catch (...) {
        return std::nullopt;
    }
}

std::string Kref::getArtifactName() const {
    return getQueryParam("a");
}

std::string Kref::getTag() const {
    return getQueryParam("t");
}

std::string Kref::getTime() const {
    return getQueryParam("time");
}

std::string Kref::getQueryParam(const std::string& param) const {
    size_t query_start = find('?');
    if (query_start == std::string::npos) {
        return "";
    }
    
    std::string query = substr(query_start + 1);
    std::string search = param + "=";
    
    // Check at start of query string
    if (query.substr(0, search.length()) == search) {
        size_t end = query.find('&', search.length());
        if (end == std::string::npos) {
            return query.substr(search.length());
        }
        return query.substr(search.length(), end - search.length());
    }
    
    // Check after &
    search = "&" + param + "=";
    size_t pos = query.find(search);
    if (pos != std::string::npos) {
        size_t start = pos + search.length();
        size_t end = query.find('&', start);
        if (end == std::string::npos) {
            return query.substr(start);
        }
        return query.substr(start, end - start);
    }
    
    return "";
}

::kumiho::Kref Kref::toPb() const {
    ::kumiho::Kref pb_kref;
    pb_kref.set_uri(*this);
    return pb_kref;
}

bool Kref::isValid() const {
    if (empty()) return false;
    
    // Must start with kref:// or kumiho://
    if (find("kref://") != 0 && find("kumiho://") != 0) {
        return false;
    }
    
    // Path must not be empty
    std::string path = getPath();
    return !path.empty();
}

namespace {

// True for the ASCII characters allowed inside a path segment (besides UTF-8
// continuation/letter bytes, which are handled separately). This mirrors the
// Python validator's Unicode-aware `[\w.-]` allow-list for the ASCII range.
bool isAllowedSegmentAsciiByte(unsigned char byte) {
    return std::isalnum(byte) != 0 || byte == '_' || byte == '.' || byte == '-';
}

// Validate one path segment. Segments may contain ASCII alphanumerics, '_',
// '.', '-', plus any UTF-8 multibyte sequence (lead/continuation bytes >= 0x80,
// i.e. Unicode letters/digits). The leading character must be a "word" byte
// (alphanumeric, '_', or a UTF-8 byte) — not a '.' or '-'.
void validateKrefSegment(const std::string& segment, const std::string& kref_uri) {
    if (segment.empty()) {
        return;  // Empty segments arise from leading '/'; skip like Python's regex.
    }

    const unsigned char first = static_cast<unsigned char>(segment.front());
    const bool firstIsWord =
        first >= 0x80 || std::isalnum(first) != 0 || first == '_';
    if (!firstIsWord) {
        throw KrefValidationError(
            "Invalid path component '" + segment + "' in kref: " + kref_uri
        );
    }

    for (char ch : segment) {
        const unsigned char byte = static_cast<unsigned char>(ch);
        // Accept UTF-8 letter/continuation bytes (>= 0x80) verbatim.
        if (byte >= 0x80) {
            continue;
        }
        if (!isAllowedSegmentAsciiByte(byte)) {
            throw KrefValidationError(
                "Invalid path component '" + segment + "' in kref: " + kref_uri
            );
        }
    }
}

// Validate the optional query string, mirroring the Python validator's
// `(\?r=\d+(&a=[a-zA-Z0-9._-]+)?)?$` tail. `query` is everything after '?'.
// The revision must be one or more ASCII digits; the artifact id is an ASCII
// allow-list only (it is a server-generated opaque id, never a content name).
void validateKrefQuery(const std::string& query, const std::string& kref_uri) {
    const auto fail = [&]() {
        throw KrefValidationError(
            "Invalid kref query '" + query + "' in kref: " + kref_uri
        );
    };

    // Must begin with "r=<digit>+". Revision digits are ASCII-only (matching
    // the Dart SDK's `\d`); Unicode digits are deliberately not accepted.
    if (query.rfind("r=", 0) != 0) {
        fail();
    }
    size_t i = 2;
    const size_t digitsStart = i;
    while (i < query.size()) {
        const unsigned char d = static_cast<unsigned char>(query[i]);
        if (d < '0' || d > '9') {
            break;
        }
        ++i;
    }
    if (i == digitsStart) {
        fail();  // need at least one ASCII digit
    }
    if (i == query.size()) {
        return;  // just ?r=<digits>
    }

    // The only allowed remainder is "&a=<artifact>".
    if (query.compare(i, 3, "&a=") != 0) {
        fail();
    }
    i += 3;
    const size_t artStart = i;
    for (; i < query.size(); ++i) {
        const unsigned char byte = static_cast<unsigned char>(query[i]);
        // ASCII allow-list only, matching Python's [a-zA-Z0-9._-]. Using
        // explicit ranges (not std::isalnum) keeps this locale-independent and
        // rejects every byte >= 0x80.
        const bool isAsciiAlnum =
            (byte >= '0' && byte <= '9') ||
            (byte >= 'A' && byte <= 'Z') ||
            (byte >= 'a' && byte <= 'z');
        if (!isAsciiAlnum && byte != '_' && byte != '.' && byte != '-') {
            fail();
        }
    }
    if (i == artStart) {
        fail();  // need at least one artifact char
    }
}

}  // namespace

void validateKref(const std::string& kref_uri) {
    if (kref_uri.empty()) {
        throw KrefValidationError("Kref cannot be empty");
    }

    // Reject path traversal attempts anywhere in the URI.
    if (kref_uri.find("..") != std::string::npos) {
        throw KrefValidationError(
            "Invalid kref URI '" + kref_uri + "': path traversal (..) not allowed"
        );
    }

    // Reject control characters (C0 range and DEL).
    for (char ch : kref_uri) {
        const unsigned char byte = static_cast<unsigned char>(ch);
        if (byte < 0x20 || byte == 0x7f) {
            throw KrefValidationError(
                "Invalid kref URI '" + kref_uri + "': control characters not allowed"
            );
        }
    }

    // Must start with kref:// or kumiho://
    if (kref_uri.find("kref://") != 0 && kref_uri.find("kumiho://") != 0) {
        throw KrefValidationError(
            "Kref must start with 'kref://' or 'kumiho://': " + kref_uri
        );
    }

    Kref kref(kref_uri);
    std::string path = kref.getPath();

    if (path.empty()) {
        throw KrefValidationError("Kref path cannot be empty: " + kref_uri);
    }

    // Validate each path segment. Unicode letters (UTF-8 bytes >= 0x80) are
    // accepted; the ASCII allow-list is [A-Za-z0-9_.-] otherwise.
    std::stringstream ss(path);
    std::string component;
    while (std::getline(ss, component, '/')) {
        validateKrefSegment(component, kref_uri);
    }

    // Validate the optional ?r=...&a=... query for parity with the Python
    // validator, which applies its regex to the whole URI (not just the path).
    const auto queryPos = kref_uri.find('?');
    if (queryPos != std::string::npos) {
        validateKrefQuery(kref_uri.substr(queryPos + 1), kref_uri);
    }
}

bool isValidKref(const std::string& kref_uri) {
    try {
        validateKref(kref_uri);
        return true;
    } catch (const KrefValidationError&) {
        return false;
    }
}

} // namespace api
} // namespace kumiho
