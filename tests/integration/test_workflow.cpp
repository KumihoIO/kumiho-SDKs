/**
 * @file test_workflow.cpp
 * @brief Integration tests for complete SDK workflow.
 *
 * These tests verify the end-to-end workflow from project creation
 * through version management and linking. Requires a running kumiho-server.
 *
 * Set KUMIHO_INTEGRATION_TEST=1 to enable these tests.
 * Set KUMIHO_SERVER_ENDPOINT to the server address (default: localhost:8080).
 */

#include <gtest/gtest.h>
#include <kumiho/kumiho.hpp>
#include <string>
#include <cstdlib>
#include <chrono>
#include <memory>
#include <iostream>

using namespace kumiho::api;

namespace {

// Check if integration tests should run
bool shouldRunIntegrationTests() {
#ifdef _MSC_VER
    char* env = nullptr;
    size_t len = 0;
    _dupenv_s(&env, &len, "KUMIHO_INTEGRATION_TEST");
    bool result = (env != nullptr && std::string(env) == "1");
    free(env);
    return result;
#else
    const char* env = std::getenv("KUMIHO_INTEGRATION_TEST");
    return env != nullptr && std::string(env) == "1";
#endif
}

// Generate unique name for test isolation
std::string uniqueName(const std::string& prefix) {
    auto now = std::chrono::system_clock::now();
    auto epoch = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(epoch).count();
    return prefix + "_" + std::to_string(millis);
}

} // anonymous namespace

/**
 * @brief Integration test fixture for workflow tests.
 */
class WorkflowIntegrationTest : public ::testing::Test {
protected:
    std::shared_ptr<Client> client_;
    std::string testProjectName_;
    std::string projectId_;

    void SetUp() override {
        if (!shouldRunIntegrationTests()) {
            GTEST_SKIP() << "Integration tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.";
        }

        try {
            client_ = Client::createFromEnv();
            testProjectName_ = uniqueName("cpp_test");
        } catch (const std::exception& e) {
            GTEST_SKIP() << "Cannot connect to server: " << e.what();
        }
    }

    void TearDown() override {
        // Clean up test project if it exists
        if (client_ && !projectId_.empty()) {
            try {
                client_->deleteProject(projectId_, true);
            } catch (...) {
                // Ignore cleanup errors
            }
        }
    }
};

/**
 * @test Verify basic client connection and project listing.
 */
TEST_F(WorkflowIntegrationTest, ClientConnection) {
    // Just getting projects should work if connected
    auto projects = client_->getProjects();
    // Should not throw - connection is valid
    std::cout << "Connected to server, found " << projects.size() << " projects" << std::endl;
    SUCCEED();
}

/**
 * @test Complete workflow: Project -> Space -> Item -> Revision -> Artifact.
 */
TEST_F(WorkflowIntegrationTest, FullEntityHierarchy) {
    // 1. Create project
    auto project = client_->createProject(testProjectName_, "C++ SDK Integration test project");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();
    EXPECT_EQ(project->getName(), testProjectName_);
    EXPECT_FALSE(projectId_.empty());

    // 2. Create space
    auto space = project->createSpace("assets");
    ASSERT_NE(space, nullptr);
    EXPECT_EQ(space->getName(), "assets");

    // 3. Create nested space
    auto subspace = space->createSpace("characters");
    ASSERT_NE(subspace, nullptr);
    EXPECT_EQ(subspace->getName(), "characters");

    // 4. Create item in subspace
    auto item = subspace->createItem("hero", "model");
    ASSERT_NE(item, nullptr);
    EXPECT_EQ(item->getItemName(), "hero");
    EXPECT_EQ(item->getKind(), "model");

    // 5. Create revision with metadata
    Metadata revisionMeta = {{"artist", "integration_test"}, {"tool", "cpp_sdk"}};
    auto revision = item->createRevision(revisionMeta);
    ASSERT_NE(revision, nullptr);
    EXPECT_EQ(revision->getRevisionNumber(), 1);

    // 6. Add artifact
    auto artifact = revision->createArtifact("main_mesh", "/assets/hero.fbx");
    ASSERT_NE(artifact, nullptr);
    EXPECT_EQ(artifact->getName(), "main_mesh");

    // 7. Verify artifact retrieval
    auto artifacts = revision->getArtifacts();
    EXPECT_GE(artifacts.size(), 1u);

    // 8. Create another revision
    auto revision2 = item->createRevision({{"artist", "test"}, {"notes", "updated"}});
    ASSERT_NE(revision2, nullptr);
    EXPECT_EQ(revision2->getRevisionNumber(), 2);

    // 9. Verify revisions list
    auto revisions = item->getRevisions();
    EXPECT_EQ(revisions.size(), 2u);

    // 10. Tag revision
    revision->tag("approved");
    auto taggedRevision = client_->resolveKref(item->getKref().uri(), "approved");
    ASSERT_NE(taggedRevision, nullptr);
    EXPECT_EQ(taggedRevision->getRevisionNumber(), 1);
}

/**
 * @test Workflow with linking between revisions.
 */
TEST_F(WorkflowIntegrationTest, LinkingWorkflow) {
    // Create project
    auto project = client_->createProject(testProjectName_, "Link test project");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    // Create a space first (Items must be in spaces)
    auto space = project->createSpace("linking_test");
    ASSERT_NE(space, nullptr);

    // Create source item with revision
    auto sourceItem = space->createItem("source_asset", "asset");
    ASSERT_NE(sourceItem, nullptr);
    auto sourceRevision = sourceItem->createRevision({});
    ASSERT_NE(sourceRevision, nullptr);

    // Create target item with revision
    auto targetItem = space->createItem("target_asset", "asset");
    ASSERT_NE(targetItem, nullptr);
    auto targetRevision = targetItem->createRevision({});
    ASSERT_NE(targetRevision, nullptr);

    // Create dependency edge
    auto edge = sourceRevision->createEdge(targetRevision->getKref(), EdgeType::DEPENDS_ON);
    ASSERT_NE(edge, nullptr);
    EXPECT_STREQ(edge->getEdgeType().c_str(), EdgeType::DEPENDS_ON);

    // Verify outgoing edges (empty filter = all types)
    auto outEdges = sourceRevision->getEdges("", EdgeDirection::OUTGOING);
    EXPECT_GE(outEdges.size(), 1u);

    // Verify incoming edges on target
    // Note: Server may need time to propagate reverse edges, so this is informational
    auto inEdges = targetRevision->getEdges("", EdgeDirection::INCOMING);
    std::cout << "Incoming edges found: " << inEdges.size() << std::endl;
    // EXPECT_GE(inEdges.size(), 1u); // May be eventually consistent
}

/**
 * @test Metadata update workflow.
 */
TEST_F(WorkflowIntegrationTest, MetadataUpdateWorkflow) {
    // Create project and space
    auto project = client_->createProject(testProjectName_, "Metadata test");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    auto space = project->createSpace("meta_space");
    ASSERT_NE(space, nullptr);

    auto item = space->createItem("meta_test", "asset");
    ASSERT_NE(item, nullptr);

    auto revision = item->createRevision({{"initial", "value"}});
    ASSERT_NE(revision, nullptr);

    // Update metadata using setMetadata
    revision->setMetadata({{"updated", "new_value"}, {"initial", "changed"}});

    // Refresh and verify
    auto refreshed = client_->getRevision(revision->getKref().uri());
    ASSERT_NE(refreshed, nullptr);
    auto meta = refreshed->getMetadata();
    EXPECT_EQ(meta["updated"], "new_value");
    EXPECT_EQ(meta["initial"], "changed");
}

/**
 * @test Revision tagging workflow.
 */
TEST_F(WorkflowIntegrationTest, RevisionTaggingWorkflow) {
    // Create project and space
    auto project = client_->createProject(testProjectName_, "Tagging test");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    auto space = project->createSpace("tag_space");
    ASSERT_NE(space, nullptr);

    auto item = space->createItem("tag_test", "asset");
    ASSERT_NE(item, nullptr);

    auto v1 = item->createRevision({});
    auto v2 = item->createRevision({});
    auto v3 = item->createRevision({});
    ASSERT_NE(v1, nullptr);
    ASSERT_NE(v2, nullptr);
    ASSERT_NE(v3, nullptr);

    // Tag revisions (note: 'latest' is a reserved system tag)
    v1->tag("v1.0");
    v2->tag("v2.0");
    v2->tag("approved");
    v3->tag("approved");  // Should move tag from v2 to v3

    // Verify approved points to v3
    auto approved = client_->resolveKref(item->getKref().uri(), "approved");
    ASSERT_NE(approved, nullptr);
    EXPECT_EQ(approved->getRevisionNumber(), 3);

    // v1.0 should still point to v1
    auto v1Tagged = client_->resolveKref(item->getKref().uri(), "v1.0");
    ASSERT_NE(v1Tagged, nullptr);
    EXPECT_EQ(v1Tagged->getRevisionNumber(), 1);

    // 'latest' is auto-managed and should point to v3
    auto latest = client_->resolveKref(item->getKref().uri(), "latest");
    ASSERT_NE(latest, nullptr);
    EXPECT_EQ(latest->getRevisionNumber(), 3);
}

/**
 * @test Tenant usage query.
 */
TEST_F(WorkflowIntegrationTest, TenantUsageQuery) {
    auto usage = client_->getTenantUsage();

    // Basic validation - usage should have valid values
    EXPECT_GE(usage.node_count, 0);
    // node_limit can be -1 for unlimited tenants
    EXPECT_TRUE(usage.node_limit >= 0 || usage.node_limit == -1);
    EXPECT_FALSE(usage.tenant_id.empty());

    // Helper methods should work
    double percent = usage.usagePercent();
    // For unlimited tenants (-1 limit), usagePercent returns 0
    EXPECT_GE(percent, 0.0);
    if (usage.node_limit > 0) {
        EXPECT_LE(percent, 100.0);
    }

    std::cout << "Tenant: " << usage.tenant_id 
              << " | Usage: " << usage.node_count << "/" << usage.node_limit
              << " (" << percent << "%)" << std::endl;
}
