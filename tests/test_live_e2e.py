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
    item_name = _unique("asset")
    location = f"s3://kumiho-ci/{uuid.uuid4().hex}.bin"
    revision_metadata = {
        "suite": "python-live-e2e",
        "timestamp": datetime.utcnow().isoformat(),
    }

    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    assert space.path == f"/{project_name}"

    item = space.create_item(item_name=item_name, kind="model")
    cleanup_test_data.append(item)
    assert item.item_name == item_name

    revision = item.create_revision(metadata=revision_metadata)
    cleanup_test_data.append(revision)
    assert revision.metadata.get("suite") == "python-live-e2e"

    artifact = revision.create_artifact("payload", location)
    cleanup_test_data.append(artifact)
    assert artifact.location == location

    resolved_location = kumiho.resolve(artifact.kref.uri)
    assert resolved_location == location

    latest_revision = item.get_latest_revision()
    assert latest_revision is not None
    assert latest_revision.kref == revision.kref

    matches = live_client.get_artifacts_by_location(location)
    assert any(match.kref == artifact.kref for match in matches)

    assert item.peek_next_revision() == revision.number + 1


def test_create_space_without_project_fails(live_client):
    """Test that creating a root space without a corresponding project fails."""
    orphan_space_name = _unique("orphan_space")
    
    # Attempt to create a space without creating a project first
    # This should fail because the project doesn't exist
    with pytest.raises(grpc.RpcError) as e:
        live_client.create_space(parent_path="/", space_name=orphan_space_name)
    
    # The server returns FAILED_PRECONDITION with a helpful error message
    assert e.value.code() == grpc.StatusCode.FAILED_PRECONDITION
    assert "No project found" in e.value.details()


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
