import uuid
from datetime import datetime

import pytest
import grpc
import kumiho


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_firebase_supabase_neo4j_roundtrip(live_client, cleanup_test_data):
    """Full-stack smoke test that exercises Firebase auth, Supabase tenancy, and Neo4j writes."""
    project_name = _unique("e2e_project")
    product_name = _unique("asset")
    location = f"s3://kumiho-ci/{uuid.uuid4().hex}.bin"
    version_metadata = {
        "suite": "python-live-e2e",
        "timestamp": datetime.utcnow().isoformat(),
    }

    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    group = project.create_group(name=project_name, parent_path="/")
    cleanup_test_data.append(group)
    assert group.path == f"/{project_name}"

    product = group.create_product(product_name=product_name, product_type="model")
    cleanup_test_data.append(product)
    assert product.product_name == product_name

    version = product.create_version(metadata=version_metadata)
    cleanup_test_data.append(version)
    assert version.metadata.get("suite") == "python-live-e2e"

    resource = version.create_resource("payload", location)
    cleanup_test_data.append(resource)
    assert resource.location == location

    resolved_location = kumiho.resolve(resource.kref.uri)
    assert resolved_location == location

    latest_version = product.get_latest_version()
    assert latest_version is not None
    assert latest_version.kref == version.kref

    matches = live_client.get_resources_by_location(location)
    assert any(match.kref == resource.kref for match in matches)

    assert product.peek_next_version() == version.number + 1


def test_create_group_without_project_fails(live_client):
    """Test that creating a root group without a corresponding project fails."""
    orphan_group_name = _unique("orphan_group")
    
    # Attempt to create a group without creating a project first
    # This should fail with an internal error or similar because the project doesn't exist
    with pytest.raises(grpc.RpcError) as e:
        live_client.create_group(parent_path="/", group_name=orphan_group_name)
    
    # The server returns Status::internal("Failed to create or retrieve group")
    # or potentially a more specific error if I updated the server to return one.
    # Based on current implementation, it returns internal error.
    assert e.value.code() == grpc.StatusCode.INTERNAL
    assert "Failed to create or retrieve group" in e.value.details()


def test_node_limit_enforcement(live_client):
    """Test that we can query tenant usage and that it returns valid numbers."""
    # Verify GetTenantUsage works
    usage = live_client.get_tenant_usage()
    assert "node_count" in usage
    assert "node_limit" in usage
    assert "tenant_id" in usage
    
    initial_count = int(usage["node_count"])
    limit = int(usage["node_limit"])
    
    print(f"Initial node count: {initial_count}, Limit: {limit}")
    
    # If limit is -1, it means no limit, so we can't test enforcement easily.
    # If limit is positive, we could try to hit it, but that might be slow or disruptive.
    # For now, we just verify the RPC returns valid data and the count increases when we create something.
    
    project_name = _unique("limit_test")
    project = live_client.create_project(project_name)
    
    new_usage = live_client.get_tenant_usage()
    new_count = int(new_usage["node_count"])
    
    # Count should have increased by at least 1 (the project)
    # It might be more if side-effects create other nodes, but at least 1.
    assert new_count > initial_count
