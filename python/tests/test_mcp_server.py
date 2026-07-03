"""Tests for the Kumiho MCP server.

These tests verify that the MCP server tools work correctly with mocked
Kumiho client responses.
"""

import json
import pytest
from unittest.mock import MagicMock, patch


# Mock MCP imports since they may not be installed
@pytest.fixture(autouse=True)
def mock_mcp_imports():
    """Mock MCP imports for testing."""
    import sys
    
    # Create mock MCP module
    mock_mcp = MagicMock()
    mock_mcp.server = MagicMock()
    mock_mcp.server.Server = MagicMock
    mock_mcp.server.stdio = MagicMock()
    mock_mcp.types = MagicMock()
    
    sys.modules['mcp'] = mock_mcp
    sys.modules['mcp.server'] = mock_mcp.server
    sys.modules['mcp.server.stdio'] = mock_mcp.server.stdio
    sys.modules['mcp.types'] = mock_mcp.types
    
    yield
    
    # Cleanup
    for mod in ['mcp', 'mcp.server', 'mcp.server.stdio', 'mcp.types']:
        if mod in sys.modules:
            del sys.modules[mod]


class MockProject:
    """Mock Project for testing."""
    def __init__(self, name: str, description: str = ""):
        self.project_id = f"proj-{name}"
        self.name = name
        self.description = description
        self.created_at = "2024-01-01T00:00:00Z"
        self.updated_at = "2024-01-01T00:00:00Z"
        self.deprecated = False
        self.allow_public = False
    
    def get_spaces(self, recursive: bool = False):
        return [MockSpace(f"/{self.name}/space1")]


class MockSpace:
    """Mock Space for testing."""
    def __init__(self, path: str):
        self.kref = MagicMock()
        self.kref.uri = f"kref:/{path}"
        self.name = path.split("/")[-1]
        self.path = path
        self.created_at = "2024-01-01T00:00:00Z"
        self.deprecated = False


class MockItem:
    """Mock Item for testing."""
    def __init__(self, kref: str):
        self.kref = MagicMock()
        self.kref.uri = kref
        self.name = "hero.model"
        self.item_name = "hero"
        self.kind = "model"
        self.created_at = "2024-01-01T00:00:00Z"
        self.author = "user1"
        self.username = "Test User"
        self.metadata = {"artist": "jane"}
        self.deprecated = False


class MockRevision:
    """Mock Revision for testing."""
    def __init__(self, kref: str, number: int = 1):
        self.kref = MagicMock()
        self.kref.uri = kref
        self.item_kref = MagicMock()
        self.item_kref.uri = kref.split("?")[0]
        self.number = number
        self.latest = True
        self._cached_tags = ["latest", "approved"]
        self.metadata = {"render": "cycles"}
        self.created_at = "2024-01-01T00:00:00Z"
        self.author = "user1"
        self.username = "Test User"
        self.deprecated = False
        self.published = False
        self.default_artifact = "mesh"
    
    def get_artifacts(self):
        return [MockArtifact(f"{self.kref.uri}&a=mesh")]
    
    def get_all_dependencies(self, edge_type_filter=None, max_depth=10):
        result = MagicMock()
        result.revision_krefs = ["kref://project/textures/skin.texture?r=1"]
        return result
    
    def get_all_dependents(self, edge_type_filter=None, max_depth=10):
        result = MagicMock()
        result.revision_krefs = ["kref://project/renders/hero_render.exr?r=1"]
        return result
    
    def analyze_impact(self, edge_type_filter=None, max_depth=10):
        impacted = MagicMock()
        impacted.revision_kref = "kref://project/renders/hero_render.exr?r=1"
        impacted.impact_depth = 1
        return [impacted]


class MockArtifact:
    """Mock Artifact for testing."""
    def __init__(self, kref: str):
        self.kref = MagicMock()
        self.kref.uri = kref
        self.name = "mesh"
        self.location = "/projects/film/hero.fbx"
        self.revision_kref = MagicMock()
        self.revision_kref.uri = kref.split("&")[0]
        self.created_at = "2024-01-01T00:00:00Z"
        self.metadata = {}


class TestMCPTools:
    """Test MCP tool implementations."""
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_projects')
    def test_tool_list_projects(self, mock_get_projects, mock_configure):
        """Test listing projects."""
        mock_get_projects.return_value = [
            MockProject("project-a", "First project"),
            MockProject("project-b", "Second project"),
        ]
        
        from kumiho.mcp_server import tool_list_projects
        result = tool_list_projects()
        
        assert result["count"] == 2
        assert len(result["projects"]) == 2
        assert result["projects"][0]["name"] == "project-a"
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_project')
    def test_tool_get_project(self, mock_get_project, mock_configure):
        """Test getting a project."""
        mock_get_project.return_value = MockProject("my-project", "Test project")
        
        from kumiho.mcp_server import tool_get_project
        result = tool_get_project("my-project")
        
        assert result["name"] == "my-project"
        assert result["description"] == "Test project"
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_project')
    def test_tool_get_project_not_found(self, mock_get_project, mock_configure):
        """Test getting a non-existent project."""
        mock_get_project.return_value = None
        
        from kumiho.mcp_server import tool_get_project
        result = tool_get_project("nonexistent")
        
        assert "error" in result
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_item')
    def test_tool_get_item(self, mock_get_item, mock_configure):
        """Test getting an item."""
        mock_get_item.return_value = MockItem("kref://project/space/hero.model")
        
        from kumiho.mcp_server import tool_get_item
        result = tool_get_item("kref://project/space/hero.model")
        
        assert result["kind"] == "model"
        assert result["item_name"] == "hero"
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_revision')
    def test_tool_get_revision(self, mock_get_revision, mock_configure):
        """Test getting a revision."""
        mock_get_revision.return_value = MockRevision(
            "kref://project/space/hero.model?r=1"
        )
        
        from kumiho.mcp_server import tool_get_revision
        result = tool_get_revision("kref://project/space/hero.model?r=1")
        
        assert result["number"] == 1
        assert result["latest"] is True
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_revision')
    def test_tool_get_dependencies(self, mock_get_revision, mock_configure):
        """Test getting dependencies."""
        mock_get_revision.return_value = MockRevision(
            "kref://project/space/hero.model?r=1"
        )
        
        from kumiho.mcp_server import tool_get_dependencies
        result = tool_get_dependencies(
            "kref://project/space/hero.model?r=1",
            max_depth=5
        )
        
        assert result["count"] == 1
        assert "skin.texture" in result["dependencies"][0]
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_revision')
    def test_tool_analyze_impact(self, mock_get_revision, mock_configure):
        """Test impact analysis."""
        mock_get_revision.return_value = MockRevision(
            "kref://project/space/hero.model?r=1"
        )
        
        from kumiho.mcp_server import tool_analyze_impact
        result = tool_analyze_impact("kref://project/space/hero.model?r=1")
        
        assert result["count"] == 1
        assert result["impacted_revisions"][0]["impact_depth"] == 1
    
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    def test_tool_search_items(self, mock_search, mock_configure):
        """Test searching items."""
        mock_search.return_value = [
            MockItem("kref://project/chars/hero.model"),
            MockItem("kref://project/chars/villain.model"),
        ]
        
        from kumiho.mcp_server import tool_search_items
        result = tool_search_items(kind_filter="model")
        
        assert result["count"] == 2
        assert result["filters"]["kind"] == "model"


class TestToolDefinitions:
    """Test that tool definitions are valid."""
    
    def test_all_tools_have_required_fields(self):
        """Verify all tools have name, description, and inputSchema."""
        from kumiho.mcp_server import TOOLS
        
        for tool in TOOLS:
            assert "name" in tool, f"Tool missing name"
            assert "description" in tool, f"Tool {tool.get('name')} missing description"
            assert "inputSchema" in tool, f"Tool {tool.get('name')} missing inputSchema"
            assert tool["inputSchema"]["type"] == "object"
    
    def test_all_tools_have_handlers(self):
        """Verify all tools have corresponding handlers."""
        from kumiho.mcp_server import TOOLS, TOOL_HANDLERS
        
        for tool in TOOLS:
            assert tool["name"] in TOOL_HANDLERS, \
                f"Tool {tool['name']} has no handler"
    
    def test_tool_names_follow_convention(self):
        """Verify tool names follow kumiho_ prefix convention."""
        from kumiho.mcp_server import TOOLS
        
        for tool in TOOLS:
            assert tool["name"].startswith("kumiho_"), \
                f"Tool {tool['name']} should start with 'kumiho_'"




class TestMemoryRetrieveFallbackBounds:
    """Regression tests for the tool_memory_retrieve RPC-storm fixes.

    Production incident: the deep search variant returned 0 results for
    every query, so every recall fell into the pattern fallback, which
    resolved published/latest revisions for EVERY item in the project
    (457 items -> 914 serial get_revision_by_tag RPCs -> ~185s -> MCP
    timeout).
    """

    def _make_item(self, idx: int, created_at: str):
        item = MockItem(f"kref://CognitiveMemory/facts/note-{idx}.conversation")
        item.kind = "conversation"
        item.created_at = created_at
        item.space = None
        item.tag_calls = 0

        rev = MockRevision(f"{item.kref.uri}?r=1")

        def get_revision_by_tag(tag, _item=item, _rev=rev):
            _item.tag_calls += 1
            return _rev if tag == "latest" else None

        item.get_revision_by_tag = get_revision_by_tag
        return item

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_pattern_fallback_bounds_revision_resolution(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """457 items in the project must NOT mean 900+ tag-resolution
        calls — the fallback resolves at most limit*2 newest items."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_search.return_value = []  # force the pattern fallback
        items = [
            self._make_item(i, f"2026-05-{(i % 28) + 1:02d}T00:00:00+00:00")
            for i in range(457)
        ]
        mock_item_search.return_value = items

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="no such thing", limit=5,
        )

        total_tag_calls = sum(item.tag_calls for item in items)
        assert total_tag_calls <= 5 * 2 * 2, (
            f"fallback made {total_tag_calls} tag-resolution calls; "
            "must be bounded by limit*2 items x 2 calls each"
        )
        assert len(result["revision_krefs"]) == 5

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_pattern_fallback_prefers_newest_items(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_search.return_value = []
        old = self._make_item(0, "2026-01-01T00:00:00+00:00")
        new = self._make_item(1, "2026-06-30T00:00:00+00:00")
        mock_item_search.return_value = [old] + [
            self._make_item(i, "2026-03-01T00:00:00+00:00") for i in range(2, 30)
        ] + [new]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="no such thing", limit=5,
        )

        assert new.kref.uri in result["item_krefs"]
        assert old.kref.uri not in result["item_krefs"]

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_deep_search_zero_results_retries_shallow(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """include_revision_metadata=True returning 0 must retry with
        False before falling into the expensive pattern fallback."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        # A retry regression must fail fast here, not fall through to the
        # pattern fallback and issue real RPCs against a live server.
        mock_item_search.return_value = []
        deep_calls = []
        shallow_item = MockItem("kref://CognitiveMemory/facts/hit.conversation")
        shallow_item.kind = "conversation"
        shallow_item.space = None
        rev = MockRevision(f"{shallow_item.kref.uri}?r=1")
        shallow_item.get_revision_by_tag = lambda tag: rev if tag == "latest" else None

        hit = MagicMock()
        hit.item = shallow_item
        hit.score = 0.9

        def search_side_effect(query, **kwargs):
            deep_calls.append(kwargs.get("include_revision_metadata"))
            if kwargs.get("include_revision_metadata"):
                return []  # deep variant broken (production behavior)
            return [hit]

        mock_search.side_effect = search_side_effect

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=5,
        )

        assert True in deep_calls and False in deep_calls, (
            f"expected deep-then-shallow retry, got calls: {deep_calls}"
        )
        assert result["revision_krefs"] == [rev.kref.uri]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
