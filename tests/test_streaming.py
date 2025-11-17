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

    # 1. Create a product and check for the event
    project_name = unique_name("stream_test_project")
    asset_name = unique_name("stream_test_asset")
    
    print(f"[TEST] Creating group: {project_name}")  # Added print for debugging
    group = kumiho.create_group(project_name)  # Updated to use new API
    cleanup_test_data.append(group)  # Add to cleanup
    print(f"[TEST] Creating product: {asset_name}")  # Added print for debugging
    product = group.create_product(product_name=asset_name, product_type="model")  # Uses instance method
    cleanup_test_data.append(product)  # Add to cleanup
    
    # First event: group creation
    print("[TEST] Waiting for 'group.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "group.created"
        assert event.kref.uri == f"kref://{group.path}"  # Event krefs now include "kref://" prefix
    except Empty:
        pytest.fail("Did not receive 'group.created' event in time.")
    
    # Second event: product creation
    print("[TEST] Waiting for 'product.model.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "product.model.created"
        assert event.kref.uri == product.kref.uri
    except Empty:
        pytest.fail("Did not receive 'product.model.created' event in time.")

    # 2. Create a version and check for the event
    print("[TEST] Creating version...")  # Added print for debugging
    version = kumiho.create_version(product_kref=product.kref)  # Uses top-level kumiho.create_version()
    cleanup_test_data.append(version)  # Add to cleanup
    print("[TEST] Waiting for 'version.created' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "version.created"
        assert event.kref.uri == version.kref.uri
    except Empty:
        pytest.fail("Did not receive 'version.created' event in time.")

    # 3. Tag the version and check for the event
    print(f"[TEST] Tagging version with '{kumiho.PUBLISHED_TAG}'...")  # Added print for debugging
    version.tag(kumiho.PUBLISHED_TAG)  # No top-level equivalent yet, so kept as object method
    print("[TEST] Waiting for 'version.tagged' event...")  # Added print for debugging
    try:
        event = event_queue.get(timeout=2)
        print(f"[TEST] Consumed event: {event.routing_key}")  # Added print for debugging
        assert event.routing_key == "version.tagged"
        assert event.kref.uri == version.kref.uri
        assert event.details["tag"] == kumiho.PUBLISHED_TAG
    except Empty:
        pytest.fail("Did not receive 'version.tagged' event in time.")
    
    print("[TEST] Event streaming test completed successfully.")  # Added print for debugging
