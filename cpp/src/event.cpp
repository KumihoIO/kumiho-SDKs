/**
 * @file event.cpp
 * @brief Implementation of Event and EventStream classes.
 */

#include "kumiho/event.hpp"

namespace kumiho {
namespace api {

Event::Event(const ::kumiho::Event& event) : event_(event) {}

std::string Event::getRoutingKey() const {
    return event_.routing_key();
}

Kref Event::getKref() const {
    return Kref(event_.kref().uri());
}

Metadata Event::getDetails() const {
    return {event_.details().begin(), event_.details().end()};
}

EventStream::EventStream(std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader)
    : reader_(std::move(reader)) {}

bool EventStream::readNext(Event& event) {
    ::kumiho::Event event_pb;
    if (reader_->Read(&event_pb)) {
        event = Event(event_pb);
        return true;
    }
    return false;
}

} // namespace api
} // namespace kumiho
