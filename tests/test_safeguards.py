import pytest
import uuid
import os
from kumiho import Client, KumihoError

# Use the existing client fixture if available, or create a new one
@pytest.fixture
def client():
    # Assuming env vars are set or we can use default
    # We need a client authenticated as a tenant member (admin/owner)
    return Client()

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

    # Verify root group exists
    print(f"Verifying root group: /{project_name}")
    try:
        client.get_group(f"/{project_name}")
    except Exception as e:
        print(f"Root group not found, attempting to create: {e}")
        # Try to create it explicitly if missing (shouldn't be needed usually)
        try:
            client.create_group("/", project_name)
        except Exception as create_e:
             print(f"Failed to create root group: {create_e}")
             # If it fails, maybe it exists now?
             pass

    # 2. Create a Draft Post (Product)
    post_name = f"post_{uuid.uuid4().hex[:8]}"
    print(f"Creating draft post: {post_name}")
    # 2. Create a Draft Post (Product)
    post_name = f"post_{uuid.uuid4().hex[:8]}"
    print(f"Creating draft post: {post_name}")
    # Create product
    product = client.create_product(
        f"/{project_name}",
        post_name,
        "post"
    )
    # Create initial version (draft)
    version = client.create_version(
        product.kref,
        metadata={"title": "Draft Post"}
    )
    assert version.kref is not None
    
    # 3. Verify we can see it (as Admin)
    print("Verifying draft visibility for Admin...")
    fetched_version = client.get_version(version.kref.uri)
    assert fetched_version.kref.uri == version.kref.uri
    
    # 4. Publish the Post
    print("Publishing post...")
    client.tag_version(version.kref, "published")
    
    # 5. Verify we can still see it
    print("Verifying published post visibility for Admin...")
    published_version = client.get_version(version.kref.uri)
    assert published_version.kref.uri == version.kref.uri
    assert client.has_tag(version.kref, "published")
    
    # 6. (Optional) Negative Test: Invalid Token
    # We can't easily switch the client's token to an "anonymous" one that is valid
    # but has no roles. But we can verify that a bad token is rejected.
    # TODO: Implement true anonymous verification when test infrastructure allows.

if __name__ == "__main__":
    # Manual run setup
    c = Client()
    test_safeguards_lifecycle(c)
