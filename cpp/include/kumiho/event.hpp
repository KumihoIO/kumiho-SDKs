/**
 * @file event.hpp
 * @brief Event and EventStream for real-time notifications.
 *
 * Kumiho provides a gRPC streaming API for receiving real-time events
 * about changes to the graph database.
 */

#pragma once

#include <string>
#include <map>
#include <memory>
#include <grpcpp/grpcpp.h>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

/**
 * @brief Event streaming capabilities for the current tenant tier.
 *
 * Returned by Client::getEventCapabilities(). Mirrors the protobuf
 * EventCapabilities message and describes which streaming features are
 * available based on the authenticated tenant's subscription tier.
 */
struct EventCapabilities {
    /** @brief Whether this tier supports replaying past events. */
    bool supports_replay = false;

    /** @brief Whether cursor-based resume is supported. */
    bool supports_cursor = false;

    /** @brief Whether consumer groups are supported (Enterprise only). */
    bool supports_consumer_groups = false;

    /** @brief Maximum event retention in hours (0 = none, -1 = unlimited). */
    long long max_retention_hours = 0;

    /** @brief Maximum events in buffer (0 = none, -1 = unlimited). */
    long long max_buffer_size = 0;

    /** @brief Tier identifier (free, creator, studio, enterprise). */
    std::string tier;
};

/**
 * @brief A real-time event from the Kumiho server.
 *
 * Events are emitted when entities are created, updated, or deleted.
 * Each event has a routing key for filtering and details about what changed.
 *
 * Example:
 * @code
 *   auto stream = client->eventStream("product.*");
 *   Event event;
 *   while (stream->readNext(event)) {
 *       std::cout << "Event: " << event.getRoutingKey() << std::endl;
 *       std::cout << "Kref: " << event.getKref().uri() << std::endl;
 *   }
 * @endcode
 */
class Event {
public:
    /**
     * @brief Construct an Event from a protobuf message.
     * @param event The protobuf Event message (default: empty).
     */
    Event(const ::kumiho::Event& event = ::kumiho::Event());

    /**
     * @brief Get the routing key for this event.
     *
     * Routing keys follow the format: entity.action (e.g., "version.created").
     *
     * @return The routing key string.
     */
    std::string getRoutingKey() const;

    /**
     * @brief Get the Kref of the affected entity.
     * @return The Kref of the entity that triggered the event.
     */
    Kref getKref() const;

    /**
     * @brief Get additional event details.
     * @return A map of detail key-value pairs.
     */
    Metadata getDetails() const;

private:
    ::kumiho::Event event_;
};

/**
 * @brief A streaming connection for receiving events.
 *
 * EventStream wraps a gRPC client reader for receiving a continuous
 * stream of events from the server. Use readNext() to block and wait
 * for the next event.
 *
 * Example:
 * @code
 *   auto stream = client->eventStream();
 *   Event event;
 *   while (stream->readNext(event)) {
 *       // Process event
 *   }
 *   // Stream ended or error occurred
 * @endcode
 */
class EventStream {
public:
    /**
     * @brief Construct an EventStream from a gRPC reader.
     * @param reader The gRPC client reader for events.
     */
    EventStream(std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader);

    /**
     * @brief Read the next event from the stream.
     *
     * Blocks until an event is available or the stream ends.
     *
     * @param[out] event The event to populate.
     * @return True if an event was read, false if the stream ended.
     */
    bool readNext(Event& event);

private:
    std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader_;
};

} // namespace api
} // namespace kumiho
