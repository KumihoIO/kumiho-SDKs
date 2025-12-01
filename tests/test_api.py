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
    mock_stub = MagicMock()
    monkeypatch.setattr("kumiho.client.kumiho_pb2_grpc.KumihoServiceStub", lambda channel: mock_stub)
    
    # Use kumiho.connect to get a client instance without importing _Client directly
    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    # Configure the global default client to use our mock
    kumiho.configure_default_client(client)
    
    yield client, mock_stub
    
    # Teardown: Reset the default client
    kumiho._default_client = None

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

def test_create_group(mock_client):
    """Test the create_group method via Project."""
    client, mock_stub = mock_client
    
    # Mock Project creation first
    mock_stub.CreateProject.return_value = mock_helpers.mock_project_response(
        project_id="p1", name="projectA"
    )
    project = kumiho.create_project("projectA")

    # Mock Group creation
    mock_stub.CreateGroup.return_value = mock_helpers.mock_group_response(path="/projectA/seqA")
    
    # Create group via project
    group = project.create_group(name="seqA")
    
    # Verify calls
    mock_stub.CreateGroup.assert_called_once_with(
        mock_helpers.mock_create_group_request(parent_path="/projectA", group_name="seqA")
    )
    assert group.path == "/projectA/seqA"

def test_get_product_from_version_kref(mock_client):
    """Test get_product_from_version method."""
    client, mock_stub = mock_client
    
    # Mock the version response
    version_response = mock_helpers.mock_version_response(
        kref_uri="kref://projectA/modelA.asset?v=1",
        product_kref_uri="kref://projectA/modelA.asset",
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
    product_response = mock_helpers.mock_product_response(
        kref_uri="kref://projectA/modelA.asset",
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
    version = kumiho.get_version("kref://projectA/modelA.asset?v=1")
    product = version.get_product()
    
    # Verify calls
    mock_stub.GetVersion.assert_called_once_with(
        mock_helpers.mock_kref_request(uri="kref://projectA/modelA.asset?v=1")
    )
    mock_stub.GetProduct.assert_called_once_with(
        mock_helpers.mock_get_product_request(
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
    product_response = mock_helpers.mock_product_response(
        kref_uri="kref://projectA/modelA.asset",
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
    product = kumiho.get_product("kref://projectA/modelA.asset")
    
    # Verify calls
    mock_stub.GetProduct.assert_called_once_with(
        mock_helpers.mock_get_product_request(
            parent_path="/projectA",
            product_name="modelA", 
            product_type="asset"
        )
    )
    
    assert product.product_name == "modelA"
    assert product.product_type == "asset"

def test_get_group_from_path(mock_client):
    """Test get_group via Project."""
    client, mock_stub = mock_client
    
    # Mock Project creation/retrieval (simulated)
    mock_stub.CreateProject.return_value = mock_helpers.mock_project_response(
        project_id="p1", name="projectA"
    )
    project = kumiho.create_project("projectA")
    
    path = "seqA"
    full_path = "/projectA/seqA"
    mock_stub.GetGroup.return_value = mock_helpers.mock_group_response(path=full_path)
    
    # Get group via project
    group = project.get_group(path)
    
    mock_stub.GetGroup.assert_called_once_with(
        mock_helpers.mock_get_group_request(path_or_kref=full_path)
    )
    assert group.path == full_path

def test_product_search_with_context(mock_client):
    """Test product_search with a context filter."""
    client, mock_stub = mock_client
    product_kref_uri = "kref://projectA/seqA/001/kumiho.model"
    response = mock_helpers.mock_get_products_response(
        products=[mock_helpers.mock_product_response(
            kref_uri=product_kref_uri,
            name="kumiho.model",
            product_name="kumiho",
            product_type="model"
        )]
    )
    mock_stub.ProductSearch.return_value = response
    results = kumiho.product_search(context_filter="projectA/seqA", ptype_filter="model")
    mock_stub.ProductSearch.assert_called_once_with(
        mock_helpers.mock_product_search_request(
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
    
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
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

    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
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

    found_resources = kumiho.get_resources_by_location(shared_location)

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
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
    cleanup_test_data.append(group)
    
    model_product = group.create_product(product_name="character_model", product_type="model")
    cleanup_test_data.append(model_product)
    texture_product = group.create_product(product_name="character_textures", product_type="texture")
    cleanup_test_data.append(texture_product)

    model_v1 = model_product.create_version()
    cleanup_test_data.append(model_v1)
    texture_v1 = texture_product.create_version()
    cleanup_test_data.append(texture_v1)

    link = texture_v1.create_link(
        target_version=model_v1,
        link_type=kumiho.LinkType.DEPENDS_ON
    )
    cleanup_test_data.append(link)

    assert link.source_kref == texture_v1.kref  
    assert link.target_kref == model_v1.kref  
    
    # Retrieve and verify
    source_links = texture_v1.get_links()
    assert len(source_links) >= 1
    retrieved_link = source_links[0]
    assert retrieved_link.target_kref == model_v1.kref  
    assert retrieved_link.link_type == kumiho.LinkType.DEPENDS_ON

def test_peek_next_version(live_client, cleanup_test_data):
    """
    Tests that peeking at the next version number works correctly.
    """
    project_name = unique_name("peek_test_project")
    asset_name = unique_name("peek_test_asset")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
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
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
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
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
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

def test_metadata_update_workflow(live_client, cleanup_test_data):
    """Tests setting and updating metadata on all object types."""
    project = kumiho.create_project(unique_name("meta_proj"))
    cleanup_test_data.append(project)
    group = project.create_group(name=project.name, parent_path="/")
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

def test_group_deletion_logic(live_client, cleanup_test_data):
    """Tests safe and forced deletion of groups."""
    # Setup
    project = kumiho.create_project(unique_name("del_proj"))
    cleanup_test_data.append(project)
    proj = project.create_group(name=project.name, parent_path="/")
    cleanup_test_data.append(proj)
    prod = proj.create_product(product_name="asset", product_type="model")
    cleanup_test_data.append(prod)
    empty_group = proj.create_group(name="empty_group")
    cleanup_test_data.append(empty_group)

    # 1. Succeed in deleting empty group without force
    empty_group.delete()
    cleanup_test_data.remove(empty_group)

    # 2. Fail to delete non-empty group without force
    with pytest.raises(grpc.RpcError) as e:
        proj.delete()
    if e.value.code() == grpc.StatusCode.UNAVAILABLE:
        pytest.skip("Control-plane JWKS unavailable in test environment")
    assert e.value.code() == grpc.StatusCode.PERMISSION_DENIED

    # 3. Succeed in deleting non-empty group with admin force
    proj.delete(force=True)
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(proj)
    with pytest.raises(grpc.RpcError) as e:
        # Use project.get_group instead of live_client.get_group
        project.get_group(proj.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND
    with pytest.raises(grpc.RpcError) as e:
        project.get_group(empty_group.path)
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_product_deprecation_and_deletion(live_client, cleanup_test_data):
    """Tests soft delete (deprecation) and hard delete for products."""
    project = kumiho.create_project(unique_name("dep_proj"))
    cleanup_test_data.append(project)
    group = project.create_group(name=project.name, parent_path="/")
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
    prod_new.delete(force=True)
    # Remove from cleanup since it's already deleted
    cleanup_test_data.remove(prod_new)
    with pytest.raises(grpc.RpcError) as e:
        group.get_product(product_name="char", product_type="rig")
    assert e.value.code() == grpc.StatusCode.NOT_FOUND

def test_version_tagging_workflow(live_client, cleanup_test_data):
    """Tests the full lifecycle of tagging a version."""
    project = kumiho.create_project(unique_name("tag_proj"))
    cleanup_test_data.append(project)
    group = project.create_group(name=project.name, parent_path="/")
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

def test_published_version_immutability(live_client, cleanup_test_data):
    """Tests that a 'published' version and its resources are immutable."""
    project = kumiho.create_project(unique_name("immutable_proj"))
    cleanup_test_data.append(project)
    group = project.create_group(name=project.name, parent_path="/")
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
    def expect_error(fn, expected_substr: str):
        try:
            fn()
            pytest.fail("Expected immutable/published error")
        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("Control-plane JWKS unavailable in test environment")
            assert expected_substr.lower() in (exc.details() or "").lower()

    expect_error(lambda: v1.set_metadata({"new_key": "new_val"}), "immutable")
    expect_error(lambda: res.set_metadata({"new_key": "new_val"}), "immutable")
    expect_error(lambda: v1.untag(PUBLISHED_TAG), "immutable")
    expect_error(lambda: v1.delete(), "immutable")
    expect_error(lambda: res.delete(), "immutable")
    expect_error(lambda: v1.create_resource("mask", "/path/to/mask.png"), "published")

def test_get_resource_and_locations(live_client, cleanup_test_data):
    """Tests retrieving specific resources and all locations from a version."""
    project = kumiho.create_project(unique_name("res_proj"))
    cleanup_test_data.append(project)
    group = project.create_group(name=project.name, parent_path="/")
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
    version_response = mock_helpers.mock_version_response(
        kref_uri="kref://obj1?v=2",
        product_kref_uri="kref://obj1",
        number=2,
        latest=True,
        tags=[],
        metadata={},
        author="test",
        username="test",
        deprecated=False,
        published=False
    )
    mock_stub.ResolveKref.return_value = version_response
    time_str = "202510131200"
    # Use kumiho.get_version with time parameter
    resolved = kumiho.get_version(f"kref://obj1?time={time_str}")
    
    mock_stub.ResolveKref.assert_called_once()
    request_arg = mock_stub.ResolveKref.call_args[0][0]
    
    assert request_arg.kref == "kref://obj1"
    assert request_arg.time == time_str
    assert not request_arg.tag
    assert resolved.number == 2

def test_resolve_kref_with_tag_and_time(mock_client):
    """Tests resolving a kref with a tag at a specific point in time."""
    client, mock_stub = mock_client  # Unpack the tuple
    version_response = mock_helpers.mock_version_response(
        kref_uri="kref://obj1?v=1",
        product_kref_uri="kref://obj1",
        number=1,
        latest=True,
        tags=[],
        metadata={},
        author="test",
        username="test",
        deprecated=False,
        published=False
    )
    mock_stub.ResolveKref.return_value = version_response
    time_str = "202510101000"
    tag_name = "published"
    
    resolved = kumiho.get_version(f"kref://obj1?tag={tag_name}&time={time_str}") 
    
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
        kumiho.get_version("kref://some_id?time=2025-10-13 12:00:00")

def test_janus_parity_features(live_client, cleanup_test_data):
    """Tests features added for Janus parity: deprecation, default resource, traversal, links."""
    project_name = unique_name("janus_proj")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
    cleanup_test_data.append(group)
    product = group.create_product(product_name="asset", product_type="model")
    cleanup_test_data.append(product)
    version = product.create_version()
    cleanup_test_data.append(version)
    resource = version.create_resource("main", "/path/to/file")
    cleanup_test_data.append(resource)

    # 1. Deprecation
    # Product
    assert product.deprecated is False
    product.set_deprecated(True)
    assert product.deprecated is True
    # Reload to verify persistence
    prod_reloaded = group.get_product("asset", "model")
    assert prod_reloaded.deprecated is True
    product.set_deprecated(False)
    assert product.deprecated is False

    # Version
    assert version.deprecated is False
    version.set_deprecated(True)
    assert version.deprecated is True
    version.set_deprecated(False)
    assert version.deprecated is False

    # Resource
    assert resource.deprecated is False
    resource.set_deprecated(True)
    assert resource.deprecated is True
    resource.set_deprecated(False)
    assert resource.deprecated is False

    # 2. Default Resource
    assert version.default_resource is None
    resource.set_default()
    # Reload version to check default resource
    v_reloaded = product.get_version(version.number)
    assert v_reloaded.default_resource == resource.name

    # 3. Traversal
    # From Resource
    assert resource.get_version().kref.uri == version.kref.uri
    assert resource.get_product().kref.uri == product.kref.uri
    assert resource.get_group().path == group.path
    assert resource.get_project().name == project.name

    # From Version
    assert version.get_product().kref.uri == product.kref.uri
    assert version.get_group().path == group.path
    assert version.get_project().name == project.name

    # From Product
    assert product.get_group().path == group.path
    assert product.get_project().name == project.name

    # From Group
    assert group.get_project().name == project.name

    # 4. Link Types
    # LinkType is now exposed at package level
    v2 = product.create_version()
    cleanup_test_data.append(v2)
    
    # Use new convenience method
    link = version.create_link(
        target_version=v2,
        link_type=kumiho.LinkType.CREATED_FROM
    )
    cleanup_test_data.append(link)
    assert link.link_type == kumiho.LinkType.CREATED_FROM
    
    # Verify get_links
    links = version.get_links()
    assert len(links) >= 1
    assert links[0].link_type == kumiho.LinkType.CREATED_FROM
    
    # Verify delete_link
    version.delete_link(v2, kumiho.LinkType.CREATED_FROM)
    links_after = version.get_links()
    # Note: get_links might return empty list or filtered list. 
    # Since we just deleted the only link we created, it should be empty or not contain that specific link.
    # But let's be safe and check if the specific link is gone.
    assert not any(l.target_kref.uri == v2.kref.uri and l.link_type == kumiho.LinkType.CREATED_FROM for l in links_after)

    # 5. Link Direction
    # Create a link: version -> v2 (CREATED_FROM)
    version.create_link(v2, kumiho.LinkType.CREATED_FROM)
    
    # Test Outgoing (Default)
    outgoing = version.get_links(direction=kumiho.OUTGOING)
    assert len(outgoing) > 0
    assert outgoing[0].source_kref.uri == version.kref.uri
    assert outgoing[0].target_kref.uri == v2.kref.uri
    
    # Test Incoming (from v2's perspective)
    incoming = v2.get_links(direction=kumiho.INCOMING)
    assert len(incoming) > 0
    assert incoming[0].source_kref.uri == version.kref.uri
    assert incoming[0].target_kref.uri == v2.kref.uri
    
    # Test Both
    both_v1 = version.get_links(direction=kumiho.BOTH)
    assert len(both_v1) > 0
    both_v2 = v2.get_links(direction=kumiho.BOTH)
    assert len(both_v2) > 0
