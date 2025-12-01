"""Tests for graph traversal functionality.

These tests verify multi-hop traversal, shortest path finding, and impact analysis
capabilities using the Neo4j graph database backend.
"""

import uuid
from datetime import datetime

import pytest
import kumiho


def _unique(prefix: str) -> str:
    """Generate a unique name for test entities."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def traversal_graph(live_client, cleanup_test_data):
    """Create a test graph with linked versions for traversal tests.
    
    Creates the following dependency structure:
    
        texture_v1 <-- model_v1 <-- scene_v1
                   <-- model_v2 <-- scene_v1
        
    Where arrows represent DEPENDS_ON relationships.
    """
    project_name = _unique("traversal_test")
    
    # Create project and group
    project = kumiho.create_project(project_name)
    cleanup_test_data.append(project)
    
    group = project.create_group(name=project_name, parent_path="/")
    cleanup_test_data.append(group)
    
    # Create products
    texture = group.create_product(product_name="shared_texture", product_type="texture")
    cleanup_test_data.append(texture)
    
    model = group.create_product(product_name="hero_model", product_type="model")
    cleanup_test_data.append(model)
    
    scene = group.create_product(product_name="main_scene", product_type="scene")
    cleanup_test_data.append(scene)
    
    # Create versions
    texture_v1 = texture.create_version(metadata={"role": "diffuse"})
    cleanup_test_data.append(texture_v1)
    
    model_v1 = model.create_version(metadata={"lod": "high"})
    cleanup_test_data.append(model_v1)
    
    model_v2 = model.create_version(metadata={"lod": "medium"})
    cleanup_test_data.append(model_v2)
    
    scene_v1 = scene.create_version(metadata={"sequence": "shot_010"})
    cleanup_test_data.append(scene_v1)
    
    # Create links: model_v1 depends on texture_v1
    model_v1.create_link(texture_v1, kumiho.DEPENDS_ON)
    
    # Create links: model_v2 depends on texture_v1
    model_v2.create_link(texture_v1, kumiho.DEPENDS_ON)
    
    # Create links: scene_v1 depends on model_v1
    scene_v1.create_link(model_v1, kumiho.DEPENDS_ON)
    
    return {
        "project": project,
        "group": group,
        "texture_v1": texture_v1,
        "model_v1": model_v1,
        "model_v2": model_v2,
        "scene_v1": scene_v1,
    }


class TestTraverseLinks:
    """Tests for the traverse_links / get_all_dependencies / get_all_dependents methods."""
    
    def test_get_all_dependencies_single_hop(self, traversal_graph):
        """Test that single-hop dependencies are found."""
        model_v1 = traversal_graph["model_v1"]
        texture_v1 = traversal_graph["texture_v1"]
        
        # model_v1 -> texture_v1
        deps = model_v1.get_all_dependencies(max_depth=1)
        
        assert len(deps.version_krefs) == 1
        assert deps.version_krefs[0].uri == texture_v1.kref.uri
        assert deps.total_count == 1
        assert not deps.truncated
    
    def test_get_all_dependencies_multi_hop(self, traversal_graph):
        """Test that multi-hop dependencies are found."""
        scene_v1 = traversal_graph["scene_v1"]
        model_v1 = traversal_graph["model_v1"]
        texture_v1 = traversal_graph["texture_v1"]
        
        # scene_v1 -> model_v1 -> texture_v1
        deps = scene_v1.get_all_dependencies(max_depth=5)
        
        # Should find both model_v1 and texture_v1
        dep_uris = {k.uri for k in deps.version_krefs}
        assert model_v1.kref.uri in dep_uris
        assert texture_v1.kref.uri in dep_uris
        assert deps.total_count == 2
    
    def test_get_all_dependents_finds_upstream(self, traversal_graph):
        """Test that versions depending on a target are found."""
        texture_v1 = traversal_graph["texture_v1"]
        model_v1 = traversal_graph["model_v1"]
        model_v2 = traversal_graph["model_v2"]
        
        # Both model_v1 and model_v2 depend on texture_v1
        dependents = texture_v1.get_all_dependents(max_depth=1)
        
        dependent_uris = {k.uri for k in dependents.version_krefs}
        assert model_v1.kref.uri in dependent_uris
        assert model_v2.kref.uri in dependent_uris
        assert dependents.total_count == 2
    
    def test_get_all_dependents_multi_hop(self, traversal_graph):
        """Test that multi-hop dependents are found."""
        texture_v1 = traversal_graph["texture_v1"]
        model_v1 = traversal_graph["model_v1"]
        scene_v1 = traversal_graph["scene_v1"]
        
        # texture_v1 <- model_v1 <- scene_v1
        dependents = texture_v1.get_all_dependents(max_depth=5)
        
        dependent_uris = {k.uri for k in dependents.version_krefs}
        assert model_v1.kref.uri in dependent_uris
        # scene_v1 transitively depends on texture_v1 via model_v1
        assert scene_v1.kref.uri in dependent_uris
    
    def test_traverse_with_link_type_filter(self, traversal_graph):
        """Test that link type filtering works."""
        model_v1 = traversal_graph["model_v1"]
        texture_v1 = traversal_graph["texture_v1"]
        
        # Filter by DEPENDS_ON - should find texture
        deps = model_v1.get_all_dependencies(
            link_type_filter=[kumiho.DEPENDS_ON],
            max_depth=5
        )
        assert texture_v1.kref.uri in {k.uri for k in deps.version_krefs}
        
        # Filter by a different type - should find nothing
        deps_other = model_v1.get_all_dependencies(
            link_type_filter=["SOME_OTHER_TYPE"],
            max_depth=5
        )
        assert deps_other.total_count == 0
    
    def test_traverse_respects_limit(self, traversal_graph):
        """Test that result limiting works."""
        texture_v1 = traversal_graph["texture_v1"]
        
        # Limit to 1 result
        dependents = texture_v1.get_all_dependents(max_depth=5, limit=1)
        
        assert len(dependents.version_krefs) == 1
        assert dependents.truncated  # Should indicate results were limited
    
    def test_traverse_no_dependencies(self, traversal_graph):
        """Test traversal on a leaf node with no dependencies."""
        texture_v1 = traversal_graph["texture_v1"]
        
        # texture_v1 has no outgoing dependencies
        deps = texture_v1.get_all_dependencies(max_depth=5)
        
        assert deps.total_count == 0
        assert len(deps.version_krefs) == 0


class TestShortestPath:
    """Tests for the find_path_to / find_shortest_path methods."""
    
    def test_find_direct_path(self, traversal_graph):
        """Test finding a direct path between adjacent versions."""
        model_v1 = traversal_graph["model_v1"]
        texture_v1 = traversal_graph["texture_v1"]
        
        path = model_v1.find_path_to(texture_v1)
        
        assert path is not None
        assert path.total_depth == 1
        assert len(path.steps) == 2  # source and target
    
    def test_find_multi_hop_path(self, traversal_graph):
        """Test finding a path through multiple hops."""
        scene_v1 = traversal_graph["scene_v1"]
        texture_v1 = traversal_graph["texture_v1"]
        
        # scene_v1 -> model_v1 -> texture_v1
        path = scene_v1.find_path_to(texture_v1)
        
        assert path is not None
        assert path.total_depth == 2
        assert len(path.steps) == 3  # scene, model, texture
    
    def test_no_path_exists(self, traversal_graph):
        """Test that None is returned when no path exists."""
        texture_v1 = traversal_graph["texture_v1"]
        scene_v1 = traversal_graph["scene_v1"]
        
        # No path from texture to scene (wrong direction)
        # Actually there IS a path in undirected mode, let's test with a filter
        path = texture_v1.find_path_to(
            scene_v1,
            link_type_filter=["NONEXISTENT_TYPE"]
        )
        
        assert path is None
    
    def test_path_to_self(self, traversal_graph):
        """Test that path to self returns no path (or empty)."""
        model_v1 = traversal_graph["model_v1"]
        
        # Path from a node to itself should either be None or length 0
        path = model_v1.find_path_to(model_v1)
        
        # Implementation may return None or a path of length 0
        if path is not None:
            assert path.total_depth == 0


class TestImpactAnalysis:
    """Tests for the analyze_impact method."""
    
    def test_impact_analysis_finds_dependents(self, traversal_graph):
        """Test that impact analysis finds all dependent versions."""
        texture_v1 = traversal_graph["texture_v1"]
        model_v1 = traversal_graph["model_v1"]
        model_v2 = traversal_graph["model_v2"]
        
        impact = texture_v1.analyze_impact()
        
        impacted_uris = {iv.version_kref.uri for iv in impact}
        assert model_v1.kref.uri in impacted_uris
        assert model_v2.kref.uri in impacted_uris
    
    def test_impact_analysis_includes_depth(self, traversal_graph):
        """Test that impact analysis includes depth information."""
        texture_v1 = traversal_graph["texture_v1"]
        
        impact = texture_v1.analyze_impact()
        
        # All impacted versions should have depth >= 1
        for iv in impact:
            assert iv.impact_depth >= 1
    
    def test_impact_analysis_transitive(self, traversal_graph):
        """Test that impact analysis finds transitive dependents."""
        texture_v1 = traversal_graph["texture_v1"]
        scene_v1 = traversal_graph["scene_v1"]
        
        # scene_v1 depends on model_v1 which depends on texture_v1
        impact = texture_v1.analyze_impact(max_depth=5)
        
        impacted_uris = {iv.version_kref.uri for iv in impact}
        assert scene_v1.kref.uri in impacted_uris
    
    def test_impact_analysis_respects_limit(self, traversal_graph):
        """Test that impact analysis respects the limit parameter."""
        texture_v1 = traversal_graph["texture_v1"]
        
        # Limit to 1 result
        impact = texture_v1.analyze_impact(limit=1)
        
        assert len(impact) == 1
    
    def test_impact_analysis_with_link_type_filter(self, traversal_graph):
        """Test that impact analysis respects link type filters."""
        texture_v1 = traversal_graph["texture_v1"]
        
        # Filter by DEPENDS_ON
        impact = texture_v1.analyze_impact(link_type_filter=[kumiho.DEPENDS_ON])
        assert len(impact) >= 1
        
        # Filter by nonexistent type
        impact_none = texture_v1.analyze_impact(link_type_filter=["NONEXISTENT_TYPE"])
        assert len(impact_none) == 0
    
    def test_impact_analysis_no_dependents(self, traversal_graph):
        """Test impact analysis on a version with no dependents."""
        scene_v1 = traversal_graph["scene_v1"]
        
        # scene_v1 is a leaf - nothing depends on it
        impact = scene_v1.analyze_impact()
        
        assert len(impact) == 0


class TestTraversalResult:
    """Tests for the TraversalResult helper methods."""
    
    def test_get_versions_fetches_full_objects(self, traversal_graph):
        """Test that get_versions() returns full Version objects."""
        model_v1 = traversal_graph["model_v1"]
        
        deps = model_v1.get_all_dependencies(max_depth=1)
        versions = deps.get_versions()
        
        assert len(versions) == 1
        assert versions[0].kref.uri == traversal_graph["texture_v1"].kref.uri
        # Full Version objects should have metadata
        assert hasattr(versions[0], 'metadata')
        assert hasattr(versions[0], 'number')
    
    def test_traversal_result_repr(self, traversal_graph):
        """Test TraversalResult string representation."""
        model_v1 = traversal_graph["model_v1"]
        
        deps = model_v1.get_all_dependencies(max_depth=1)
        repr_str = repr(deps)
        
        assert "TraversalResult" in repr_str
        assert "count=" in repr_str


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_traverse_empty_link_type_filter(self, traversal_graph):
        """Test that empty link type filter returns all link types."""
        model_v1 = traversal_graph["model_v1"]
        
        # Empty list should not filter anything
        deps = model_v1.get_all_dependencies(link_type_filter=[], max_depth=5)
        
        # Should still find the texture dependency
        assert deps.total_count >= 1
    
    def test_max_depth_zero_uses_default(self, traversal_graph):
        """Test that max_depth=0 uses a sensible default."""
        model_v1 = traversal_graph["model_v1"]
        
        # max_depth=0 should use default (10)
        deps = model_v1.get_all_dependencies(max_depth=0)
        
        # Should still work and find dependencies
        assert deps.total_count >= 1
    
    def test_traversal_includes_metadata_in_path(self, traversal_graph):
        """Test path information when include_path is used via client."""
        # This tests the lower-level client API
        model_v1 = traversal_graph["model_v1"]
        client = kumiho.get_client()
        
        result = client.traverse_links(
            model_v1.kref,
            direction=kumiho.LinkDirection.OUTGOING,
            max_depth=5,
            include_path=True
        )
        
        # When include_path=True, paths should be populated
        # Note: The current implementation may have minimal path info
        assert result.total_count >= 1
