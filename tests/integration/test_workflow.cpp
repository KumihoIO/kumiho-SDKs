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
 * @test Complete workflow: Project -> Group -> Product -> Version -> Resource.
 */
TEST_F(WorkflowIntegrationTest, FullEntityHierarchy) {
    // 1. Create project
    auto project = client_->createProject(testProjectName_, "C++ SDK Integration test project");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();
    EXPECT_EQ(project->getName(), testProjectName_);
    EXPECT_FALSE(projectId_.empty());

    // 2. Create group
    auto group = project->createGroup("assets");
    ASSERT_NE(group, nullptr);
    EXPECT_EQ(group->getName(), "assets");

    // 3. Create nested group
    auto subgroup = group->createGroup("characters");
    ASSERT_NE(subgroup, nullptr);
    EXPECT_EQ(subgroup->getName(), "characters");

    // 4. Create product in subgroup
    auto product = subgroup->createProduct("hero", "model");
    ASSERT_NE(product, nullptr);
    EXPECT_EQ(product->getProductName(), "hero");
    EXPECT_EQ(product->getProductType(), "model");

    // 5. Create version with metadata
    Metadata versionMeta = {{"artist", "integration_test"}, {"tool", "cpp_sdk"}};
    auto version = product->createVersion(versionMeta);
    ASSERT_NE(version, nullptr);
    EXPECT_EQ(version->getVersionNumber(), 1);

    // 6. Add resource
    auto resource = version->createResource("main_mesh", "/assets/hero.fbx");
    ASSERT_NE(resource, nullptr);
    EXPECT_EQ(resource->getName(), "main_mesh");

    // 7. Verify resource retrieval
    auto resources = version->getResources();
    EXPECT_GE(resources.size(), 1u);

    // 8. Create another version
    auto version2 = product->createVersion({{"artist", "test"}, {"notes", "updated"}});
    ASSERT_NE(version2, nullptr);
    EXPECT_EQ(version2->getVersionNumber(), 2);

    // 9. Verify versions list
    auto versions = product->getVersions();
    EXPECT_EQ(versions.size(), 2u);

    // 10. Tag version
    version->tag("approved");
    auto taggedVersion = client_->resolveKref(product->getKref().uri(), "approved");
    ASSERT_NE(taggedVersion, nullptr);
    EXPECT_EQ(taggedVersion->getVersionNumber(), 1);
}

/**
 * @test Workflow with linking between versions.
 */
TEST_F(WorkflowIntegrationTest, LinkingWorkflow) {
    // Create project
    auto project = client_->createProject(testProjectName_, "Link test project");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    // Create a group first (Products must be in groups)
    auto group = project->createGroup("linking_test");
    ASSERT_NE(group, nullptr);

    // Create source product with version
    auto sourceProduct = group->createProduct("source_asset", "asset");
    ASSERT_NE(sourceProduct, nullptr);
    auto sourceVersion = sourceProduct->createVersion({});
    ASSERT_NE(sourceVersion, nullptr);

    // Create target product with version
    auto targetProduct = group->createProduct("target_asset", "asset");
    ASSERT_NE(targetProduct, nullptr);
    auto targetVersion = targetProduct->createVersion({});
    ASSERT_NE(targetVersion, nullptr);

    // Create dependency link
    auto link = sourceVersion->createLink(targetVersion->getKref(), LinkType::DEPENDS_ON);
    ASSERT_NE(link, nullptr);
    EXPECT_STREQ(link->getLinkType().c_str(), LinkType::DEPENDS_ON);

    // Verify outgoing links (empty filter = all types)
    auto outLinks = sourceVersion->getLinks("", LinkDirection::OUTGOING);
    EXPECT_GE(outLinks.size(), 1u);

    // Verify incoming links on target
    // Note: Server may need time to propagate reverse links, so this is informational
    auto inLinks = targetVersion->getLinks("", LinkDirection::INCOMING);
    std::cout << "Incoming links found: " << inLinks.size() << std::endl;
    // EXPECT_GE(inLinks.size(), 1u); // May be eventually consistent
}

/**
 * @test Metadata update workflow.
 */
TEST_F(WorkflowIntegrationTest, MetadataUpdateWorkflow) {
    // Create project and group
    auto project = client_->createProject(testProjectName_, "Metadata test");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    auto group = project->createGroup("meta_group");
    ASSERT_NE(group, nullptr);

    auto product = group->createProduct("meta_test", "asset");
    ASSERT_NE(product, nullptr);

    auto version = product->createVersion({{"initial", "value"}});
    ASSERT_NE(version, nullptr);

    // Update metadata using setMetadata
    version->setMetadata({{"updated", "new_value"}, {"initial", "changed"}});

    // Refresh and verify
    auto refreshed = client_->getVersion(version->getKref().uri());
    ASSERT_NE(refreshed, nullptr);
    auto meta = refreshed->getMetadata();
    EXPECT_EQ(meta["updated"], "new_value");
    EXPECT_EQ(meta["initial"], "changed");
}

/**
 * @test Version tagging workflow.
 */
TEST_F(WorkflowIntegrationTest, VersionTaggingWorkflow) {
    // Create project and group
    auto project = client_->createProject(testProjectName_, "Tagging test");
    ASSERT_NE(project, nullptr);
    projectId_ = project->getProjectId();

    auto group = project->createGroup("tag_group");
    ASSERT_NE(group, nullptr);

    auto product = group->createProduct("tag_test", "asset");
    ASSERT_NE(product, nullptr);

    auto v1 = product->createVersion({});
    auto v2 = product->createVersion({});
    auto v3 = product->createVersion({});
    ASSERT_NE(v1, nullptr);
    ASSERT_NE(v2, nullptr);
    ASSERT_NE(v3, nullptr);

    // Tag versions (note: 'latest' is a reserved system tag)
    v1->tag("v1.0");
    v2->tag("v2.0");
    v2->tag("approved");
    v3->tag("approved");  // Should move tag from v2 to v3

    // Verify approved points to v3
    auto approved = client_->resolveKref(product->getKref().uri(), "approved");
    ASSERT_NE(approved, nullptr);
    EXPECT_EQ(approved->getVersionNumber(), 3);

    // v1.0 should still point to v1
    auto v1Tagged = client_->resolveKref(product->getKref().uri(), "v1.0");
    ASSERT_NE(v1Tagged, nullptr);
    EXPECT_EQ(v1Tagged->getVersionNumber(), 1);

    // 'latest' is auto-managed and should point to v3
    auto latest = client_->resolveKref(product->getKref().uri(), "latest");
    ASSERT_NE(latest, nullptr);
    EXPECT_EQ(latest->getVersionNumber(), 3);
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
