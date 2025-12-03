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
#include <regex>
#include <sstream>

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

void validateKref(const std::string& kref_uri) {
    if (kref_uri.empty()) {
        throw KrefValidationError("Kref cannot be empty");
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
    
    // Path components should be valid identifiers
    std::regex component_regex("^[a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)?$");
    std::stringstream ss(path);
    std::string component;
    while (std::getline(ss, component, '/')) {
        if (component.empty()) continue;
        if (!std::regex_match(component, component_regex)) {
            throw KrefValidationError(
                "Invalid path component '" + component + "' in kref: " + kref_uri
            );
        }
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
