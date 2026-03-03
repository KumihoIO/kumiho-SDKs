import pytest
import uuid
import os
from kumiho import KumihoError
import kumiho

# Use the existing client fixture if available, or create a new one
@pytest.fixture
def client():
    # Assuming env vars are set or we can use default
    # We need a client authenticated as a tenant member (admin/owner)
    return kumiho.get_client()

def test_safeguards_lifecycle(client):
    """
    Verifies that we can create a draft, publish it, and retrieve it.
    Note: Full anonymous access verification requires a valid Firebase token
    for a user with no tenant roles, which is hard to simulate here without
    Control Plane modification.
    """
    project_name = f"safeguard_test_{uuid.uuid4().hex[:8]}"
    
    # 1. Create a Project
    try:
        client.create_project(project_name, "Test Project for Safeguards")
    except KumihoError as e:
        if "already exists" not in str(e):
            raise

    # Verify root space exists
    print(f"Verifying root space: /{project_name}")
    try:
        client.get_space(f"/{project_name}")
    except Exception as e:
        print(f"Root space not found, attempting to create: {e}")
        # Try to create it explicitly if missing (shouldn't be needed usually)
        try:
            client.create_space("/", project_name)
        except Exception as create_e:
             print(f"Failed to create root space: {create_e}")
             # If it fails, maybe it exists now?
             pass

    # 2. Create a Draft Post (Item)
    post_name = f"post_{uuid.uuid4().hex[:8]}"
    print(f"Creating draft post: {post_name}")
    # 2. Create a Draft Post (Item)
    post_name = f"post_{uuid.uuid4().hex[:8]}"
    print(f"Creating draft post: {post_name}")
    # Create item
    item = client.create_item(
        f"/{project_name}",
        post_name,
        "post"
    )
    # Create initial revision (draft)
    revision = client.create_revision(
        item.kref,
        metadata={"title": "Draft Post"}
    )
    assert revision.kref is not None
    
    # 3. Verify we can see it (as Admin)
    print("Verifying draft visibility for Admin...")
    fetched_revision = client.get_revision(revision.kref.uri)
    assert fetched_revision.kref.uri == revision.kref.uri
    
    # 4. Publish the Post
    print("Publishing post...")
    client.tag_revision(revision.kref, "published")
    
    # 5. Verify we can still see it
    print("Verifying published post visibility for Admin...")
    published_revision = client.get_revision(revision.kref.uri)
    assert published_revision.kref.uri == revision.kref.uri
    assert client.has_tag(revision.kref, "published")
    
    # 6. (Optional) Negative Test: Invalid Token
    # We can't easily switch the client's token to an "anonymous" one that is valid
    # but has no roles. But we can verify that a bad token is rejected.
    # TODO: Implement true anonymous verification when test infrastructure allows.

if __name__ == "__main__":
    # Manual run setup
    c = kumiho.get_client()
    test_safeguards_lifecycle(c)
