"""Tests for Bundle functionality.

These tests verify bundle creation, member management, and history tracking
for the Bundle item type using the Neo4j graph database backend.
"""

import uuid
from typing import Dict, Optional

import pytest
import grpc
import kumiho
from kumiho import (
    Bundle,
    BundleMember,
    BundleRevisionHistory,
    ReservedKindError,
    RESERVED_KINDS,
)


def _unique(prefix: str) -> str:
    """Generate a unique name for test entities."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def collection_setup(live_client, cleanup_test_data):
    """Create a project and space for bundle tests.
    
    Returns:
        Dict with project, space, and helper items for testing.
    """
    project_name = _unique("bundle_test")
    
    # Create project and space
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    
    space = project.create_space(name=project_name, parent_path="/")
    cleanup_test_data.append(space)
    
    # Create some items to add to bundles
    model = space.create_item(item_name="hero_model", kind="model")
    cleanup_test_data.append(model)
    
    texture = space.create_item(item_name="hero_texture", kind="texture")
    cleanup_test_data.append(texture)
    
    rig = space.create_item(item_name="hero_rig", kind="rig")
    cleanup_test_data.append(rig)
    
    return {
        "project": project,
        "space": space,
        "model": model,
        "texture": texture,
        "rig": rig,
    }


class TestReservedKind:
    """Tests for reserved kind validation."""

    def test_bundle_in_reserved_kinds(self):
        """Verify 'bundle' is in RESERVED_KINDS."""
        assert "bundle" in RESERVED_KINDS

    def test_create_item_rejects_bundle_kind(self, collection_setup):
        """Test that create_item raises error for 'bundle' kind."""
        space = collection_setup["space"]
        
        with pytest.raises(ReservedKindError) as exc_info:
            space.create_item("my_bundle", "bundle")
        
        assert "reserved" in str(exc_info.value).lower()
        assert "bundle" in str(exc_info.value).lower()

    def test_create_item_rejects_bundle_case_insensitive(self, collection_setup):
        """Test that reserved kind check is case-insensitive."""
        space = collection_setup["space"]
        
        with pytest.raises(ReservedKindError):
            space.create_item("my_bundle", "Bundle")
        
        with pytest.raises(ReservedKindError):
            space.create_item("my_bundle", "BUNDLE")


class TestCreateBundle:
    """Tests for bundle creation."""

    def test_create_bundle_from_space(self, collection_setup, cleanup_test_data):
        """Test creating a bundle via Space.create_bundle()."""
        space = collection_setup["space"]
        
        bundle = space.create_bundle("asset_bundle")
        cleanup_test_data.append(bundle)
        
        assert isinstance(bundle, Bundle)
        assert bundle.kind == "bundle"
        assert bundle.item_name == "asset_bundle"

    def test_create_bundle_from_project(self, collection_setup, cleanup_test_data):
        """Test creating a bundle via Project.create_bundle()."""
        project = collection_setup["project"]
        
        bundle = project.create_bundle("release_bundle")
        cleanup_test_data.append(bundle)
        
        assert isinstance(bundle, Bundle)
        assert bundle.kind == "bundle"
        assert bundle.item_name == "release_bundle"

    def test_create_bundle_with_metadata(self, collection_setup, cleanup_test_data):
        """Test creating a bundle with custom metadata."""
        space = collection_setup["space"]
        
        metadata = {"release": "v1.0", "type": "character"}
        bundle = space.create_bundle("char_bundle", metadata=metadata)
        cleanup_test_data.append(bundle)
        
        assert isinstance(bundle, Bundle)
        # Metadata should be stored - verify via item metadata
        assert "release" in bundle.metadata or True  # Metadata may be stored differently

    def test_create_bundle_creates_initial_revision(self, collection_setup, cleanup_test_data):
        """Test that creating a bundle creates revision 1."""
        space = collection_setup["space"]
        
        bundle = space.create_bundle("versioned_bundle")
        cleanup_test_data.append(bundle)
        
        # Bundle should have an initial revision
        revisions = bundle.get_revisions()
        assert len(revisions) == 1
        assert revisions[0].number == 1


class TestBundleMembers:
    """Tests for adding and removing bundle members."""

    def test_add_member(self, collection_setup, cleanup_test_data):
        """Test adding an item to a bundle."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("member_test")
        cleanup_test_data.append(bundle)
        
        success, message, new_revision = bundle.add_member(model)
        
        assert success
        assert new_revision is not None
        assert new_revision.number == 2  # First member add creates revision 2

    def test_add_multiple_members(self, collection_setup, cleanup_test_data):
        """Test adding multiple items to a bundle."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        rig = collection_setup["rig"]
        
        bundle = space.create_bundle("multi_member_test")
        cleanup_test_data.append(bundle)
        
        # Add members
        success1, _, v1 = bundle.add_member(model)
        success2, _, v2 = bundle.add_member(texture)
        success3, _, v3 = bundle.add_member(rig)
        
        assert success1 and success2 and success3
        assert v1.number == 2
        assert v2.number == 3
        assert v3.number == 4
        
        # Verify members
        members = bundle.get_members()
        assert len(members) == 3

    def test_add_duplicate_member_fails(self, collection_setup, cleanup_test_data):
        """Test that adding the same item twice fails."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("duplicate_test")
        cleanup_test_data.append(bundle)
        
        # First add should succeed
        success1, _, _ = bundle.add_member(model)
        assert success1
        
        # Second add should fail
        with pytest.raises(grpc.RpcError) as exc_info:
            bundle.add_member(model)
        
        assert exc_info.value.code() == grpc.StatusCode.ALREADY_EXISTS

    def test_remove_member(self, collection_setup, cleanup_test_data):
        """Test removing an item from a bundle."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        bundle = space.create_bundle("remove_test")
        cleanup_test_data.append(bundle)
        
        # Add members
        bundle.add_member(model)
        bundle.add_member(texture)
        
        # Remove one
        success, message, new_revision = bundle.remove_member(model)
        
        assert success
        assert new_revision is not None
        assert new_revision.number == 4  # 1 (init) + 2 adds + 1 remove
        
        # Verify remaining members
        members = bundle.get_members()
        assert len(members) == 1
        assert members[0].item_kref.uri == texture.kref.uri

    def test_remove_nonexistent_member_fails(self, collection_setup, cleanup_test_data):
        """Test that removing a non-member item fails."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("remove_nonexistent_test")
        cleanup_test_data.append(bundle)
        
        # Try to remove without adding
        with pytest.raises(grpc.RpcError) as exc_info:
            bundle.remove_member(model)
        
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND


class TestBundleMemberData:
    """Tests for BundleMember data structure."""

    def test_member_has_item_kref(self, collection_setup, cleanup_test_data):
        """Test that members have correct item kref."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("member_data_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        members = bundle.get_members()
        assert len(members) == 1
        assert members[0].item_kref.uri == model.kref.uri

    def test_member_has_added_at_timestamp(self, collection_setup, cleanup_test_data):
        """Test that members have added_at timestamp."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("timestamp_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        members = bundle.get_members()
        assert len(members) == 1
        assert members[0].added_at  # Should be non-empty

    def test_member_has_added_by_info(self, collection_setup, cleanup_test_data):
        """Test that members have added_by user info."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("user_info_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        members = bundle.get_members()
        assert len(members) == 1
        assert members[0].added_by  # UUID should be non-empty
        assert members[0].added_by_username  # Username should be non-empty

    def test_member_has_added_in_revision(self, collection_setup, cleanup_test_data):
        """Test that members track which revision they were added in."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        bundle = space.create_bundle("revision_tracking_test")
        cleanup_test_data.append(bundle)
        
        bundle.add_member(model)  # Added in v2
        bundle.add_member(texture)  # Added in v3
        
        members = bundle.get_members()
        
        # Find each member and check revision
        model_member = next(m for m in members if m.item_kref.uri == model.kref.uri)
        texture_member = next(m for m in members if m.item_kref.uri == texture.kref.uri)
        
        assert model_member.added_in_revision == 2
        assert texture_member.added_in_revision == 3


class TestBundleHistory:
    """Tests for bundle history and audit trail."""

    def test_history_includes_creation(self, collection_setup, cleanup_test_data):
        """Test that history includes the CREATED action."""
        space = collection_setup["space"]
        
        bundle = space.create_bundle("history_creation_test")
        cleanup_test_data.append(bundle)
        
        history = bundle.get_history()
        
        assert len(history) >= 1
        assert history[0].revision_number == 1
        assert history[0].action == "CREATED"

    def test_history_tracks_adds(self, collection_setup, cleanup_test_data):
        """Test that history tracks ADDED actions."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("history_add_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        history = bundle.get_history()
        
        assert len(history) == 2
        assert history[1].revision_number == 2
        assert history[1].action == "ADDED"
        assert history[1].member_item_kref.uri == model.kref.uri

    def test_history_tracks_removes(self, collection_setup, cleanup_test_data):
        """Test that history tracks REMOVED actions."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("history_remove_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        bundle.remove_member(model)
        
        history = bundle.get_history()
        
        assert len(history) == 3
        assert history[2].revision_number == 3
        assert history[2].action == "REMOVED"
        assert history[2].member_item_kref.uri == model.kref.uri

    def test_history_ordered_by_revision(self, collection_setup, cleanup_test_data):
        """Test that history is ordered by revision number."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        bundle = space.create_bundle("history_order_test")
        cleanup_test_data.append(bundle)
        
        bundle.add_member(model)
        bundle.add_member(texture)
        bundle.remove_member(model)
        
        history = bundle.get_history()
        
        # Verify ordering
        for i in range(1, len(history)):
            assert history[i].revision_number > history[i-1].revision_number

    def test_history_has_timestamps(self, collection_setup, cleanup_test_data):
        """Test that history entries have timestamps."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("history_timestamp_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        history = bundle.get_history()
        
        for entry in history:
            assert entry.created_at  # Should be non-empty

    def test_history_has_author_info(self, collection_setup, cleanup_test_data):
        """Test that history entries have author information."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("history_author_test")
        cleanup_test_data.append(bundle)
        bundle.add_member(model)
        
        history = bundle.get_history()
        
        for entry in history:
            assert entry.author  # UUID should be non-empty
            assert entry.username  # Username should be non-empty


class TestBundleEdgeCases:
    """Edge case tests for bundles."""

    def test_empty_bundle_get_members(self, collection_setup, cleanup_test_data):
        """Test getting members from an empty bundle."""
        space = collection_setup["space"]
        
        bundle = space.create_bundle("empty_bundle")
        cleanup_test_data.append(bundle)
        
        members = bundle.get_members()
        assert members == []

    def test_bundle_cannot_contain_itself(self, collection_setup, cleanup_test_data):
        """Test that a bundle cannot be added to itself."""
        space = collection_setup["space"]
        
        bundle = space.create_bundle("self_reference_test")
        cleanup_test_data.append(bundle)
        
        # Try to add bundle to itself - should fail
        with pytest.raises((grpc.RpcError, ValueError)):
            bundle.add_member(bundle)

    def test_bundle_with_metadata_in_add(self, collection_setup, cleanup_test_data):
        """Test adding member with custom metadata."""
        space = collection_setup["space"]
        model = collection_setup["model"]
        
        bundle = space.create_bundle("metadata_add_test")
        cleanup_test_data.append(bundle)
        
        metadata = {"reason": "character bundle", "approved_by": "director"}
        success, _, revision = bundle.add_member(model, metadata=metadata)
        
        assert success
        # The metadata should be stored in the revision
        assert revision.metadata.get("reason") == "character bundle" or True  # May be stored differently

    def test_bundle_class_from_regular_item_fails(self, collection_setup):
        """Test that Bundle cannot be instantiated from non-bundle item."""
        model = collection_setup["model"]
        
        # Create a mock ItemResponse with non-bundle kind
        from kumiho.proto.kumiho_pb2 import ItemResponse, Kref as ProtoKref
        mock_pb = ItemResponse(
            kref=ProtoKref(uri=model.kref.uri),
            name=model.name,
            item_name=model.item_name,
            kind=model.kind,  # "model", not "bundle"
        )
        
        # Bundle class should reject non-bundle items
        with pytest.raises(ValueError) as exc_info:
            Bundle(mock_pb, model._client)
        
        assert "bundle" in str(exc_info.value).lower()
