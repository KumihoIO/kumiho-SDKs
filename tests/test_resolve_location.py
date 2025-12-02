
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
    # Setup: Create Space, Item, Revision, Artifact
    space_name = "test_space"
    space = client.create_space(f"/{unique_project.name}", space_name)
    
    item_name = "test_item"
    kind = "model"
    item = client.create_item(space.path, item_name, kind)
    
    # Create Revision 1
    v1 = client.create_revision(item.kref, metadata={"v": "1"})
    
    print(f"DEBUG: Item Kref: {item.kref.uri}")
    print(f"DEBUG: V1 Kref: {v1.kref.uri}")
    
    # Create Artifact for V1
    r1_name = "main.obj"
    r1_loc = "s3://bucket/v1/main.obj"
    r1 = client.create_artifact(v1.kref, r1_name, r1_loc)
    
    # Set default artifact for V1
    v1.set_default_artifact(r1_name)
    
    # Create Revision 2
    v2 = client.create_revision(item.kref, metadata={"v": "2"})
    
    # Create Artifact for V2
    r2_name = "main.obj"
    r2_loc = "s3://bucket/v2/main.obj"
    r2 = client.create_artifact(v2.kref, r2_name, r2_loc)
    
    # Set default artifact for V2
    v2.set_default_artifact(r2_name)
    
    # Tag V1 as 'stable'
    v1.tag("stable")
    
    # Test 1: Resolve Item Kref (should get latest revision -> V2 default artifact)
    # Note: create_revision automatically tags as 'latest'
    resolved_loc = client.resolve(item.kref.uri)
    assert resolved_loc == r2_loc
    
    # Test 2: Resolve Revision Kref (V1)
    resolved_loc_v1 = client.resolve(v1.kref.uri)
    assert resolved_loc_v1 == r1_loc
    
    # Test 3: Resolve Artifact Kref (V1 artifact)
    resolved_loc_r1 = client.resolve(r1.kref.uri)
    assert resolved_loc_r1 == r1_loc
    
    # Test 4: Resolve with Tag (stable -> V1)
    # Using query param in Kref
    tagged_kref = f"{item.kref.uri}?t=stable"
    resolved_loc_stable = client.resolve(tagged_kref)
    assert resolved_loc_stable == r1_loc
    
    # Test 5: Resolve with Tag via explicit arg (if client.resolve supported it, but it takes string)
    # The client.resolve method parses the string.
    
    # Test 6: Resolve non-existent tag
    bad_tag_kref = f"{item.kref.uri}?t=nonexistent"
    resolved_loc_bad = client.resolve(bad_tag_kref)
    assert resolved_loc_bad is None

def test_get_revision_with_resolve(client, unique_project):
    # Setup similar to above
    space = client.create_space(f"/{unique_project.name}", "grp")
    item = client.create_item(space.path, "prod", "type")
    v1 = client.create_revision(item.kref)
    v1.tag("release")
    
    # Test get_revision with tag in URI
    kref_with_tag = f"{item.kref.uri}?t=release"
    v_resolved = client.get_revision(kref_with_tag)
    
    assert v_resolved.kref.uri == v1.kref.uri
    assert v_resolved.number == v1.number
