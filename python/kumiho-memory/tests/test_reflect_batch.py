"""Batch-aware reflect (kumiho-SDKs#71) + core store-batch unit checks.

Layer 1: ``tool_memory_reflect`` routes through ``tool_memory_store_batch``
when — and only when — the caller supplies an ``idempotency_prefix`` with more
than one capture; live reflects (no prefix) keep the per-capture loop
byte-identical. ``capture_results`` is positionally 1:1 in both paths.

Layer 2: ``kumiho.mcp_server.tool_memory_store_batch`` builds rows, isolates
per-capture failures, forwards the idempotency prefix, and aligns results.
"""

from unittest.mock import patch

from test_mcp_tools import _cleanup_manager, _install_test_manager

from kumiho_memory.mcp_tools import tool_memory_ingest, tool_memory_reflect


def _two_captures():
    return [
        {"type": "summary", "title": "Digest (2026-03-14)",
         "content": "Session digest.", "event_date": "2026-03-14"},
        {"type": "decision", "title": "Chose bge-m3 on 2026-03-14",
         "content": "bge-m3 over OpenAI embeddings.", "event_date": "2026-03-14"},
    ]


def _batch_recorder(calls, fail_index=None):
    def fake_batch(**kwargs):
        calls.append(kwargs)
        results = []
        for i, _cap in enumerate(kwargs["captures"]):
            if i == fail_index:
                results.append({"error": "batch row rejected"})
            else:
                results.append({"revision_kref": f"kref://memory/batch/{i}",
                                "item_kref": "kref://memory/item"})
        return {"results": results, "succeeded": len(results) - (fail_index is not None)}
    return fake_batch


def test_reflect_batches_with_idempotency_prefix():
    """Prefix + >1 capture -> one batch call; krefs aligned; event_date validated."""
    try:
        _install_test_manager()
        ingest = tool_memory_ingest({"user_id": "u-batch", "message": "hi"})
        batch_calls, store_calls = [], []

        def fake_store(**kwargs):
            store_calls.append(kwargs)
            return {"revision_kref": "kref://memory/single"}

        with patch("kumiho.mcp_server.tool_memory_store", fake_store), \
             patch("kumiho.mcp_server.tool_memory_store_batch",
                   _batch_recorder(batch_calls), create=True):
            result = tool_memory_reflect({
                "session_id": ingest["session_id"],
                "response": "Noted.",
                "captures": _two_captures(),
                "discover_edges": False,
                "idempotency_prefix": "backfill:sess-1",
            })
        assert len(batch_calls) == 1 and store_calls == []
        call = batch_calls[0]
        assert call["idempotency_prefix"] == "backfill:sess-1"
        assert [c["memory_type"] for c in call["captures"]] == ["summary", "decision"]
        assert all(c["metadata"] == {"event_date": "2026-03-14"}
                   for c in call["captures"])
        assert result["captures_stored"] == 2
        assert result["stored_krefs"] == ["kref://memory/batch/0", "kref://memory/batch/1"]
        assert [r.get("revision_kref") for r in result["capture_results"]] == \
               ["kref://memory/batch/0", "kref://memory/batch/1"]
    finally:
        _cleanup_manager()


def test_reflect_without_prefix_keeps_per_capture_loop():
    """No prefix -> the pre-#71 loop, even with the batch function available."""
    try:
        _install_test_manager()
        ingest = tool_memory_ingest({"user_id": "u-loop", "message": "hi"})
        batch_calls, store_calls = [], []

        def fake_store(**kwargs):
            store_calls.append(kwargs)
            return {"revision_kref": f"kref://memory/single/{len(store_calls)}"}

        with patch("kumiho.mcp_server.tool_memory_store", fake_store), \
             patch("kumiho.mcp_server.tool_memory_store_batch",
                   _batch_recorder(batch_calls), create=True):
            result = tool_memory_reflect({
                "session_id": ingest["session_id"],
                "response": "Noted.",
                "captures": _two_captures(),
                "discover_edges": False,
            })
        assert batch_calls == [] and len(store_calls) == 2
        assert result["captures_stored"] == 2
        assert len(result["capture_results"]) == 2
    finally:
        _cleanup_manager()


def test_reflect_batch_row_failure_stays_aligned():
    """A rejected row surfaces as an aligned error; the rest still store."""
    try:
        _install_test_manager()
        ingest = tool_memory_ingest({"user_id": "u-fail", "message": "hi"})
        batch_calls = []
        with patch("kumiho.mcp_server.tool_memory_store_batch",
                   _batch_recorder(batch_calls, fail_index=0), create=True):
            result = tool_memory_reflect({
                "session_id": ingest["session_id"],
                "response": "Noted.",
                "captures": _two_captures(),
                "discover_edges": False,
                "idempotency_prefix": "backfill:sess-2",
            })
        assert result["captures_stored"] == 1
        assert "error" in result["capture_results"][0]
        assert result["capture_results"][1]["revision_kref"] == "kref://memory/batch/1"
    finally:
        _cleanup_manager()


# ---------------------------------------------------------------------------
# Layer 2 — kumiho.mcp_server.tool_memory_store_batch unit checks
# ---------------------------------------------------------------------------

def test_core_store_batch_rows_isolation_and_alignment(monkeypatch, tmp_path):
    import kumiho.mcp_server as core

    monkeypatch.setattr(core, "_ensure_configured", lambda: True)
    monkeypatch.setattr(core, "_get_project_cached", lambda name: object())
    monkeypatch.setattr(core, "_ensure_space_path",
                        lambda project, path: f"/CognitiveMemory/{path or 'conversations'}")
    monkeypatch.setattr(core, "_find_similar_item", lambda *a, **k: None)
    monkeypatch.setattr(
        core, "_write_memory_artifact",
        lambda **kwargs: str(tmp_path / f"{kwargs['item_name']}.md"))
    monkeypatch.setattr(core, "_get_or_create_bundle",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no bundle")))

    class FakeRevision:
        def __init__(self, i):
            self.kref = type("K", (), {"uri": f"kref://CognitiveMemory/conv/x.conversation?r={i}"})()
            self.tags_applied = []

        def tag(self, t):
            self.tags_applied.append(t)

    batch_calls = {}

    def fake_batch_create(rows, idempotency_prefix=""):
        batch_calls["rows"] = rows
        batch_calls["prefix"] = idempotency_prefix
        results = [FakeRevision(i) if i != 1 else None for i in range(len(rows))]
        return results, ([(1, "missing space")] if len(rows) > 1 else [])

    monkeypatch.setattr(core.kumiho, "batch_create_revisions", fake_batch_create,
                        raising=False)

    captures = [
        {"memory_type": "summary", "title": "Digest", "summary": "ok",
         "assistant_text": "ok", "metadata": {"event_date": "2026-03-14"}},
        {"memory_type": "fact", "title": "Doomed row", "summary": "ok",
         "assistant_text": "ok"},
        {"memory_type": "fact", "title": "Key row", "summary": "x",
         "assistant_text": 'api_key = "supersecretvalue1"'},  # credential -> pre-batch reject
        {"memory_type": "fact", "title": "Fine row", "summary": "ok",
         "assistant_text": "ok"},
    ]
    out = core.tool_memory_store_batch(
        captures, project="CognitiveMemory", idempotency_prefix="backfill:s")

    assert batch_calls["prefix"] == "backfill:s"
    # Credential capture never reached the server: 3 rows for 4 captures.
    assert len(batch_calls["rows"]) == 3
    assert all(row["artifacts"][0]["name"] == "chat_io" for row in batch_calls["rows"])
    assert batch_calls["rows"][0]["metadata"]["event_date"] == "2026-03-14"

    results = out["results"]
    assert len(results) == 4 and out["succeeded"] == 2
    assert results[0]["revision_kref"].endswith("?r=0")
    assert results[1]["error"] == "missing space"
    assert "Credential pattern detected" in results[2]["error"]
    assert results[3]["revision_kref"].endswith("?r=2")
    assert results[0]["stacked"] is False


def test_core_item_kref_construction():
    from kumiho.mcp_server import _item_kref_for

    assert _item_kref_for("Proj", "/Proj/conv", "name", "conversation") == \
        "kref://Proj/conv/name.conversation"
    assert _item_kref_for("Proj", "conv/sub", "name", "conversation") == \
        "kref://Proj/conv/sub/name.conversation"
    assert _item_kref_for("Proj", "", "name", "conversation") == \
        "kref://Proj/name.conversation"
