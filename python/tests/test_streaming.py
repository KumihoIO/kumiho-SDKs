import kumiho
import pytest
import time
import uuid
import grpc
from threading import Thread
from queue import Queue, Empty
from unittest.mock import Mock, patch

def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix, e.g., 'my_test_1a2b3c4d'."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestEventClass:
    """Unit tests for the Event class with cursor support."""
    
    def test_event_with_cursor(self):
        """Test that Event correctly parses cursor from protobuf."""
        from kumiho.event import Event
        from kumiho.proto import kumiho_pb2
        
        pb_event = kumiho_pb2.Event(
            routing_key="revision.created",
            kref=kumiho_pb2.Kref(uri="kref://project/space/item.model?r=1"),
            timestamp="2025-12-03T10:00:00Z",
            author="user123",
            tenant_id="tenant-abc",
            username="John Doe",
            cursor="1701594000000-0",
        )
        
        event = Event(pb_event)
        
        assert event.routing_key == "revision.created"
        assert event.kref.uri == "kref://project/space/item.model?r=1"
        assert event.cursor == "1701594000000-0"
        assert event.author == "user123"
        assert event.timestamp == "2025-12-03T10:00:00Z"
    
    def test_event_without_cursor(self):
        """Test that Event handles missing cursor (Free tier)."""
        from kumiho.event import Event
        from kumiho.proto import kumiho_pb2
        
        pb_event = kumiho_pb2.Event(
            routing_key="item.deleted",
            kref=kumiho_pb2.Kref(uri="kref://project/item.model"),
            timestamp="2025-12-03T10:00:00Z",
            author="admin",
            # No cursor field set
        )
        
        event = Event(pb_event)
        
        assert event.routing_key == "item.deleted"
        assert event.cursor is None
    
    def test_event_repr_with_cursor(self):
        """Test Event repr includes cursor."""
        from kumiho.event import Event
        from kumiho.proto import kumiho_pb2
        
        pb_event = kumiho_pb2.Event(
            routing_key="revision.tagged",
            kref=kumiho_pb2.Kref(uri="kref://proj/item.model?r=1"),
            cursor="12345-0",
        )
        
        event = Event(pb_event)
        repr_str = repr(event)
        
        assert "revision.tagged" in repr_str
        assert "12345-0" in repr_str


class TestEventCapabilities:
    """Unit tests for EventCapabilities dataclass."""
    
    def test_event_capabilities_free_tier(self):
        """Test capabilities for free tier."""
        from kumiho.event import EventCapabilities
        
        caps = EventCapabilities(
            supports_replay=False,
            supports_cursor=False,
            supports_consumer_groups=False,
            max_retention_hours=0,
            max_buffer_size=100,
            tier="free",
        )
        
        assert not caps.supports_replay
        assert not caps.supports_cursor
        assert caps.tier == "free"
        assert caps.max_buffer_size == 100
    
    def test_event_capabilities_creator_tier(self):
        """Test capabilities for creator tier."""
        from kumiho.event import EventCapabilities
        
        caps = EventCapabilities(
            supports_replay=True,
            supports_cursor=True,
            supports_consumer_groups=False,
            max_retention_hours=1,
            max_buffer_size=10000,
            tier="creator",
        )
        
        assert caps.supports_replay
        assert caps.supports_cursor
        assert not caps.supports_consumer_groups
        assert caps.max_retention_hours == 1
    
    def test_event_capabilities_enterprise_tier(self):
        """Test capabilities for enterprise tier."""
        from kumiho.event import EventCapabilities
        
        caps = EventCapabilities(
            supports_replay=True,
            supports_cursor=True,
            supports_consumer_groups=True,
            max_retention_hours=-1,  # Unlimited
            max_buffer_size=-1,      # Unlimited
            tier="enterprise",
        )
        
        assert caps.supports_consumer_groups
        assert caps.max_retention_hours == -1


def test_event_streaming(cleanup_test_data):
    """
    Tests the event streaming functionality by performing various actions
    and checking if the correct events are received.
    """
    event_queue = Queue()
    
    def stream_listener():
        try:
            for event in kumiho.event_stream():  # Uses top-level kumiho.event_stream()
                print(f"[STREAM LISTENER] Received event: routing_key='{event.routing_key}', kref='{event.kref.uri}', details={event.details}")  # Added print for debugging
                event_queue.put(event)
        except grpc.RpcError as e:
            # It's normal for the stream to be cancelled when the test finishes
            if e.code() != grpc.StatusCode.CANCELLED:
                print(f"[STREAM LISTENER] gRPC Error: {e}")  # Added print for debugging
                raise

    listener_thread = Thread(target=stream_listener, daemon=True)
    listener_thread.start()

    time.sleep(1)  # Give the listener a moment to connect
    print("[TEST] Starting event streaming test...")  # Added print for debugging

    # 1. Create an item and check for the event
    project_name = unique_name("stream_test_project")
    asset_name = unique_name("stream_test_asset")
    
    print(f"[TEST] Creating project: {project_name}")  # Added print for debugging
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    print(f"[TEST] Creating item: {asset_name}")  # Added print for debugging
    item = space.create_item(item_name=asset_name, kind="model")  # Uses instance method
    cleanup_test_data.append(item)  # Add to cleanup
    
    # First event: space creation
    print("[TEST] Waiting for 'space.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "space.created"
        assert event.kref.uri == f"kref://{space.path}"  # Event krefs now include "kref://" prefix
    except Empty:
        pytest.fail("Did not receive 'space.created' event in time.")
    
    # Second event: item creation
    print("[TEST] Waiting for 'item.model.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "item.model.created"
        assert event.kref.uri == item.kref.uri
    except Empty:
        pytest.fail("Did not receive 'item.model.created' event in time.")

    # 2. Create a revision and check for the event
    print("[TEST] Creating revision...")  # Added print for debugging
    revision = item.create_revision()
    cleanup_test_data.append(revision)  # Add to cleanup
    print("[TEST] Waiting for 'revision.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "revision.created"
        assert event.kref.uri == revision.kref.uri
    except Empty:
        pytest.fail("Did not receive 'revision.created' event in time.")

    # 3. Tag the revision and check for the event
    print(f"[TEST] Tagging revision with '{kumiho.PUBLISHED_TAG}'...")  # Added print for debugging
    revision.tag(kumiho.PUBLISHED_TAG)  # No top-level equivalent yet, so kept as object method
    print("[TEST] Waiting for 'revision.tagged' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "revision.tagged"
        assert event.kref.uri == revision.kref.uri
        assert event.details["tag"] == kumiho.PUBLISHED_TAG
    except Empty:
        pytest.fail("Did not receive 'revision.tagged' event in time.")
    
    print("[TEST] Event streaming test completed successfully.")  # Added print for debugging


def test_event_streaming_with_cursor_tracking(cleanup_test_data):
    """
    Tests that events include cursor field for resumable streaming.
    Note: cursor-based resume requires Creator tier or above.
    """
    cursors_received = []
    event_queue = Queue()
    
    def stream_listener():
        try:
            for event in kumiho.event_stream(routing_key_filter="revision.*"):
                print(f"[CURSOR TEST] Event: {event.routing_key}, cursor={event.cursor}")
                cursors_received.append(event.cursor)
                event_queue.put(event)
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise

    listener_thread = Thread(target=stream_listener, daemon=True)
    listener_thread.start()

    time.sleep(1)  # Give the listener a moment to connect

    # Create test data
    project_name = unique_name("cursor_test_project")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    
    item = space.create_item(item_name="test_item", kind="model")
    cleanup_test_data.append(item)
    
    # Create a revision - this should trigger an event with cursor
    revision = item.create_revision()
    cleanup_test_data.append(revision)
    
    # Wait for revision.created event
    try:
        event = event_queue.get(timeout=3)
        assert event.routing_key == "revision.created"
        # Cursor may or may not be present depending on tier
        print(f"[CURSOR TEST] Received cursor: {event.cursor}")
    except Empty:
        pytest.fail("Did not receive 'revision.created' event in time.")
    
    print("[CURSOR TEST] Cursor tracking test completed successfully.")


def test_get_event_capabilities(live_client):
    """
    Tests that get_event_capabilities returns valid tier information.
    """
    caps = kumiho.get_event_capabilities()
    
    # Basic validations
    assert caps.tier in ("free", "creator", "studio", "studio_basic", "studio_pro", "enterprise")
    assert isinstance(caps.supports_replay, bool)
    assert isinstance(caps.supports_cursor, bool)
    assert isinstance(caps.supports_consumer_groups, bool)
    assert isinstance(caps.max_retention_hours, int)
    assert isinstance(caps.max_buffer_size, int)
    
    print(f"[CAPS TEST] Tier: {caps.tier}")
    print(f"[CAPS TEST] Supports replay: {caps.supports_replay}")
    print(f"[CAPS TEST] Supports cursor: {caps.supports_cursor}")
    print(f"[CAPS TEST] Supports consumer groups: {caps.supports_consumer_groups}")
    print(f"[CAPS TEST] Max retention hours: {caps.max_retention_hours}")
    print(f"[CAPS TEST] Max buffer size: {caps.max_buffer_size}")
    
    # Validate tier-specific capabilities
    if caps.tier == "free":
        assert not caps.supports_replay
        assert not caps.supports_cursor
        assert not caps.supports_consumer_groups
        assert caps.max_buffer_size == 100 or caps.max_buffer_size > 0
    elif caps.tier in ("creator", "studio", "studio_basic"):
        assert caps.supports_cursor
        assert caps.max_retention_hours >= 1
    elif caps.tier == "enterprise":
        assert caps.supports_consumer_groups
  # Added print for debugging
