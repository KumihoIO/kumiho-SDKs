/**
 * @file test_kref_vectors.cpp
 * @brief The shared kref conformance corpus (spec/kref/vectors.json), case by case.
 *
 * Every one of the corpus's 133 cases goes through the structured parser,
 * kumiho::api::parseKref: the kernel verdict, the error_class, every field of
 * the reading and the GetItem tuple are checked here, together with the Kref
 * accessors (decision 3 of 2026-10-29: getItemName()/getKind() split at the LAST
 * '.') and the rule that validation is never stricter than before.
 *
 * The requests the client sends for these cases are checked against the same
 * corpus in test_api.cpp, which has the mock gRPC stub.
 */

#include <gtest/gtest.h>

#include <optional>
#include <set>
#include <string>
#include <vector>

#include <kumiho/error.hpp>
#include <kumiho/kref.hpp>
#include <kumiho/kref_parts.hpp>

#include "kref_vectors.hpp"

using namespace kumiho::api;
using kumiho_test::loadKrefVectors;
using kumiho_test::optString;

namespace {

std::optional<std::vector<std::string>> optStrings(const nlohmann::json& value) {
    if (value.is_null()) return std::nullopt;
    return value.get<std::vector<std::string>>();
}

std::optional<std::string> optClass(KrefErrorClass error) {
    if (error == KrefErrorClass::None) return std::nullopt;
    return std::string(toString(error));
}

}  // namespace

TEST(KrefVectors, CorpusIsTheSharedOne) {
    const auto cases = loadKrefVectors();
    ASSERT_EQ(cases.size(), 133u);
    std::set<std::string> ids;
    for (const auto& c : cases) ids.insert(c.at("id").get<std::string>());
    EXPECT_EQ(ids.size(), 133u) << "case ids are unique";
}

TEST(KrefVectors, ParseMatchesTheKernelReading) {
    for (const auto& c : loadKrefVectors()) {
        SCOPED_TRACE(c.at("id").get<std::string>());
        const KrefParts p = parseKref(c.at("input").get<std::string>());

        EXPECT_EQ(p.valid(), c.at("valid").get<bool>());
        EXPECT_EQ(optClass(p.error_class), optString(c.at("error_class")));
        EXPECT_EQ(p.base, optString(c.at("base")));
        std::vector<std::string> shapes;
        for (const KrefShape s : p.shapes) shapes.emplace_back(toString(s));
        EXPECT_EQ(shapes, c.at("shapes").get<std::vector<std::string>>());
        EXPECT_EQ(p.project, optString(c.at("project")));
        EXPECT_EQ(p.space_path, optStrings(c.at("space_path")));
        EXPECT_EQ(p.item_name, optString(c.at("item_name")));
        EXPECT_EQ(p.kind, optString(c.at("kind")));
        const auto& root = c.at("is_project_root_item");
        EXPECT_EQ(p.is_project_root_item,
                  root.is_null() ? std::nullopt : std::optional<bool>(root.get<bool>()));
        const auto& revision = c.at("revision");
        EXPECT_EQ(p.revision, revision.is_null()
                                  ? std::nullopt
                                  : std::optional<std::uint64_t>(revision.get<std::uint64_t>()));
        EXPECT_EQ(p.tag, optString(c.at("tag")));
        EXPECT_EQ(p.artifact, optString(c.at("artifact")));
    }
}

TEST(KrefVectors, GetItemTupleMatchesTheGrammar) {
    int checked = 0;
    for (const auto& c : loadKrefVectors()) {
        const auto& want = c.at("get_item_tuple");
        if (want.is_null()) continue;
        SCOPED_TRACE(c.at("id").get<std::string>());
        const KrefItemTuple got = parseKref(c.at("input").get<std::string>()).getItemTuple();
        EXPECT_EQ(got.parent_path, want.at("parent_path").get<std::string>());
        EXPECT_EQ(got.item_name, want.at("item_name").get<std::string>());
        EXPECT_EQ(got.kind, want.at("kind").get<std::string>());
        ++checked;
    }
    EXPECT_EQ(checked, 55);
}

// This SDK does not validate a kref before using it, and isValidKref() is
// lenient (any byte >= 0x80 is a word byte). The corpus rule is only that an SDK
// must accept at least every case today's Python SDK accepts; the validator is
// not touched by the parser. One case differs by design, before and after: the
// query validator accepts ASCII digits only ("Unicode digits are deliberately not
// accepted", kref.cpp), where Python's `\d` accepts the digit U+0663 in `?r=`.
TEST(KrefVectors, ValidationAcceptsEverythingPythonAccepts) {
    const std::set<std::string> asciiDigitsOnly = {"r-unicode-digit"};
    for (const auto& c : loadKrefVectors()) {
        if (!c.at("sdk_current_accepts").get<bool>()) continue;
        const auto id = c.at("id").get<std::string>();
        SCOPED_TRACE(id);
        EXPECT_EQ(isValidKref(c.at("input").get<std::string>()), asciiDigitsOnly.count(id) == 0);
    }
}

// Decision 3: the accessors split the leaf at the LAST '.', like the kernel.
TEST(KrefVectors, AccessorsSplitTheLeafAtTheLastDot) {
    int checked = 0;
    for (const auto& c : loadKrefVectors()) {
        const auto& tuple = c.at("get_item_tuple");
        if (tuple.is_null()) continue;
        SCOPED_TRACE(c.at("id").get<std::string>());
        const Kref kref(c.at("input").get<std::string>());
        const std::string name = tuple.at("item_name").get<std::string>();
        const std::string kind = tuple.at("kind").get<std::string>();
        EXPECT_EQ(kref.getItemName(), name);
        EXPECT_EQ(kref.getKind(), kind);
        EXPECT_EQ(kref.getFullItemName(), name + "." + kind);
        EXPECT_EQ(kref.getPath(), c.at("base").get<std::string>());
        ++checked;
    }
    EXPECT_EQ(checked, 55);
}

TEST(KrefVectors, KindSplitsAtTheLastDot) {
    EXPECT_EQ(Kref("kref://p/s/my.file.v2.k").getKind(), "k");
    EXPECT_EQ(Kref("kref://p/s/my.file.v2.k").getItemName(), "my.file.v2");
    EXPECT_EQ(Kref("kref://p/s/x.tar.gz").getKind(), "gz");
    EXPECT_EQ(Kref("kref://p/s/x.tar.gz").getItemName(), "x.tar");
    EXPECT_EQ(Kref("kref://p/s/x").getKind(), "");
    EXPECT_EQ(Kref("kref://p/s/x").getItemName(), "");
}
