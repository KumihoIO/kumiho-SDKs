"""Read-direction query screening (#140).

#138/#139 closed the WRITE direction — nothing raw reaches the summarizer LLM
or the stored payload.  These tests pin the READ direction: a recall query is
screened INSIDE ``recall_memories``, above the graph branch and above every
backend call, and again at the two remote boundaries that are re-exported at
package top level and so can be reached without a manager at all
(``two_pass_rerank``, ``GraphAugmentedRecall.recall``).

Assertions are made at the RETRIEVER / EMBEDDER BOUNDARY wherever possible —
on what the stub actually received — not on the caller's intent.  That is the
only thing that proves the leak is closed.

THE DECISIVE TEST is ``test_clean_queries_pass_through_byte_identical``: a
query matching no pattern is returned as the IDENTICAL object.  That makes
retrieval impact exactly zero for it, and is the reason this ships without a
benchmark run.  If that test is weakened, the no-benchmark argument is weakened
with it.  Its corpus deliberately includes the shapes an adversarial review
measured as FALSE POSITIVES of the write-path pattern set — four-segment
version strings, IP literals, epoch timestamps, bare 10-digit ids, year lists,
"Bearer" as prose.  Those are core developer-tool recall vocabulary, so a
corpus that dodged them would prove nothing about this product's real queries.
The query-side pattern set was narrowed until they all pass through clean; see
``PIIRedactor.QUERY_PII_PATTERNS``.

Secret-shaped strings are assembled at RUNTIME by concatenation so no literal
credential shape ever lands in the repository.
"""

import asyncio
import logging
import tempfile

import pytest

from kumiho_memory.memory_manager import UniversalMemoryManager
from kumiho_memory.privacy import (
    QUERY_SCREEN_FAILED,
    PIIRedactor,
    screen_query_for_egress,
)
from kumiho_memory.redis_memory import RedisMemoryBuffer

from fakes import FakeRedis


# --- planted needles, built at runtime (never a literal in the repo) -------
PLANTED_EMAIL = "dana.kim" + "@" + "example.com"
PLANTED_CREDENTIAL = "sk-" + ("Q" * 12) + ("4" * 12)
PLANTED_SSN = "123" + "-" + "45" + "-" + "6789"
PLANTED_KR_RRN = "901231" + "-" + "1234567"
PLANTED_KR_PHONE = "010" + "-" + "1234" + "-" + "5678"


class RecordingRetriever:
    """Captures every kwargs dict the retriever was called with.

    Defaults to a NON-EMPTY result so that ``results == []`` assertions in the
    fail-closed tests are load-bearing: an empty list can then only come from
    the screen short-circuiting before the backend call, never from the stub.
    """

    def __init__(self, revision_krefs=None):
        self.calls = []
        self._krefs = (
            ["kref://memory/item.conversation?r=1"]
            if revision_krefs is None
            else revision_krefs
        )

    async def __call__(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {"revision_krefs": list(self._krefs)}

    def queries(self):
        return [c.get("query", "") for c in self.calls]

    def seen_text(self):
        return "\n".join(str(c.get("query", "")) for c in self.calls)


def _make_manager(retriever, **kwargs):
    return UniversalMemoryManager(
        redis_buffer=RedisMemoryBuffer(
            client=FakeRedis(), redis_url="redis://test",
        ),
        memory_retrieve=retriever,
        **kwargs,
    )


@pytest.fixture
def exploding_screen(monkeypatch):
    """Force the module-owned query redactor to raise."""

    class _Boom(PIIRedactor):
        def screen_query(self, query):
            raise RuntimeError("redactor exploded")

    monkeypatch.setattr("kumiho_memory.privacy._QUERY_REDACTOR", _Boom())


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
    # ISO-8601 timestamps (write path already pins these match nothing)
    "what happened on 2026-07-18T09:30:00+00:00",
    "compare 2026-07-11 against 2026-02-14",
    # --- shapes an adversarial review measured as write-path FALSE POSITIVES.
    # Each one was rewritten by the write-path set and is byte-identical here.
    # FOUR-SEGMENT VERSION STRINGS and IP LITERALS (were `[ip_address]`)
    "the bug appears in version 1.2.3.4 of the parser",
    "bump to 1.20.3.4",
    "kernel 5.15.0.91 changelog",
    "protobuf 3.21.12.1 upgrade notes",
    "server on 127.0.0.1 port 8080",
    "why does it only bind to 192.168.1.10",
    # BARE 10-DIGIT RUNS: every epoch-seconds timestamp, order id, invoice
    # number (were `[phone]`, because the write-path separators are optional)
    "what happened at unix timestamp 1752969600",
    "logs around 1753000000 show the crash",
    "order number 1234567890 status",
    "invoice 9876543210 was refunded",
    # FOUR SPACE-SEPARATED 4-DIGIT GROUPS, i.e. a year list (was
    # `[credit_card]`, because the write-path separator class includes \s)
    "compare 2020 2021 2022 2023 revenue",
    # "Bearer" AS PROSE (was `[redacted]`; the query-side pattern now demands
    # a >=20-char unbroken alphanumeric run after the keyword)
    "Bearer authentication scheme",
    "what did we decide about Bearer token auth?",
    # other version and numeric runs
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
    # --- THREE-GROUP SPACE-SEPARATED NUMERIC PROSE, i.e. `NNN NNN NNNN`.
    # The corpus above had 4-4-4-4 ("compare 2020 2021 2022 2023") but never
    # 3-3-4, which is exactly why three adversarial reviewers missed that the
    # query-side phone separator class admitted a space.  It rewrote 11 of 16
    # realistic numeric queries to `[phone]`, destroying every search term.
    # These are the measured cases; they are the regression pin for that class.
    "benchmark 512 256 1024 tokens per batch",
    "took 250 500 1000 ms across runs",
    "latency p50 p95 p99 was 120 450 3200 microseconds",
    "memory 256 512 1024 MB tiers",
    "grid size 100 200 3000 nodes",
    "SELECT * FROM t WHERE id = 100 200 3000",
    # LONG BARE DIGIT RUNS that are not payment cards.  The separator-less
    # card shape is "13-19 digits in a row", which is also every long order id
    # and snowflake id; these fail Luhn and so pass through.
    "id 123456789012345 in the ledger",
    "snowflake 1234567890123456789 lookup",
    "invoice 12345678901234 reissued",
    # Korean prose carrying numbers, the primary-locale equivalent
    "한글 질의 회의 결과 정리해줘",
    "테스트 100 200 3000 건 결과 비교",
]


@pytest.mark.parametrize("query", CLEAN_QUERIES)
def test_clean_queries_pass_through_byte_identical(query):
    """A query matching no pattern is the CALLER'S OWN OBJECT, unchanged.

    Identity (``is``), not merely equality — this is the property that makes
    the retrieval impact of #140 provably zero for these queries, and it is
    what lets this ship without a paired benchmark run.
    """
    assert screen_query_for_egress(query) is query


def test_clean_query_reaches_retriever_byte_identical():
    """Same property observed at the RETRIEVER BOUNDARY, end to end."""
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)
    query = "what did we decide about the rollout on 2026-07-18?"

    asyncio.run(manager.recall_memories(query, limit=3))

    assert retriever.queries() == [query]


def test_injected_redactor_does_not_rewrite_queries():
    """``pii_redactor=`` is the SUMMARY anonymizer, not a query screen.

    Screening runs on a module-owned :class:`PIIRedactor` instead, for two
    reasons.  (1) Contract: an SDK consumer who injects a domain-specific
    redactor — product-name masking, locale rules — would otherwise have it
    silently applied to every search string with no opt-out.  (2) Provability:
    byte-identical passthrough is the whole no-benchmark argument, and it
    cannot be established for an arbitrary caller-supplied pattern set.
    """

    class ShoutyRedactor(PIIRedactor):
        def anonymize_summary(self, summary):
            return summary.replace("tea", "[topic]")

    retriever = RecordingRetriever()
    manager = _make_manager(retriever, pii_redactor=ShoutyRedactor())

    asyncio.run(manager.recall_memories("tea preferences", limit=3))

    assert retriever.queries() == ["tea preferences"]


def test_oversized_query_is_capped_not_scanned_whole():
    """The ONE documented exception to byte-identical passthrough.

    The ``email`` pattern is quadratic in the length of an unbroken
    ``[A-Za-z0-9._%+-]`` run, and ``handle_user_message`` feeds the screen the
    caller's raw message with no length bound — so a pasted 32 KB log line used
    to add ~0.6 s of blocking CPU to the turn, on a synchronous call inside an
    ``async def``.  The cap bounds that.  Queries at or under it are untouched.
    """
    at_cap = "y" * PIIRedactor.QUERY_MAX_CHARS
    assert screen_query_for_egress(at_cap) is at_cap

    over = "x" * (PIIRedactor.QUERY_MAX_CHARS + 1000)
    screened = screen_query_for_egress(over)
    assert len(screened) == PIIRedactor.QUERY_MAX_CHARS


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


def test_korean_locale_pii_is_screened():
    """The write-path pattern set is US-ASCII-shaped, so this package's own
    primary-locale PII used to pass through byte-identical and reach the wire.

    Both directions now carry the two Korean shapes that matter: the resident
    registration number (YYMMDD-Gxxxxxx, month/day validated, so far more
    precise than the US ``ssn`` shape) and the mobile number.  Both fold into
    the EXISTING descriptor vocabulary rather than inventing read-only tokens.
    See :func:`test_query_and_index_agree_on_every_descriptor` for why they
    must be shared with the write path and not query-only.

    Still open by design (stated, not overlooked): non-ASCII email local parts,
    international dialling formats, and separator-less digit runs — a bare
    ``01012345678`` is an 11-digit run indistinguishable from an identifier,
    exactly as for the ASCII shape.
    """
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)

    asyncio.run(manager.recall_memories(
        f"주민번호 {PLANTED_KR_RRN} 랑 휴대폰 {PLANTED_KR_PHONE} 확인해줘", limit=3,
    ))

    sent = retriever.seen_text()
    assert PLANTED_KR_RRN not in sent
    assert PLANTED_KR_PHONE not in sent
    assert "[ssn]" in sent
    assert "[phone]" in sent
    # the Korean prose around them survives — span excision, not line drop
    assert "주민번호" in sent
    assert "확인해줘" in sent


@pytest.mark.parametrize(
    "raw",
    [
        PLANTED_KR_PHONE,
        PLANTED_KR_RRN,
        "555-123-4567",
        "123-45-6789",
        "4532-0151-1283-0366",
    ],
)
def test_query_and_index_agree_on_every_descriptor(raw):
    """The screened QUERY and the anonymized INDEX must emit the SAME token.

    This is the invariant that makes screening retrieval-safe rather than
    retrieval-destroying, and it is not automatic — it broke once already.
    When the Korean shapes existed only on the query side, ``010-1234-5678``
    became ``[phone]`` in the query while the index still held the raw digits:
    a query that MATCHED before the screen existed MISSED after it.  Screening
    had made recall worse for the package's primary locale.

    The fix was to define those shapes once at module scope and share them,
    so this test pins the symmetry rather than the individual patterns — it
    fails for any future shape added to one direction only.
    """
    sentence = f"contact {raw} today"
    assert screen_query_for_egress(sentence) == PIIRedactor().anonymize_summary(sentence)


def test_long_digit_runs_that_are_not_cards_survive():
    """Luhn separates a pasted card from an ordinary long identifier.

    The separator-less card shape is just "13-19 digits in a row", which also
    describes every order id, ledger entry and snowflake id.  Without a
    checksum those were rewritten to ``[credit_card]`` — a measured
    byte-identity violation.  A real card always satisfies Luhn; an arbitrary
    run does so about one time in ten.
    """
    # a genuine (test-vector) card number still screens, in both forms
    assert screen_query_for_egress("card 4532015112830366 charged") == "card [credit_card] charged"
    assert screen_query_for_egress("card 4532-0151-1283-0366 x") == "card [credit_card] x"
    # ...while non-card digit runs of card-like LENGTH pass through untouched
    for benign in (
        "id 123456789012345 in the ledger",
        "snowflake 1234567890123456789 lookup",
        "invoice 12345678901234 reissued",
    ):
        assert screen_query_for_egress(benign) is benign


def test_pii_query_still_retrieves_the_anonymized_memory():
    """A raw-PII query still finds the memory stored under the descriptor.

    Scope, honestly: this is a REGRESSION test, not evidence about real
    retrieval scoring.  The stub's matching rule is lexical and of our own
    making; what it pins is that the query the scorer sees is the SCREENED one
    (it fails on revert, when ``q`` still holds the raw address).

    The premise it illustrates — that the summary index is descriptor-form —
    was traced end to end and holds for ``summary``.  It does NOT hold for
    ``payload['user_text']``/``['assistant_text']``, which carry the raw turns
    and are credential-scanned but never PII-anonymized (#139's stated known
    boundary), nor for pre-#139 rows' ``structured_metadata``.  So the
    vocabulary argument is a nice-to-have here, not the load-bearing one;
    byte-identical passthrough is.
    """
    stored_summary = PIIRedactor().anonymize_summary(
        f"Dana confirmed the rollout date by mail to {PLANTED_EMAIL}."
    )
    assert "[email]" in stored_summary  # summary index really is descriptor-form

    matched = []

    async def retriever(**kwargs):
        q = kwargs.get("query", "")
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
    # abort it again on every retry, since the message is unchanged.  The query
    # is still ISSUED (a drop is not a failure), so results come back.
    results = asyncio.run(manager.recall_memories(query, limit=3))
    assert len(results) == 1

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

    with caplog.at_level(logging.WARNING, logger="kumiho_memory.privacy"):
        asyncio.run(manager.recall_memories(
            f"is {PLANTED_CREDENTIAL} rotated?", limit=3,
        ))

    text = caplog.text
    assert "credential span" in text
    assert PLANTED_CREDENTIAL not in text


# --------------------------------------------------------------------------
# (d) fail CLOSED when screening itself breaks — and say so ACCURATELY
# --------------------------------------------------------------------------

def test_screen_failure_sends_nothing_at_all(exploding_screen):
    """Fail-closed short-circuits BEFORE the backend call.

    Not to ``"[redacted]"``: that is not an inert query, it is a live search
    term that lexically matches exactly those memories whose own text was
    credential-redacted — so a screening failure would have returned a ranked
    list biased toward the most sensitive rows in the store.
    """
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)

    results = asyncio.run(manager.recall_memories(
        f"tell me about {PLANTED_EMAIL}", limit=3,
    ))

    assert retriever.calls == [], "a failed screen still hit the backend"
    # Load-bearing: RecordingRetriever returns a non-empty result set, so []
    # can only come from the short circuit.
    assert results == []
    # The caller learns WHY the set is empty instead of inferring a miss.
    assert "screening failed" in (manager._last_backend_error or "")


def test_screen_failure_is_not_reported_as_a_credential_hit(
    exploding_screen, caplog,
):
    """A crashed screen must not tell the operator a secret was found.

    The write-path helper collapses both conditions into one counter, so a
    redactor that merely raised logged "removed 1 credential span(s)" — a
    signal pointing away from the real cause.  ``screen_query`` returns
    ``failed`` separately from ``dropped`` so the two stay distinguishable.
    """
    manager = _make_manager(RecordingRetriever())

    with caplog.at_level(logging.WARNING, logger="kumiho_memory.privacy"):
        asyncio.run(manager.recall_memories(
            "what did we decide about the rollout?", limit=3,
        ))

    text = caplog.text
    assert "screening FAILED" in text
    assert "credential span" not in text


def test_residual_credential_after_excision_fails_closed():
    """Stage [3], the verification pass, is a real gate — not decoration.

    Credential excision runs BEFORE the PII pass, so anything the PII pass
    introduces has never been screened.  This subclass makes that concrete with
    a descriptor that is itself credential-shaped; only verification can catch
    it, and it must report FAILED (not a credential drop) and yield nothing
    usable.
    """

    class _ReintroducingRedactor(PIIRedactor):
        QUERY_PII_PATTERNS = (
            ("Bearer " + "A" * 25, r"\bWIDGET\b"),
        )

    screened, dropped, failed = _ReintroducingRedactor().screen_query(
        "the WIDGET rollout",
    )

    assert failed is True
    assert dropped == 0, "a screening failure must not be counted as a drop"
    assert screened == "[redacted]"


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


def test_graph_recall_screens_when_driven_directly():
    """``GraphAugmentedRecall`` is re-exported at package top level, so an
    external harness reaches ``_reformulate_query``'s LLM call without ever
    constructing a manager.  The screen has to be inside ``recall`` too.
    """
    from kumiho_memory.graph_augmentation import GraphAugmentedRecall

    seen = []

    async def recall_fn(query, *, limit, space_paths, memory_types):
        seen.append(query)
        return []

    gr = GraphAugmentedRecall(recall_fn=recall_fn)
    asyncio.run(gr.recall(f"who is {PLANTED_EMAIL}", limit=3))

    assert seen, "recall leg was not exercised"
    assert PLANTED_EMAIL not in seen[0]
    assert "[email]" in seen[0]


# --------------------------------------------------------------------------
# (f) the caller's input is never shared with what goes on the wire
# --------------------------------------------------------------------------

def test_screened_query_is_a_distinct_object_from_the_caller_s():
    """When screening changes the text, the retriever gets a NEW object and the
    caller's own string is untouched.

    (Asserting only ``query == original`` would be vacuous — Python strings are
    immutable, so no implementation could fail it.)
    """
    retriever = RecordingRetriever()
    manager = _make_manager(retriever)
    query = f"mail {PLANTED_EMAIL} now"

    asyncio.run(manager.recall_memories(query, limit=3))

    sent = retriever.queries()[0]
    assert sent is not query
    assert PLANTED_EMAIL in query      # caller keeps the raw local copy
    assert PLANTED_EMAIL not in sent   # the wire does not


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

class _RecordingEmbedder:
    def __init__(self):
        self.batches = []

    def embed(self, texts):
        self.batches.append(list(texts))
        return [[1.0, 0.0] for _ in texts]


def test_sibling_embedding_filter_screens_the_query():
    """``build_recalled_context`` is called by ``tool_memory_engage`` with the
    tool's RAW query, independently of the recall — so a ``recall_memories``
    screen does not reach this remote embedding call.  It has its own.
    """
    embedder = _RecordingEmbedder()
    manager = _make_manager(
        RecordingRetriever(),
        embedding_adapter=embedder,
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

    assert embedder.batches, "embedding leg was not exercised"
    sent = "\n".join(embedder.batches[0])
    assert PLANTED_EMAIL not in sent
    assert "[email]" in sent


def test_two_pass_rerank_screens_when_imported_directly():
    """The screen lives in ``two_pass_rerank`` itself, not in the manager
    method that calls it.

    ``two_pass_rerank`` is re-exported at package top level, so an external
    harness — the very consumer the manager-level screen was written for — can
    ``from kumiho_memory import two_pass_rerank`` and reach the remote
    embedding endpoint with a raw query, never touching the manager at all.
    """
    from kumiho_memory import two_pass_rerank

    embedder = _RecordingEmbedder()
    two_pass_rerank(
        f"who is {PLANTED_EMAIL}", [{"title": "t", "summary": "s"}], embedder,
    )

    assert embedder.batches, "embedding leg was not exercised"
    sent = "\n".join(embedder.batches[0])
    assert PLANTED_EMAIL not in sent
    assert "[email]" in sent


def test_rerank_memories_delegates_to_the_screened_boundary():
    """The manager method inherits the screen from ``two_pass_rerank``."""
    embedder = _RecordingEmbedder()
    manager = _make_manager(RecordingRetriever(), embedding_adapter=embedder)

    manager.rerank_memories(
        [{"title": "t", "summary": "s"}], f"who is {PLANTED_EMAIL}",
    )

    assert embedder.batches, "two_pass_rerank embedding leg was not exercised"
    sent = "\n".join(embedder.batches[0])
    assert PLANTED_EMAIL not in sent
    assert "[email]" in sent


def test_code_why_screens_the_question(monkeypatch):
    """``code_query.why`` fans the question out to two direct ``kumiho.search``
    RPCs, bypassing ``recall_memories`` entirely.

    Without this test the ``code_why`` screen is the one choke point that can
    be deleted by a refactor with the suite still green — the other three each
    fail loudly.
    """
    monkeypatch.setenv("KUMIHO_MEMORY_CODE", "1")
    manager = _make_manager(RecordingRetriever())
    # Stubbed rather than built: the real context constructs an LLM adapter and
    # needs live credentials.  The screen under test sits between this and the
    # `why` call, so the stub is faithful for the property being pinned.
    monkeypatch.setattr(
        manager, "_code_memory_context",
        lambda: (object(), "proj", None, "model"),
    )

    seen = []

    async def _fake_why(question, **kwargs):
        seen.append(question)
        return {"decisions": [], "context": ""}

    monkeypatch.setattr("kumiho_memory.code_query.why", _fake_why)

    asyncio.run(manager.code_why(f"why did we mail {PLANTED_EMAIL}"))

    assert seen, "code_why leg was not exercised"
    assert PLANTED_EMAIL not in seen[0]
    assert "[email]" in seen[0]


# --------------------------------------------------------------------------
# (i) helper-level edge cases
# --------------------------------------------------------------------------

def test_screen_is_idempotent():
    """Descriptors match no pattern, so a second pass is a byte-identical
    no-op.  That is what keeps the downstream choke points free on the
    already-screened recall path.
    """
    once = screen_query_for_egress(
        f"mail {PLANTED_EMAIL} key {PLANTED_CREDENTIAL}",
    )
    assert screen_query_for_egress(once) is once


def test_container_queries_are_screened_not_passed_through():
    """The MCP boundary forwards ``args["query"]`` with no type check, and the
    package already treats message ``content`` as possibly a list of multimodal
    blocks.  A non-``str`` query must not bypass the screen — that would make
    "covers every caller by construction" false.
    """
    screened = screen_query_for_egress(["contact", PLANTED_EMAIL])
    assert PLANTED_EMAIL not in screened
    assert "[email]" in screened[1]

    nested = screen_query_for_egress({"q": [PLANTED_EMAIL], "limit": 5})
    assert PLANTED_EMAIL not in nested["q"][0]
    assert nested["limit"] == 5

    # ...and a clean container is still the caller's own object.
    clean = ["what did we decide", "about the rollout"]
    assert screen_query_for_egress(clean) is clean


def test_screen_tolerates_empty_and_non_text_queries():
    assert screen_query_for_egress("") == ""
    assert screen_query_for_egress(None) is None
    assert screen_query_for_egress(7) == 7


def test_failed_container_element_fails_the_whole_query(exploding_screen):
    """One unscreenable element poisons the container — no partial egress."""
    assert screen_query_for_egress(["ok", "also ok"]) is QUERY_SCREEN_FAILED
