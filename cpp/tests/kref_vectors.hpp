/**
 * @file kref_vectors.hpp
 * @brief Loader for the shared kref conformance corpus, spec/kref/vectors.json.
 *
 * The corpus is the single source of truth for every Kumiho SDK. It is read from
 * the repository root at run time (CMake passes its path as
 * KUMIHO_KREF_VECTORS_PATH); it is never copied into this directory.
 */

#pragma once

#include <fstream>
#include <optional>
#include <stdexcept>
#include <string>

#include <nlohmann/json.hpp>

#ifndef KUMIHO_KREF_VECTORS_PATH
#error "KUMIHO_KREF_VECTORS_PATH must point at spec/kref/vectors.json"
#endif

namespace kumiho_test {

/** The "cases" array of spec/kref/vectors.json (133 cases). */
inline nlohmann::json loadKrefVectors() {
    std::ifstream in(KUMIHO_KREF_VECTORS_PATH, std::ios::binary);
    if (!in) {
        throw std::runtime_error(std::string("cannot open ") + KUMIHO_KREF_VECTORS_PATH);
    }
    const nlohmann::json doc = nlohmann::json::parse(in);
    if (doc.at("schema").get<std::string>() != "kumiho-kref-vectors/1") {
        throw std::runtime_error("unexpected corpus schema");
    }
    return doc.at("cases");
}

/** A corpus string field that may be null. */
inline std::optional<std::string> optString(const nlohmann::json& value) {
    if (value.is_null()) return std::nullopt;
    return value.get<std::string>();
}

}  // namespace kumiho_test
