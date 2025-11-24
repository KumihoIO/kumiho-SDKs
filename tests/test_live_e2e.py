import uuid
from datetime import datetime

import pytest
import kumiho
from kumiho import Client


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_firebase_supabase_neo4j_roundtrip(live_client: Client, cleanup_test_data):
    """Full-stack smoke test that exercises Firebase auth, Supabase tenancy, and Neo4j writes."""
    project_name = _unique("e2e_project")
    product_name = _unique("asset")
    location = f"s3://kumiho-ci/{uuid.uuid4().hex}.bin"
    version_metadata = {
        "suite": "python-live-e2e",
        "timestamp": datetime.utcnow().isoformat(),
    }

    group = kumiho.create_group(project_name)
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
