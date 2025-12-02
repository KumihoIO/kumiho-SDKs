/**
 * @file test_kref.cpp
 * @brief Unit tests for Kref URI parsing and validation.
 */

#include <gtest/gtest.h>
#include <kumiho/kref.hpp>
#include <kumiho/error.hpp>

using namespace kumiho::api;

// --- Kref Parsing Tests ---

class KrefParsingTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

// Test project-level Kref
TEST_F(KrefParsingTest, ParseProjectKref) {
    Kref kref("kref://my-project");
    
    EXPECT_EQ(kref.uri(), "kref://my-project");
    EXPECT_EQ(kref.getPath(), "my-project");
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "");
    EXPECT_EQ(kref.getProductName(), "");
    EXPECT_EQ(kref.getType(), "");
    EXPECT_EQ(kref.getFullProductName(), "");
    EXPECT_FALSE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getResourceName(), "");
}

// Test group-level Kref (single level)
TEST_F(KrefParsingTest, ParseSingleGroupKref) {
    Kref kref("kref://my-project/assets");
    
    EXPECT_EQ(kref.getPath(), "my-project/assets");
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "assets");
    EXPECT_EQ(kref.getProductName(), "");
    EXPECT_EQ(kref.getType(), "");
}

// Test nested group Kref
TEST_F(KrefParsingTest, ParseNestedGroupKref) {
    Kref kref("kref://my-project/seq/shot/assets");
    
    EXPECT_EQ(kref.getPath(), "my-project/seq/shot/assets");
    EXPECT_EQ(kref.getProject(), "my-project");
    // The group should be the path between project and last component
    // "assets" is the last component (could be product or final group)
    EXPECT_EQ(kref.getGroup(), "seq/shot");
    EXPECT_EQ(kref.getProductName(), "");  // "assets" doesn't have a dot, so not a product
}

// Test product-level Kref
TEST_F(KrefParsingTest, ParseProductKref) {
    Kref kref("kref://my-project/assets/hero.model");
    
    EXPECT_EQ(kref.getPath(), "my-project/assets/hero.model");
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "assets");
    EXPECT_EQ(kref.getProductName(), "hero");
    EXPECT_EQ(kref.getType(), "model");
    EXPECT_EQ(kref.getFullProductName(), "hero.model");
    EXPECT_FALSE(kref.getVersion().has_value());
}

// Test product with nested groups
TEST_F(KrefParsingTest, ParseProductWithNestedGroups) {
    Kref kref("kref://my-project/seq/shot/assets/hero.model");
    
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "seq/shot/assets");
    EXPECT_EQ(kref.getProductName(), "hero");
    EXPECT_EQ(kref.getType(), "model");
    EXPECT_EQ(kref.getFullProductName(), "hero.model");
}

// Test version-level Kref
TEST_F(KrefParsingTest, ParseVersionKref) {
    Kref kref("kref://my-project/assets/hero.model?v=3");
    
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "assets");
    EXPECT_EQ(kref.getProductName(), "hero");
    EXPECT_EQ(kref.getType(), "model");
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 3);
    EXPECT_EQ(kref.getResourceName(), "");
}

// Test resource-level Kref
TEST_F(KrefParsingTest, ParseResourceKref) {
    Kref kref("kref://my-project/assets/hero.model?v=1&r=mesh");
    
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "assets");
    EXPECT_EQ(kref.getProductName(), "hero");
    EXPECT_EQ(kref.getType(), "model");
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 1);
    EXPECT_EQ(kref.getResourceName(), "mesh");
}

// Test Kref with tag
TEST_F(KrefParsingTest, ParseKrefWithTag) {
    Kref kref("kref://my-project/assets/hero.model?t=approved");
    
    EXPECT_EQ(kref.getTag(), "approved");
    EXPECT_FALSE(kref.getVersion().has_value());
}

// Test Kref with time
TEST_F(KrefParsingTest, ParseKrefWithTime) {
    Kref kref("kref://my-project/assets/hero.model?time=202512021000");
    
    EXPECT_EQ(kref.getTime(), "202512021000");
}

// Test Kref with multiple query params
TEST_F(KrefParsingTest, ParseKrefWithMultipleParams) {
    Kref kref("kref://my-project/assets/hero.model?v=2&r=texture&t=latest");
    
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 2);
    EXPECT_EQ(kref.getResourceName(), "texture");
    EXPECT_EQ(kref.getTag(), "latest");
}

// Test legacy kumiho:// scheme
TEST_F(KrefParsingTest, ParseLegacyScheme) {
    Kref kref("kumiho://my-project/assets/hero.model?v=1");
    
    EXPECT_EQ(kref.getProject(), "my-project");
    EXPECT_EQ(kref.getGroup(), "assets");
    EXPECT_EQ(kref.getProductName(), "hero");
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 1);
}

// Test empty Kref
TEST_F(KrefParsingTest, EmptyKref) {
    Kref kref("");
    
    EXPECT_EQ(kref.uri(), "");
    EXPECT_EQ(kref.getPath(), "");
    EXPECT_FALSE(kref.isValid());
}

// Test Kref equality
TEST_F(KrefParsingTest, KrefEquality) {
    Kref kref1("kref://my-project/assets/hero.model?v=1");
    Kref kref2("kref://my-project/assets/hero.model?v=1");
    Kref kref3("kref://my-project/assets/hero.model?v=2");
    
    EXPECT_TRUE(kref1 == kref2);
    EXPECT_FALSE(kref1 == kref3);
    EXPECT_TRUE(kref1 == std::string("kref://my-project/assets/hero.model?v=1"));
}

// Test Kref to protobuf conversion
TEST_F(KrefParsingTest, KrefToProtobuf) {
    Kref kref("kref://my-project/assets/hero.model?v=1");
    
    auto pb = kref.toPb();
    EXPECT_EQ(pb.uri(), "kref://my-project/assets/hero.model?v=1");
}

// --- Kref Validation Tests ---

class KrefValidationTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

// Test valid Kref URIs
TEST_F(KrefValidationTest, ValidKrefs) {
    EXPECT_TRUE(isValidKref("kref://project"));
    EXPECT_TRUE(isValidKref("kref://project/group"));
    EXPECT_TRUE(isValidKref("kref://project/group/product.type"));
    EXPECT_TRUE(isValidKref("kref://project/group/product.type?v=1"));
    EXPECT_TRUE(isValidKref("kref://project/group/product.type?v=1&r=resource"));
    EXPECT_TRUE(isValidKref("kumiho://project/group/product.type"));
}

// Test invalid Kref URIs
TEST_F(KrefValidationTest, InvalidKrefs) {
    EXPECT_FALSE(isValidKref(""));
    EXPECT_FALSE(isValidKref("not-a-kref"));
    EXPECT_FALSE(isValidKref("http://example.com"));
    EXPECT_FALSE(isValidKref("kref://"));  // Empty path
}

// Test validateKref throws on invalid
TEST_F(KrefValidationTest, ValidateKrefThrows) {
    EXPECT_NO_THROW(validateKref("kref://project"));
    EXPECT_THROW(validateKref(""), KrefValidationError);
    EXPECT_THROW(validateKref("invalid"), KrefValidationError);
}

// --- Edge Cases ---

class KrefEdgeCasesTest : public ::testing::Test {};

// Test product name with multiple dots
TEST_F(KrefEdgeCasesTest, ProductNameWithMultipleDots) {
    Kref kref("kref://proj/group/file.v001.exr.texture");
    
    // First dot separates name from type
    EXPECT_EQ(kref.getProductName(), "file");
    EXPECT_EQ(kref.getType(), "v001.exr.texture");
}

// Test hyphenated names
TEST_F(KrefEdgeCasesTest, HyphenatedNames) {
    Kref kref("kref://my-cool-project/asset-group/hero-character.model");
    
    EXPECT_EQ(kref.getProject(), "my-cool-project");
    EXPECT_EQ(kref.getGroup(), "asset-group");
    EXPECT_EQ(kref.getProductName(), "hero-character");
    EXPECT_EQ(kref.getType(), "model");
}

// Test underscored names
TEST_F(KrefEdgeCasesTest, UnderscoredNames) {
    Kref kref("kref://my_project/asset_group/hero_char.model_v2");
    
    EXPECT_EQ(kref.getProject(), "my_project");
    EXPECT_EQ(kref.getGroup(), "asset_group");
    EXPECT_EQ(kref.getProductName(), "hero_char");
    EXPECT_EQ(kref.getType(), "model_v2");
}

// Test numeric project/group names
TEST_F(KrefEdgeCasesTest, NumericNames) {
    Kref kref("kref://project123/seq001/shot010/asset.model");
    
    EXPECT_EQ(kref.getProject(), "project123");
    EXPECT_EQ(kref.getGroup(), "seq001/shot010");
    EXPECT_EQ(kref.getProductName(), "asset");
}

// Test version number 0
TEST_F(KrefEdgeCasesTest, VersionZero) {
    Kref kref("kref://proj/group/prod.type?v=0");
    
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 0);
}

// Test large version number
TEST_F(KrefEdgeCasesTest, LargeVersionNumber) {
    Kref kref("kref://proj/group/prod.type?v=999999");
    
    ASSERT_TRUE(kref.getVersion().has_value());
    EXPECT_EQ(kref.getVersion().value(), 999999);
}

// Test invalid version (non-numeric)
TEST_F(KrefEdgeCasesTest, InvalidVersionFormat) {
    Kref kref("kref://proj/group/prod.type?v=abc");
    
    // Should return nullopt for non-numeric version
    EXPECT_FALSE(kref.getVersion().has_value());
}

// Test query param at different positions
TEST_F(KrefEdgeCasesTest, QueryParamOrder) {
    // Resource before version
    Kref kref1("kref://proj/group/prod.type?r=mesh&v=1");
    ASSERT_TRUE(kref1.getVersion().has_value());
    EXPECT_EQ(kref1.getVersion().value(), 1);
    EXPECT_EQ(kref1.getResourceName(), "mesh");
    
    // Tag first
    Kref kref2("kref://proj/group/prod.type?t=latest&v=2&r=tex");
    ASSERT_TRUE(kref2.getVersion().has_value());
    EXPECT_EQ(kref2.getVersion().value(), 2);
    EXPECT_EQ(kref2.getResourceName(), "tex");
    EXPECT_EQ(kref2.getTag(), "latest");
}

// Test Kref isValid method
TEST_F(KrefEdgeCasesTest, IsValidMethod) {
    Kref valid("kref://project/group/product.type");
    Kref empty("");
    
    EXPECT_TRUE(valid.isValid());
    EXPECT_FALSE(empty.isValid());
}
