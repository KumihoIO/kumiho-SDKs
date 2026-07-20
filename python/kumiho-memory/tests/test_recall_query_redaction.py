"""Read-direction query screening (#140).

#138/#139 closed the WRITE direction — nothing raw reaches the summarizer LLM
or the stored payload.  These tests pin the READ direction: a recall query is
screened INSIDE ``recall_memories``, above the graph branch and above every
backend call, so it is already in descriptor form by the time it crosses any of
the three machine boundaries recall touches (the Kumiho server, the LLM
provider, an embedding provider).

Assertions are made at the RETRIEVER BOUNDARY wherever possible — on what the
``memory_retrieve`` stub actually received — not on the caller's intent.  That
is the only thing that proves the leak is closed.

THE DECISIVE TEST is ``test_clean_queries_pass_through_byte_identical``: a query
matching no pattern is returned as the IDENTICAL object.  That makes retrieval
impact exactly zero for the overwhelming majority of queries and is the reason
this ships without a benchmark run.  If that test is weakened, the no-benchmark
argument is weakened with it.

Secret-shaped strings are assembled at RUNTIME by concatenation so no literal
credential shape ever lands in the repository.
"""

import asyncio
import tempfile

import pytest

from kumiho_memory.memory_manager import (
    UniversalMemoryManager,
    _screen_query_for_egress,
)
from kumiho_memory.privacy import PIIRedactor
from kumiho_memory.redis_memory import RedisMemoryBuffer

from fakes import FakeRedis


# --- planted needles, built at runtime (never a literal in the repo) -------
PLANTED_EMAIL = "dana.kim" + "@" + "example.com"
PLANTED_CREDENTIAL = "sk-" + ("Q" * 12) + ("4" * 12)
PLANTED_SSN = "123" + "-" + "45" + "-" + "6789"


class RecordingRetriever:
    """Captures every kwargs dict the retriever was called with."""

    def __init__(self, revision_krefs=None):
        self.calls = []
        self._krefs = revision_krefs or []

    async def __call__(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {"revision_krefs": list(self._krefs)}

    def queries(self):
        return [c.get("query", "") for c in self.calls]

    def seen_text(self):
        return "\n".join(str(c.get("query", "")) for c in self.calls)


class ExplodingRedactor(PIIRedactor):
    """Real redactor that blows up on a marked query."""

    def anonymize_summary(self, summary):
        if "BOOM" in summary:
            raise RuntimeError("redactor exploded")
        return super().anonymize_summary(summary)


def _make_manager(retriever, redactor=None, **kwargs):
    return UniversalMemoryManager(
        redis_buffer=RedisMemoryBuffer(
            client=FakeRedis(), redis_url="redis://test",
        ),
        pii_redactor=redactor if redactor is not None else PIIRedactor(),
        memory_retrieve=retriever,
        **kwargs,
    )


# --------------------------------------------------------------------------
# (a) THE DECISIVE PROPERTY — clean queries pass through BYTE-IDENTICAL
# --------------------------------------------------------------------------

CLEAN_QUERIES = [
    # ordinary natural-language recall
    "what did we decide about the rollout schedule?",
    "summarize yesterday's discussion",
    "who is responsible for the migration",
    # LoCoMo-style question shapes
    "When did Melanie say she started counseling?",
    "How many years has Caroline lived in Sweden?",
    "What did the user mention about their sister's wedding?",
    # Korean (mixed-script tokenizer path)
    "우리가 임베딩 백엔드를 왜 바꿨지?",
    "지난주 회의에서 결정한 릴리즈 일정 알려줘",
    "BM25 커플링 이슈 정리해줘",
    # code identifiers and dotted/underscored names
    "why does neo4j_uri fail to resolve in HAS_REVISION",
    "explain _redact_messages_for_llm ordering",
    "kumiho_memory.memory_manager.recall_memories",
    # the documented api_key_generic near-miss: hyphenated dictionary prose
    "sk-learn-based-approach-is-better than the alternative",
    "should we use pk-style-naming-for-these-columns",
    # NOTE: "Bearer token auth" as prose is deliberately NOT in this corpus —
    # it is a known false positive of the shared ``bearer_token`` pattern and
    # has its own test below.
    # ISO-8601 timestamps (write path already pins these match nothing)
    "what happened on 2026-07-18T09:30:00+00:00",
    "compare 2026-07-11 against 2026-02-14",
    # version numbers and numeric runs that are NOT phone/SSN/card shapes
    "regression between v0.19.0 and v0.20.0",
    "the 0.565 result versus the 0.521 gate",
    "issue 138 and issue 139 and issue 140",
    # punctuation, quotes, unicode, newlines
    'the "max-of-raw" fusion bug — what replaced it?',
    "line one\nline two\nline three",
    "50% of 1024-dim vectors, 100% recall?",
    # near-miss shapes that must NOT trip the detectors
    "192.168 is not a full address",
    "call me at 555-1234",
    "AKIA is a prefix but not a key",
]


@pytest.mark.parametrize("query", CLEAN_QUERIES)
def test_clean_queries_pass_through_byte_identical(query):
    """A query matching no pattern is the CALLER'S OWN OBJECT, unchanged.

    Identity (``is``), not merely equality — this is the property that makes
    the retrieval impact of #140 provably zero for the common case, and it is
    what lets this ship without a paired benchmark run.
    """
    screened = _screen_query_for_egress(PIIRedactor(), query)
    assert screened is query


def test_clean_query_reaches_retriever_byte_identical():
    """Same property observed at the RETRIEVER BOUNDARY, end to end."""
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)
    query = "what did we decide about the rollout on 2026-07-18?"

    asyncio.run(manager.recall_memories(query, limit=3))

    assert retriever.queries() == [query]


def test_known_false_positive_bearer_prose_degrades_gracefully():
    """"Bearer token auth" as PROSE trips ``bearer_token``. Pinned, not fixed.

    This is a pre-existing property of the credential regex #139 already ships:
    the WRITE path redacts this exact string identically, so the read path
    matching it is the *consistent* behaviour, not a new defect. Loosening the
    pattern here would fork the policy in two directions at once — a weaker
    credential detector AND two divergent redaction policies in one file.

    It IS a real cost on the read side that has no write-side equivalent: the
    query loses a search term it would otherwise match on. The cost is bounded
    by exactly this test — the surrounding prose survives (span excision, not
    line drop), nothing raises, and the query stays usable.
    """
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)

    results = asyncio.run(manager.recall_memories(
        "what did we decide about Bearer token auth?", limit=3,
    ))

    assert results == []
    sent = retriever.seen_text()
    assert "[redacted]" in sent
    # the retrieval-bearing prose is intact on both sides of the excised span
    assert "what did we decide about" in sent
    assert "auth?" in sent


# --------------------------------------------------------------------------
# (b) PII is anonymized into the SAME vocabulary the stored index uses
# --------------------------------------------------------------------------

def test_pii_query_reaches_retriever_as_descriptors():
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)

    asyncio.run(manager.recall_memories(
        f"what did {PLANTED_EMAIL} say about the SSN {PLANTED_SSN}?", limit=3,
    ))

    sent = retriever.seen_text()
    assert PLANTED_EMAIL not in sent
    assert PLANTED_SSN not in sent
    # ...and it is the descriptor form, i.e. the same vocabulary
    # ``anonymize_summary`` writes into the stored index.
    assert "[email]" in sent
    assert "[ssn]" in sent
    # surrounding prose — the actual retrieval signal — survives intact
    assert "what did" in sent
    assert "say about the SSN" in sent


def test_pii_query_still_retrieves_the_anonymized_memory():
    """A raw-PII query still finds the memory stored under the descriptor.

    The index holds ``[email]`` (``anonymize_summary`` runs before storage), so
    a raw query was searching for a string the index does not contain.  After
    screening, query and index share the literal token — this test pins that
    the screened query is the one the retrieval scoring actually sees.
    """
    stored_summary = PIIRedactor().anonymize_summary(
        f"Dana confirmed the rollout date by mail to {PLANTED_EMAIL}."
    )
    assert "[email]" in stored_summary  # index really is descriptor-form

    matched = []

    async def retriever(**kwargs):
        q = kwargs.get("query", "")
        # Crude lexical stand-in for the server's scoring: a hit requires the
        # query and the indexed summary to share the descriptor token.
        if "[email]" in q and "[email]" in stored_summary:
            matched.append(q)
            return {"revision_krefs": ["kref://memory/item.conversation?r=1"]}
        return {"revision_krefs": []}

    manager = _make_manager(retriever)
    results = asyncio.run(manager.recall_memories(
        f"what did we send to {PLANTED_EMAIL}?", limit=3,
    ))

    assert matched, "screened query failed to match the descriptor-form index"
    assert len(results) == 1


# --------------------------------------------------------------------------
# (c) credentials are DROPPED span-wise, never raised
# --------------------------------------------------------------------------

def test_credential_in_query_is_dropped_not_raised():
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)
    query = f"does {PLANTED_CREDENTIAL} still work for staging?"

    # No raise: a pasted secret must not abort the caller's turn — and would
    # abort it again on every retry, since the message is unchanged.
    results = asyncio.run(manager.recall_memories(query, limit=3))
    assert results == []

    sent = retriever.seen_text()
    assert PLANTED_CREDENTIAL not in sent
    assert "[redacted]" in sent
    # SPAN-level excision: the surrounding prose is retained, so the query is
    # still a usable search. Dropping the line would drop the whole query.
    assert "still work for staging?" in sent


def test_credential_drop_is_logged_with_counts_only(caplog):
    """The drop is attributable, and the log never carries the secret."""
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)

    with caplog.at_level("WARNING", logger="kumiho_memory.memory_manager"):
        asyncio.run(manager.recall_memories(
            f"is {PLANTED_CREDENTIAL} rotated?", limit=3,
        ))

    text = caplog.text
    assert "credential span" in text
    assert PLANTED_CREDENTIAL not in text


# --------------------------------------------------------------------------
# (d) fail CLOSED when the redactor itself raises
# --------------------------------------------------------------------------

def test_redactor_exception_fails_closed():
    retriever = RecordingRetriever()
    manager = _make_manager(retriever, redactor=ExplodingRedactor())
    query = f"BOOM tell me about {PLANTED_EMAIL}"

    results = asyncio.run(manager.recall_memories(query, limit=3))

    sent = retriever.seen_text()
    # Nothing of the original query survives — not the needle, not the prose.
    assert PLANTED_EMAIL not in sent
    assert "BOOM" not in sent
    assert sent == "[redacted]"
    # A guaranteed-empty result is the correct failure mode, not a leak.
    assert results == []


# --------------------------------------------------------------------------
# (e) the graph reformulation LLM receives the SCREENED query
# --------------------------------------------------------------------------

def test_graph_augmented_reformulation_receives_screened_query():
    """The choke point sits ABOVE the graph branch, so the reformulation LLM —
    a different machine boundary from the Kumiho server — never sees raw text.
    """
    retriever = RecordingRetriever()
    manager = _make_manager(retriever, graph_augmentation=True)

    seen = []

    class _FakeGraphRecall:
        async def recall(self, query, **kwargs):
            seen.append(query)
            return []

    manager._get_graph_recall = lambda: _FakeGraphRecall()

    asyncio.run(manager.recall_memories(
        f"contact {PLANTED_EMAIL} about {PLANTED_CREDENTIAL}",
        limit=3,
        graph_augmented=True,
    ))

    assert seen, "graph recall leg was not exercised"
    assert PLANTED_EMAIL not in seen[0]
    assert PLANTED_CREDENTIAL not in seen[0]
    assert "[email]" in seen[0]
    assert "[redacted]" in seen[0]


# --------------------------------------------------------------------------
# (f) the caller's input is never mutated
# --------------------------------------------------------------------------

def test_caller_query_is_not_mutated():
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)
    query = f"mail {PLANTED_EMAIL} now"
    original = f"mail {PLANTED_EMAIL} now"

    asyncio.run(manager.recall_memories(query, limit=3))

    assert query == original
    assert PLANTED_EMAIL in query  # caller keeps the raw local copy


# --------------------------------------------------------------------------
# (g) the two known leak sites, asserted AT THE RETRIEVER BOUNDARY
# --------------------------------------------------------------------------

def test_handle_user_message_recall_reaches_retriever_screened():
    """Known site #2: ``handle_user_message`` recalls on the RAW user message.

    Asserted on what the retriever received, not on what the caller passed.
    """
    retriever = RecordingRetriever()
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = _make_manager(retriever, artifact_root=tmpdir)
        asyncio.run(manager.handle_user_message(
            user_id="user-1",
            message=f"ping {PLANTED_EMAIL} with key {PLANTED_CREDENTIAL}",
        ))

    sent = retriever.seen_text()
    assert sent, "recall leg was not exercised"
    assert PLANTED_EMAIL not in sent
    assert PLANTED_CREDENTIAL not in sent
    assert "[email]" in sent
    assert "[redacted]" in sent


def test_background_assess_recall_reaches_retriever_screened():
    """Known site #1: ``_background_assess`` builds the query from the tail of
    the last 3 buffered turns and recalls on it RAW.

    The adjacent assessor leg was screened in #138; this pins the recall leg on
    the same buffer.  Asserted at the retriever boundary.
    """
    retriever = RecordingRetriever()
    assessed = []

    async def assess_fn(messages, recalled):
        assessed.append([dict(m) for m in messages])
        from kumiho_memory.memory_manager import MemoryAssessResult
        return MemoryAssessResult(should_store=False, content="", reason="")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = _make_manager(
            retriever,
            artifact_root=tmpdir,
            auto_assess_fn=assess_fn,
            auto_assess_min_messages=1,
        )
        ingest = asyncio.run(manager.ingest_message(
            user_id="user-1",
            message=f"my address is {PLANTED_EMAIL}",
            context="personal",
        ))
        asyncio.run(manager.add_assistant_response(
            session_id=ingest["session_id"],
            response=f"noted, key is {PLANTED_CREDENTIAL}",
        ))
        asyncio.run(manager._background_assess(ingest["session_id"]))

    sent = retriever.seen_text()
    assert sent, "background-assess recall leg was not exercised"
    assert PLANTED_EMAIL not in sent
    assert PLANTED_CREDENTIAL not in sent
    assert "[email]" in sent
    assert "[redacted]" in sent
    # #138's assessor leg is still screened too — one buffer, both legs closed.
    assert assessed, "assessor leg was not exercised"
    flat = "\n".join(
        str(m.get("content", "")) for call in assessed for m in call
    )
    assert PLANTED_EMAIL not in flat
    assert PLANTED_CREDENTIAL not in flat


# --------------------------------------------------------------------------
# (h) the choke points OUTSIDE recall_memories
# --------------------------------------------------------------------------

def test_sibling_embedding_filter_screens_the_query():
    """``build_recalled_context`` is called by ``tool_memory_engage`` with the
    tool's RAW query, independently of the recall — so a ``recall_memories``
    screen does not reach this remote embedding call.  It has its own.
    """
    embedded = []

    class _RecordingEmbedder:
        def embed(self, texts):
            embedded.append(list(texts))
            return [[1.0, 0.0] for _ in texts]

    manager = _make_manager(
        RecordingRetriever(),
        embedding_adapter=_RecordingEmbedder(),
        sibling_similarity_threshold=0.1,
    )

    manager.build_recalled_context(
        [{
            "title": "t", "summary": "s", "content": "c",
            "sibling_revisions": [{"title": "st", "summary": "ss", "content": "sc"}],
        }],
        f"who is {PLANTED_EMAIL}",
        "full",
    )

    assert embedded, "embedding leg was not exercised"
    sent = "\n".join(embedded[0])
    assert PLANTED_EMAIL not in sent
    assert "[email]" in sent


def test_rerank_memories_screens_the_query():
    """``rerank_memories`` has zero in-package callers — it is API surface for
    external harnesses, so it never passes through ``recall_memories`` and
    needs its own screen before ``two_pass_rerank`` embeds the query.
    """
    embedded = []

    class _RecordingEmbedder:
        def embed(self, texts):
            embedded.append(list(texts))
            return [[1.0, 0.0] for _ in texts]

    manager = _make_manager(
        RecordingRetriever(), embedding_adapter=_RecordingEmbedder(),
    )

    manager.rerank_memories(
        [{"title": "t", "summary": "s"}], f"who is {PLANTED_EMAIL}",
    )

    assert embedded, "two_pass_rerank embedding leg was not exercised"
    sent = "\n".join(embedded[0])
    assert PLANTED_EMAIL not in sent
    assert "[email]" in sent


# --------------------------------------------------------------------------
# (i) helper-level edge cases
# --------------------------------------------------------------------------

def test_screen_is_idempotent():
    """Descriptors match no pattern, so a second pass is a byte-identical
    no-op.  That is what keeps the second choke point free on the already-
    screened recall path.
    """
    redactor = PIIRedactor()
    once = _screen_query_for_egress(
        redactor, f"mail {PLANTED_EMAIL} key {PLANTED_CREDENTIAL}",
    )
    twice = _screen_query_for_egress(redactor, once)
    assert twice is once


def test_screen_tolerates_missing_redactor_and_empty_query():
    assert _screen_query_for_egress(None, "anything") == "anything"
    assert _screen_query_for_egress(PIIRedactor(), "") == ""
    assert _screen_query_for_egress(PIIRedactor(), None) is None
