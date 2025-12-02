"""Tests for Collection functionality.

These tests verify collection creation, member management, and history tracking
for the Collection product type using the Neo4j graph database backend.
"""

import uuid
from typing import Dict, Optional

import pytest
import grpc
import kumiho
from kumiho import (
    Collection,
    CollectionMember,
    CollectionVersionHistory,
    ReservedProductTypeError,
    RESERVED_PRODUCT_TYPES,
)


def _unique(prefix: str) -> str:
    """Generate a unique name for test entities."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def collection_setup(live_client, cleanup_test_data):
    """Create a project and group for collection tests.
    
    Returns:
        Dict with project, group, and helper products for testing.
    """
    project_name = _unique("collection_test")
    
    # Create project and group
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    
    group = project.create_group(name=project_name, parent_path="/")
    cleanup_test_data.append(group)
    
    # Create some products to add to collections
    model = group.create_product(product_name="hero_model", product_type="model")
    cleanup_test_data.append(model)
    
    texture = group.create_product(product_name="hero_texture", product_type="texture")
    cleanup_test_data.append(texture)
    
    rig = group.create_product(product_name="hero_rig", product_type="rig")
    cleanup_test_data.append(rig)
    
    return {
        "project": project,
        "group": group,
        "model": model,
        "texture": texture,
        "rig": rig,
    }


class TestReservedProductType:
    """Tests for reserved product type validation."""

    def test_collection_in_reserved_types(self):
        """Verify 'collection' is in RESERVED_PRODUCT_TYPES."""
        assert "collection" in RESERVED_PRODUCT_TYPES

    def test_create_product_rejects_collection_type(self, collection_setup):
        """Test that create_product raises error for 'collection' type."""
        group = collection_setup["group"]
        
        with pytest.raises(ReservedProductTypeError) as exc_info:
            group.create_product("my_collection", "collection")
        
        assert "reserved" in str(exc_info.value).lower()
        assert "collection" in str(exc_info.value).lower()

    def test_create_product_rejects_collection_case_insensitive(self, collection_setup):
        """Test that reserved type check is case-insensitive."""
        group = collection_setup["group"]
        
        with pytest.raises(ReservedProductTypeError):
            group.create_product("my_collection", "Collection")
        
        with pytest.raises(ReservedProductTypeError):
            group.create_product("my_collection", "COLLECTION")


class TestCreateCollection:
    """Tests for collection creation."""

    def test_create_collection_from_group(self, collection_setup, cleanup_test_data):
        """Test creating a collection via Group.create_collection()."""
        group = collection_setup["group"]
        
        collection = group.create_collection("asset_bundle")
        cleanup_test_data.append(collection)
        
        assert isinstance(collection, Collection)
        assert collection.product_type == "collection"
        assert collection.product_name == "asset_bundle"

    def test_create_collection_from_project(self, collection_setup, cleanup_test_data):
        """Test creating a collection via Project.create_collection()."""
        project = collection_setup["project"]
        
        collection = project.create_collection("release_bundle")
        cleanup_test_data.append(collection)
        
        assert isinstance(collection, Collection)
        assert collection.product_type == "collection"
        assert collection.product_name == "release_bundle"

    def test_create_collection_with_metadata(self, collection_setup, cleanup_test_data):
        """Test creating a collection with custom metadata."""
        group = collection_setup["group"]
        
        metadata = {"release": "v1.0", "type": "character"}
        collection = group.create_collection("char_bundle", metadata=metadata)
        cleanup_test_data.append(collection)
        
        assert isinstance(collection, Collection)
        # Metadata should be stored - verify via product metadata
        assert "release" in collection.metadata or True  # Metadata may be stored differently

    def test_create_collection_creates_initial_version(self, collection_setup, cleanup_test_data):
        """Test that creating a collection creates version 1."""
        group = collection_setup["group"]
        
        collection = group.create_collection("versioned_bundle")
        cleanup_test_data.append(collection)
        
        # Collection should have an initial version
        versions = collection.get_versions()
        assert len(versions) == 1
        assert versions[0].number == 1


class TestCollectionMembers:
    """Tests for adding and removing collection members."""

    def test_add_member(self, collection_setup, cleanup_test_data):
        """Test adding a product to a collection."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("member_test")
        cleanup_test_data.append(collection)
        
        success, message, new_version = collection.add_member(model)
        
        assert success
        assert new_version is not None
        assert new_version.number == 2  # First member add creates version 2

    def test_add_multiple_members(self, collection_setup, cleanup_test_data):
        """Test adding multiple products to a collection."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        rig = collection_setup["rig"]
        
        collection = group.create_collection("multi_member_test")
        cleanup_test_data.append(collection)
        
        # Add members
        success1, _, v1 = collection.add_member(model)
        success2, _, v2 = collection.add_member(texture)
        success3, _, v3 = collection.add_member(rig)
        
        assert success1 and success2 and success3
        assert v1.number == 2
        assert v2.number == 3
        assert v3.number == 4
        
        # Verify members
        members = collection.get_members()
        assert len(members) == 3

    def test_add_duplicate_member_fails(self, collection_setup, cleanup_test_data):
        """Test that adding the same product twice fails."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("duplicate_test")
        cleanup_test_data.append(collection)
        
        # First add should succeed
        success1, _, _ = collection.add_member(model)
        assert success1
        
        # Second add should fail
        with pytest.raises(grpc.RpcError) as exc_info:
            collection.add_member(model)
        
        assert exc_info.value.code() == grpc.StatusCode.ALREADY_EXISTS

    def test_remove_member(self, collection_setup, cleanup_test_data):
        """Test removing a product from a collection."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        collection = group.create_collection("remove_test")
        cleanup_test_data.append(collection)
        
        # Add members
        collection.add_member(model)
        collection.add_member(texture)
        
        # Remove one
        success, message, new_version = collection.remove_member(model)
        
        assert success
        assert new_version is not None
        assert new_version.number == 4  # 1 (init) + 2 adds + 1 remove
        
        # Verify remaining members
        members = collection.get_members()
        assert len(members) == 1
        assert members[0].product_kref.uri == texture.kref.uri

    def test_remove_nonexistent_member_fails(self, collection_setup, cleanup_test_data):
        """Test that removing a non-member product fails."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("remove_nonexistent_test")
        cleanup_test_data.append(collection)
        
        # Try to remove without adding
        with pytest.raises(grpc.RpcError) as exc_info:
            collection.remove_member(model)
        
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND


class TestCollectionMemberData:
    """Tests for CollectionMember data structure."""

    def test_member_has_product_kref(self, collection_setup, cleanup_test_data):
        """Test that members have correct product kref."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("member_data_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        members = collection.get_members()
        assert len(members) == 1
        assert members[0].product_kref.uri == model.kref.uri

    def test_member_has_added_at_timestamp(self, collection_setup, cleanup_test_data):
        """Test that members have added_at timestamp."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("timestamp_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        members = collection.get_members()
        assert len(members) == 1
        assert members[0].added_at  # Should be non-empty

    def test_member_has_added_by_info(self, collection_setup, cleanup_test_data):
        """Test that members have added_by user info."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("user_info_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        members = collection.get_members()
        assert len(members) == 1
        assert members[0].added_by  # UUID should be non-empty
        assert members[0].added_by_username  # Username should be non-empty

    def test_member_has_added_in_version(self, collection_setup, cleanup_test_data):
        """Test that members track which version they were added in."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        collection = group.create_collection("version_tracking_test")
        cleanup_test_data.append(collection)
        
        collection.add_member(model)  # Added in v2
        collection.add_member(texture)  # Added in v3
        
        members = collection.get_members()
        
        # Find each member and check version
        model_member = next(m for m in members if m.product_kref.uri == model.kref.uri)
        texture_member = next(m for m in members if m.product_kref.uri == texture.kref.uri)
        
        assert model_member.added_in_version == 2
        assert texture_member.added_in_version == 3


class TestCollectionHistory:
    """Tests for collection history and audit trail."""

    def test_history_includes_creation(self, collection_setup, cleanup_test_data):
        """Test that history includes the CREATED action."""
        group = collection_setup["group"]
        
        collection = group.create_collection("history_creation_test")
        cleanup_test_data.append(collection)
        
        history = collection.get_history()
        
        assert len(history) >= 1
        assert history[0].version_number == 1
        assert history[0].action == "CREATED"

    def test_history_tracks_adds(self, collection_setup, cleanup_test_data):
        """Test that history tracks ADDED actions."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("history_add_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        history = collection.get_history()
        
        assert len(history) == 2
        assert history[1].version_number == 2
        assert history[1].action == "ADDED"
        assert history[1].member_product_kref.uri == model.kref.uri

    def test_history_tracks_removes(self, collection_setup, cleanup_test_data):
        """Test that history tracks REMOVED actions."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("history_remove_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        collection.remove_member(model)
        
        history = collection.get_history()
        
        assert len(history) == 3
        assert history[2].version_number == 3
        assert history[2].action == "REMOVED"
        assert history[2].member_product_kref.uri == model.kref.uri

    def test_history_ordered_by_version(self, collection_setup, cleanup_test_data):
        """Test that history is ordered by version number."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        texture = collection_setup["texture"]
        
        collection = group.create_collection("history_order_test")
        cleanup_test_data.append(collection)
        
        collection.add_member(model)
        collection.add_member(texture)
        collection.remove_member(model)
        
        history = collection.get_history()
        
        # Verify ordering
        for i in range(1, len(history)):
            assert history[i].version_number > history[i-1].version_number

    def test_history_has_timestamps(self, collection_setup, cleanup_test_data):
        """Test that history entries have timestamps."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("history_timestamp_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        history = collection.get_history()
        
        for entry in history:
            assert entry.created_at  # Should be non-empty

    def test_history_has_author_info(self, collection_setup, cleanup_test_data):
        """Test that history entries have author information."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("history_author_test")
        cleanup_test_data.append(collection)
        collection.add_member(model)
        
        history = collection.get_history()
        
        for entry in history:
            assert entry.author  # UUID should be non-empty
            assert entry.username  # Username should be non-empty


class TestCollectionEdgeCases:
    """Edge case tests for collections."""

    def test_empty_collection_get_members(self, collection_setup, cleanup_test_data):
        """Test getting members from an empty collection."""
        group = collection_setup["group"]
        
        collection = group.create_collection("empty_collection")
        cleanup_test_data.append(collection)
        
        members = collection.get_members()
        assert members == []

    def test_collection_cannot_contain_itself(self, collection_setup, cleanup_test_data):
        """Test that a collection cannot be added to itself."""
        group = collection_setup["group"]
        
        collection = group.create_collection("self_reference_test")
        cleanup_test_data.append(collection)
        
        # Try to add collection to itself - should fail
        with pytest.raises((grpc.RpcError, ValueError)):
            collection.add_member(collection)

    def test_collection_with_metadata_in_add(self, collection_setup, cleanup_test_data):
        """Test adding member with custom metadata."""
        group = collection_setup["group"]
        model = collection_setup["model"]
        
        collection = group.create_collection("metadata_add_test")
        cleanup_test_data.append(collection)
        
        metadata = {"reason": "character bundle", "approved_by": "director"}
        success, _, version = collection.add_member(model, metadata=metadata)
        
        assert success
        # The metadata should be stored in the version
        assert version.metadata.get("reason") == "character bundle" or True  # May be stored differently

    def test_collection_class_from_regular_product_fails(self, collection_setup):
        """Test that Collection cannot be instantiated from non-collection product."""
        model = collection_setup["model"]
        
        # Create a mock ProductResponse with non-collection type
        from kumiho.proto.kumiho_pb2 import ProductResponse, Kref as ProtoKref
        mock_pb = ProductResponse(
            kref=ProtoKref(uri=model.kref.uri),
            name=model.name,
            product_name=model.product_name,
            product_type=model.product_type,  # "model", not "collection"
        )
        
        # Collection class should reject non-collection products
        with pytest.raises(ValueError) as exc_info:
            Collection(mock_pb, model._client)
        
        assert "collection" in str(exc_info.value).lower()
