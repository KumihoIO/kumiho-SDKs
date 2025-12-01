
import pytest
import uuid
import kumiho
from kumiho.kref import Kref

@pytest.fixture
def client():
    # Assumes local server is running or configured via env vars
    return kumiho.get_client()

@pytest.fixture
def unique_project(client):
    name = f"TestProject_{uuid.uuid4().hex[:8]}"
    project = client.create_project(name, "Test Project for ResolveLocation")
    yield project
    # Cleanup
    try:
        client.delete_project(project.id, force=True)
    except Exception:
        pass

def test_resolve_location_flow(client, unique_project):
    # Setup: Create Group, Product, Version, Resource
    group_name = "test_group"
    group = client.create_group(f"/{unique_project.name}", group_name)
    
    product_name = "test_product"
    product_type = "model"
    product = client.create_product(group.path, product_name, product_type)
    
    # Create Version 1
    v1 = client.create_version(product.kref, metadata={"v": "1"})
    
    print(f"DEBUG: Product Kref: {product.kref.uri}")
    print(f"DEBUG: V1 Kref: {v1.kref.uri}")
    
    # Create Resource for V1
    r1_name = "main.obj"
    r1_loc = "s3://bucket/v1/main.obj"
    r1 = client.create_resource(v1.kref, r1_name, r1_loc)
    
    # Set default resource for V1
    v1.set_default_resource(r1_name)
    
    # Create Version 2
    v2 = client.create_version(product.kref, metadata={"v": "2"})
    
    # Create Resource for V2
    r2_name = "main.obj"
    r2_loc = "s3://bucket/v2/main.obj"
    r2 = client.create_resource(v2.kref, r2_name, r2_loc)
    
    # Set default resource for V2
    v2.set_default_resource(r2_name)
    
    # Tag V1 as 'stable'
    v1.tag("stable")
    
    # Test 1: Resolve Product Kref (should get latest version -> V2 default resource)
    # Note: create_version automatically tags as 'latest'
    resolved_loc = client.resolve(product.kref.uri)
    assert resolved_loc == r2_loc
    
    # Test 2: Resolve Version Kref (V1)
    resolved_loc_v1 = client.resolve(v1.kref.uri)
    assert resolved_loc_v1 == r1_loc
    
    # Test 3: Resolve Resource Kref (V1 resource)
    resolved_loc_r1 = client.resolve(r1.kref.uri)
    assert resolved_loc_r1 == r1_loc
    
    # Test 4: Resolve with Tag (stable -> V1)
    # Using query param in Kref
    tagged_kref = f"{product.kref.uri}?t=stable"
    resolved_loc_stable = client.resolve(tagged_kref)
    assert resolved_loc_stable == r1_loc
    
    # Test 5: Resolve with Tag via explicit arg (if client.resolve supported it, but it takes string)
    # The client.resolve method parses the string.
    
    # Test 6: Resolve non-existent tag
    bad_tag_kref = f"{product.kref.uri}?t=nonexistent"
    resolved_loc_bad = client.resolve(bad_tag_kref)
    assert resolved_loc_bad is None

def test_get_version_with_resolve(client, unique_project):
    # Setup similar to above
    group = client.create_group(f"/{unique_project.name}", "grp")
    product = client.create_product(group.path, "prod", "type")
    v1 = client.create_version(product.kref)
    v1.tag("release")
    
    # Test get_version with tag in URI
    kref_with_tag = f"{product.kref.uri}?t=release"
    v_resolved = client.get_version(kref_with_tag)
    
    assert v_resolved.kref.uri == v1.kref.uri
    assert v_resolved.number == v1.number
