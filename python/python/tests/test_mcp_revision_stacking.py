"""Revision stacking: does a second capture about one subject land on one item?

``kumiho_memory_reflect`` promises that a capture revisiting a topic becomes a
new *revision* of the existing item rather than a brand-new item. Issue #163
showed it never did: new item names carry a content hash, so name matching is
impossible by construction, and the whole mechanism rested on
``_find_similar_item`` gating on a fuzzy score ``>= 0.92``.

That gate was not merely strict, it was unreachable. Replaying real duplicate
pairs against a live CE graph showed an item scores only **0.72-0.83 against
its own exact title** -- the scorer's ceiling sits below the gate, so no input
could ever stack. Same-subject/different-title duplicates scored 0.58-0.68,
while unrelated items in the same space reached 0.62 in a topically
homogeneous space. Those two bands overlap, which is why the fix is two-tiered
rather than simply a lower number.

These tests mock ``kumiho.search`` -- they must never touch a server, and in
particular must never write to one.
"""

from __future__ import annotations

from typing import Any, List, Optional
from unittest.mock import patch

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

from kumiho import mcp_server


# --- Test doubles -----------------------------------------------------------


class _FakeRevision:
    def __init__(self, memory_type: str) -> None:
        self.metadata = {"memory_type": memory_type}


class _FakeKref:
    def __init__(self, uri: str) -> None:
        self.uri = uri


class _FakeItem:
    """The bare surface ``_find_similar_item`` touches on a match."""

    def __init__(self, name: str, memory_type: str = "summary") -> None:
        self.item_name = name
        self.kref = _FakeKref(f"kref://CognitiveMemory/work/{name}.conversation")
        self._memory_type = memory_type

    def get_revision_by_tag(self, tag: str) -> Optional[_FakeRevision]:
        return _FakeRevision(self._memory_type) if tag == "published" else None

    def get_revision(self, selector: str) -> _FakeRevision:
        return _FakeRevision(self._memory_type)


class _FakeSearchResult:
    def __init__(self, item: _FakeItem, score: float) -> None:
        self.item = item
        self.score = score
        self.matched_in = ["item", "revision"]


class _SearchSpy:
    """Stands in for ``kumiho.search``; records the queries it was handed."""

    def __init__(self, results: List[_FakeSearchResult]) -> None:
        self._results = results
        self.queries: List[str] = []

    def __call__(self, query: str, **kwargs: Any) -> List[_FakeSearchResult]:
        self.queries.append(query)
        return self._results


# Scores taken from the live-graph measurement described in the module
# docstring, so the constants stay tethered to observed behaviour.
SELF_MATCH_CEILING = 0.83   # an item vs. its OWN exact title, at best
DUPLICATE_SCORE = 0.60      # same subject, different title
UNRELATED_SCORE = 0.30      # different subject, same space (mixed space)


# --- The bug that issue #163 reported --------------------------------------


def test_threshold_sits_below_the_scorers_observed_ceiling() -> None:
    """The regression guard proper.

    The old 0.92 gate was above the highest score the CE fulltext scorer was
    ever observed to emit -- including an item matched against its own exact
    title -- so stacking was dead code. Whatever the threshold becomes, it
    must stay reachable.
    """
    assert mcp_server._STACK_SIMILARITY_THRESHOLD < SELF_MATCH_CEILING
    assert (
        mcp_server._STACK_TYPE_MATCH_THRESHOLD
        <= mcp_server._STACK_SIMILARITY_THRESHOLD
    )


def test_two_captures_on_one_subject_stack() -> None:
    """Different titles, same subject -> the second lands on the first's item."""
    existing = _FakeItem("kumiho-plugins-pr-64-skill-md-edge-ontology-39be818a")
    spy = _SearchSpy([_FakeSearchResult(existing, DUPLICATE_SCORE)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score = mcp_server._find_similar_item(
            "CognitiveMemory",
            "CognitiveMemory/work/kumiho-sdks",
            mcp_server._build_stack_query(
                "kumiho-plugins 0.20.2 release complete, PR #64 merged",
                "PR #64 was rewritten after review and merged; edge type list "
                "corrected and SUPPORTS marked create-only.",
            ),
            "conversation",
            memory_type="summary",
        )

    assert item is existing, "a same-subject capture must stack, not fork"
    assert score == pytest.approx(DUPLICATE_SCORE)


def test_two_captures_on_unrelated_subjects_do_not_stack() -> None:
    """A low-scoring neighbour in the same space must still mint a new item."""
    neighbour = _FakeItem("pr-73-batch-aware-reflect-superseded-874e9f14")
    spy = _SearchSpy([_FakeSearchResult(neighbour, UNRELATED_SCORE)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score = mcp_server._find_similar_item(
            "CognitiveMemory",
            "CognitiveMemory/work/kumiho-sdks",
            mcp_server._build_stack_query(
                "Moved the plugin interpreter to Python 3.13.15",
                "The system PATH pointed at another account's interpreter, so "
                "the venv was rebuilt on a per-user install.",
            ),
            "conversation",
            memory_type="summary",
        )

    assert item is None, "unrelated subjects must not be merged onto one item"
    assert score == pytest.approx(UNRELATED_SCORE)


# --- The query is built from title AND summary ------------------------------


def test_stack_query_carries_the_summary_not_just_the_title() -> None:
    """Title-only search was the mechanism behind #163's fragmentation."""
    query = mcp_server._build_stack_query(
        "Release complete",
        "PR #64 rewritten after adversarial review, then merged.",
    )
    assert query.startswith("Release complete"), "the title must lead"
    assert "adversarial review" in query, "the summary must reach the search"


def test_stack_query_is_capped() -> None:
    """Over-long queries fail server-side on Lucene's clause limit."""
    query = mcp_server._build_stack_query("t" * 500, "s" * 500)
    assert len(query) <= mcp_server._STACK_QUERY_MAX_CHARS


def test_stack_query_falls_back_when_there_is_no_title() -> None:
    assert mcp_server._build_stack_query("", "body text") == "body text"
    assert mcp_server._build_stack_query("", "", "fallback") == "fallback"


# --- The middle band needs a second signal ----------------------------------


def test_middle_band_stacks_when_memory_type_agrees() -> None:
    existing = _FakeItem("prior-decision", memory_type="decision")
    midband = (
        mcp_server._STACK_TYPE_MATCH_THRESHOLD
        + mcp_server._STACK_SIMILARITY_THRESHOLD
    ) / 2
    spy = _SearchSpy([_FakeSearchResult(existing, midband)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score = mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/decisions",
            "some query", "conversation", memory_type="decision",
        )

    assert item is existing
    assert score == pytest.approx(midband)


def test_middle_band_refuses_when_memory_type_differs() -> None:
    """Topically homogeneous spaces push unrelated items into this band."""
    existing = _FakeItem("prior-decision", memory_type="decision")
    midband = (
        mcp_server._STACK_TYPE_MATCH_THRESHOLD
        + mcp_server._STACK_SIMILARITY_THRESHOLD
    ) / 2
    spy = _SearchSpy([_FakeSearchResult(existing, midband)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score = mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/decisions",
            "some query", "conversation", memory_type="preference",
        )

    assert item is None
    assert score == pytest.approx(midband), "the near-miss is still reported"


# --- A failing search must not look like "nothing similar" ------------------


def test_search_failure_logs_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A search that fails every call is a broken install, not a quiet no-op."""
    def _boom(query: str, **kwargs: Any) -> List[_FakeSearchResult]:
        raise RuntimeError("maxClauseCount is set to 1024")

    with patch.object(mcp_server.kumiho, "search", _boom):
        with caplog.at_level("WARNING", logger=mcp_server.logger.name):
            item, score = mcp_server._find_similar_item(
                "CognitiveMemory", "CognitiveMemory/work",
                "some query", "conversation",
            )

    assert item is None
    assert score == 0.0
    assert caplog.records, "the failure must not be swallowed at DEBUG"
    assert any("maxClauseCount" in r.getMessage() for r in caplog.records)


def test_search_retries_with_the_title_alone() -> None:
    """A clause-limit blowup on the long query must not kill stacking."""
    existing = _FakeItem("prior")
    calls: List[str] = []

    def _fail_long(query: str, **kwargs: Any) -> List[_FakeSearchResult]:
        calls.append(query)
        if len(calls) == 1:
            raise RuntimeError("maxClauseCount is set to 1024")
        return [_FakeSearchResult(existing, DUPLICATE_SCORE)]

    with patch.object(mcp_server.kumiho, "search", _fail_long):
        item, _score = mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/work",
            "long title plus summary", "conversation",
            memory_type="summary",
            retry_query="long title",
        )

    assert calls == ["long title plus summary", "long title"]
    assert item is existing


# --- The score is exposed either way ----------------------------------------


def test_empty_query_reports_a_zero_score() -> None:
    assert mcp_server._find_similar_item(
        "CognitiveMemory", "CognitiveMemory/work", "   ", "conversation"
    ) == (None, 0.0)


def test_no_results_reports_a_zero_score() -> None:
    with patch.object(mcp_server.kumiho, "search", _SearchSpy([])):
        assert mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/work", "q", "conversation"
        ) == (None, 0.0)
