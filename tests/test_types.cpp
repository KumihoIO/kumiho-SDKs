/**
 * @file test_types.cpp
 * @brief Unit tests for Kumiho type definitions and helper methods.
 */

#include <gtest/gtest.h>
#include <kumiho/types.hpp>
#include <kumiho/link.hpp>

using namespace kumiho::api;

// --- TenantUsage Tests ---

class TenantUsageTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(TenantUsageTest, UsagePercent) {
    TenantUsage usage;
    usage.node_count = 500;
    usage.node_limit = 1000;
    usage.tenant_id = "test-tenant";
    
    EXPECT_DOUBLE_EQ(usage.usagePercent(), 50.0);
}

TEST_F(TenantUsageTest, UsagePercentZeroLimit) {
    TenantUsage usage;
    usage.node_count = 100;
    usage.node_limit = 0;
    
    EXPECT_DOUBLE_EQ(usage.usagePercent(), 0.0);
}

TEST_F(TenantUsageTest, UsagePercentNegativeLimit) {
    TenantUsage usage;
    usage.node_count = 100;
    usage.node_limit = -1;
    
    EXPECT_DOUBLE_EQ(usage.usagePercent(), 0.0);
}

TEST_F(TenantUsageTest, IsNearLimit) {
    TenantUsage usage;
    usage.node_limit = 100;
    
    usage.node_count = 79;
    EXPECT_FALSE(usage.isNearLimit());
    
    usage.node_count = 80;
    EXPECT_TRUE(usage.isNearLimit());
    
    usage.node_count = 95;
    EXPECT_TRUE(usage.isNearLimit());
    
    usage.node_count = 100;
    EXPECT_TRUE(usage.isNearLimit());
}

TEST_F(TenantUsageTest, IsAtLimit) {
    TenantUsage usage;
    usage.node_limit = 100;
    
    usage.node_count = 99;
    EXPECT_FALSE(usage.isAtLimit());
    
    usage.node_count = 100;
    EXPECT_TRUE(usage.isAtLimit());
    
    usage.node_count = 101;
    EXPECT_TRUE(usage.isAtLimit());
}

// --- PathStep Tests ---

class PathStepTest : public ::testing::Test {};

TEST_F(PathStepTest, Construction) {
    PathStep step;
    step.version_kref = "kref://proj/group/prod.type?v=1";
    step.link_type = "DEPENDS_ON";
    step.depth = 2;
    
    EXPECT_EQ(step.version_kref, "kref://proj/group/prod.type?v=1");
    EXPECT_EQ(step.link_type, "DEPENDS_ON");
    EXPECT_EQ(step.depth, 2);
}

// --- VersionPath Tests ---

class VersionPathTest : public ::testing::Test {};

TEST_F(VersionPathTest, EmptyPath) {
    VersionPath path;
    
    EXPECT_TRUE(path.empty());
    EXPECT_EQ(path.total_depth, 0);
}

TEST_F(VersionPathTest, PathWithSteps) {
    VersionPath path;
    path.total_depth = 3;
    
    PathStep step1;
    step1.version_kref = "kref://proj/a.type?v=1";
    step1.link_type = "DEPENDS_ON";
    step1.depth = 0;
    
    PathStep step2;
    step2.version_kref = "kref://proj/b.type?v=1";
    step2.link_type = "DEPENDS_ON";
    step2.depth = 1;
    
    path.steps.push_back(step1);
    path.steps.push_back(step2);
    
    EXPECT_FALSE(path.empty());
    EXPECT_EQ(path.steps.size(), 2);
    EXPECT_EQ(path.total_depth, 3);
}

// --- TraversalResult Tests ---

class TraversalResultTest : public ::testing::Test {};

TEST_F(TraversalResultTest, DefaultValues) {
    TraversalResult result;
    
    EXPECT_TRUE(result.paths.empty());
    EXPECT_TRUE(result.version_krefs.empty());
    EXPECT_TRUE(result.links.empty());
    EXPECT_EQ(result.total_count, 0);
    EXPECT_FALSE(result.truncated);
}

TEST_F(TraversalResultTest, WithResults) {
    TraversalResult result;
    result.version_krefs.push_back("kref://proj/a.type?v=1");
    result.version_krefs.push_back("kref://proj/b.type?v=2");
    result.total_count = 2;
    result.truncated = false;
    
    EXPECT_EQ(result.version_krefs.size(), 2);
    EXPECT_EQ(result.total_count, 2);
    EXPECT_FALSE(result.truncated);
}

// --- ShortestPathResult Tests ---

class ShortestPathResultTest : public ::testing::Test {};

TEST_F(ShortestPathResultTest, NoPathFound) {
    ShortestPathResult result;
    result.path_exists = false;
    result.path_length = 0;
    
    EXPECT_FALSE(result.path_exists);
    EXPECT_EQ(result.first_path(), nullptr);
}

TEST_F(ShortestPathResultTest, PathFound) {
    ShortestPathResult result;
    result.path_exists = true;
    result.path_length = 2;
    
    VersionPath path;
    path.total_depth = 2;
    result.paths.push_back(path);
    
    EXPECT_TRUE(result.path_exists);
    EXPECT_EQ(result.path_length, 2);
    EXPECT_NE(result.first_path(), nullptr);
}

// --- ImpactedVersion Tests ---

class ImpactedVersionTest : public ::testing::Test {};

TEST_F(ImpactedVersionTest, Construction) {
    ImpactedVersion iv;
    iv.version_kref = "kref://proj/a.type?v=1";
    iv.product_kref = "kref://proj/a.type";
    iv.impact_depth = 3;
    iv.impact_path_types.push_back("DEPENDS_ON");
    iv.impact_path_types.push_back("DERIVED_FROM");
    
    EXPECT_EQ(iv.version_kref, "kref://proj/a.type?v=1");
    EXPECT_EQ(iv.product_kref, "kref://proj/a.type");
    EXPECT_EQ(iv.impact_depth, 3);
    EXPECT_EQ(iv.impact_path_types.size(), 2);
}

// --- ImpactAnalysisResult Tests ---

class ImpactAnalysisResultTest : public ::testing::Test {};

TEST_F(ImpactAnalysisResultTest, DefaultValues) {
    ImpactAnalysisResult result;
    
    EXPECT_TRUE(result.impacted_versions.empty());
    EXPECT_EQ(result.total_impacted, 0);
    EXPECT_FALSE(result.truncated);
}

TEST_F(ImpactAnalysisResultTest, WithImpact) {
    ImpactAnalysisResult result;
    
    ImpactedVersion iv;
    iv.version_kref = "kref://proj/a.type?v=1";
    iv.impact_depth = 1;
    result.impacted_versions.push_back(iv);
    result.total_impacted = 1;
    
    EXPECT_EQ(result.impacted_versions.size(), 1);
    EXPECT_EQ(result.total_impacted, 1);
}

// --- LinkType Tests ---

class LinkTypeTest : public ::testing::Test {};

TEST_F(LinkTypeTest, PredefinedTypes) {
    EXPECT_STREQ(LinkType::DEPENDS_ON, "DEPENDS_ON");
    EXPECT_STREQ(LinkType::DERIVED_FROM, "DERIVED_FROM");
    EXPECT_STREQ(LinkType::CREATED_FROM, "CREATED_FROM");
    EXPECT_STREQ(LinkType::REFERENCED, "REFERENCED");
    EXPECT_STREQ(LinkType::CONTAINS, "CONTAINS");
    EXPECT_STREQ(LinkType::BELONGS_TO, "BELONGS_TO");
}

// --- LinkDirection Tests ---

class LinkDirectionTest : public ::testing::Test {};

TEST_F(LinkDirectionTest, EnumValues) {
    EXPECT_EQ(static_cast<int>(LinkDirection::OUTGOING), 0);
    EXPECT_EQ(static_cast<int>(LinkDirection::INCOMING), 1);
    EXPECT_EQ(static_cast<int>(LinkDirection::BOTH), 2);
}

// --- Constants Tests ---

class ConstantsTest : public ::testing::Test {};

TEST_F(ConstantsTest, TagConstants) {
    EXPECT_STREQ(LATEST_TAG, "latest");
    EXPECT_STREQ(PUBLISHED_TAG, "published");
}

TEST_F(ConstantsTest, ReservedProductTypes) {
    EXPECT_EQ(RESERVED_PRODUCT_TYPES.size(), 1);
    EXPECT_EQ(RESERVED_PRODUCT_TYPES[0], "collection");
}

TEST_F(ConstantsTest, IsReservedProductType) {
    EXPECT_TRUE(isReservedProductType("collection"));
    EXPECT_FALSE(isReservedProductType("model"));
    EXPECT_FALSE(isReservedProductType("texture"));
    EXPECT_FALSE(isReservedProductType("Collection"));  // Case sensitive
}
