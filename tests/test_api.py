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
from kumiho import Client
from kumiho.proto import kumiho_pb2

# --- Constants ---
PUBLISHED_TAG = "published"

# --- Mocked Unit Tests ---

@pytest.fixture
def mock_client(monkeypatch):
    """Pytest fixture to provide a Kumiho client with a mocked gRPC stub."""
    mock_stub = MagicMock()
    monkeypatch.setattr("kumiho.client.kumiho_pb2_grpc.KumihoServiceStub", lambda channel: mock_stub)
    client = Client()
    yield client, mock_stub

def test_create_group(mock_client):
    """Test the create_group method."""
    client, mock_stub = mock_client
    mock_stub.CreateGroup.return_value = kumiho_pb2.GroupResponse(path="/projectA/seqA")
    group = client.create_group(parent_path="/projectA", group_name="seqA")  # Mocked test: keep as-is for direct client testing
    assert group.path == "/projectA/seqA"

def test_get_product_from_version_kref(mock_client):
    """Test get_product_from_version method."""
    client, mock_stub = mock_client
    
    # Mock the version response
    version_response = kumiho_pb2.VersionResponse(
        kref=kumiho_pb2.Kref(uri="kumiho://projectA/modelA.asset?v=1"),
        product_kref=kumiho_pb2.Kref(uri="kumiho://projectA/modelA.asset"),
        number=1,
        latest=True,
        tags=[],
        metadata={},
        author="test_author",
        username="test_user",
        deprecated=False,
        published=False
    )
    mock_stub.GetVersion.return_value = version_response
    
    # Mock the product response
    product_response = kumiho_pb2.ProductResponse(
        kref=kumiho_pb2.Kref(uri="kumiho://projectA/modelA.asset"),
        name="modelA.asset",
        product_name="modelA",
        product_type="asset",
        author="test_author",
        username="test_user",
        deprecated=False,
        metadata={}
    )
    mock_stub.GetProduct.return_value = product_response
    
    # Test the method
    product = client.get_product_from_version("kumiho://projectA/modelA.asset?v=1")
    
    # Verify calls
    mock_stub.GetVersion.assert_called_once_with(
        kumiho_pb2.KrefRequest(kref=kumiho_pb2.Kref(uri="kumiho://projectA/modelA.asset?v=1"))
    )
    mock_stub.GetProduct.assert_called_once_with(
        kumiho_pb2.GetProductRequest(
            parent_path="/projectA",
            product_name="modelA", 
            product_type="asset"
        )
    )
    
    assert product.product_name == "modelA"
    assert product.product_type == "asset"

def test_get_product_by_kref(mock_client):
    """Test get_product_by_kref method."""
    client, mock_stub = mock_client
    
    # Mock the product response
    product_response = kumiho_pb2.ProductResponse(
        kref=kumiho_pb2.Kref(uri="kumiho://projectA/modelA.asset"),
        name="modelA.asset",
        product_name="modelA",
        product_type="asset",
        author="test_author",
        username="test_user",
        deprecated=False,
        metadata={}
    )
    mock_stub.GetProduct.return_value = product_response
    
    # Test the method
    product = client.get_product_by_kref("kumiho://projectA/modelA.asset")
    
    # Verify calls
    mock_stub.GetProduct.assert_called_once_with(
        kumiho_pb2.GetProductRequest(
            parent_path="/projectA",
            product_name="modelA", 
            product_type="asset"
        )
    )
    
    assert product.product_name == "modelA"
    assert product.product_type == "asset"

def test_get_group_from_path(mock_client):
    """Test get_group with a direct path."""
    client, mock_stub = mock_client
    path = "projectA/seqA"
    mock_stub.GetGroup.return_value = kumiho_pb2.GroupResponse(path=f"/{path}")
    group = client.get_group(path)
    mock_stub.GetGroup.assert_called_once_with(
        kumiho_pb2.GetGroupRequest(path_or_kref=path)
    )
    assert group.path == "/projectA/seqA"

def test_product_search_with_context(mock_client):
    """Test product_search with a context filter."""
    client, mock_stub = mock_client
    product_kref_uri = "kref://projectA/seqA/001/kumiho.model"
    response = kumiho_pb2.GetProductsResponse(
        products=[kumiho_pb2.ProductResponse(kref=kumiho_pb2.Kref(uri=product_kref_uri))]
    )
    mock_stub.ProductSearch.return_value = response
    results = client.product_search(context_filter="projectA/seqA", product_type_filter="model")
    mock_stub.ProductSearch.assert_called_once_with(
        kumiho_pb2.ProductSearchRequest(
            context_filter="projectA/seqA",
            product_name_filter="",
            product_type_filter="model"
        )
    )
    assert len(results) == 1
    assert results[0].kref.uri == product_kref_uri


# --- Integration Tests (requires running server and DB) ---

def test_full_creation_workflow(live_client, cleanup_test_data):
    """
    Tests the fundamental workflow of creating a group, product, version, and resource.
    """
    project_name = unique_name("smoke_test_project")
    asset_name = unique_name("smoke_test_asset")
    
    group = kumiho.create_group(project_name)  # Updated: Use new top-level API
    cleanup_test_data.append(group)
    assert group.path == f"/{project_name}"

    product = group.create_product(product_name=asset_name, product_type="model")
    cleanup_test_data.append(product)
    assert product.kref.uri == f"kref://{project_name}/{asset_name}.model"

    version = product.create_version()
    cleanup_test_data.append(version)
    assert version.kref.uri.endswith("?v=1")

    resource = version.create_resource("data", "/path/to/smoke_test.dat")
    cleanup_test_data.append(resource)
    assert resource.kref.uri.endswith("&r=data")
    assert resource.location == "/path/to/smoke_test.dat"

def test_get_resources_by_location(live_client, cleanup_test_data):
    """
    Tests that searching for resources by location returns a time-sorted list
    with full parent context.
    """
    project_name = unique_name("loc_test_project")
    asset_name = unique_name("loc_test_asset")
    shared_location = f"/mnt/data/test_data/{uuid.uuid4().hex}.vdb"

    group = kumiho.create_group(project_name)
    cleanup_test_data.append(group)
    product = group.create_product(product_name=asset_name, product_type="model")
    cleanup_test_data.append(product)
    v1 = product.create_version()
    cleanup_test_data.append(v1)
    time.sleep(1.1)
    v2 = product.create_version()
    cleanup_test_data.append(v2)

    res1 = v1.create_resource("model_data", shared_location)
    cleanup_test_data.append(res1)
    res2 = v2.create_resource("model_data", shared_location)
    cleanup_test_data.append(res2)

    found_resources = live_client.get_resources_by_location(shared_location)

    assert len(found_resources) >= 2
    # The most recently created resource (res2) should be the first in the list
    newest_res = found_resources[0]
    oldest_res = found_resources[1]

    assert newest_res.kref == res2.kref  
    assert newest_res.version_kref == v2.kref  
    assert newest_res.product_kref == product.kref  

    assert oldest_res.kref == res1.kref  
    assert oldest_res.version_kref == v1.kref  
    assert oldest_res.product_kref == product.kref  

def test_linking_workflow(live_client, cleanup_test_data):
    """
    Tests creating and retrieving links between versions.
    """
    project_name = unique_name("link_proj")
    group = kumiho.create_group(project_name)
    cleanup_test_data.append(group)
    
    model_product = group.create_product(product_name="character_model", product_type="model")
    cleanup_test_data.append(model_product)
    texture_product = group.create_product(product_name="character_textures", product_type="texture")
    cleanup_test_data.append(texture_product)

    model_v1 = model_product.create_version()
    cleanup_test_data.append(model_v1)
    texture_v1 = texture_product.create_version()
    cleanup_test_data.append(texture_v1)

    link = live_client.create_link(
        source_version=texture_v1,
        target_version=model_v1,
        link_type="texture_for"
    )
    cleanup_test_data.append(link)

    assert link.source_kref == texture_v1.kref  
    assert link.target_kref == model_v1.kref  
    
    # Retrieve and verify
    source_links = live_client.get_links(texture_v1.kref)
    assert len(source_links) >= 1
    retrieved_link = source_links[0]
    assert retrieved_link.target_kref == model_v1.kref  
    assert retrieved_link.link_type == "texture_for"

def test_peek_next_version(live_client, cleanup_test_data):
    """
    Tests that peeking at the next version number works correctly.
    """
    project_name = unique_name("peek_test_project")
    asset_name = unique_name("peek_test_asset")
    group = kumiho.create_group(project_name)
    cleanup_test_data.append(group)
    product = group.create_product(product_name=asset_name, product_type="rig")
    cleanup_test_data.append(product)

    assert product.peek_next_version() == 1
    v1 = product.create_version()
    cleanup_test_data.append(v1)
    assert v1.number == 1
    assert product.peek_next_version() == 2
    v2 = product.create_version()
    cleanup_test_data.append(v2)
    assert v2.number == 2
    assert product.peek_next_version() == 3

def test_get_latest_version(live_client, cleanup_test_data):
    """
    Tests getting the latest version of a product.
    """
    project_name = unique_name("latest_test_project")
    asset_name = unique_name("latest_test_asset")
    group = kumiho.create_group(project_name)
    cleanup_test_data.append(group)
    product = group.create_product(product_name=asset_name, product_type="rig")
    cleanup_test_data.append(product)

    # No versions yet
    assert product.get_latest_version() is None

    # Create first version
    v1 = product.create_version()
    cleanup_test_data.append(v1)
    assert v1.number == 1
    assert v1.latest == True
    assert product.get_latest_version().number == 1

    # Create second version
    v2 = product.create_version()
    cleanup_test_data.append(v2)
    assert v2.number == 2
    assert v2.latest == True
    # Check that get_latest_version returns v2
    latest = product.get_latest_version()
    assert latest is not None
    assert latest.number == 2

def test_version_by_tag_and_time(live_client, cleanup_test_data):
    """
    Tests getting versions by tag and time.
    """
    project_name = unique_name("tag_time_test_project")
    asset_name = unique_name("tag_time_test_asset")
    group = kumiho.create_group(project_name)
    cleanup_test_data.append(group)
    product = group.create_product(product_name=asset_name, product_type="item")
    cleanup_test_data.append(product)
    version1 = product.create_version()
    cleanup_test_data.append(version1)
    version2 = product.create_version()
    cleanup_test_data.append(version2)

    version1.tag("hello")

    tag_version = product.get_version_by_tag("hello")
    assert tag_version is not None

    time_version = product.get_version_by_time(version1.created_at)
    assert time_version is not None

# --- New Feature Tests ---

def test_metadata_update_workflow(live_client: Client, cleanup_test_data):
    """Tests setting and updating metadata on all object types."""
    group = kumiho.create_group(unique_name("meta_proj"))
    cleanup_test_data.append(group)
    product = group.create_product(product_name=unique_name("asset"), product_type="model")
    cleanup_test_data.append(product)
    version = product.create_version()
    cleanup_test_data.append(version)
    resource = version.create_resource("geo", "/path/to/file.abc")
    cleanup_test_data.append(resource)

    # Test setting metadata
    group = group.set_metadata({"status": "active"})
    product = product.set_metadata({"pipeline_step": "modeling"})
    version = version.set_metadata({"approved_by": "lead"})
    resource = resource.set_metadata({"format": "alembic"})

    assert group.metadata["status"] == "active"
    assert product.metadata["pipeline_step"] == "modeling"
    assert version.metadata["approved_by"] == "lead"
    assert resource.metadata["format"] == "alembic"

def test_group_deletion_logic(live_client: Client, cleanup_test_data):
    """Tests safe and forced deletion of groups."""
    # Setup
    proj = kumiho.create_group(unique_name("del_proj"))
    cleanup_test_data.append(proj)
    prod = proj.create_product(product_name="asset", product_type="model")
    cleanup_test_data.append(prod)
    empty_group = kumiho.create_group(unique_name("del_empty"))
    cleanup_test_data.append(empty_group)

    # 1. Fail to delete non-empty group without force
    with pytest.raises(grpc.RpcError) as e:
        proj.delete()
    assert e.value.code() == grpc.StatusCode.PERMISSION_DENIED

    # 2. Succeed in deleting non-empty group with admin force
    proj.delete(force=True)  # Removed user_permission; client handles current user
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(proj)
    with pytest.raises(grpc.RpcError) as e:
        live_client.get_group(proj.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

    # 3. Succeed in deleting empty group without force
    empty_group.delete()
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(empty_group)
    with pytest.raises(grpc.RpcError) as e:
        live_client.get_group(empty_group.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_product_deprecation_and_deletion(live_client: Client, cleanup_test_data):
    """Tests soft delete (deprecation) and hard delete for products."""
    group = kumiho.create_group(unique_name("dep_proj"))
    cleanup_test_data.append(group)
    prod = group.create_product(product_name="char", product_type="rig")
    cleanup_test_data.append(prod)
    
    # 1. Deprecate the product
    prod.delete()
    prod_reloaded = group.get_product(product_name="char", product_type="rig")
    assert prod_reloaded.deprecated is True

    # 2. Re-creating it should un-deprecate it
    prod_new = group.create_product(product_name="char", product_type="rig")
    cleanup_test_data.append(prod_new)
    assert prod_new.deprecated is False

    # 3. Hard-delete with admin rights (assume current user is admin in test env)
    prod_new.delete(force=True)  # Removed user_permission; expect success
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(prod_new)
    with pytest.raises(grpc.RpcError) as e:
        group.get_product(product_name="char", product_type="rig")
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_version_tagging_workflow(live_client: Client, cleanup_test_data):
    """Tests the full lifecycle of tagging a version."""
    group = kumiho.create_group(unique_name("tag_proj"))
    cleanup_test_data.append(group)
    prod = group.create_product(product_name="fx", product_type="cache")
    cleanup_test_data.append(prod)
    v1 = prod.create_version()
    cleanup_test_data.append(v1)

    assert v1.has_tag("approved") is False
    
    v1.tag("approved")
    assert v1.has_tag("approved") is True
    assert v1.was_tagged("approved") is True

    v1.untag("approved")
    assert v1.has_tag("approved") is False
    # was_tagged should still be true as it checks history
    assert v1.was_tagged("approved") is True

def test_published_version_immutability(live_client: Client, cleanup_test_data):
    """Tests that a 'published' version and its resources are immutable."""
    group = kumiho.create_group(unique_name("immutable_proj"))
    cleanup_test_data.append(group)
    prod = group.create_product(product_name="shot", product_type="comp")
    cleanup_test_data.append(prod)
    v1 = prod.create_version()
    cleanup_test_data.append(v1)
    res = v1.create_resource("main", "/path/to/exr_seq")
    cleanup_test_data.append(res)

    v1.tag(PUBLISHED_TAG)
    v1_reloaded = prod.get_version(1)
    assert v1_reloaded.published is True

    # Test immutability rules - all these should fail
    with pytest.raises(grpc.RpcError, match="immutable"):
        v1.set_metadata({"new_key": "new_val"})
    with pytest.raises(grpc.RpcError, match="immutable"):
        res.set_metadata({"new_key": "new_val"})
    with pytest.raises(grpc.RpcError, match="immutable"):
        v1.untag(PUBLISHED_TAG)
    with pytest.raises(grpc.RpcError, match="immutable"):
        v1.delete()
    with pytest.raises(grpc.RpcError, match="immutable"):
        res.delete()
    with pytest.raises(grpc.RpcError, match="published"):
        v1.create_resource("mask", "/path/to/mask.png")

def test_get_resource_and_locations(live_client: Client, cleanup_test_data):
    """Tests retrieving specific resources and all locations from a version."""
    group = kumiho.create_group(unique_name("res_proj"))
    cleanup_test_data.append(group)
    prod = group.create_product(product_name="set", product_type="env")
    cleanup_test_data.append(prod)
    v = prod.create_version()
    cleanup_test_data.append(v)
    res1 = v.create_resource("hdri", "/loc/hdri.exr")
    cleanup_test_data.append(res1)
    res2 = v.create_resource("lidar", "/loc/lidar.obj")
    cleanup_test_data.append(res2)

    # Get all resources
    resources = v.get_resources()
    assert len(resources) == 2
    
    # Get one specific resource
    lidar_res = v.get_resource("lidar")
    assert lidar_res.kref == res2.kref  
    assert lidar_res.location == "/loc/lidar.obj"

    # Get all locations
    locations = v.get_locations()
    assert set(locations) == {"/loc/hdri.exr", "/loc/lidar.obj"}

def test_resolve_kref_with_time(mock_client):
    """Tests resolving a kref at a specific point in time."""
    client, mock_stub = mock_client  # Unpack the tuple
    version_response = kumiho_pb2.VersionResponse(  # Use VersionResponse, not Version
        kref=kumiho_pb2.Kref(uri="kref://obj1?v=2"),
        product_kref=kumiho_pb2.Kref(uri="kref://obj1"),
        number=2,
        latest=True,
        tags=[],  # Add required fields
        metadata={},
        created_at=None,
        modified_at=None,
        author="test",
        deprecated=False,
        published=False,
        username="test",
    )
    mock_stub.ResolveKref.return_value = version_response
    time_str = "202510131200"
    resolved = client.resolve_kref("kref://obj1", time=time_str)  # Use client, not mock_client
    
    mock_stub.ResolveKref.assert_called_once()
    request_arg = mock_stub.ResolveKref.call_args[0][0]
    
    assert request_arg.kref == "kref://obj1"
    assert request_arg.time == time_str
    assert not request_arg.tag
    assert resolved["number"] == 2  # Correct key: number (snake_case)

def test_resolve_kref_with_tag_and_time(mock_client):
    """Tests resolving a kref with a tag at a specific point in time."""
    client, mock_stub = mock_client  # Unpack the tuple
    version_response = kumiho_pb2.VersionResponse(  # Use VersionResponse, not Version
        kref=kumiho_pb2.Kref(uri="kref://obj1?v=1"),
        product_kref=kumiho_pb2.Kref(uri="kref://obj1"),
        number=1,
        latest=True,
        tags=[],  # Add required fields
        metadata={},
        created_at=None,
        modified_at=None,
        author="test",
        deprecated=False,
        published=False,
        username="test",
    )
    mock_stub.ResolveKref.return_value = version_response
    time_str = "202510101000"
    tag_name = "published"
    
    resolved = client.resolve_kref("kref://obj1", tag=tag_name, time=time_str) 
    
    mock_stub.ResolveKref.assert_called_once()
    request_arg = mock_stub.ResolveKref.call_args[0][0]
    
    assert request_arg.kref == "kref://obj1"
    assert request_arg.tag == tag_name
    assert request_arg.time == time_str
    assert resolved["number"] == 1

def test_resolve_kref_invalid_time_format(mock_client):
    """Tests that an invalid time format raises a ValueError."""
    client, mock_stub = mock_client  # Unpack the tuple
    with pytest.raises(ValueError, match="time must be in YYYYMMDDHHMM format"):
        client.resolve_kref("kref://some_id", time="2025-10-13 12:00:00")
