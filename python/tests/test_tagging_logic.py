import pytest
import kumiho
import uuid
# from kumiho import Client

def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def test_latest_tag_logic(live_client, cleanup_test_data):
    """
    Verifies that 'latest' tag is automatically managed:
    1. First revision gets 'latest' tag.
    2. Second revision gets 'latest' tag, and first revision loses it.
    """
    project_name = unique_name("latest_tag_test")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="asset", kind="model")
    cleanup_test_data.append(item)

    # 1. Create first revision
    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    
    # Verify v1 has 'latest' tag
    assert v1.has_tag("latest") is True
    # Verify v1 is returned as latest
    latest_v = item.get_latest_revision()
    assert latest_v.number == v1.number

    # 2. Create second revision
    v2 = item.create_revision()
    cleanup_test_data.append(v2)

    # Verify v2 has 'latest' tag
    assert v2.has_tag("latest") is True
    
    # Verify v1 NO LONGER has 'latest' tag
    # We need to re-fetch v1 to check its current tags
    v1_refreshed = item.get_revision(v1.number)
    assert v1_refreshed.has_tag("latest") is False

    # Verify v2 is returned as latest
    latest_v = item.get_latest_revision()
    assert latest_v.number == v2.number

def test_manual_tag_uniqueness(live_client, cleanup_test_data):
    """
    Verifies that manual tags are unique per item:
    1. Tag v1 with 'stable'.
    2. Tag v2 with 'stable'.
    3. Verify v1 lost 'stable' and v2 has it.
    """
    project_name = unique_name("unique_tag_test")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="asset", kind="model")
    cleanup_test_data.append(item)

    v1 = item.create_revision()
    cleanup_test_data.append(v1)
    v2 = item.create_revision()
    cleanup_test_data.append(v2)

    # 1. Tag v1 with 'stable'
    v1.tag("stable")
    assert v1.has_tag("stable") is True

    # 2. Tag v2 with 'stable'
    v2.tag("stable")
    assert v2.has_tag("stable") is True

    # 3. Verify v1 lost 'stable'
    v1_refreshed = item.get_revision(v1.number)
    assert v1_refreshed.has_tag("stable") is False

def test_published_tag_logic(live_client, cleanup_test_data):
    """
    Verifies that 'published' tag updates the published field.
    """
    project_name = unique_name("published_tag_test")
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    item = space.create_item(item_name="asset", kind="model")
    cleanup_test_data.append(item)

    v1 = item.create_revision()
    cleanup_test_data.append(v1)

    assert v1.published is False
    
    v1.tag("published")
    
    v1_refreshed = item.get_revision(v1.number)
    assert v1_refreshed.published is True
    assert v1_refreshed.has_tag("published") is True
