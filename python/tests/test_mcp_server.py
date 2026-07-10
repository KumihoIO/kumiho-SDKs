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
    @patch('kumiho.mcp_server._find_similar_item', return_value=None)
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
    @patch('kumiho.mcp_server._find_similar_item', return_value=None)
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
    @patch('kumiho.mcp_server._find_similar_item', return_value=None)
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
