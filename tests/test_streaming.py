import kumiho
import pytest
import time
import uuid
import grpc
from threading import Thread
from queue import Queue, Empty

def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix, e.g., 'my_test_1a2b3c4d'."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

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
