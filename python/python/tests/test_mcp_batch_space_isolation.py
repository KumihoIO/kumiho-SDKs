"""``tool_memory_store_batch``: one unusable space hint must not lose the batch.

Phase 1 of the batch resolves every capture's space with ``_ensure_space_path``.
That helper creates each missing segment, and a server may refuse a segment
(INVALID_ARGUMENT for edge whitespace such as ``"alpha / beta"`` or an empty
segment such as ``"a//b"``).  The refusal used to escape Phase 1 and the whole
call raised, so captures with perfectly good hints were lost with the bad one.

The contract pinned here:

* a capture whose space cannot be created becomes ``{"error": ...}`` at its own
  position and the remaining captures are still written in the one batch call;
* hints that resolve today keep EXACTLY the space path and request they always
  had.  The batch path does not slugify hints (the single-capture path does), so
  ``"Alpha/Beta Gamma"`` still creates spaces ``Alpha`` and ``Beta Gamma``.
  Slugifying would silently move those captures to different spaces.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import grpc
import pytest

PROJECT = "CognitiveMemory"


class _FakeRpcError(grpc.RpcError):
    def __init__(self, code: grpc.StatusCode, details: str) -> None:
        super().__init__(details)
        self._code = code
        self._details = details

    def code(self) -> grpc.StatusCode:
        return self._code

    def details(self) -> str:
        return self._details


class _ServerProject:
    """A project whose ``create_space`` behaves like a validating server."""

    name = PROJECT

    def __init__(self) -> None:
        self.created: list[tuple[str, str]] = []
        self.attempted: list[tuple[str, str]] = []
        self._existing: set[tuple[str, str]] = set()

    def create_space(self, name: str, parent_path: str = "/") -> object:
        self.attempted.append((name, parent_path))
        if name == "boom":
            raise RuntimeError("transport exploded")
        if not name or name != name.strip():
            raise _FakeRpcError(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"space name {name!r} must not be empty or have edge whitespace",
            )
        if (name, parent_path) in self._existing:
            raise _FakeRpcError(grpc.StatusCode.ALREADY_EXISTS, "exists")
        self._existing.add((name, parent_path))
        self.created.append((name, parent_path))
        return MagicMock()


@pytest.fixture
def batch_env(monkeypatch):
    import kumiho
    from kumiho import mcp_server

    project = _ServerProject()
    seen: dict = {"batch_calls": []}

    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: True)
    monkeypatch.setattr(mcp_server, "_get_project_cached", lambda name: project)
    monkeypatch.setattr(mcp_server, "_known_spaces", set())
    monkeypatch.setattr(
        mcp_server, "_find_similar_item", lambda *a, **k: (None, 0.0, 0.0, 0.0)
    )
    monkeypatch.setattr(mcp_server, "_write_memory_artifact", lambda **kw: "")
    monkeypatch.setattr(mcp_server, "_get_or_create_bundle", lambda *a, **k: MagicMock())
    monkeypatch.setattr(kumiho, "get_item", lambda uri: MagicMock())

    def fake_batch(rows, idempotency_prefix=""):
        seen["batch_calls"].append(rows)
        revs = []
        for row in rows:
            rev = MagicMock()
            rev.kref.uri = row["item_kref"] + "?r=1"
            revs.append(rev)
        return (revs, [])

    monkeypatch.setattr(kumiho, "batch_create_revisions", fake_batch)
    seen["project"] = project
    return seen


def _capture(title: str, space_hint: str) -> dict:
    return {
        "type": "fact",
        "title": title,
        "content": f"content of {title}",
        "space_hint": space_hint,
    }


def _store_batch(captures, **kwargs):
    from kumiho import mcp_server

    return mcp_server.tool_memory_store_batch(captures=captures, project=PROJECT, **kwargs)


def test_unusable_hint_costs_only_its_own_capture(batch_env):
    out = _store_batch(
        [
            _capture("first", "alpha"),
            _capture("edge whitespace", "alpha / beta"),
            _capture("empty segment", "a//b"),
            _capture("last", "gamma"),
        ]
    )

    first, edge_ws, empty_seg, last = out["results"]
    assert len(out["results"]) == 4, "results stay positional"
    assert first["revision_kref"] and last["revision_kref"]
    assert first["item_kref"].startswith("kref://CognitiveMemory/alpha/")
    assert last["item_kref"].startswith("kref://CognitiveMemory/gamma/")

    # The failed captures use the same shape the batch uses for rejected rows.
    for bad, hint in ((edge_ws, "alpha / beta"), (empty_seg, "a//b")):
        assert set(bad) == {"error"}
        assert isinstance(bad["error"], str)
        assert repr(hint) in bad["error"]
        assert "INVALID_ARGUMENT" in bad["error"]

    # The good captures still went out in ONE batched write, and only they did.
    assert len(batch_env["batch_calls"]) == 1
    rows = batch_env["batch_calls"][0]
    assert [r["item_kref"].split("/")[3] for r in rows] == ["alpha", "gamma"]
    assert out["stored_krefs"] == [first["revision_kref"], last["revision_kref"]]


def test_every_capture_failing_returns_errors_and_writes_nothing(batch_env):
    out = _store_batch([_capture("one", "x / y"), _capture("two", "p//q")])

    assert all("error" in r and "revision_kref" not in r for r in out["results"])
    assert out["stored_krefs"] == []
    assert out["stacked"] == 0
    assert batch_env["batch_calls"] == []


def test_a_non_grpc_failure_is_isolated_too(batch_env):
    out = _store_batch([_capture("boom", "boom"), _capture("fine", "fine")])

    assert out["results"][0]["error"].endswith("transport exploded")
    assert out["results"][1]["revision_kref"]
    assert len(batch_env["batch_calls"][0]) == 1


def test_a_failed_hint_is_not_remembered_as_an_existing_space(batch_env):
    # Phase 1 must not mark a half-created path as known: the same refused
    # hint fails again, and a later valid hint still resolves normally.
    first = _store_batch([_capture("a", "ok / bad")])
    second = _store_batch([_capture("b", "ok / bad"), _capture("c", "ok/good")])

    assert "error" in first["results"][0]
    assert "error" in second["results"][0]
    assert second["results"][1]["item_kref"].startswith("kref://CognitiveMemory/ok/good/")


def test_hints_that_work_today_keep_their_exact_space_path(batch_env):
    """No slugification on the batch path: uppercase and interior spaces stay."""
    out = _store_batch(
        [
            _capture("mixed case and interior space", "Alpha/Beta Gamma"),
            _capture("leading and trailing slash", "/Delta/"),
            _capture("falls back to space_path", ""),
        ],
        space_path="Fallback/Space Path",
    )

    assert all("error" not in r for r in out["results"]), out["results"]
    rows = batch_env["batch_calls"][0]
    assert [r["metadata"]["space"] for r in rows] == [
        "/CognitiveMemory/Alpha/Beta Gamma",
        "/CognitiveMemory/Delta",
        "/CognitiveMemory/Fallback/Space Path",
    ]
    assert rows[0]["item_kref"].startswith("kref://CognitiveMemory/Alpha/Beta Gamma/")
    assert rows[1]["item_kref"].startswith("kref://CognitiveMemory/Delta/")
    assert rows[2]["item_kref"].startswith("kref://CognitiveMemory/Fallback/Space Path/")
    assert batch_env["project"].created == [
        ("Alpha", "/CognitiveMemory"),
        ("Beta Gamma", "/CognitiveMemory/Alpha"),
        ("Delta", "/CognitiveMemory"),
        ("Fallback", "/CognitiveMemory"),
        ("Space Path", "/CognitiveMemory/Fallback"),
    ]
