"""Revision stacking: does a second capture about one subject land on one item?

``kumiho_memory_reflect`` promises that a capture revisiting a topic becomes a
new *revision* of the existing item rather than a brand-new item. Issue #163
showed it never did: new item names carry a content hash, so name matching is
impossible by construction, and the whole mechanism rested on
``_find_similar_item`` gating on a fuzzy score ``>= 0.92``.

That gate was not merely strict, it was unreachable. Replaying real duplicate
pairs against a live CE graph showed an item scores only **0.72-0.83 against
its own exact title** -- the scorer's ceiling sits below the gate, so no input
could ever stack.

Stacking is not a cheap operation to get wrong. It tags the NEW revision
"published", and every recall path resolves ``get_revision_by_tag("published")``
first, so the prior revision is DISPLACED off the default retrieval surface --
a belief revision performed without the SUPERSEDES edge. A false stack hides a
memory just as surely as a false split fragments one, which is why the gate
below needs a signal that actually separates rather than a threshold tuned to
err in the "safer" direction. There is no safer direction.

These tests mock ``kumiho.search`` -- they must never touch a server, and in
particular must never write to one.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple
from unittest.mock import patch

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

from kumiho import mcp_server


# ===========================================================================
# The measured table
# ===========================================================================
#
# Every row below is a real (query item, candidate item) pair from the live CE
# graph, with the score the server actually returned and the token overlap
# computed from the two items' stored title+summary. Self-matches are excluded:
# at capture time the incoming item does not exist in the index yet, so the
# candidate a real call sees is the runner-up of these probes.
#
# The `decisions` rows are the load-bearing ones. That space is topically
# homogeneous -- nearly every capture is about Kumiho memory design and typed
# "decision" -- so the score bands overlap (duplicates 0.670/0.676 sit barely
# above unrelated neighbours at 0.616/0.600/0.575, and an unrelated pair there
# outscores both genuine duplicates measured in the other space) and
# memory_type agreement adds no separation at all. Only the lexical column
# splits them.
#
#   (space, query, candidate, is_duplicate, score, overlap)
MEASURED: List[Tuple[str, str, str, bool, float, float]] = [
    # --- decisions: a homogeneous space; every pair below is type-matched ---
    ("decisions", "supersedes-mcp", "pr-152-scope",   True,  0.6697, 0.2525),
    ("decisions", "supersedes-mcp", "redis-20turn",   False, 0.6165, 0.0875),
    ("decisions", "supersedes-mcp", "consolidation",  False, 0.5578, 0.1481),
    ("decisions", "supersedes-mcp", "followup-tasks", False, 0.4662, 0.1027),
    ("decisions", "consolidation",  "redis-20turn",   True,  0.6761, 0.2174),
    ("decisions", "consolidation",  "followup-tasks", False, 0.5745, 0.1060),
    ("decisions", "consolidation",  "pr-152-scope",   False, 0.5191, 0.1429),
    ("decisions", "consolidation",  "supersedes-mcp", False, 0.5178, 0.1481),
    # The dangerous row: a capture with NO duplicate in the space still put an
    # unrelated item at top1, above the lowest true duplicate score.
    ("decisions", "followup-tasks", "consolidation",  False, 0.5998, 0.1060),
    ("decisions", "followup-tasks", "pr-152-scope",   False, 0.5063, 0.0914),
    ("decisions", "followup-tasks", "redis-20turn",   False, 0.5051, 0.0876),
    # --- work/kumiho-sdks: a mixed space, where scores separate on their own --
    ("work", "plugins-release", "plugins-pr64",    True,  0.5797, 0.1881),
    ("work", "plugins-release", "sdk-pr152",       False, 0.2888, 0.1435),
    ("work", "plugins-release", "sdk-pr73",        False, 0.2250, 0.0352),
    ("work", "plugins-pr64",    "plugins-release", True,  0.5783, 0.1881),
    ("work", "plugins-pr64",    "sdk-pr152",       False, 0.3495, 0.1230),
    ("work", "plugins-pr64",    "sdk-pr73",        False, 0.2140, 0.0282),
]

#: Top1/top2 for each probe once the self-match is removed, i.e. what a real
#: call would see. Pinned to show the margin rule fails to separate.
MEASURED_MARGINS = {
    # probe:          (top1,   top2,   top1_is_duplicate)
    "supersedes-mcp": (0.6697, 0.6165, True),   # true duplicate, margin 0.053
    "consolidation":  (0.6761, 0.5745, True),   # true duplicate, margin 0.102
    "followup-tasks": (0.5998, 0.5063, False),  # IMPOSTOR,       margin 0.094
}

#: In `decisions` every capture is typed "decision", so the type gate is
#: satisfied by every pair there -- which is exactly why it cannot be the thing
#: doing the work. The `work` rows are all "summary" and likewise agree.
TYPE_ALWAYS_MATCHES = True


def _decide(row: Tuple[str, str, str, bool, float, float]) -> bool:
    """Run the gate over one measured row, in that row's space configuration."""
    _space, _query, _candidate, _is_dup, score, overlap = row
    return mcp_server._should_stack(score, TYPE_ALWAYS_MATCHES, overlap)


# --- The table is the test ---------------------------------------------------


@pytest.mark.parametrize("row", MEASURED, ids=lambda r: f"{r[1]}-vs-{r[2]}")
def test_measured_pair_is_classified_correctly(
    row: Tuple[str, str, str, bool, float, float]
) -> None:
    """Every real pair measured on the live graph must land on the right side."""
    space, query, candidate, is_duplicate, score, overlap = row
    assert _decide(row) is is_duplicate, (
        f"{space}: {query} vs {candidate} (score={score}, overlap={overlap}) "
        f"should {'stack' if is_duplicate else 'NOT stack'}"
    )


def test_every_measured_duplicate_stacks_and_no_impostor_does() -> None:
    """The table as a whole, so a partial regression cannot hide in one row."""
    stacked = {(r[1], r[2]) for r in MEASURED if _decide(r)}
    expected = {(r[1], r[2]) for r in MEASURED if r[3]}
    assert stacked == expected


def test_score_alone_cannot_separate_the_classes() -> None:
    """Why a second signal is required at all, pinned against the measurements."""
    worst_duplicate = min(r[4] for r in MEASURED if r[3])
    best_impostor = max(r[4] for r in MEASURED if not r[3])
    assert best_impostor > worst_duplicate, (
        "an unrelated pair outscores a genuine duplicate, so no score "
        "threshold can separate the two classes"
    )


def test_type_match_alone_cannot_separate_the_decisions_space() -> None:
    """Type agreement holds for every `decisions` pair, duplicate or not."""
    impostors = [r for r in MEASURED if r[0] == "decisions" and not r[3]]
    # With the lexical floor satisfied artificially, the score+type gate alone
    # admits unrelated decisions -- the hole the lexical floor was added to close.
    admitted = [
        r for r in impostors
        if mcp_server._should_stack(r[4], True, 1.0)
    ]
    assert admitted, (
        "sanity: without the lexical floor the type gate lets unrelated "
        "decisions through"
    )


def test_margin_rule_would_not_have_worked() -> None:
    """top1-minus-top2 does not separate, which is why nothing gates on it."""
    duplicate_margins = [
        top1 - top2 for top1, top2, is_dup in MEASURED_MARGINS.values() if is_dup
    ]
    impostor_margins = [
        top1 - top2 for top1, top2, is_dup in MEASURED_MARGINS.values() if not is_dup
    ]
    assert min(duplicate_margins) < max(impostor_margins), (
        "an impostor's margin exceeds a real duplicate's, so any margin floor "
        "admitting the duplicate also admits the impostor"
    )


def test_lexical_overlap_separates_where_score_does_not() -> None:
    duplicates = [r[5] for r in MEASURED if r[3]]
    impostors = [r[5] for r in MEASURED if not r[3]]
    assert min(duplicates) > max(impostors), "the classes must be separable"
    assert max(impostors) < mcp_server._STACK_MIN_LEXICAL_OVERLAP < min(duplicates), (
        "the configured floor must sit inside the measured gap"
    )


# ===========================================================================
# Test doubles for the end-to-end path
# ===========================================================================


class _FakeRevision:
    def __init__(self, memory_type: str, title: str, summary: str) -> None:
        self.metadata = {
            "memory_type": memory_type, "title": title, "summary": summary,
        }


class _FakeKref:
    def __init__(self, uri: str) -> None:
        self.uri = uri


class _FakeItem:
    """The bare surface ``_find_similar_item`` touches on a match."""

    def __init__(
        self, name: str, memory_type: str = "summary",
        title: str = "", summary: str = "",
    ) -> None:
        self.item_name = name
        self.kref = _FakeKref(f"kref://CognitiveMemory/work/{name}.conversation")
        self._rev = _FakeRevision(memory_type, title, summary)

    def get_revision_by_tag(self, tag: str) -> Optional[_FakeRevision]:
        return self._rev if tag == "published" else None

    def get_revision(self, selector: str) -> _FakeRevision:
        return self._rev


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


# Two captures about one subject: different headlines, shared body vocabulary.
DUP_TITLE_A = "kumiho-plugins PR #64 SKILL.md edge ontology cleanup and 0.20.2 bump"
DUP_BODY_A = (
    "SKILL.md Contradictions section claimed SUPERSEDES edges are automatic; "
    "corrected to say the memory layer owns belief revision because the status "
    "demotion and the grounding ripple travel with the edge as one protocol."
)
DUP_TITLE_B = "kumiho-plugins 0.20.2 release complete, PR #64 merged after rewrite"
DUP_BODY_B = (
    "PR #64 was rewritten after adversarial review then merged. The edge "
    "ontology list in SKILL.md now names all nine types, SUPERSEDES stays with "
    "the memory layer, and the status demotion plus grounding ripple are "
    "described as one protocol rather than automatic."
)
UNRELATED_TITLE = "Moved the plugin interpreter to Python 3.13.15 on the kacy account"
UNRELATED_BODY = (
    "The system PATH pointed at another account's interpreter directory, so the "
    "venv was deleted and rebuilt against a per-user winget install; grpcio and "
    "pydantic-core both ship cp313 win_amd64 wheels so nothing needs compiling."
)


# --- The bug that issue #163 reported --------------------------------------


def test_threshold_sits_below_the_scorers_observed_ceiling() -> None:
    """The regression guard proper.

    The old 0.92 gate was above the highest score the CE fulltext scorer was
    ever observed to emit -- including an item matched against its own exact
    title (0.83) -- so stacking was dead code. Whatever the threshold becomes,
    it must stay reachable.
    """
    assert mcp_server._STACK_SIMILARITY_THRESHOLD < 0.83
    assert (
        mcp_server._STACK_TYPE_MATCH_THRESHOLD
        <= mcp_server._STACK_SIMILARITY_THRESHOLD
    )


def test_two_captures_on_one_subject_stack() -> None:
    """Different titles, same subject -> the second lands on the first's item."""
    existing = _FakeItem(
        "kumiho-plugins-pr-64-39be818a", title=DUP_TITLE_A, summary=DUP_BODY_A,
    )
    spy = _SearchSpy([_FakeSearchResult(existing, 0.60)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score, _runner_up, overlap = mcp_server._find_similar_item(
            "CognitiveMemory",
            "CognitiveMemory/work/kumiho-sdks",
            mcp_server._build_stack_query(DUP_TITLE_B, DUP_BODY_B),
            "conversation",
            memory_type="summary",
            compare_text=f"{DUP_TITLE_B} {DUP_BODY_B}",
        )

    assert item is existing, "a same-subject capture must stack, not fork"
    assert score == pytest.approx(0.60)
    assert overlap >= mcp_server._STACK_MIN_LEXICAL_OVERLAP


def test_two_captures_on_unrelated_subjects_do_not_stack() -> None:
    """A same-type neighbour in the same space must still mint a new item."""
    neighbour = _FakeItem(
        "plugins-pr-64-39be818a", title=DUP_TITLE_A, summary=DUP_BODY_A,
    )
    # Score high enough for the middle band, and the type agrees: only the
    # lexical gate stands between this and a displaced published revision.
    spy = _SearchSpy([_FakeSearchResult(neighbour, 0.62)])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score, _runner_up, overlap = mcp_server._find_similar_item(
            "CognitiveMemory",
            "CognitiveMemory/work/kumiho-sdks",
            mcp_server._build_stack_query(UNRELATED_TITLE, UNRELATED_BODY),
            "conversation",
            memory_type="summary",
            compare_text=f"{UNRELATED_TITLE} {UNRELATED_BODY}",
        )

    assert item is None, "unrelated subjects must not be merged onto one item"
    assert score == pytest.approx(0.62)
    assert overlap < mcp_server._STACK_MIN_LEXICAL_OVERLAP


# --- The gate's individual conditions ---------------------------------------


def test_lexical_floor_binds_in_the_strong_band_too() -> None:
    assert mcp_server._should_stack(0.99, True, 0.0) is False
    assert mcp_server._should_stack(0.99, True, 0.30) is True


def test_middle_band_needs_both_type_and_overlap() -> None:
    mid = (
        mcp_server._STACK_TYPE_MATCH_THRESHOLD
        + mcp_server._STACK_SIMILARITY_THRESHOLD
    ) / 2
    assert mcp_server._should_stack(mid, True, 0.30) is True
    assert mcp_server._should_stack(mid, False, 0.30) is False
    assert mcp_server._should_stack(mid, True, 0.05) is False


def test_below_the_lower_band_nothing_stacks() -> None:
    low = mcp_server._STACK_TYPE_MATCH_THRESHOLD - 0.01
    assert mcp_server._should_stack(low, True, 0.99) is False


def test_short_texts_refuse_rather_than_guess() -> None:
    """Thin token sets make the ratio noise, so they must not license a stack."""
    assert mcp_server._lexical_overlap("edge case", "edge case") == 0.0
    long_a = " ".join(f"token{i}" for i in range(20))
    assert mcp_server._lexical_overlap(long_a, long_a) == pytest.approx(1.0)


def test_overlap_handles_cjk_without_spaces() -> None:
    """Korean is written without spaces, so tokens come from character bigrams."""
    a = "레디스 워킹 메모리 20턴 자동 콘솔리데이션 도입 결정 사항 기록"
    b = "레디스 워킹 메모리 20턴 자동 콘솔리데이션 도입 관련 후속 기록"
    unrelated = "플러그인 인터프리터를 파이썬 3.13.15 버전으로 이전 설치 작업"
    assert mcp_server._lexical_overlap(a, b) > mcp_server._lexical_overlap(a, unrelated)


def test_overlap_is_symmetric() -> None:
    a, b = f"{DUP_TITLE_A} {DUP_BODY_A}", f"{DUP_TITLE_B} {DUP_BODY_B}"
    assert mcp_server._lexical_overlap(a, b) == pytest.approx(
        mcp_server._lexical_overlap(b, a)
    )


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


# --- A failing search must not look like "nothing similar" ------------------


def test_search_failure_logs_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A search that fails every call is a broken install, not a quiet no-op."""
    def _boom(query: str, **kwargs: Any) -> List[_FakeSearchResult]:
        raise RuntimeError("maxClauseCount is set to 1024")

    with patch.object(mcp_server.kumiho, "search", _boom):
        with caplog.at_level("WARNING", logger=mcp_server.logger.name):
            item, score, _runner_up, _overlap = mcp_server._find_similar_item(
                "CognitiveMemory", "CognitiveMemory/work",
                "some query", "conversation",
            )

    assert item is None
    assert score == 0.0
    assert caplog.records, "the failure must not be swallowed at DEBUG"
    assert any("maxClauseCount" in r.getMessage() for r in caplog.records)


def test_search_retries_with_the_title_alone() -> None:
    """A clause-limit blowup on the long query must not kill stacking."""
    existing = _FakeItem("prior", title=DUP_TITLE_A, summary=DUP_BODY_A)
    calls: List[str] = []

    def _fail_long(query: str, **kwargs: Any) -> List[_FakeSearchResult]:
        calls.append(query)
        if len(calls) == 1:
            raise RuntimeError("maxClauseCount is set to 1024")
        return [_FakeSearchResult(existing, 0.60)]

    with patch.object(mcp_server.kumiho, "search", _fail_long):
        item, _score, _runner_up, _overlap = mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/work",
            "long title plus summary", "conversation",
            memory_type="summary",
            retry_query="long title",
            compare_text=f"{DUP_TITLE_B} {DUP_BODY_B}",
        )

    assert calls == ["long title plus summary", "long title"]
    assert item is existing


# --- The diagnostics are exposed either way ---------------------------------


def test_runner_up_is_reported() -> None:
    """The margin is not gated on, but it must stay inspectable."""
    top = _FakeItem("top", title=UNRELATED_TITLE, summary=UNRELATED_BODY)
    second = _FakeItem("second", title=DUP_TITLE_A, summary=DUP_BODY_A)
    spy = _SearchSpy([
        _FakeSearchResult(top, 0.5998), _FakeSearchResult(second, 0.5063),
    ])

    with patch.object(mcp_server.kumiho, "search", spy):
        item, score, runner_up, _overlap = mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/decisions",
            "query", "conversation", memory_type="decision",
            compare_text=f"{DUP_TITLE_B} {DUP_BODY_B}",
        )

    assert item is None
    assert score == pytest.approx(0.5998)
    assert runner_up == pytest.approx(0.5063)


def test_empty_query_reports_zeroes() -> None:
    assert mcp_server._find_similar_item(
        "CognitiveMemory", "CognitiveMemory/work", "   ", "conversation"
    ) == (None, 0.0, 0.0, 0.0)


def test_no_results_reports_zeroes() -> None:
    with patch.object(mcp_server.kumiho, "search", _SearchSpy([])):
        assert mcp_server._find_similar_item(
            "CognitiveMemory", "CognitiveMemory/work", "q", "conversation"
        ) == (None, 0.0, 0.0, 0.0)
