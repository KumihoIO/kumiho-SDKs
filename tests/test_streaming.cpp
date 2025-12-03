#include <grpcpp/grpcpp.h>
#include <gtest/gtest.h>
#include <kumiho/kumiho.hpp>
#include <memory>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>

// --- Helper Functions ---
std::string unique_name_stream(const std::string& prefix) {
    auto now = std::chrono::high_resolution_clock::now();
    auto nanos = std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
    return prefix + "_" + std::to_string(nanos);
}

// --- Test Fixture for Streaming ---
class KumihoStreamingTest : public ::testing::Test {
protected:
    void SetUp() override {
        auto channel = grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials());
        client = std::make_unique<kumiho::api::Client>(channel);
    }

    std::unique_ptr<kumiho::api::Client> client;
};

// --- Integration Test for Event Streaming ---
TEST_F(KumihoStreamingTest, EventStreaming) {
    std::vector<kumiho::api::Event> received_events;
    std::mutex mtx;
    bool stream_ended = false;

    // Start a listener thread
    std::thread listener_thread([&]() {
        auto stream = client->eventStream();
        kumiho::api::Event event; // Correctly default-construct the Event object
        while (stream->readNext(event)) {
            std::lock_guard<std::mutex> lock(mtx);
            received_events.push_back(event);
        }
        stream_ended = true;
    });

    // Give the listener a moment to connect
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    // --- Perform actions to generate events ---
    std::string project_name = unique_name_stream("stream_test_project");
    std::string asset_name = unique_name_stream("stream_test_asset");
    
    auto space = client->createSpace("/", project_name);
    ASSERT_NE(space, nullptr);

    auto item = space->createItem(asset_name, "model");
    ASSERT_NE(item, nullptr);
    
    auto revision = item->createRevision();
    ASSERT_NE(revision, nullptr);

    revision->tag("published");

    // Wait for events to be processed
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // --- Assertions ---
    std::lock_guard<std::mutex> lock(mtx);

    ASSERT_GE(received_events.size(), 4);

    // 1. Space creation event
    const auto& event1 = received_events[0];
    EXPECT_EQ(event1.getRoutingKey(), "space.created");
    EXPECT_EQ(event1.getKref().uri(), "/" + project_name);

    // 2. Item creation event
    const auto& event2 = received_events[1];
    EXPECT_EQ(event2.getRoutingKey(), "item.model.created");
    EXPECT_EQ(event2.getKref().uri(), item->getKref().uri());

    // 3. Revision creation event
    const auto& event3 = received_events[2];
    EXPECT_EQ(event3.getRoutingKey(), "revision.created");
    EXPECT_EQ(event3.getKref().uri(), revision->getKref().uri());

    // 4. Revision tagging event
    const auto& event4 = received_events[3];
    EXPECT_EQ(event4.getRoutingKey(), "revision.tagged");
    EXPECT_EQ(event4.getKref().uri(), revision->getKref().uri());
    EXPECT_EQ(event4.getDetails().at("tag"), "published");

    // Detach the thread as we are done. The stream will be closed
    // when the client (and its context) is destroyed at the end of the test.
    listener_thread.detach();
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
