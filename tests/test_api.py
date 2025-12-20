import kumiho
import pytest
import time
import uuid
import grpc
from unittest.mock import MagicMock

# --- Helper for unique naming in tests ---
def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix, e.g., 'my_test_1a2b3c4d'."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# Import classes directly from the .client module
import mock_helpers


# --- Constants ---
PUBLISHED_TAG = "published"

# --- Mocked Unit Tests ---

@pytest.fixture
def mock_client(monkeypatch):
    """Pytest fixture to provide a Kumiho client with a mocked gRPC stub."""
    # Save the original default client to restore after the test
    original_client = kumiho._default_client
    
    mock_stub = MagicMock()
    monkeypatch.setattr("kumiho.client.kumiho_pb2_grpc.KumihoServiceStub", lambda channel: mock_stub)
    
    # Use kumiho.connect to get a client instance without importing _Client directly
    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    # Configure the global default client to use our mock
    kumiho.configure_default_client(client)
    
    yield client, mock_stub
    
    # Teardown: Restore the original default client (may be None or the live_client)
    kumiho._default_client = original_client

def test_project_crud(mock_client):
    client, mock_stub = mock_client
    # Create
    create_pb = mock_helpers.mock_project_response(
        project_id="p1", name="demo"
    )
    mock_stub.CreateProject.return_value = create_pb
    project = kumiho.create_project(name="demo")
    mock_stub.CreateProject.assert_called_once()
    assert project.project_id == "p1"

    # List
    mock_stub.GetProjects.return_value = mock_helpers.mock_get_projects_response(projects=[create_pb])
    projects = kumiho.get_projects()
    mock_stub.GetProjects.assert_called_once()
    assert projects[0].name == "demo"

    # Delete
    mock_stub.DeleteProject.return_value = mock_helpers.mock_status_response(success=True, message="ok")
    resp = kumiho.delete_project(project_id="p1", force=True)
    mock_stub.DeleteProject.assert_called_once()
    assert resp.success

def test_pagination(mock_client):
    client, mock_stub = mock_client
    
    # Setup mock items
    item1 = mock_helpers.mock_item_response(
        kref_uri="kref://p1/s1/i1", name="i1", item_name="i1", kind="model"
    )
    item2 = mock_helpers.mock_item_response(
        kref_uri="kref://p1/s1/i2", name="i2", item_name="i2", kind="model"
    )
    
    # Mock GetItems response with pagination
    mock_response = mock_helpers.mock_get_items_response(
        items=[item1, item2],
        next_cursor="cursor_123",
        total_count=10
    )
    mock_stub.GetItems.return_value = mock_response
    mock_stub.ItemSearch.return_value = mock_response
    
    # Test Project.get_items
    pb = mock_helpers.mock_project_response(project_id="p1", name="demo")
    project = kumiho.Project(pb, client)
    results = project.get_items(page_size=2)
    
    # Verify request
    args, _ = mock_stub.ItemSearch.call_args
    request = args[0]
    assert request.pagination.page_size == 2
    assert request.pagination.cursor == ""
    
    # Verify response
    assert len(results) == 2
    assert results.next_cursor == "cursor_123"
    assert results.total_count == 10
    assert results[0].name == "i1"
    
    # Test Space.get_items with cursor
    space_pb = mock_helpers.mock_space_response(path="p1/s1")
    space = kumiho.Space(space_pb, client)
    results_page2 = space.get_items(page_size=2, cursor="cursor_123")
    
    # Verify request
    args, _ = mock_stub.GetItems.call_args
    request = args[0]
    assert request.pagination.page_size == 2
    assert request.pagination.cursor == "cursor_123"

def test_create_space(mock_client):
    """Test the create_space method via Project."""
    client, mock_stub = mock_client
    
    # Mock Project creation first
    mock_stub.CreateProject.return_value = mock_helpers.mock_project_response(
        project_id="p1", name="projectA"
    )
    project = kumiho.create_project("projectA")

    # Mock Space creation
    mock_stub.CreateSpace.return_value = mock_helpers.mock_space_response(path="/projectA/seqA")
    
    # Create space via project
    space = project.create_space(name="seqA")
    
    # Verify calls
    mock_stub.CreateSpace.assert_called_once_with(
        mock_helpers.mock_create_space_request(parent_path="/projectA", space_name="seqA")
    )
    assert space.path == "/projectA/seqA"

def test_get_item_from_revision_kref(mock_client):
    """Test get_item_from_revision method."""
    client, mock_stub = mock_client
    
    # Mock the revision response
    revision_response = mock_helpers.mock_revision_response(
        kref_uri="kref://projectA/modelA.asset?r=1",
        item_kref_uri="kref://projectA/modelA.asset",
        number=1,
        latest=True,
        tags=[],
        metadata={},
        author="test_author",
        username="test_user",
        deprecated=False,
        published=False
    )
    mock_stub.GetRevision.return_value = revision_response
    
    # Mock the item response
    item_response = mock_helpers.mock_item_response(
        kref_uri="kref://projectA/modelA.asset",
        name="modelA.asset",
        item_name="modelA",
        kind="asset",
        author="test_author",
        username="test_user",
        deprecated=False,
        metadata={}
    )
    mock_stub.GetItem.return_value = item_response
    
    # Test the method
    revision = kumiho.get_revision("kref://projectA/modelA.asset?r=1")
    item = revision.get_item()
    
    # Verify calls
    mock_stub.GetRevision.assert_called_once_with(
        mock_helpers.mock_kref_request(uri="kref://projectA/modelA.asset?r=1")
    )
    mock_stub.GetItem.assert_called_once_with(
        mock_helpers.mock_get_item_request(
            parent_path="/projectA",
            item_name="modelA", 
            kind="asset"
        )
    )
    
    assert item.item_name == "modelA"
    assert item.kind == "asset"

def test_get_item_by_kref(mock_client):
    """Test get_item_by_kref method."""
    client, mock_stub = mock_client
    
    # Mock the item response
    item_response = mock_helpers.mock_item_response(
        kref_uri="kref://projectA/modelA.asset",
        name="modelA.asset",
        item_name="modelA",
        kind="asset",
        author="test_author",
        username="test_user",
        deprecated=False,
        metadata={}
    )
    mock_stub.GetItem.return_value = item_response
    
    # Test the method
    item = kumiho.get_item("kref://projectA/modelA.asset")
    
    # Verify calls
    mock_stub.GetItem.assert_called_once_with(
        mock_helpers.mock_get_item_request(
            parent_path="/projectA",
            item_name="modelA", 
            kind="asset"
        )
    )
    
    assert item.item_name == "modelA"
    assert item.kind == "asset"

def test_get_space_from_path(mock_client):
    """Test get_space via Project."""
    client, mock_stub = mock_client
    
    # Mock Project creation/retrieval (simulated)
    mock_stub.CreateProject.return_value = mock_helpers.mock_project_response(
        project_id="p1", name="projectA"
    )
    project = kumiho.create_project("projectA")
    
    path = "seqA"
    full_path = "/projectA/seqA"
    mock_stub.GetSpace.return_value = mock_helpers.mock_space_response(path=full_path)
    
    # Get space via project
    space = project.get_space(path)
    
    mock_stub.GetSpace.assert_called_once_with(
        mock_helpers.mock_get_space_request(path_or_kref=full_path)
    )
    assert space.path == full_path

def test_item_search_with_context(mock_client):
    """Test item_search with a context filter."""
    client, mock_stub = mock_client
    item_kref_uri = "kref://projectA/seqA/001/kumiho.model"
    response = mock_helpers.mock_get_items_response(
        items=[mock_helpers.mock_item_response(
            kref_uri=item_kref_uri,
            name="kumiho.model",
            item_name="kumiho",
            kind="model"
        )]
    )
    mock_stub.ItemSearch.return_value = response
    results = kumiho.item_search(context_filter="projectA/seqA", kind_filter="model")
    mock_stub.ItemSearch.assert_called_once_with(
        mock_helpers.mock_item_search_request(
            context_filter="projectA/seqA",
            item_name_filter="",
            kind_filter="model"
        )
    )
    assert len(results) == 1
    assert results[0].kref.uri == item_kref_uri


# --- Integration Tests (requires running server and DB) ---

def test_full_creation_workflow(live_client, cleanup_test_data):
    """
    Tests the fundamental workflow of creating a space, item, revision, and artifact.
    """
    project_name = unique_name("smoke_test_project")
    asset_name = unique_name("smoke_test_asset")
    
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    assert space.path == f"/{project_name}"

    item = space.create_item(item_name=asset_name, kind="model")
    cleanup_test_data.append(item)
    assert item.kref.uri == f"kref://{project_name}/{asset_name}.model"

    revision = item.create_revision()
    cleanup_test_data.append(revision)
    assert revision.kref.uri.endswith("?r=1")

    artifact = revision.create_artifact("data", "/path/to/smoke_test.dat")
    cleanup_test_data.append(artifact)
    assert artifact.kref.uri.endswith("&a=data")
    assert artifact.location == "/path/to/smoke_test.dat"

def test_get_artifacts_by_location(live_client, cleanup_test_data):
    """
    Tests that searching for artifacts by location returns a time-sorted list
    with full parent context.
    """
    project_name = unique_name("loc_test_project")
    asset_name = unique_name("loc_test_asset")
    shared_location = f"/mnt/data/test_data/{uuid.uuid4().hex}.vdb"

    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name=asset_name, kind="model")
    cleanup_test_data.append(item)
    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    time.sleep(1.1)
    v2 = item.create_revision()
    cleanup_test_data.append(v2)

    res1 = v1.create_artifact("model_data", shared_location)
    cleanup_test_data.append(res1)
    res2 = v2.create_artifact("model_data", shared_location)
    cleanup_test_data.append(res2)

    found_artifacts = kumiho.get_artifacts_by_location(shared_location)

    assert len(found_artifacts) >= 2
    # The most recently created artifact (res2) should be the first in the list
    newest_res = found_artifacts[0]
    oldest_res = found_artifacts[1]

    assert newest_res.kref == res2.kref  
    assert newest_res.revision_kref == v2.kref  
    assert newest_res.item_kref == item.kref  

    assert oldest_res.kref == res1.kref  
    assert oldest_res.revision_kref == v1.kref  
    assert oldest_res.item_kref == item.kref  

def test_edge_workflow(live_client, cleanup_test_data):
    """
    Tests creating and retrieving edges between revisions.
    """
    project_name = unique_name("edge_proj")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    
    model_item = space.create_item(item_name="character_model", kind="model")
    cleanup_test_data.append(model_item)
    texture_item = space.create_item(item_name="character_textures", kind="texture")
    cleanup_test_data.append(texture_item)

    model_v1 = model_item.create_revision()
    cleanup_test_data.append(model_v1)
    texture_v1 = texture_item.create_revision()
    cleanup_test_data.append(texture_v1)

    edge = texture_v1.create_edge(
        target_revision=model_v1,
        edge_type=kumiho.EdgeType.DEPENDS_ON
    )
    cleanup_test_data.append(edge)

    assert edge.source_kref == texture_v1.kref  
    assert edge.target_kref == model_v1.kref  
    
    # Retrieve and verify
    source_edges = texture_v1.get_edges()
    assert len(source_edges) >= 1
    retrieved_edge = source_edges[0]
    assert retrieved_edge.target_kref == model_v1.kref  
    assert retrieved_edge.edge_type == kumiho.EdgeType.DEPENDS_ON

def test_peek_next_revision(live_client, cleanup_test_data):
    """
    Tests that peeking at the next revision number works correctly.
    """
    project_name = unique_name("peek_test_project")
    asset_name = unique_name("peek_test_asset")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name=asset_name, kind="rig")
    cleanup_test_data.append(item)

    assert item.peek_next_revision() == 1
    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    assert v1.number == 1
    assert item.peek_next_revision() == 2
    v2 = item.create_revision()
    cleanup_test_data.append(v2)
    assert v2.number == 2
    assert item.peek_next_revision() == 3

def test_get_latest_revision(live_client, cleanup_test_data):
    """
    Tests getting the latest revision of an item.
    """
    project_name = unique_name("latest_test_project")
    asset_name = unique_name("latest_test_asset")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name=asset_name, kind="rig")
    cleanup_test_data.append(item)

    # No revisions yet
    assert item.get_latest_revision() is None

    # Create first revision
    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    assert v1.number == 1
    assert v1.latest == True
    assert item.get_latest_revision().number == 1

    # Create second revision
    v2 = item.create_revision()
    cleanup_test_data.append(v2)
    assert v2.number == 2
    assert v2.latest == True
    # Check that get_latest_revision returns v2
    latest = item.get_latest_revision()
    assert latest is not None
    assert latest.number == 2

def test_revision_by_tag_and_time(live_client, cleanup_test_data):
    """
    Tests getting revisions by tag, by time, and by combined tag+time.
    
    The combined tag+time query is essential for reproducible builds:
    "What was the published version of this asset on June 1st?"
    """
    import time
    from datetime import datetime, timedelta
    
    project_name = unique_name("tag_time_test_project")
    asset_name = unique_name("tag_time_test_asset")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name=asset_name, kind="item")
    cleanup_test_data.append(item)
    revision1 = item.create_revision()
    cleanup_test_data.append(revision1)

    # Tag revision1 with a custom tag
    revision1.tag("hello")
    
    # Tag revision1 as published (simulating a milestone)
    revision1.tag("published")
    
    # Avoid brittle client-local timestamps when running against a remote server (Cloud Run):
    # use a server-derived timestamp as our "after revision1 was published" moment.
    #
    # Note: server timestamps for created_at are second precision, while tag_history may include
    # sub-second precision. Sleeping ensures we cross a second boundary so the derived timestamp
    # is definitely after the publish tag was applied.
    time.sleep(1.1)
    revision2 = item.create_revision()
    cleanup_test_data.append(revision2)
    assert revision2.created_at is not None
    time_after_tag1 = datetime.fromisoformat(revision2.created_at.replace("Z", "+00:00"))

    # Test: get revision by tag
    tag_revision = item.get_revision_by_tag("hello")
    assert tag_revision is not None
    assert tag_revision.number == revision1.number

    # Test: get revision by time only (should return latest at that time)
    time_revision = item.get_revision_by_time(revision1.created_at)
    assert time_revision is not None

    # Test: get revision by combined tag+time
    # This answers: "What was the published version at this point in time?"
    # We query at time_after_tag1 when revision1 had the published tag
    published_at_time = item.get_revision_by_time(
        time_after_tag1,
        tag="published"
    )
    assert published_at_time is not None
    assert published_at_time.number == revision1.number
    
    # Ensure the "superseding" publish tag is applied after time_after_tag1 (second precision).
    time.sleep(1.1)
    
    # Now tag revision2 as published (superseding revision1)
    revision2.tag("published")
    
    # Query for published at time_after_tag1 should still return revision1
    # (because at that time, revision1 was the published one, and revision2 wasn't tagged yet)
    historical_published = item.get_revision_by_time(
        time_after_tag1,
        tag="published"
    )
    assert historical_published is not None
    assert historical_published.number == revision1.number
    
    # Query for published NOW (after revision2 was tagged) should return revision2
    time_after_tag2 = time_after_tag1 + timedelta(seconds=5)
    current_published = item.get_revision_by_time(
        time_after_tag2,
        tag="published"
    )
    assert current_published is not None
    assert current_published.number == revision2.number

# --- New Feature Tests ---

def test_metadata_update_workflow(live_client, cleanup_test_data):
    """Tests setting and updating metadata on all object types."""
    project = kumiho.create_project(unique_name("meta_proj"))
    cleanup_test_data.append(project)
    space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name=unique_name("asset"), kind="model")
    cleanup_test_data.append(item)
    revision = item.create_revision()
    cleanup_test_data.append(revision)
    artifact = revision.create_artifact("geo", "/path/to/file.abc")
    cleanup_test_data.append(artifact)

    # Test setting metadata
    space = space.set_metadata({"status": "active"})
    item = item.set_metadata({"pipeline_step": "modeling"})
    revision = revision.set_metadata({"approved_by": "lead"})
    artifact = artifact.set_metadata({"format": "alembic"})

    assert space.metadata["status"] == "active"
    assert item.metadata["pipeline_step"] == "modeling"
    assert revision.metadata["approved_by"] == "lead"
    assert artifact.metadata["format"] == "alembic"

def test_space_deletion_logic(live_client, cleanup_test_data):
    """Tests safe and forced deletion of spaces."""
    # Setup
    project = kumiho.create_project(unique_name("del_proj"))
    cleanup_test_data.append(project)
    proj_space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(proj_space)
    item = proj_space.create_item(item_name="asset", kind="model")
    cleanup_test_data.append(item)
    empty_space = proj_space.create_space(name="empty_space")
    cleanup_test_data.append(empty_space)

    # 1. Succeed in deleting empty space without force
    empty_space.delete()
    cleanup_test_data.remove(empty_space)

    # 2. Fail to delete non-empty space without force
    with pytest.raises(grpc.RpcError) as e:
        proj_space.delete()
    if e.value.code() == grpc.StatusCode.UNAVAILABLE:
        pytest.skip("Control-plane JWKS unavailable in test environment")
    assert e.value.code() == grpc.StatusCode.PERMISSION_DENIED

    # 3. Succeed in deleting non-empty space with admin force
    proj_space.delete(force=True)
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(proj_space)
    with pytest.raises(grpc.RpcError) as e:
        # Use project.get_space instead of live_client.get_space
        project.get_space(proj_space.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND
    with pytest.raises(grpc.RpcError) as e:
        project.get_space(empty_space.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_item_deprecation_and_deletion(live_client, cleanup_test_data):
    """Tests soft delete (deprecation) and hard delete for items."""
    project = kumiho.create_project(unique_name("dep_proj"))
    cleanup_test_data.append(project)
    space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="char", kind="rig")
    cleanup_test_data.append(item)
    
    # 1. Deprecate the item
    item.delete()
    item_reloaded = space.get_item(item_name="char", kind="rig")
    assert item_reloaded.deprecated is True

    # 2. Re-creating it should un-deprecate it
    item_new = space.create_item(item_name="char", kind="rig")
    cleanup_test_data.append(item_new)
    assert item_new.deprecated is False

    # 3. Hard-delete with admin rights (assume current user is admin in test env)
    item_new.delete(force=True)
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(item_new)
    with pytest.raises(grpc.RpcError) as e:
        space.get_item(item_name="char", kind="rig")
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_revision_tagging_workflow(live_client, cleanup_test_data):
    """Tests the full lifecycle of tagging a revision."""
    project = kumiho.create_project(unique_name("tag_proj"))
    cleanup_test_data.append(project)
    space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="fx", kind="cache")
    cleanup_test_data.append(item)
    v1 = item.create_revision()
    cleanup_test_data.append(v1)

    assert v1.has_tag("approved") is False
    
    v1.tag("approved")
    assert v1.has_tag("approved") is True
    assert v1.was_tagged("approved") is True

    v1.untag("approved")
    assert v1.has_tag("approved") is False
    # was_tagged should still be true as it checks history
    assert v1.was_tagged("approved") is True

def test_published_revision_immutability(live_client, cleanup_test_data):
    """Tests that a 'published' revision and its artifacts are immutable."""
    project = kumiho.create_project(unique_name("immutable_proj"))
    cleanup_test_data.append(project)
    space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="shot", kind="comp")
    cleanup_test_data.append(item)
    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    artifact = v1.create_artifact("main", "/path/to/exr_seq")
    cleanup_test_data.append(artifact)

    v1.tag(PUBLISHED_TAG)
    v1_reloaded = item.get_revision(1)
    assert v1_reloaded.published is True

    # Test immutability rules - all these should fail
    def expect_error(fn, expected_substr: str):
        try:
            fn()
            pytest.fail("Expected immutable/published error")
        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("Control-plane JWKS unavailable in test environment")
            assert expected_substr.lower() in (exc.details() or "").lower()

    expect_error(lambda: v1.set_metadata({"new_key": "new_val"}), "immutable")
    expect_error(lambda: artifact.set_metadata({"new_key": "new_val"}), "immutable")
    expect_error(lambda: v1.untag(PUBLISHED_TAG), "immutable")
    expect_error(lambda: v1.delete(), "immutable")
    expect_error(lambda: artifact.delete(), "immutable")
    expect_error(lambda: v1.create_artifact("mask", "/path/to/mask.png"), "published")

def test_get_artifact_and_locations(live_client, cleanup_test_data):
    """Tests retrieving specific artifacts and all locations from a revision."""
    project = kumiho.create_project(unique_name("res_proj"))
    cleanup_test_data.append(project)
    space = project.create_space(name=project.name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="set", kind="env")
    cleanup_test_data.append(item)
    v = item.create_revision()
    cleanup_test_data.append(v)
    res1 = v.create_artifact("hdri", "/loc/hdri.exr")
    cleanup_test_data.append(res1)
    res2 = v.create_artifact("lidar", "/loc/lidar.obj")
    cleanup_test_data.append(res2)

    # Get all artifacts
    artifacts = v.get_artifacts()
    assert len(artifacts) == 2
    
    # Get one specific artifact
    lidar_res = v.get_artifact("lidar")
    assert lidar_res.kref == res2.kref  
    assert lidar_res.location == "/loc/lidar.obj"

    # Get all locations
    locations = v.get_locations()
    assert set(locations) == {"/loc/hdri.exr", "/loc/lidar.obj"}

def test_resolve_kref_with_time(mock_client):
    """Tests resolving a kref at a specific point in time."""
    client, mock_stub = mock_client  # Unpack the tuple
    revision_response = mock_helpers.mock_revision_response(
        kref_uri="kref://obj1?r=2",
        item_kref_uri="kref://obj1",
        number=2,
        latest=True,
        tags=[],
        metadata={},
        author="test",
        username="test",
        deprecated=False,
        published=False
    )
    mock_stub.ResolveKref.return_value = revision_response
    time_str = "202510131200"
    # Use kumiho.get_revision with time parameter
    resolved = kumiho.get_revision(f"kref://obj1?time={time_str}")
    
    mock_stub.ResolveKref.assert_called_once()
    request_arg = mock_stub.ResolveKref.call_args[0][0]
    
    assert request_arg.kref == "kref://obj1"
    assert request_arg.time == time_str
    assert not request_arg.tag
    assert resolved.number == 2

def test_resolve_kref_with_tag_and_time(mock_client):
    """Tests resolving a kref with a tag at a specific point in time."""
    client, mock_stub = mock_client  # Unpack the tuple
    revision_response = mock_helpers.mock_revision_response(
        kref_uri="kref://obj1?r=1",
        item_kref_uri="kref://obj1",
        number=1,
        latest=True,
        tags=[],
        metadata={},
        author="test",
        username="test",
        deprecated=False,
        published=False
    )
    mock_stub.ResolveKref.return_value = revision_response
    time_str = "202510101000"
    tag_name = "published"
    
    resolved = kumiho.get_revision(f"kref://obj1?tag={tag_name}&time={time_str}") 
    
    mock_stub.ResolveKref.assert_called_once()
    request_arg = mock_stub.ResolveKref.call_args[0][0]
    
    assert request_arg.kref == "kref://obj1"
    assert request_arg.tag == tag_name
    assert request_arg.time == time_str
    assert resolved.number == 1

def test_resolve_kref_invalid_time_format(mock_client):
    """Tests that an invalid time format raises a ValueError."""
    client, mock_stub = mock_client  # Unpack the tuple
    with pytest.raises(ValueError, match="time must be in YYYYMMDDHHMM format"):
        kumiho.get_revision("kref://some_id?time=2025-10-13 12:00:00")

def test_janus_parity_features(live_client, cleanup_test_data):
    """Tests features added for Janus parity: deprecation, default artifact, traversal, edges."""
    project_name = unique_name("janus_proj")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="asset", kind="model")
    cleanup_test_data.append(item)
    revision = item.create_revision()
    cleanup_test_data.append(revision)
    artifact = revision.create_artifact("main", "/path/to/file")
    cleanup_test_data.append(artifact)

    # 1. Deprecation
    # Item
    assert item.deprecated is False
    item.set_deprecated(True)
    assert item.deprecated is True
    # Reload to verify persistence
    item_reloaded = space.get_item("asset", "model")
    assert item_reloaded.deprecated is True
    item.set_deprecated(False)
    assert item.deprecated is False

    # Revision
    assert revision.deprecated is False
    revision.set_deprecated(True)
    assert revision.deprecated is True
    revision.set_deprecated(False)
    assert revision.deprecated is False

    # Artifact
    assert artifact.deprecated is False
    artifact.set_deprecated(True)
    assert artifact.deprecated is True
    artifact.set_deprecated(False)
    assert artifact.deprecated is False

    # 2. Default Artifact
    assert revision.default_artifact is None
    artifact.set_default()
    # Reload revision to check default artifact
    v_reloaded = item.get_revision(revision.number)
    assert v_reloaded.default_artifact == artifact.name

    # 3. Traversal
    # From Artifact
    assert artifact.get_revision().kref.uri == revision.kref.uri
    assert artifact.get_item().kref.uri == item.kref.uri
    assert artifact.get_space().path == space.path
    assert artifact.get_project().name == project.name

    # From Revision
    assert revision.get_item().kref.uri == item.kref.uri
    assert revision.get_space().path == space.path
    assert revision.get_project().name == project.name

    # From Item
    assert item.get_space().path == space.path
    assert item.get_project().name == project.name

    # From Space
    assert space.get_project().name == project.name

    # 4. Edge Types
    # EdgeType is now exposed at package level
    v2 = item.create_revision()
    cleanup_test_data.append(v2)
    
    # Use new convenience method
    edge = revision.create_edge(
        target_revision=v2,
        edge_type=kumiho.EdgeType.CREATED_FROM
    )
    cleanup_test_data.append(edge)
    assert edge.edge_type == kumiho.EdgeType.CREATED_FROM
    
    # Verify get_edges
    edges = revision.get_edges()
    assert len(edges) >= 1
    assert edges[0].edge_type == kumiho.EdgeType.CREATED_FROM
    
    # Verify delete_edge
    revision.delete_edge(v2, kumiho.EdgeType.CREATED_FROM)
    edges_after = revision.get_edges()
    # Note: get_edges might return empty list or filtered list. 
    # Since we just deleted the only edge we created, it should be empty or not contain that specific edge.
    # But let's be safe and check if the specific edge is gone.
    assert not any(e.target_kref.uri == v2.kref.uri and e.edge_type == kumiho.EdgeType.CREATED_FROM for e in edges_after)

    # 5. Edge Direction
    # Create an edge: revision -> v2 (CREATED_FROM)
    revision.create_edge(v2, kumiho.EdgeType.CREATED_FROM)
    
    # Test Outgoing (Default)
    outgoing = revision.get_edges(direction=kumiho.OUTGOING)
    assert len(outgoing) > 0
    assert outgoing[0].source_kref.uri == revision.kref.uri
    assert outgoing[0].target_kref.uri == v2.kref.uri
    
    # Test Incoming (from v2's perspective)
    incoming = v2.get_edges(direction=kumiho.INCOMING)
    assert len(incoming) > 0
    assert incoming[0].source_kref.uri == revision.kref.uri
    assert incoming[0].target_kref.uri == v2.kref.uri
    
    # Test Both
    both_v1 = revision.get_edges(direction=kumiho.BOTH)
    assert len(both_v1) > 0
    both_v2 = v2.get_edges(direction=kumiho.BOTH)
    assert len(both_v2) > 0
