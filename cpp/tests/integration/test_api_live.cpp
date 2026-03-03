#include <gtest/gtest.h>
#include <kumiho/kumiho.hpp>
#include <kumiho/discovery.hpp>
#include <kumiho/token_loader.hpp>

#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using namespace kumiho::api;

namespace {

const std::string PUBLISHED_TAG_NAME = "published";

std::string unique_name(const std::string& prefix) {
    auto now = std::chrono::high_resolution_clock::now();
    auto nanos = std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
    return prefix + "_" + std::to_string(nanos);
}

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

} // namespace

class KumihoApiTest : public ::testing::Test {
protected:
    void SetUp() override {
        if (!shouldRunIntegrationTests()) {
            GTEST_SKIP() << "Integration tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable.";
        }

        try {
            client = clientFromDiscovery();
        } catch (const std::exception& e) {
            GTEST_SKIP() << "Cannot connect to server: " << e.what();
        }
    }

    void TearDown() override {
        // Clean up created objects in reverse dependency order.
        for (auto it = created_artifacts.rbegin(); it != created_artifacts.rend(); ++it) {
            try {
                (*it)->deleteArtifact(true);
            } catch (...) {
            }
        }
        created_artifacts.clear();

        for (auto it = created_revisions.rbegin(); it != created_revisions.rend(); ++it) {
            try {
                (*it)->deleteRevision(true);
            } catch (...) {
            }
        }
        created_revisions.clear();

        for (auto it = created_items.rbegin(); it != created_items.rend(); ++it) {
            try {
                (*it)->deleteItem(true);
            } catch (...) {
            }
        }
        created_items.clear();

        for (auto it = created_spaces.rbegin(); it != created_spaces.rend(); ++it) {
            try {
                (*it)->deleteSpace(true);
            } catch (...) {
            }
        }
        created_spaces.clear();

        for (auto it = created_projects.rbegin(); it != created_projects.rend(); ++it) {
            try {
                (*it)->deleteProject(true);
            } catch (...) {
            }
        }
        created_projects.clear();
    }

    std::shared_ptr<Client> client;
    std::vector<std::shared_ptr<Project>> created_projects;
    std::vector<std::shared_ptr<Space>> created_spaces;
    std::vector<std::shared_ptr<Item>> created_items;
    std::vector<std::shared_ptr<Revision>> created_revisions;
    std::vector<std::shared_ptr<Artifact>> created_artifacts;
};

TEST_F(KumihoApiTest, DeleteLatestRevisionPreservesLatestResolution) {
    std::string project_name = unique_name("delete_latest_project");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("delete_latest_asset"), "model");
    created_items.push_back(item);

    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    auto v2 = item->createRevision();

    // Delete the revision that currently holds the server-managed 'latest' tag.
    v2->deleteRevision(true);

    // After deletion, resolving by tag should still work and point to v1.
    auto resolved_latest = item->getRevisionByTag("latest");
    ASSERT_NE(resolved_latest, nullptr);
    EXPECT_EQ(resolved_latest->getRevisionNumber(), 1);
    EXPECT_EQ(resolved_latest->getKref().uri(), v1->getKref().uri());

    auto latest = item->getLatestRevision();
    ASSERT_NE(latest, nullptr);
    EXPECT_EQ(latest->getRevisionNumber(), 1);
}

TEST_F(KumihoApiTest, MovePublishedThenDeleteRevision) {
    std::string project_name = unique_name("move_published_project");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("move_published_asset"), "model");
    created_items.push_back(item);

    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    auto v2 = item->createRevision();

    // Publish v2.
    v2->tag(PUBLISHED_TAG_NAME);
    EXPECT_TRUE(client->hasTag(v2->getKref(), PUBLISHED_TAG_NAME));

    // Move published back to v1.
    v1->tag(PUBLISHED_TAG_NAME);
    EXPECT_TRUE(client->hasTag(v1->getKref(), PUBLISHED_TAG_NAME));
    EXPECT_FALSE(client->hasTag(v2->getKref(), PUBLISHED_TAG_NAME));

    // Now v2 is not published anymore and can be deleted.
    v2->deleteRevision(true);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
