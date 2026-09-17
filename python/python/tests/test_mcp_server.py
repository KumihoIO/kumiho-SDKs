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


class TestMemoryTypeRoundTrip:
    """Regression tests for issue #21: the server reserves the "type"
    metadata key and strips it from every read, so the memory type must
    travel as "memory_type" and alias back to "type" for legacy readers."""

    def test_serialize_revision_aliases_memory_type(self):
        from kumiho.mcp_server import _serialize_revision
        rev = MockRevision("kref://p/s/i.conversation?r=1")
        rev.metadata = {"memory_type": "decision", "title": "t"}

        data = _serialize_revision(rev)

        assert data["metadata"]["type"] == "decision"
        assert data["metadata"]["memory_type"] == "decision"

    def test_serialize_revision_keeps_explicit_type(self):
        from kumiho.mcp_server import _serialize_revision
        rev = MockRevision("kref://p/s/i.conversation?r=1")
        rev.metadata = {"memory_type": "decision", "type": "fact"}

        data = _serialize_revision(rev)

        assert data["metadata"]["type"] == "fact"

    def test_matches_memory_types(self):
        from kumiho.mcp_server import _matches_memory_types
        rev = MockRevision("kref://p/s/i.conversation?r=1")

        rev.metadata = {"memory_type": "Decision"}
        assert _matches_memory_types(rev, {"decision"})
        assert not _matches_memory_types(rev, {"fact"})

        rev.metadata = {"type": "fact"}  # legacy key still honoured
        assert _matches_memory_types(rev, {"fact"})

        rev.metadata = {}  # untyped legacy revision
        assert not _matches_memory_types(rev, {"fact"})
        assert _matches_memory_types(rev, None)  # no filter -> everything

    @patch('kumiho.mcp_server._write_memory_artifact', return_value="")
    @patch('kumiho.mcp_server._get_or_create_item')
    @patch('kumiho.mcp_server._find_similar_item', return_value=(None, 0.0, 0.0, 0.0))
    @patch('kumiho.mcp_server._ensure_space_path', return_value="facts")
    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    def test_store_stamps_memory_type_metadata(
        self, mock_configure, mock_get_project, mock_ensure_space,
        mock_find_similar, mock_get_item, mock_artifact,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        captured = {}

        item = MockItem("kref://CognitiveMemory/facts/note.conversation")
        rev = MockRevision(f"{item.kref.uri}?r=1")
        rev.tag = lambda tag: None

        def create_revision(metadata=None):
            captured.update(metadata or {})
            return rev

        item.create_revision = create_revision
        mock_get_item.return_value = item

        from kumiho.mcp_server import tool_memory_store
        result = tool_memory_store(
            project="CognitiveMemory",
            space_path="facts",
            memory_type="decision",
            title="t",
            summary="s",
            user_text="u",
        )

        assert "error" not in result
        assert captured["memory_type"] == "decision"
        assert captured["type"] == "decision"

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_retrieve_filters_by_memory_types(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """memory_types must actually filter (it was dead code)."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_search.return_value = []  # force the pattern fallback

        def typed_item(idx, mem_type):
            item = MockItem(f"kref://CognitiveMemory/facts/note-{idx}.conversation")
            item.kind = "conversation"
            item.created_at = "2026-06-01T00:00:00+00:00"
            item.space = None
            rev = MockRevision(f"{item.kref.uri}?r=1")
            rev.metadata = {"memory_type": mem_type}
            item.get_revision_by_tag = lambda tag, _rev=rev: _rev if tag == "latest" else None
            return item

        decisions = [typed_item(i, "decision") for i in range(2)]
        facts = [typed_item(i + 10, "fact") for i in range(3)]
        mock_item_search.return_value = decisions + facts

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="no such thing", limit=5,
            memory_types=["decision"],
        )

        assert sorted(result["item_krefs"]) == sorted(d.kref.uri for d in decisions)

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.search')
    def test_search_path_filters_by_memory_types(
        self, mock_search, mock_configure, mock_get_project,
    ):
        """The primary search path must apply the filter too — not just
        the pattern fallback."""
        mock_get_project.return_value = MockProject("CognitiveMemory")

        def typed_hit(idx, mem_type, score):
            item = MockItem(f"kref://CognitiveMemory/facts/hit-{idx}.conversation")
            item.kind = "conversation"
            item.space = None
            rev = MockRevision(f"{item.kref.uri}?r=1")
            rev.metadata = {"memory_type": mem_type}
            item.get_revision_by_tag = lambda tag, _rev=rev: _rev if tag == "latest" else None
            hit = MagicMock()
            hit.item = item
            hit.score = score
            return hit

        decision_hit = typed_hit(1, "decision", 0.9)
        fact_hit = typed_hit(2, "fact", 0.8)
        mock_search.return_value = [decision_hit, fact_hit]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=5,
            memory_types=["decision"],
        )

        assert result["item_krefs"] == [decision_hit.item.kref.uri]

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    def test_first_mode_respects_memory_types(
        self, mock_item_search, mock_configure, mock_get_project,
    ):
        """mode="first" must return the oldest MATCHING item, not the
        oldest item outright."""
        mock_get_project.return_value = MockProject("CognitiveMemory")

        def typed_item(idx, mem_type, created_at):
            item = MockItem(f"kref://CognitiveMemory/facts/note-{idx}.conversation")
            item.kind = "conversation"
            item.created_at = created_at
            item.space = None
            rev = MockRevision(f"{item.kref.uri}?r=1")
            rev.metadata = {"memory_type": mem_type}
            item.get_revision_by_tag = lambda tag, _rev=rev: _rev if tag == "latest" else None
            return item

        oldest_fact = typed_item(1, "fact", "2026-01-01T00:00:00+00:00")
        older_decision = typed_item(2, "decision", "2026-02-01T00:00:00+00:00")
        newer_decision = typed_item(3, "decision", "2026-03-01T00:00:00+00:00")
        mock_item_search.return_value = [newer_decision, oldest_fact, older_decision]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="first", memory_types=["decision"],
        )
        assert result["item_krefs"] == [older_decision.kref.uri]

        # Without a filter the oldest item wins, as before.
        result = tool_memory_retrieve(project="CognitiveMemory", mode="first")
        assert result["item_krefs"] == [oldest_fact.kref.uri]


class TestMemoryRetrieveLatestMode:
    """mode="latest" was advertised in the tool schema but had no branch, so
    it silently behaved as search: relevance order with a query, and item
    creation order (blind to stacked revisions) without one."""

    @staticmethod
    def _item(
        name, rev_created_at, *, created_at="2025-01-01T00:00:00+00:00",
        modified_at=None, space="facts", mem_type=None,
        published_created_at=None,
    ):
        """A memory item whose resolved revision has ``rev_created_at``.

        ``published_created_at`` pins ``published`` on an older revision
        while ``latest`` stays at ``rev_created_at``.  ``modified_at`` is
        only set when given, like a server that does not report it.
        """
        item = MockItem(f"kref://CognitiveMemory/{space}/{name}.conversation")
        item.kind = "conversation"
        item.created_at = created_at
        item.space = None
        if modified_at is not None:
            item.modified_at = modified_at
        item.resolved = 0

        latest = MockRevision(f"{item.kref.uri}?r=2")
        latest.created_at = rev_created_at
        latest.metadata = {"memory_type": mem_type} if mem_type else {}
        published = None
        if published_created_at is not None:
            published = MockRevision(f"{item.kref.uri}?r=1")
            published.created_at = published_created_at
            published.metadata = dict(latest.metadata)
        item.returned_rev = published or latest

        def get_revision_by_tag(tag, _item=item, _pub=published, _latest=latest):
            if tag == "published":
                _item.resolved += 1
                return _pub
            return _latest if tag == "latest" else None

        item.get_revision_by_tag = get_revision_by_tag
        return item

    @staticmethod
    def _hit(item, score):
        hit = MagicMock()
        hit.item = item
        hit.score = score
        return hit

    # -- (a) with a query: relevance filters, date orders ------------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_query_orders_relevant_matches_by_revision_date(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        best = self._item("best-match", "2026-01-10T00:00:00+00:00")
        newest = self._item("newest-match", "2026-03-10T00:00:00+00:00")
        middle = self._item("middle-match", "2026-02-10T00:00:00+00:00")
        mock_search.return_value = [
            self._hit(best, 0.9), self._hit(newest, 0.8), self._hit(middle, 0.7),
        ]
        # A newer memory that did NOT match the query must not appear.
        mock_item_search.return_value = [
            self._item("unrelated", "2026-09-01T00:00:00+00:00"),
        ]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="deploy pipeline", mode="latest",
        )

        assert result["item_krefs"] == [
            newest.kref.uri, middle.kref.uri, best.kref.uri,
        ]
        assert result["scores"] == [0.8, 0.7, 0.9]  # kept, not sorted by
        assert result["created_at"] == [
            "2026-03-10T00:00:00+00:00",
            "2026-02-10T00:00:00+00:00",
            "2026-01-10T00:00:00+00:00",
        ]
        mock_item_search.assert_not_called()
        assert mock_search.call_args.args[0] == "deploy pipeline"

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_query_pool_reaches_past_search_modes_cut(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """Search mode resolves limit*2 hits; latest must look further, or
        the newest relevant memory ranked 11th could never come back."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_item_search.return_value = []
        hits = [
            self._hit(
                self._item(f"hit-{i}", f"2026-01-{i + 1:02d}T00:00:00+00:00"),
                1.0 - i * 0.01,
            )
            for i in range(25)
        ]
        newest = hits[10].item
        newest.returned_rev.created_at = "2026-08-01T00:00:00+00:00"
        mock_search.return_value = hits

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=2, mode="latest",
        )
        assert result["item_krefs"][0] == newest.kref.uri

        # Hits ranked beyond max(limit * 4, 20) are not resolved at all.
        assert all(hit.item.resolved == 0 for hit in hits[20:])

        search = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=2,
        )
        assert newest.kref.uri not in search["item_krefs"]

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.search')
    def test_query_unrolled_revisions_order_by_their_own_dates(
        self, mock_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        stacked = self._item("stacked", "2026-01-01T00:00:00+00:00")
        r1 = MockRevision(f"{stacked.kref.uri}?r=1")
        r1.created_at = "2026-01-01T00:00:00+00:00"
        r2 = MockRevision(f"{stacked.kref.uri}?r=2")
        r2.created_at = "2026-05-01T00:00:00+00:00"
        stacked.get_revisions = lambda: [r1, r2]
        single = self._item("single", "2026-03-01T00:00:00+00:00")
        single.get_revisions = lambda: [single.returned_rev]
        mock_search.return_value = [self._hit(stacked, 0.9), self._hit(single, 0.5)]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", mode="latest",
            unroll_revisions=True,
        )

        assert result["revision_krefs"] == [
            r2.kref.uri, single.returned_rev.kref.uri, r1.kref.uri,
        ]

    # -- (b) without a query: a stacked update counts as recent ------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_empty_query_old_item_with_newest_revision_comes_first(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        restacked = self._item(
            "old-but-updated", "2026-07-01T00:00:00+00:00",
            created_at="2025-01-01T00:00:00+00:00",
            modified_at="2026-07-01T00:00:00+00:00",
        )
        recent = self._item(
            "recently-created", "2026-06-01T00:00:00+00:00",
            created_at="2026-06-01T00:00:00+00:00",
            modified_at="2026-06-01T00:00:00+00:00",
        )
        older = self._item(
            "older", "2026-05-01T00:00:00+00:00",
            created_at="2026-05-01T00:00:00+00:00",
            modified_at="2026-05-01T00:00:00+00:00",
        )
        mock_item_search.return_value = [recent, older, restacked]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(project="CognitiveMemory", mode="latest")

        mock_search.assert_not_called()
        assert result["item_krefs"] == [
            restacked.kref.uri, recent.kref.uri, older.kref.uri,
        ]
        assert result["created_at"][0] == "2026-07-01T00:00:00+00:00"

        # Search mode (the old accidental behaviour) orders by item creation.
        search = tool_memory_retrieve(project="CognitiveMemory")
        assert search["item_krefs"][0] == recent.kref.uri

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    def test_empty_query_orders_by_published_not_newest_revision(
        self, mock_item_search, mock_configure, mock_get_project,
    ):
        """modified_at bounds the key from above; the key itself is the
        returned (published) revision's date, and early stopping must not
        cut an item that ranks below the bound but above the key."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        pinned = self._item(
            "published-pinned-old", "2026-08-01T00:00:00+00:00",
            modified_at="2026-08-01T00:00:00+00:00",
            published_created_at="2026-01-01T00:00:00+00:00",
        )
        fresh = self._item(
            "fresh", "2026-07-01T00:00:00+00:00",
            modified_at="2026-07-01T00:00:00+00:00",
        )
        stale = self._item(
            "stale", "2026-06-01T00:00:00+00:00",
            modified_at="2026-06-01T00:00:00+00:00",
        )
        mock_item_search.return_value = [pinned, fresh, stale]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=1,
        )

        assert result["item_krefs"] == [fresh.kref.uri]
        assert result["revision_krefs"] == [fresh.returned_rev.kref.uri]
        assert stale.resolved == 0  # bound 06-01 < accepted 07-01: stopped

    # -- (c) space_paths and memory_types ----------------------------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_honors_space_paths_and_memory_types_without_cross_space_fallback(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        in_space_decision = self._item(
            "decision", "2026-03-01T00:00:00+00:00", mem_type="decision",
        )
        in_space_fact = self._item(
            "fact", "2026-04-01T00:00:00+00:00", mem_type="fact",
        )
        other_space = self._item(
            "elsewhere", "2026-09-01T00:00:00+00:00", space="other",
            mem_type="decision",
        )
        contexts = []

        def item_search(context_filter="", name_filter="", kind_filter=""):
            contexts.append(context_filter)
            if context_filter == "CognitiveMemory/facts":
                return [in_space_decision, in_space_fact]
            return [in_space_decision, in_space_fact, other_space]

        mock_item_search.side_effect = item_search

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", space_paths=["facts"],
        )
        assert result["item_krefs"] == [in_space_fact.kref.uri, in_space_decision.kref.uri]
        assert contexts == ["CognitiveMemory/facts"]
        assert result["spaces_used"] == ["CognitiveMemory/facts"]

        contexts.clear()
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", space_paths=["facts"],
            memory_types=["decision"],
        )
        assert result["item_krefs"] == [in_space_decision.kref.uri]

        # Nothing in scope matches: empty, never the newer out-of-scope item.
        contexts.clear()
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", space_paths=["facts"],
            memory_types=["preference"],
        )
        assert result["item_krefs"] == []
        assert result["created_at"] == []
        assert contexts == ["CognitiveMemory/facts"]

        # With a query the relevance search is scoped the same way.
        mock_search.return_value = [self._hit(in_space_fact, 0.4)]
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="facts", mode="latest",
            space_paths=["facts"],
        )
        assert {c.kwargs["context"] for c in mock_search.call_args_list} == {
            "CognitiveMemory/facts"
        }
        assert result["item_krefs"] == [in_space_fact.kref.uri]

    # -- (d) limit, created_at alignment, missing timestamps ---------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    def test_limit_and_aligned_created_at_with_missing_timestamps_last(
        self, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        undated = self._item("undated", None)
        blank = self._item("blank", "")
        jan = self._item("jan", "2026-01-01T00:00:00Z")
        # Same instant as 09:00 UTC, written with an offset.
        mar = self._item("mar", "2026-03-01T18:00:00+09:00")
        feb = self._item("feb", "2026-02-01T00:00:00+00:00")
        mock_item_search.return_value = [undated, jan, blank, mar, feb]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=3,
        )
        assert result["item_krefs"] == [mar.kref.uri, feb.kref.uri, jan.kref.uri]
        assert result["created_at"] == [
            "2026-03-01T18:00:00+09:00",
            "2026-02-01T00:00:00+00:00",
            "2026-01-01T00:00:00Z",
        ]

        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=10,
        )
        assert len(result["created_at"]) == len(result["revision_krefs"]) == 5
        assert result["item_krefs"][3:] == sorted([undated.kref.uri, blank.kref.uri])
        assert result["created_at"][3:] == [None, None]

    # -- (e) aliases and normalization -------------------------------------

    @pytest.mark.parametrize(
        "mode", ["latest", "newest", "recent", "most_recent", "  LATEST ", "Newest\n", "RECENT"],
    )
    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.search')
    def test_alias_modes_behave_as_latest(
        self, mock_search, mock_configure, mock_get_project, mode,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        older = self._item("older", "2026-01-01T00:00:00+00:00")
        newer = self._item("newer", "2026-02-01T00:00:00+00:00")
        mock_search.return_value = [self._hit(older, 0.9), self._hit(newer, 0.1)]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", mode=mode,
        )

        assert result["item_krefs"] == [newer.kref.uri, older.kref.uri]
        assert "created_at" in result

    # -- (f) search mode and mode-less callers are unchanged ---------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_search_mode_and_modeless_callers_keep_relevance_order(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_item_search.return_value = []
        best = self._item("best", "2026-01-01T00:00:00+00:00")
        newest = self._item("newest", "2026-03-01T00:00:00+00:00")
        mock_search.return_value = [self._hit(newest, 0.4), self._hit(best, 0.9)]
        expected = {
            "item_krefs": [best.kref.uri, newest.kref.uri],
            "revision_krefs": [
                best.returned_rev.kref.uri, newest.returned_rev.kref.uri,
            ],
            "spaces_used": ["CognitiveMemory/facts"],
            "scores": [0.9, 0.4],
        }

        from kumiho.mcp_server import TOOL_HANDLERS, tool_memory_retrieve
        assert tool_memory_retrieve(
            project="CognitiveMemory", query="anything", mode="search",
        ) == expected
        # kumiho-memory's recall passes no mode; words in the query must not
        # switch it to date order.
        assert tool_memory_retrieve(
            project="CognitiveMemory", query="what is the latest recent newest thing",
        ) == expected
        assert tool_memory_retrieve(
            project="CognitiveMemory", query="the most recent update", mode="",
        ) == expected
        # MCP dispatch without a mode argument.
        assert TOOL_HANDLERS["kumiho_memory_retrieve"](
            {"query": "latest news"},
        ) == expected

    # -- (g) the no-query window is bounded --------------------------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_empty_query_resolves_at_most_the_window(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """457 items (the production incident size): no modified_at from the
        server means no early stop, so the cap is what binds."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        items = [
            self._item(
                f"note-{i}", f"2026-05-{(i % 28) + 1:02d}T{i % 24:02d}:00:00+00:00",
                created_at=f"2026-05-{(i % 28) + 1:02d}T{i % 24:02d}:00:00+00:00",
            )
            for i in range(457)
        ]
        mock_item_search.return_value = items

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=5,
            memory_types=["never-matches"],
        )
        assert sum(item.resolved for item in items) <= max(5 * 4, 20)
        assert result["item_krefs"] == []

        for item in items:
            item.resolved = 0
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=5,
        )
        assert sum(item.resolved for item in items) <= max(5 * 4, 20)
        assert len(result["revision_krefs"]) == 5

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_modified_at_window_finds_old_restacked_item_and_stops_early(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        """Item created_at alone would window 20 newer-created items and
        miss the one old item that received today's stacked revision."""
        mock_get_project.return_value = MockProject("CognitiveMemory")
        items = []
        for i in range(457):
            stamp = f"2026-05-01T00:{i // 60:02d}:{i % 60:02d}+00:00"
            items.append(self._item(
                f"note-{i:03d}", stamp, created_at=stamp, modified_at=stamp,
            ))
        restacked = self._item(
            "ancient", "2026-09-01T00:00:00+00:00",
            created_at="2024-01-01T00:00:00+00:00",
            modified_at="2026-09-01T00:00:00+00:00",
        )
        mock_item_search.return_value = items + [restacked]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=5,
        )

        assert result["item_krefs"][0] == restacked.kref.uri
        assert result["item_krefs"][1:] == [items[i].kref.uri for i in (456, 455, 454, 453)]
        resolved = sum(item.resolved for item in items + [restacked])
        assert resolved == 5, f"expected an early stop at limit, resolved {resolved}"

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    def test_untrustworthy_modified_at_disables_early_stop(
        self, mock_item_search, mock_configure, mock_get_project,
    ):
        """A server whose modified_at never moves past created_at is not an
        upper bound: once a resolved revision proves it, keep walking."""
        mock_get_project.return_value = MockProject("CognitiveMemory")

        def frozen(name, day, rev_created_at):
            stamp = f"2026-06-{day:02d}T00:00:00+00:00"
            return self._item(name, rev_created_at, created_at=stamp, modified_at=stamp)

        n1 = frozen("n1", 5, "2026-06-05T00:00:00+00:00")
        proof = frozen("proof", 4, "2026-09-01T00:00:00+00:00")
        n2 = frozen("n2", 3, "2026-06-03T00:00:00+00:00")
        hidden = frozen("hidden", 1, "2026-08-01T00:00:00+00:00")
        mock_item_search.return_value = [n1, proof, n2, hidden]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", limit=2,
        )

        assert result["item_krefs"] == [proof.kref.uri, hidden.kref.uri]

    # -- bundles ------------------------------------------------------------

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.get_item')
    @patch('kumiho.get_bundle')
    @patch('kumiho.item_search')
    def test_bundle_members_are_date_ordered(
        self, mock_item_search, mock_get_bundle, mock_get_item,
        mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        older = self._item("bundled-older", "2026-01-01T00:00:00+00:00")
        newer = self._item("bundled-newer", "2026-02-01T00:00:00+00:00")
        by_kref = {older.kref.uri: older, newer.kref.uri: newer}
        bundle_item = MockItem("kref://CognitiveMemory/facts/project-x.bundle")
        mock_item_search.side_effect = (
            lambda context_filter="", name_filter="", kind_filter="":
            [bundle_item] if kind_filter == "bundle" else []
        )
        members = []
        for uri in (older.kref.uri, newer.kref.uri):
            member = MagicMock()
            member.item_kref.uri = uri
            members.append(member)
        mock_get_bundle.return_value.get_members.return_value = members
        mock_get_item.side_effect = lambda uri: by_kref[uri]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="latest", bundle_names=["project-x"],
        )

        assert result["item_krefs"] == [newer.kref.uri, older.kref.uri]
        assert result["created_at"] == [
            "2026-02-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00",
        ]


def _memory_item(path, created_at="2026-01-01T00:00:00+00:00", mem_type=None):
    """A memory item at ``kref://<path>.conversation`` whose published
    revision counts ``resolved`` calls."""
    item = MockItem(f"kref://{path}.conversation")
    item.kind = "conversation"
    item.created_at = created_at
    # Item.space is the kref's space WITHOUT the project, as a str.
    item.space = "/".join(path.split("/")[1:-1])
    item.resolved = 0
    rev = MockRevision(f"{item.kref.uri}?r=1")
    rev.metadata = {"memory_type": mem_type} if mem_type else {}
    item.returned_rev = rev

    def get_revision_by_tag(tag, _item=item, _rev=rev):
        if tag == "published":
            _item.resolved += 1
            return _rev
        return None

    item.get_revision_by_tag = get_revision_by_tag
    return item


def _search_hit(item, score):
    hit = MagicMock()
    hit.item = item
    hit.score = score
    return hit


class TestMemoryRetrieveSpacesUsed:
    """spaces_used was never filled from search hits: the loop read
    ``sr.item.space.path``, but ``Item.space`` is a ``str``, so the
    AttributeError was swallowed after each result had been appended."""

    def test_kref_space_context_is_project_prefixed(self):
        from kumiho.mcp_server import _kref_space_context
        assert _kref_space_context(
            "kref://CognitiveMemory/personal/prefs.conversation",
        ) == "CognitiveMemory/personal"
        assert _kref_space_context(
            "kref://CognitiveMemory/work/infra/deploy.conversation?r=3",
        ) == "CognitiveMemory/work/infra"
        assert _kref_space_context(
            "kref://CognitiveMemory/root-note.conversation",
        ) == "CognitiveMemory"

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_search_hits_populate_deduped_project_prefixed_spaces(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_item_search.return_value = []
        personal_a = _memory_item("CognitiveMemory/personal/a")
        work = _memory_item("CognitiveMemory/work/infra/b")
        personal_c = _memory_item("CognitiveMemory/personal/c")
        cut = _memory_item("CognitiveMemory/elsewhere/d")
        mock_search.return_value = [
            _search_hit(personal_a, 0.9), _search_hit(work, 0.8),
            _search_hit(personal_c, 0.7), _search_hit(cut, 0.1),
        ]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=3,
        )

        assert result["item_krefs"] == [
            personal_a.kref.uri, work.kref.uri, personal_c.kref.uri,
        ]
        # Deduped, in result order, and not index-aligned with the results.
        # The hit cut by `limit` contributes nothing.
        assert result["spaces_used"] == [
            "CognitiveMemory/personal", "CognitiveMemory/work/infra",
        ]

        # Both modes resolve the cut hit as a candidate but report only the
        # spaces of what they return.  Equal revision dates here, so latest
        # falls back to score order.
        assert cut.resolved == 1
        cut.resolved = 0
        latest = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", limit=3, mode="latest",
        )
        assert cut.resolved == 1
        assert latest["spaces_used"] == [
            "CognitiveMemory/personal", "CognitiveMemory/work/infra",
        ]

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.search')
    def test_unrolled_search_hits_populate_spaces_used(
        self, mock_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        stacked = _memory_item("CognitiveMemory/decisions/auth")
        revisions = [
            MockRevision(f"{stacked.kref.uri}?r={n}", number=n) for n in (1, 2)
        ]
        stacked.get_revisions = lambda: revisions
        single = _memory_item("CognitiveMemory/facts/db")
        single.get_revisions = lambda: [single.returned_rev]
        mock_search.return_value = [_search_hit(stacked, 0.9), _search_hit(single, 0.5)]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="anything", unroll_revisions=True,
        )

        assert result["revision_krefs"] == [
            revisions[0].kref.uri, revisions[1].kref.uri, single.returned_rev.kref.uri,
        ]
        assert result["spaces_used"] == [
            "CognitiveMemory/decisions", "CognitiveMemory/facts",
        ]

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_listing_fallback_keeps_reporting_the_scope_context(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        mock_search.return_value = []
        mock_item_search.return_value = [_memory_item("CognitiveMemory/personal/x")]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="nothing matches", space_paths=["personal"],
        )
        assert result["spaces_used"] == ["CognitiveMemory/personal"]


class TestMemoryRetrieveFirstMode:
    """mode="first" listed the whole project and ignored both space_paths
    and the query — and auto-detect only selects it when a query is present."""

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_no_query_walks_the_project_oldest_first_as_before(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        newer = _memory_item("CognitiveMemory/personal/newer", "2026-03-01T00:00:00+00:00")
        oldest = _memory_item("CognitiveMemory/work/oldest", "2025-01-01T00:00:00+00:00")
        middle = _memory_item("CognitiveMemory/personal/middle", "2026-02-01T00:00:00+00:00")
        mock_item_search.return_value = [newer, oldest, middle]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(project="CognitiveMemory", mode="first")

        assert result == {
            "item_krefs": [oldest.kref.uri],
            "revision_krefs": [oldest.returned_rev.kref.uri],
            "spaces_used": ["CognitiveMemory/work"],
        }
        mock_search.assert_not_called()
        mock_item_search.assert_called_once_with(
            context_filter="CognitiveMemory", name_filter="",
            kind_filter="conversation",
        )
        # Stops at the first passing item.
        assert (newer.resolved, oldest.resolved, middle.resolved) == (0, 1, 0)

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_space_paths_stay_inside_the_space(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        outside_oldest = _memory_item("CognitiveMemory/work/ancient", "2024-01-01T00:00:00+00:00")
        inside_old = _memory_item("CognitiveMemory/personal/old", "2025-06-01T00:00:00+00:00")
        inside_new = _memory_item("CognitiveMemory/personal/new", "2026-06-01T00:00:00+00:00")
        contexts = []

        def item_search(context_filter="", name_filter="", kind_filter=""):
            contexts.append(context_filter)
            if context_filter == "CognitiveMemory/personal":
                return [inside_new, inside_old]
            return [inside_new, inside_old, outside_oldest]

        mock_item_search.side_effect = item_search

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="first", space_paths=["personal"],
        )
        assert result["item_krefs"] == [inside_old.kref.uri]
        assert result["spaces_used"] == ["CognitiveMemory/personal"]
        assert contexts == ["CognitiveMemory/personal"]

        # Nothing in scope passes: empty, never the older out-of-scope item.
        contexts.clear()
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="first", space_paths=["personal"],
            memory_types=["decision"],
        )
        assert result == {"item_krefs": [], "revision_krefs": [], "spaces_used": []}
        assert contexts == ["CognitiveMemory/personal"]

        # With a query the relevance search is scoped the same way.
        mock_search.return_value = [_search_hit(inside_new, 0.9)]
        contexts.clear()
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="the first thing", mode="first",
            space_paths=["personal"],
        )
        assert {c.kwargs["context"] for c in mock_search.call_args_list} == {
            "CognitiveMemory/personal"
        }
        assert result["item_krefs"] == [inside_new.kref.uri]
        assert contexts == []

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_query_returns_oldest_relevant_match_not_oldest_item(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        unrelated_oldest = _memory_item("CognitiveMemory/work/ancient", "2024-01-01T00:00:00+00:00")
        best_newer = _memory_item("CognitiveMemory/auth/jwt", "2026-05-01T00:00:00+00:00")
        weaker_older = _memory_item("CognitiveMemory/auth/sessions", "2025-03-01T00:00:00+00:00")
        mock_item_search.return_value = [unrelated_oldest, best_newer, weaker_older]
        hits = [_search_hit(best_newer, 0.9), _search_hit(weaker_older, 0.4)]
        # Hits past the widened pool (max(limit * 4, 20)) are never resolved.
        beyond = [
            _search_hit(_memory_item(f"CognitiveMemory/auth/far-{i}", "2020-01-01T00:00:00+00:00"), 0.01)
            for i in range(25)
        ]
        mock_search.return_value = hits + [
            _search_hit(_memory_item(f"CognitiveMemory/auth/mid-{i}", "2026-08-01T00:00:00+00:00"), 0.3)
            for i in range(18)
        ] + beyond

        from kumiho.mcp_server import tool_memory_retrieve
        # Auto-detect: no mode, a query containing "first".
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="first auth decision", mode="",
        )

        assert result == {
            "item_krefs": [weaker_older.kref.uri],
            "revision_krefs": [weaker_older.returned_rev.kref.uri],
            "spaces_used": ["CognitiveMemory/auth"],
        }
        assert mock_search.call_args.args[0] == "first auth decision"
        mock_item_search.assert_not_called()
        assert all(hit.item.resolved == 0 for hit in beyond)
        assert best_newer.resolved == 0  # stopped at the oldest passing

    @patch('kumiho.get_project')
    @patch('kumiho.auto_configure_from_discovery')
    @patch('kumiho.item_search')
    @patch('kumiho.search')
    def test_memory_types_filters_query_and_listing_paths(
        self, mock_search, mock_item_search, mock_configure, mock_get_project,
    ):
        mock_get_project.return_value = MockProject("CognitiveMemory")
        old_fact = _memory_item("CognitiveMemory/auth/fact", "2025-01-01T00:00:00+00:00", "fact")
        new_decision = _memory_item("CognitiveMemory/auth/decision", "2026-01-01T00:00:00+00:00", "decision")
        mock_search.return_value = [_search_hit(old_fact, 0.9), _search_hit(new_decision, 0.8)]
        listed_decision = _memory_item("CognitiveMemory/misc/decision", "2024-01-01T00:00:00+00:00", "decision")
        mock_item_search.return_value = [old_fact, listed_decision]

        from kumiho.mcp_server import tool_memory_retrieve
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="auth", mode="first",
            memory_types=["decision"],
        )
        assert result["item_krefs"] == [new_decision.kref.uri]
        mock_item_search.assert_not_called()

        # No relevant hit passes: the scoped listing, like search and latest.
        result = tool_memory_retrieve(
            project="CognitiveMemory", query="auth", mode="first",
            memory_types=["preference"],
        )
        assert result == {"item_krefs": [], "revision_krefs": [], "spaces_used": []}

        # A revision-less item cannot satisfy a type filter.
        bare = _memory_item("CognitiveMemory/misc/bare", "2023-01-01T00:00:00+00:00")
        bare.get_revision_by_tag = lambda tag: None
        mock_item_search.return_value = [bare, listed_decision]
        result = tool_memory_retrieve(
            project="CognitiveMemory", mode="first", memory_types=["decision"],
        )
        assert result["item_krefs"] == [listed_decision.kref.uri]
        # ...but without a filter it is still returned, as before.
        result = tool_memory_retrieve(project="CognitiveMemory", mode="first")
        assert result == {
            "item_krefs": [bare.kref.uri], "revision_krefs": [],
            "spaces_used": ["CognitiveMemory/misc"],
        }


class TestSpaceRegistry:
    """Resolve-or-create: hint-derived spaces unify with existing ones."""

    def setup_method(self):
        from kumiho import mcp_server
        mcp_server._space_registry_cache.clear()

    class _FakeSpace:
        def __init__(self, path):
            self.path = path
            self.attributes = {}

        def get_attribute(self, key):
            return self.attributes.get(key)

        def set_attribute(self, key, value):
            self.attributes[key] = value
            return True

    class _FakeProject:
        name = "CognitiveMemory"

        def __init__(self, paths):
            self.spaces = {p: TestSpaceRegistry._FakeSpace(p) for p in paths}

        def get_spaces(self, recursive=False):
            return list(self.spaces.values())

        def get_space(self, path):
            return self.spaces[path]

    def test_stem_slug_unifies_plural_and_gerund(self):
        from kumiho.mcp_server import _stem_slug
        assert _stem_slug("benchmarks") == _stem_slug("benchmarking") == "benchmark"
        assert _stem_slug("notes") == "note"
        # Short stems are left alone — failing to unify is the safe direction.
        assert _stem_slug("as") == "as"
        assert _stem_slug("ing") == "ing"

    def test_exact_match_returns_existing(self):
        from kumiho.mcp_server import _resolve_space_hint_path
        project = self._FakeProject(["/CognitiveMemory/benchmark"])
        resolved = _resolve_space_hint_path(project, "benchmark")
        assert resolved == "/CognitiveMemory/benchmark"

    def test_stem_match_off_by_default_does_not_unify(self, monkeypatch):
        # Without the opt-in flag, only exact matches unify — stem matching
        # is too false-merge-prone to be a default.
        monkeypatch.delenv("KUMIHO_MEMORY_SPACE_STEM_MATCH", raising=False)
        from kumiho.mcp_server import _resolve_space_hint_path
        project = self._FakeProject(["/CognitiveMemory/benchmark"])
        resolved = _resolve_space_hint_path(project, "benchmarking")
        assert resolved == "/CognitiveMemory/benchmarking"

    def test_stem_match_unifies_and_records_alias_when_enabled(self, monkeypatch):
        monkeypatch.setenv("KUMIHO_MEMORY_SPACE_STEM_MATCH", "1")
        from kumiho.mcp_server import _resolve_space_hint_path
        project = self._FakeProject(["/CognitiveMemory/benchmark"])
        resolved = _resolve_space_hint_path(project, "benchmarking")
        assert resolved == "/CognitiveMemory/benchmark"
        aliases = project.spaces["/CognitiveMemory/benchmark"].attributes
        assert "benchmarking" in aliases.get("memory_aliases", "")

    def test_no_match_returns_normalized_input(self):
        from kumiho.mcp_server import _resolve_space_hint_path
        project = self._FakeProject(["/CognitiveMemory/travel"])
        resolved = _resolve_space_hint_path(project, "quantum-computing")
        assert resolved == "/CognitiveMemory/quantum-computing"

    def test_different_parents_do_not_unify(self, monkeypatch):
        monkeypatch.setenv("KUMIHO_MEMORY_SPACE_STEM_MATCH", "1")
        from kumiho.mcp_server import _resolve_space_hint_path
        project = self._FakeProject(["/CognitiveMemory/work/benchmark"])
        resolved = _resolve_space_hint_path(project, "benchmarks")
        assert resolved == "/CognitiveMemory/benchmarks"

    def test_kill_switch_env(self, monkeypatch):
        from kumiho.mcp_server import _space_registry_enabled
        monkeypatch.setenv("KUMIHO_MEMORY_SPACE_REGISTRY", "0")
        assert not _space_registry_enabled()
        monkeypatch.setenv("KUMIHO_MEMORY_SPACE_REGISTRY", "1")
        assert _space_registry_enabled()

    def test_listing_failure_falls_back_to_input(self):
        from kumiho.mcp_server import _resolve_space_hint_path

        class _Broken:
            name = "CognitiveMemory"

            def get_spaces(self, recursive=False):
                raise RuntimeError("registry down")

        resolved = _resolve_space_hint_path(_Broken(), "benchmarks")
        assert resolved == "/CognitiveMemory/benchmarks"


class TestMemoryKindVocabulary:
    """The store tool enforces the closed memory-kind vocabulary."""

    def setup_method(self):
        from kumiho import mcp_server
        mcp_server._project_cache.clear()
        mcp_server._space_registry_cache.clear()

    def test_default_kinds_are_the_agreed_vocabulary(self):
        from kumiho.mcp_server import DEFAULT_MEMORY_KINDS
        assert DEFAULT_MEMORY_KINDS == (
            "conversation", "skill", "space-profile", "entity", "decision",
        )

    def test_store_schema_advertises_kinds_without_strict_enum(self):
        # No `enum`: policies can widen the vocabulary at runtime, so a
        # strict MCP client must not be blocked from sending a widened kind.
        from kumiho.mcp_server import TOOLS, DEFAULT_MEMORY_KINDS
        store_tool = next(t for t in TOOLS if t["name"] == "kumiho_memory_store")
        prop = store_tool["inputSchema"]["properties"]["memory_item_kind"]
        assert "enum" not in prop
        for kind in DEFAULT_MEMORY_KINDS:
            assert kind in prop["description"]

    @patch('kumiho.mcp_server._write_memory_artifact', return_value="")
    @patch('kumiho.mcp_server._get_or_create_item')
    @patch('kumiho.mcp_server._find_similar_item', return_value=(None, 0.0, 0.0, 0.0))
    @patch('kumiho.mcp_server._ensure_space_path', return_value="facts")
    @patch("kumiho.get_project")
    @patch("kumiho.auto_configure_from_discovery")
    def test_unknown_kind_warns_but_accepts(
        self, mock_configure, mock_get_project, mock_ensure_space,
        mock_find_similar, mock_get_item, mock_artifact, caplog,
    ):
        import logging
        mock_get_project.return_value = MockProject("CognitiveMemory")
        item = MockItem("kref://CognitiveMemory/facts/note.vibes")
        rev = MockRevision(f"{item.kref.uri}?r=1")
        rev.tag = lambda tag: None
        item.create_revision = lambda metadata=None: rev
        mock_get_item.return_value = item

        from kumiho.mcp_server import tool_memory_store
        with caplog.at_level(logging.WARNING):
            result = tool_memory_store(
                project="CognitiveMemory", space_path="facts",
                user_text="hello", memory_item_kind="vibes",
            )
        # Accepted (no kind error), but a drift warning was logged.
        assert "Unknown memory_item_kind" not in str(result.get("error", ""))
        assert any("recommended vocabulary" in r.message for r in caplog.records)

    @patch('kumiho.mcp_server._write_memory_artifact', return_value="")
    @patch('kumiho.mcp_server._get_or_create_item')
    @patch('kumiho.mcp_server._find_similar_item', return_value=(None, 0.0, 0.0, 0.0))
    @patch('kumiho.mcp_server._ensure_space_path', return_value="facts")
    @patch("kumiho.get_revision")
    @patch("kumiho.get_project")
    @patch("kumiho.auto_configure_from_discovery")
    def test_string_memory_kinds_policy_rejected_not_substring_matched(
        self, mock_configure, mock_get_project, mock_get_revision,
        mock_ensure_space, mock_find_similar, mock_get_item, mock_artifact, caplog,
    ):
        # A string (not list) `memory_kinds` policy must be rejected, not left to
        # degrade `kind not in allowed_kinds` into a substring test that would
        # wrongly accept "con" as a member of "conversation,entity".
        import json
        import logging
        mock_get_project.return_value = MockProject("CognitiveMemory")
        item = MockItem("kref://CognitiveMemory/facts/note.con")
        rev = MockRevision(f"{item.kref.uri}?r=1")
        rev.tag = lambda tag: None
        item.create_revision = lambda metadata=None: rev
        mock_get_item.return_value = item
        policy_rev = MockRevision("kref://CognitiveMemory/policies/p.policy?r=1")
        policy_rev.metadata = {"policy": json.dumps({"memory_kinds": "conversation,entity"})}
        mock_get_revision.return_value = policy_rev

        from kumiho.mcp_server import tool_memory_store
        with caplog.at_level(logging.WARNING):
            result = tool_memory_store(
                project="CognitiveMemory", space_path="facts", user_text="hi",
                memory_item_kind="con",  # a substring of the malformed policy string
                policy_kref="kref://CognitiveMemory/policies/p.policy?r=1",
            )
        msgs = " ".join(r.message for r in caplog.records)
        assert "must be a list of strings" in msgs   # malformed override rejected
        assert "recommended vocabulary" in msgs       # "con" no longer substring-accepted
        assert "Failed to load policy_kref" not in str(result.get("error", ""))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ---------------------------------------------------------------------------
# Tests — tool_memory_store_batch (bulk write path)
# ---------------------------------------------------------------------------


def test_tool_memory_store_batch_builds_rows_and_finalizes():
    """Resolves each capture, batches the writes, and still stamps event_date +
    tags per row (parity with the single tool_memory_store path)."""
    from kumiho.mcp_server import tool_memory_store_batch

    captured = {}
    tagged = []

    def make_rev(i):
        rev = MagicMock()
        rev.kref.uri = f"kref://CognitiveMemory/work/x/mem{i}.conversation?r=1"
        rev.tag.side_effect = lambda t, _i=i: tagged.append((_i, t))
        return rev

    def fake_batch(rows, idempotency_prefix=""):
        captured["rows"] = rows
        return ([make_rev(i) for i in range(len(rows))], [])

    with patch("kumiho.mcp_server._ensure_configured", return_value=True), \
            patch("kumiho.mcp_server._get_project_cached", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.mcp_server._ensure_space_path", return_value="/CognitiveMemory/work/x"), \
            patch("kumiho.mcp_server._find_similar_item", return_value=(None, 0.0, 0.0, 0.0)), \
            patch("kumiho.mcp_server._write_memory_artifact", return_value=""), \
            patch("kumiho.mcp_server._get_or_create_bundle", return_value=MagicMock()), \
            patch("kumiho.get_item", return_value=MagicMock()), \
            patch("kumiho.batch_create_revisions", side_effect=fake_batch):
        out = tool_memory_store_batch(
            captures=[
                {"type": "decision", "title": "Chose bge-m3",
                 "content": "because keyless", "tags": ["published"],
                 "metadata": {"event_date": "2026-03-14"}},
                {"type": "fact", "title": "Founded 2019",
                 "content": "founded then", "metadata": {"event_date": "2019"}},
            ],
            project="CognitiveMemory", space_path="work/x",
        )

    rows = captured["rows"]
    assert len(rows) == 2
    # New items get a hash-named kref under the resolved space, correct kind.
    assert rows[0]["item_kref"].startswith("kref://CognitiveMemory/work/x/")
    assert rows[0]["item_kref"].endswith(".conversation")
    # Metadata carries the validated event_date + memory_type (stringified).
    assert rows[0]["metadata"]["event_date"] == "2026-03-14"
    assert rows[0]["metadata"]["memory_type"] == "decision"
    assert rows[1]["metadata"]["event_date"] == "2019"
    # No embedding_text override -> the server embeds from concatenated metadata,
    # exactly like the single tool_memory_store path (parity).
    assert "embedding_text" not in rows[0]
    # The "published" tag is applied to every created revision.
    assert (0, "published") in tagged and (1, "published") in tagged
    assert len(out["stored_krefs"]) == 2
    assert out["stacked"] == 0


def test_tool_memory_store_batch_stacks_on_similar_item():
    """When a similar item exists, the row targets that item's kref (stack)."""
    from kumiho.mcp_server import tool_memory_store_batch

    existing = MagicMock()
    existing.kref.uri = "kref://CognitiveMemory/x/existing.conversation"

    def fake_batch(rows, idempotency_prefix=""):
        rev = MagicMock()
        rev.kref.uri = "kref://CognitiveMemory/x/existing.conversation?r=2"
        return ([rev], [])

    with patch("kumiho.mcp_server._ensure_configured", return_value=True), \
            patch("kumiho.mcp_server._get_project_cached", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.mcp_server._ensure_space_path", return_value="/CognitiveMemory/x"), \
            patch("kumiho.mcp_server._find_similar_item", return_value=(existing, 0.9, 0.4, 0.5)), \
            patch("kumiho.mcp_server._write_memory_artifact", return_value=""), \
            patch("kumiho.mcp_server._get_or_create_bundle", return_value=MagicMock()), \
            patch("kumiho.batch_create_revisions", side_effect=fake_batch) as mock_batch:
        out = tool_memory_store_batch(
            captures=[{"type": "fact", "title": "dup", "content": "same thing"}],
            project="CognitiveMemory", space_path="x",
        )

    rows = mock_batch.call_args[0][0]
    assert rows[0]["item_kref"] == "kref://CognitiveMemory/x/existing.conversation"
    assert out["stacked"] == 1
    assert len(out["stored_krefs"]) == 1


def test_tool_memory_store_batch_chunks_over_200_rows():
    """>200 captures are split into <=200-row batch calls (the server row cap),
    with offset-suffixed idempotency prefixes and aligned results."""
    from kumiho.mcp_server import tool_memory_store_batch

    calls = []

    def fake_batch(rows, idempotency_prefix=""):
        calls.append((len(rows), idempotency_prefix))
        revs = []
        for i in range(len(rows)):
            rev = MagicMock()
            rev.kref.uri = f"kref://x/m{len(calls)}_{i}.conversation?r=1"
            revs.append(rev)
        return (revs, [])

    caps = [{"type": "fact", "title": f"c{i}", "content": f"content {i}"} for i in range(250)]
    with patch("kumiho.mcp_server._ensure_configured", return_value=True), \
            patch("kumiho.mcp_server._get_project_cached", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.mcp_server._ensure_space_path", return_value="/CognitiveMemory/x"), \
            patch("kumiho.mcp_server._find_similar_item", return_value=(None, 0.0, 0.0, 0.0)), \
            patch("kumiho.mcp_server._write_memory_artifact", return_value=""), \
            patch("kumiho.mcp_server._get_or_create_bundle", return_value=MagicMock()), \
            patch("kumiho.get_item", return_value=MagicMock()), \
            patch("kumiho.batch_create_revisions", side_effect=fake_batch):
        out = tool_memory_store_batch(
            captures=caps, project="CognitiveMemory",
            space_path="x", idempotency_prefix="run0",
        )

    # Two chunks: 200 + 50, offset-suffixed prefixes, all rows accounted for.
    assert [n for n, _ in calls] == [200, 50]
    assert [p for _, p in calls] == ["run0:0", "run0:200"]
    assert len(out["stored_krefs"]) == 250


# ---------------------------------------------------------------------------
# Tests — keep_published: moving an existing "published" tag forward (0.13.2)
# ---------------------------------------------------------------------------
#
# "published" is an approval/immutability marker (docs/concepts.md), so the
# store never stamps it on its own. The defect it leaves is narrow: when a
# store STACKS onto an item whose current revision is published, and the new
# revision carries caller tags (reflect passes each capture's classification
# tags), "published" stays on the OLD revision. Every recall path resolves
# ``get_revision_by_tag("published") or get_revision_by_tag("latest")``, so
# the stacked update is invisible. ``keep_published=True`` is the opt-in that
# carries the tag forward; everything else is unchanged.


CLASSIFICATION_TAGS = ["preference", "color", "personal"]


class _TaggedRevision(MockRevision):
    """A MockRevision under the server's two tag rules.

    * A tag lives on one revision per item, so tagging MOVES it
      (``test_manual_tag_uniqueness`` in tests/test_tagging_logic.py).
    * A published revision is frozen and rejects tags applied to it
      afterwards (``test_published_revision_immutability``; the server
      answers PERMISSION_DENIED — see the note in ``kumiho/client.py``).
    """

    def __init__(self, item, number):
        super().__init__(f"{item.kref.uri}?r={number}", number=number)
        self.item = item
        self.tags = {"latest"}
        self.created_at = f"2026-09-{number:02d}T00:00:00+00:00"

    def tag(self, tag):
        self.item.tag_calls.append((self.number, tag))
        if tag in self.item.failing_tags:
            raise RuntimeError(f"tag RPC failed for {tag!r}")
        if self.published:
            raise RuntimeError("PERMISSION_DENIED: revision is published and immutable")
        for other in self.item.revisions:  # tags are exclusive per item
            other.tags.discard(tag)
            other.published = "published" in other.tags
        self.tags.add(tag)
        self.published = "published" in self.tags

    def create_artifact(self, name, location):
        return MagicMock()

    def create_edge(self, target, edge_type):
        return MagicMock()


class _TaggedItem(MockItem):
    """A MockItem that stacks revisions and resolves tags like the server."""

    def __init__(self, path="CognitiveMemory/personal/favorite-color-3f9a"):
        super().__init__(f"kref://{path}.conversation")
        self.kind = "conversation"
        self.item_name = path.rsplit("/", 1)[-1]
        self.space = "/".join(path.split("/")[1:-1])
        self.revisions = []
        self.tag_calls = []
        self.failing_tags = set()

    def create_revision(self, metadata=None):
        revision = _TaggedRevision(self, len(self.revisions) + 1)
        revision.metadata = dict(metadata or {})
        for prior in self.revisions:
            prior.tags.discard("latest")
            prior.latest = False
        self.revisions.append(revision)
        return revision

    def get_revision_by_tag(self, tag):
        return next((r for r in self.revisions if tag in r.tags), None)

    def get_revisions(self):
        return list(self.revisions)


def _store_on(item, *, stacks, **kwargs):
    """Run the real ``tool_memory_store`` against *item*, graph writes stubbed.

    ``stacks`` decides what the similarity gate returns; the gate itself is
    covered by test_mcp_revision_stacking.py and is not under test here.
    """
    similar = (item, 0.81, 0.2, 0.3) if stacks else (None, 0.0, 0.0, 0.0)
    arguments = {
        "project": "CognitiveMemory", "space_path": "personal",
        "memory_type": "preference", "user_text": "u",
    }
    arguments.update(kwargs)
    with patch("kumiho.mcp_server._ensure_configured", return_value=True), \
            patch("kumiho.mcp_server._get_project_cached", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.mcp_server._ensure_space_path", return_value="/CognitiveMemory/personal"), \
            patch("kumiho.mcp_server._find_similar_item", return_value=similar), \
            patch("kumiho.mcp_server._get_or_create_item", return_value=item), \
            patch("kumiho.mcp_server._write_memory_artifact", return_value=""), \
            patch("kumiho.mcp_server._get_or_create_bundle", return_value=MagicMock()):
        from kumiho.mcp_server import tool_memory_store
        return tool_memory_store(**arguments)


def _recall_revision_krefs(item, query):
    """Default retrieve (search mode) for a query that hits *item*."""
    with patch("kumiho.auto_configure_from_discovery"), \
            patch("kumiho.get_project", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.item_search", return_value=[]), \
            patch("kumiho.search", return_value=[_search_hit(item, 0.7)]):
        from kumiho.mcp_server import tool_memory_retrieve
        return tool_memory_retrieve(
            project="CognitiveMemory", query=query
        )["revision_krefs"]


class TestMemoryStoreKeepPublished:

    def test_stacked_correction_takes_published_from_the_revision_it_supersedes(self):
        """The opt-in case: blue was published, black was captured with tags."""
        item = _TaggedItem()
        _store_on(
            item, stacks=False, title="Favorite color is blue",
            summary="The user's favorite color is blue.",
        )
        blue = item.revisions[0]
        assert blue.published
        assert _recall_revision_krefs(item, "favorite color") == [blue.kref.uri]

        result = _store_on(
            item, stacks=True, title="Favorite color is black",
            summary="Correction: the user's favorite color is black, not blue.",
            tags=CLASSIFICATION_TAGS, keep_published=True,
        )

        black = item.revisions[1]
        assert result["stacked"] is True
        assert result["revision_kref"] == black.kref.uri
        assert result["previous_revision_kref"] == blue.kref.uri
        # Caller tags first, "published" last, and the tag moved off blue.
        assert item.tag_calls[1:] == [
            (2, "preference"), (2, "color"), (2, "personal"), (2, "published"),
        ]
        assert black.tags >= {"published", *CLASSIFICATION_TAGS}
        assert not blue.published
        assert item.get_revision_by_tag("published") is black
        # ...so recall, which resolves published before latest, reads black.
        assert _recall_revision_krefs(item, "favorite color") == [black.kref.uri]

    def test_no_effect_when_the_stacked_item_had_no_published_revision(self):
        item = _TaggedItem()
        _store_on(item, stacks=False, title="t", summary="s", tags=["draft"])
        assert item.get_revision_by_tag("published") is None

        _store_on(
            item, stacks=True, title="t2", summary="s2",
            tags=["draft"], keep_published=True,
        )

        assert item.tag_calls == [(1, "draft"), (2, "draft")]
        assert not item.revisions[1].published
        assert item.get_revision_by_tag("published") is None

    def test_no_effect_on_a_new_item(self):
        """Nothing is published on the store's own initiative."""
        item = _TaggedItem()
        _store_on(
            item, stacks=False, title="t", summary="s",
            tags=CLASSIFICATION_TAGS, keep_published=True,
        )

        assert item.tag_calls == [(1, t) for t in CLASSIFICATION_TAGS]
        assert not item.revisions[0].published

    def test_untagged_new_item_keeps_the_existing_published_default(self):
        item = _TaggedItem()
        _store_on(item, stacks=False, title="t", summary="s", keep_published=True)
        assert item.tag_calls == [(1, "published")]
        assert item.revisions[0].published

    def test_default_leaves_published_on_the_old_revision(self):
        """The defect a caller must opt out of: today's behavior, unchanged."""
        item = _TaggedItem()
        _store_on(item, stacks=False, title="t", summary="s")
        blue = item.revisions[0]

        _store_on(
            item, stacks=True, title="t2", summary="s2", tags=CLASSIFICATION_TAGS,
        )

        black = item.revisions[1]
        assert item.tag_calls == [(1, "published")] + [(2, t) for t in CLASSIFICATION_TAGS]
        assert not black.published
        assert item.get_revision_by_tag("published") is blue
        assert _recall_revision_krefs(item, "favorite color") == [blue.kref.uri]

    def test_published_in_caller_tags_is_applied_once_and_last(self):
        """A published revision is frozen, so tags applied after it are lost."""
        item = _TaggedItem()
        _store_on(item, stacks=False, title="t", summary="s")

        _store_on(
            item, stacks=True, title="t2", summary="s2",
            tags=["published", "preference"], keep_published=True,
        )

        assert item.tag_calls[1:] == [(2, "preference"), (2, "published")]
        assert item.revisions[1].tags >= {"preference", "published"}

    def test_a_failing_classification_tag_does_not_block_published(self):
        item = _TaggedItem()
        _store_on(item, stacks=False, title="t", summary="s")
        item.failing_tags = {"color"}

        _store_on(
            item, stacks=True, title="t2", summary="s2",
            tags=CLASSIFICATION_TAGS, keep_published=True,
        )

        stacked = item.revisions[1]
        assert stacked.published
        assert stacked.tags == {"latest", "preference", "personal", "published"}


# -- batch path -------------------------------------------------------------


def _batch_stack_target(kref, *, published):
    item = MagicMock()
    item.kref.uri = kref
    item.get_revision_by_tag.side_effect = (
        lambda tag: MagicMock() if (published and tag == "published") else None
    )
    return item


def _run_store_batch(captures, similar, **kwargs):
    """``tool_memory_store_batch`` over stubbed writes; returns (out, tagged)."""
    from kumiho.mcp_server import tool_memory_store_batch

    tagged = []

    def fake_batch(rows, idempotency_prefix=""):
        revs = []
        for i in range(len(rows)):
            rev = MagicMock()
            rev.kref.uri = f"kref://CognitiveMemory/work/x/mem{i}.conversation?r=2"
            rev.tag.side_effect = lambda t, _i=i: tagged.append((_i, t))
            revs.append(rev)
        return (revs, [])

    with patch("kumiho.mcp_server._ensure_configured", return_value=True), \
            patch("kumiho.mcp_server._get_project_cached", return_value=MockProject("CognitiveMemory")), \
            patch("kumiho.mcp_server._ensure_space_path", return_value="/CognitiveMemory/work/x"), \
            patch("kumiho.mcp_server._find_similar_item", side_effect=similar), \
            patch("kumiho.mcp_server._write_memory_artifact", return_value=""), \
            patch("kumiho.mcp_server._get_or_create_bundle", return_value=MagicMock()), \
            patch("kumiho.get_item", return_value=MagicMock()), \
            patch("kumiho.batch_create_revisions", side_effect=fake_batch):
        out = tool_memory_store_batch(
            captures=captures, project="CognitiveMemory",
            space_path="work/x", **kwargs
        )
    return out, tagged


_BATCH_CAPTURES = [
    {"type": "preference", "title": "Favorite color is black",
     "content": "black, not blue", "tags": CLASSIFICATION_TAGS},
    {"type": "summary", "title": "draft", "content": "wip", "tags": ["draft"]},
    {"type": "fact", "title": "new", "content": "brand new"},
]


def test_tool_memory_store_batch_keep_published_moves_the_tag_forward():
    """Call-level opt-in, same three conditions as the single path."""
    on_published = _batch_stack_target(
        "kref://CognitiveMemory/work/x/color.conversation", published=True
    )
    on_unpublished = _batch_stack_target(
        "kref://CognitiveMemory/work/x/draft.conversation", published=False
    )
    out, tagged = _run_store_batch(
        _BATCH_CAPTURES,
        similar=[(on_published, 0.81, 0.2, 0.3),
                 (on_unpublished, 0.81, 0.2, 0.3),
                 (None, 0.0, 0.0, 0.0)],
        keep_published=True,
    )

    assert out["stacked"] == 2
    # Stacked onto a published revision: caller tags, then "published".
    assert [t for i, t in tagged if i == 0] == [*CLASSIFICATION_TAGS, "published"]
    # Stacked onto an item with no published revision: untouched.
    assert [t for i, t in tagged if i == 1] == ["draft"]
    # New item, untagged: the long-standing default, unchanged.
    assert [t for i, t in tagged if i == 2] == ["published"]


def test_tool_memory_store_batch_default_leaves_published_where_it_was():
    """Default False: today's behavior, and not even a tag lookup."""
    on_published = _batch_stack_target(
        "kref://CognitiveMemory/work/x/color.conversation", published=True
    )
    out, tagged = _run_store_batch(
        _BATCH_CAPTURES[:1],
        similar=[(on_published, 0.81, 0.2, 0.3)],
    )

    assert out["stacked"] == 1
    assert [t for i, t in tagged if i == 0] == CLASSIFICATION_TAGS
    assert on_published.get_revision_by_tag.call_count == 0
