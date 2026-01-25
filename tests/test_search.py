"""Tests for full-text search functionality.

This module tests:
- SearchResult dataclass behavior
- Client.search() method with mocked gRPC
- High-level kumiho.search() function
- Pagination handling for search results
- Search depth options (revision/artifact metadata)
"""

import pytest
from unittest.mock import MagicMock

import kumiho
from kumiho.base import SearchResult
import mock_helpers


# --- Unit Tests for SearchResult ---

class TestSearchResultDataclass:
    """Tests for the SearchResult dataclass."""

    def test_search_result_creation(self, mock_client):
        """Test basic SearchResult creation."""
        client, mock_stub = mock_client

        # Create a mock item
        item_pb = mock_helpers.mock_item_response(
            kref_uri="kref://project/space/hero.model",
            name="hero.model",
            item_name="hero",
            kind="model"
        )
        mock_stub.GetItem.return_value = item_pb
        item = kumiho.Item(item_pb, client)

        result = SearchResult(
            item=item,
            score=0.95,
            matched_in=["item"]
        )

        assert result.item == item
        assert result.score == 0.95
        assert result.matched_in == ["item"]

    def test_search_result_repr(self, mock_client):
        """Test SearchResult string representation."""
        client, mock_stub = mock_client

        item_pb = mock_helpers.mock_item_response(
            kref_uri="kref://project/space/hero.model",
            name="hero.model",
            item_name="hero",
            kind="model"
        )
        item = kumiho.Item(item_pb, client)

        result = SearchResult(
            item=item,
            score=0.875,
            matched_in=["item", "revision"]
        )

        repr_str = repr(result)
        assert "hero.model" in repr_str
        assert "0.875" in repr_str
        assert "item" in repr_str
        assert "revision" in repr_str

    def test_search_result_multiple_match_sources(self, mock_client):
        """Test SearchResult with matches in multiple places."""
        client, mock_stub = mock_client

        item_pb = mock_helpers.mock_item_response(
            kref_uri="kref://project/space/texture.texture",
            name="texture.texture",
            item_name="texture",
            kind="texture"
        )
        item = kumiho.Item(item_pb, client)

        result = SearchResult(
            item=item,
            score=1.2,  # Score can exceed 1.0 in Lucene
            matched_in=["item", "revision", "artifact"]
        )

        assert len(result.matched_in) == 3
        assert "item" in result.matched_in
        assert "revision" in result.matched_in
        assert "artifact" in result.matched_in


# --- Mocked Client Tests ---

class TestSearchClient:
    """Tests for the Client.search() method with mocked gRPC."""

    def test_search_basic(self, mock_client):
        """Test basic search functionality."""
        client, mock_stub = mock_client

        # Setup mock response
        result1 = mock_helpers.mock_search_result(
            kref_uri="kref://project/chars/hero.model",
            name="hero.model",
            item_name="hero",
            kind="model",
            score=0.95,
            matched_in=["item"]
        )
        result2 = mock_helpers.mock_search_result(
            kref_uri="kref://project/chars/villain.model",
            name="villain.model",
            item_name="villain",
            kind="model",
            score=0.85,
            matched_in=["item"]
        )
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=[result1, result2]
        )

        # Execute search
        results = client.search("hero villain")

        # Verify
        mock_stub.Search.assert_called_once()
        assert len(results) == 2
        assert results[0].item.name == "hero.model"
        assert results[0].score == 0.95
        assert results[1].item.name == "villain.model"
        assert results[1].score == 0.85

    def test_search_with_kind_filter(self, mock_client):
        """Test search with kind filter."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search("hero", kind_filter="model")

        # Verify the request
        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.query == "hero"
        assert request.kind_filter == "model"

    def test_search_with_context_filter(self, mock_client):
        """Test search with context filter."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search("texture", context_filter="film-project/assets")

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.query == "texture"
        assert request.context_filter == "film-project/assets"

    def test_search_include_deprecated(self, mock_client):
        """Test search with deprecated items included."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search("old_asset", include_deprecated=True)

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.include_deprecated is True

    def test_search_with_min_score(self, mock_client):
        """Test search with minimum score threshold."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search("high_quality", min_score=0.5)

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.min_score == 0.5

    def test_search_include_revision_metadata(self, mock_client):
        """Test deep search with revision metadata."""
        client, mock_stub = mock_client

        result = mock_helpers.mock_search_result(
            kref_uri="kref://project/space/approved.model",
            name="approved.model",
            item_name="approved",
            kind="model",
            score=0.9,
            matched_in=["revision"]  # Found in revision metadata
        )
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=[result]
        )

        results = client.search("approved", include_revision_metadata=True)

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.include_revision_metadata is True
        assert request.include_artifact_metadata is False
        assert results[0].matched_in == ["revision"]

    def test_search_include_artifact_metadata(self, mock_client):
        """Test deep search with artifact metadata."""
        client, mock_stub = mock_client

        result = mock_helpers.mock_search_result(
            kref_uri="kref://project/space/render.model",
            name="render.model",
            item_name="render",
            kind="model",
            score=0.8,
            matched_in=["artifact"]  # Found in artifact location/metadata
        )
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=[result]
        )

        results = client.search("final_render.fbx", include_artifact_metadata=True)

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.include_artifact_metadata is True
        assert results[0].matched_in == ["artifact"]

    def test_search_full_deep_search(self, mock_client):
        """Test search with both revision and artifact metadata."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search(
            "comprehensive",
            include_revision_metadata=True,
            include_artifact_metadata=True
        )

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.include_revision_metadata is True
        assert request.include_artifact_metadata is True

    def test_search_pagination(self, mock_client):
        """Test search with pagination."""
        client, mock_stub = mock_client

        result = mock_helpers.mock_search_result(
            kref_uri="kref://project/space/item.model",
            name="item.model",
            item_name="item",
            kind="model",
            score=0.9
        )
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=[result],
            next_cursor="offset:10",
            total_count=-1
        )

        results = client.search("query", page_size=10)

        # Verify request
        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.pagination.page_size == 10
        assert request.pagination.cursor == ""

        # Verify response has pagination info
        assert hasattr(results, 'next_cursor')
        assert results.next_cursor == "offset:10"

    def test_search_pagination_with_cursor(self, mock_client):
        """Test search continuation with cursor."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        client.search("query", page_size=10, cursor="offset:10")

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.pagination.cursor == "offset:10"

    def test_search_empty_results(self, mock_client):
        """Test search with no matching results."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        results = client.search("nonexistent_asset_xyz123")

        assert len(results) == 0

    def test_search_results_ordered_by_score(self, mock_client):
        """Test that search results maintain score ordering."""
        client, mock_stub = mock_client

        # Results should come back ordered by score (highest first)
        results_pb = [
            mock_helpers.mock_search_result(
                kref_uri="kref://p/s/best.model",
                name="best.model",
                item_name="best",
                kind="model",
                score=0.99
            ),
            mock_helpers.mock_search_result(
                kref_uri="kref://p/s/good.model",
                name="good.model",
                item_name="good",
                kind="model",
                score=0.75
            ),
            mock_helpers.mock_search_result(
                kref_uri="kref://p/s/ok.model",
                name="ok.model",
                item_name="ok",
                kind="model",
                score=0.50
            ),
        ]
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=results_pb
        )

        results = client.search("model")

        assert len(results) == 3
        assert results[0].score == 0.99
        assert results[1].score == 0.75
        assert results[2].score == 0.50


# --- High-Level API Tests ---

class TestSearchHighLevelAPI:
    """Tests for the kumiho.search() high-level function."""

    def test_kumiho_search_basic(self, mock_client):
        """Test kumiho.search() convenience function."""
        client, mock_stub = mock_client

        result = mock_helpers.mock_search_result(
            kref_uri="kref://project/space/hero.model",
            name="hero.model",
            item_name="hero",
            kind="model",
            score=0.9
        )
        mock_stub.Search.return_value = mock_helpers.mock_search_response(
            results=[result]
        )

        results = kumiho.search("hero")

        assert len(results) == 1
        assert results[0].item.name == "hero.model"

    def test_kumiho_search_with_filters(self, mock_client):
        """Test kumiho.search() with all filter options."""
        client, mock_stub = mock_client

        mock_stub.Search.return_value = mock_helpers.mock_search_response(results=[])

        kumiho.search(
            "texture",
            context="film-project",
            kind="texture",
            include_deprecated=True,
            include_revision_metadata=True,
            include_artifact_metadata=True
        )

        args, _ = mock_stub.Search.call_args
        request = args[0]
        assert request.query == "texture"
        assert request.context_filter == "film-project"
        assert request.kind_filter == "texture"
        assert request.include_deprecated is True
        assert request.include_revision_metadata is True
        assert request.include_artifact_metadata is True


# --- Fixture ---

@pytest.fixture
def mock_client(monkeypatch):
    """Pytest fixture to provide a Kumiho client with a mocked gRPC stub."""
    original_client = kumiho._default_client

    mock_stub = MagicMock()
    monkeypatch.setattr("kumiho.client.kumiho_pb2_grpc.KumihoServiceStub", lambda channel: mock_stub)

    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    kumiho.configure_default_client(client)

    yield client, mock_stub

    kumiho._default_client = original_client
