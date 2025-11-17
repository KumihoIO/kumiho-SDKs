"""Event-related classes and functionality."""

from .kref import Kref
from .proto.kumiho_pb2 import Event as PbEvent


class Event:
    """A high-level object representing a Kumiho event.

    An Event represents a change or action that occurred in the Kumiho system,
    such as creating, updating, or deleting objects. Events are streamed in
    real-time to notify clients of changes.

    Attributes:
        routing_key (str): The routing key identifying the type of event
                          (e.g., "group.created", "version.tagged").
        kref (Kref): Reference to the object that was affected.
        timestamp (Optional[datetime]): When the event occurred.
        author (str): The user who triggered the event.
        details (Dict[str, str]): Additional details about the event.
    """

    def __init__(self, pb_event: PbEvent) -> None:
        """Initialize an Event from a protobuf message.

        Args:
            pb_event: The protobuf Event message.
        """
        self.routing_key = pb_event.routing_key
        self.kref = Kref(pb_event.kref.uri)
        self.timestamp = pb_event.timestamp or None
        self.author = pb_event.author
        self.details = dict(pb_event.details)

    def __repr__(self) -> str:
        """Return a string representation of the Event."""
        return f"<Event key='{self.routing_key}' kref='{self.kref.uri}'>"
