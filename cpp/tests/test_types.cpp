/**
 * @file test_types.cpp
 * @brief Unit tests for Kumiho type definitions and helper methods.
 */

#include <gtest/gtest.h>
#include <kumiho/types.hpp>
#include <kumiho/edge.hpp>

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
    step.revision_kref = "kref://proj/space/item.kind?r=1";
    step.edge_type = "DEPENDS_ON";
    step.depth = 2;
    
    EXPECT_EQ(step.revision_kref, "kref://proj/space/item.kind?r=1");
    EXPECT_EQ(step.edge_type, "DEPENDS_ON");
    EXPECT_EQ(step.depth, 2);
}

// --- RevisionPath Tests ---

class RevisionPathTest : public ::testing::Test {};

TEST_F(RevisionPathTest, EmptyPath) {
    RevisionPath path;
    
    EXPECT_TRUE(path.empty());
    EXPECT_EQ(path.total_depth, 0);
}

TEST_F(RevisionPathTest, PathWithSteps) {
    RevisionPath path;
    path.total_depth = 3;
    
    PathStep step1;
    step1.revision_kref = "kref://proj/a.kind?r=1";
    step1.edge_type = "DEPENDS_ON";
    step1.depth = 0;
    
    PathStep step2;
    step2.revision_kref = "kref://proj/b.kind?r=1";
    step2.edge_type = "DEPENDS_ON";
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
    EXPECT_TRUE(result.revision_krefs.empty());
    EXPECT_TRUE(result.edges.empty());
    EXPECT_EQ(result.total_count, 0);
    EXPECT_FALSE(result.truncated);
}

TEST_F(TraversalResultTest, WithResults) {
    TraversalResult result;
    result.revision_krefs.push_back("kref://proj/a.kind?r=1");
    result.revision_krefs.push_back("kref://proj/b.kind?r=2");
    result.total_count = 2;
    result.truncated = false;
    
    EXPECT_EQ(result.revision_krefs.size(), 2);
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
    
    RevisionPath path;
    path.total_depth = 2;
    result.paths.push_back(path);
    
    EXPECT_TRUE(result.path_exists);
    EXPECT_EQ(result.path_length, 2);
    EXPECT_NE(result.first_path(), nullptr);
}

// --- ImpactedRevision Tests ---

class ImpactedRevisionTest : public ::testing::Test {};

TEST_F(ImpactedRevisionTest, Construction) {
    ImpactedRevision ir;
    ir.revision_kref = "kref://proj/a.kind?r=1";
    ir.item_kref = "kref://proj/a.kind";
    ir.impact_depth = 3;
    ir.impact_path_types.push_back("DEPENDS_ON");
    ir.impact_path_types.push_back("DERIVED_FROM");
    
    EXPECT_EQ(ir.revision_kref, "kref://proj/a.kind?r=1");
    EXPECT_EQ(ir.item_kref, "kref://proj/a.kind");
    EXPECT_EQ(ir.impact_depth, 3);
    EXPECT_EQ(ir.impact_path_types.size(), 2);
}

// --- ImpactAnalysisResult Tests ---

class ImpactAnalysisResultTest : public ::testing::Test {};

TEST_F(ImpactAnalysisResultTest, DefaultValues) {
    ImpactAnalysisResult result;
    
    EXPECT_TRUE(result.impacted_revisions.empty());
    EXPECT_EQ(result.total_impacted, 0);
    EXPECT_FALSE(result.truncated);
}

TEST_F(ImpactAnalysisResultTest, WithImpact) {
    ImpactAnalysisResult result;
    
    ImpactedRevision ir;
    ir.revision_kref = "kref://proj/a.kind?r=1";
    ir.impact_depth = 1;
    result.impacted_revisions.push_back(ir);
    result.total_impacted = 1;
    
    EXPECT_EQ(result.impacted_revisions.size(), 1);
    EXPECT_EQ(result.total_impacted, 1);
}

// --- EdgeType Tests ---

class EdgeTypeTest : public ::testing::Test {};

TEST_F(EdgeTypeTest, PredefinedTypes) {
    EXPECT_STREQ(EdgeType::DEPENDS_ON, "DEPENDS_ON");
    EXPECT_STREQ(EdgeType::DERIVED_FROM, "DERIVED_FROM");
    EXPECT_STREQ(EdgeType::CREATED_FROM, "CREATED_FROM");
    EXPECT_STREQ(EdgeType::REFERENCED, "REFERENCED");
    EXPECT_STREQ(EdgeType::CONTAINS, "CONTAINS");
    EXPECT_STREQ(EdgeType::BELONGS_TO, "BELONGS_TO");
}

// --- EdgeDirection Tests ---

class EdgeDirectionTest : public ::testing::Test {};

TEST_F(EdgeDirectionTest, EnumValues) {
    EXPECT_EQ(static_cast<int>(EdgeDirection::OUTGOING), 0);
    EXPECT_EQ(static_cast<int>(EdgeDirection::INCOMING), 1);
    EXPECT_EQ(static_cast<int>(EdgeDirection::BOTH), 2);
}

// --- Constants Tests ---

class ConstantsTest : public ::testing::Test {};

TEST_F(ConstantsTest, TagConstants) {
    EXPECT_STREQ(LATEST_TAG, "latest");
    EXPECT_STREQ(PUBLISHED_TAG, "published");
}

TEST_F(ConstantsTest, ReservedKinds) {
    EXPECT_EQ(RESERVED_KINDS.size(), 1);
    EXPECT_EQ(RESERVED_KINDS[0], "bundle");
}

TEST_F(ConstantsTest, IsReservedKind) {
    EXPECT_TRUE(isReservedKind("bundle"));
    EXPECT_FALSE(isReservedKind("model"));
    EXPECT_FALSE(isReservedKind("texture"));
    EXPECT_FALSE(isReservedKind("Bundle"));  // Case sensitive
}
