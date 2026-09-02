"""The hosted connector surface: profiles, annotations, instructions, tenancy.

Everything here exists because one process is about to stop belonging to one
user. The stdio server is single-tenant by construction, so it could key its
caches by project name, publish a caller-supplied token into ``os.environ`` and
write memory artifacts under ``~/.kumiho`` — all correct for exactly one user
and a cross-tenant leak for two. These tests pin the difference.

They also pin the connector's *shape*: which tools it lists (the directory
syncs whatever is exposed, so an accidental ``kumiho_delete_project`` is a
public one), what each tool claims about itself (Anthropic's directory
requires a title plus a read-only or destructive hint on every listed tool),
and the protocol the server hands the model at ``initialize`` — the only
channel a remote connector has, since there is no skill and no hook out there.

Assertions run against whichever mcp major is installed; dispatch goes through
the shared ``_dispatch`` helper for that reason.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import threading
from typing import Any, Dict, List

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

import kumiho  # noqa: E402
from kumiho import mcp_server  # noqa: E402
from kumiho.mcp_server import (  # noqa: E402
    CONNECTOR_INSTRUCTIONS,
    CONNECTOR_PROFILE_TOOLS,
    TOOL_ANNOTATIONS,
    TOOL_PROFILES,
    _MCP_HAS_DECORATORS,
    create_mcp_server,
    resolve_tool_profile,
    tools_for_profile,
)
from kumiho.request_context import RequestContext, request_context  # noqa: E402

# Reuse the version-agnostic handler driver rather than growing a second copy;
# its module docstring explains why results are read through model_dump.
from test_mcp_server_construction import _dispatch  # noqa: E402


# ---------------------------------------------------------------------------
# kumiho.request_context
# ---------------------------------------------------------------------------


def test_the_four_names_are_exported_from_kumiho() -> None:
    """WP-B and WP-C import these off ``kumiho``, not off the submodule."""
    for name in ("RequestContext", "current_request", "request_context", "hosted_mode"):
        assert hasattr(kumiho, name), name
        assert name in kumiho.__all__, name


def test_current_request_is_none_outside_a_request() -> None:
    assert kumiho.current_request() is None


def test_request_context_binds_and_resets() -> None:
    ctx = RequestContext(tenant_id="t-1", user_id="u-1", auth_token="jwt")
    with request_context(ctx) as bound:
        assert bound is ctx
        assert kumiho.current_request() is ctx
    assert kumiho.current_request() is None


def test_request_context_nests_without_leaking() -> None:
    outer = RequestContext(tenant_id="t-outer", user_id="u", auth_token="a")
    inner = RequestContext(tenant_id="t-inner", user_id="u", auth_token="b")
    with request_context(outer):
        with request_context(inner):
            assert kumiho.current_request().tenant_id == "t-inner"
        assert kumiho.current_request().tenant_id == "t-outer"
    assert kumiho.current_request() is None


def test_request_context_resets_on_exception() -> None:
    """A leaked context is a tenant leak, so the reset must survive a raise."""
    with pytest.raises(RuntimeError):
        with request_context(RequestContext(tenant_id="t", user_id="u", auth_token="a")):
            raise RuntimeError("boom")
    assert kumiho.current_request() is None


def test_request_context_is_immutable() -> None:
    """Mutating it would change it for every frame sharing the context copy."""
    ctx = RequestContext(tenant_id="t", user_id="u", auth_token="a")
    with pytest.raises(Exception):
        ctx.tenant_id = "other"  # type: ignore[misc]


def test_request_context_defaults() -> None:
    ctx = RequestContext(tenant_id="t", user_id="u", auth_token="a")
    assert ctx.context == "claude"
    assert ctx.session_id is None
    assert ctx.scopes == []


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", True), ("true", True), ("TRUE", True), ("yes", True), (" 1 ", True),
        ("0", False), ("", False), ("no", False), ("maybe", False),
    ],
)
def test_hosted_mode_reads_the_env_flag(
    monkeypatch: pytest.MonkeyPatch, value: str, expected: bool
) -> None:
    monkeypatch.setenv("KUMIHO_MCP_HOSTED", value)
    assert kumiho.hosted_mode() is expected


def test_hosted_mode_is_off_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KUMIHO_MCP_HOSTED", raising=False)
    assert kumiho.hosted_mode() is False


# ---------------------------------------------------------------------------
# TOOL_ANNOTATIONS
# ---------------------------------------------------------------------------

#: Every tool name that can appear in TOOLS: the 45 this module defines plus
#: the 18 kumiho-memory appends at import time (13 memory + 4 env-gated
#: ``kumiho_code_*`` + the ontology tool). Written out rather than derived from
#: TOOLS on purpose — deriving it would make the coverage test tautological,
#: and would go quiet exactly when kumiho-memory is missing or a gate is shut.
EXPECTED_ANNOTATED_TOOLS = {
    # Core (45)
    "kumiho_list_projects", "kumiho_get_project", "kumiho_get_spaces",
    "kumiho_get_space", "kumiho_get_item", "kumiho_search_items",
    "kumiho_fulltext_search", "kumiho_memory_store", "kumiho_memory_retrieve",
    "kumiho_get_item_revisions", "kumiho_get_revision",
    "kumiho_get_revision_by_tag", "kumiho_get_revision_as_of",
    "kumiho_batch_get_revisions", "kumiho_get_artifacts", "kumiho_get_artifact",
    "kumiho_get_bundle", "kumiho_resolve_kref",
    "kumiho_get_artifacts_by_location", "kumiho_get_dependencies",
    "kumiho_get_dependents", "kumiho_get_provenance_summary",
    "kumiho_analyze_impact", "kumiho_find_path", "kumiho_get_edges",
    "kumiho_create_revision", "kumiho_tag_revision", "kumiho_create_edge",
    "kumiho_create_project", "kumiho_create_space", "kumiho_create_item",
    "kumiho_create_artifact", "kumiho_create_bundle", "kumiho_delete_project",
    "kumiho_delete_space", "kumiho_delete_item", "kumiho_delete_revision",
    "kumiho_delete_artifact", "kumiho_delete_edge", "kumiho_untag_revision",
    "kumiho_set_metadata", "kumiho_deprecate_item", "kumiho_add_bundle_member",
    "kumiho_remove_bundle_member", "kumiho_get_bundle_members",
    # kumiho-memory (18)
    "kumiho_chat_add", "kumiho_chat_get", "kumiho_chat_clear",
    "kumiho_memory_ingest", "kumiho_memory_add_response",
    "kumiho_memory_consolidate", "kumiho_memory_recall",
    "kumiho_memory_discover_edges", "kumiho_memory_store_execution",
    "kumiho_memory_engage", "kumiho_memory_reflect", "kumiho_memory_dream_state",
    "kumiho_memory_space_profile", "kumiho_memory_decompose",
    "kumiho_code_why", "kumiho_code_ingest", "kumiho_code_capture",
    "kumiho_code_mine_session",
}


def test_the_annotation_table_covers_every_known_tool() -> None:
    assert set(TOOL_ANNOTATIONS) == EXPECTED_ANNOTATED_TOOLS
    assert len(TOOL_ANNOTATIONS) == 63


def test_every_tool_in_the_merged_list_has_an_annotation() -> None:
    """The directory requires a title on everything exposed.

    ``TOOLS`` is the *merged* list — kumiho-memory extends it at import time —
    so this is what catches a memory tool that ships without an entry here.
    """
    unannotated = [t["name"] for t in mcp_server.TOOLS if t["name"] not in TOOL_ANNOTATIONS]
    assert unannotated == []


@pytest.mark.parametrize("name", sorted(TOOL_ANNOTATIONS))
def test_each_annotation_is_complete_and_well_typed(name: str) -> None:
    spec = TOOL_ANNOTATIONS[name]
    assert set(spec) == set(mcp_server._ANNOTATION_FIELDS)
    assert isinstance(spec["title"], str) and spec["title"].strip()
    for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
        assert isinstance(spec[hint], bool), hint
    # Every tool addresses one closed system: the caller's own Kumiho graph.
    assert spec["openWorldHint"] is False
    # destructiveHint is only meaningful when the tool writes at all; a
    # read-only destructive tool is a contradiction a client cannot act on.
    if spec["readOnlyHint"]:
        assert spec["destructiveHint"] is False, name


def test_the_forget_verb_keeps_its_user_facing_title() -> None:
    """The directory shows the title, not the tool name."""
    assert TOOL_ANNOTATIONS["kumiho_deprecate_item"]["title"] == "Forget a memory"
    assert TOOL_ANNOTATIONS["kumiho_deprecate_item"]["destructiveHint"] is True


def test_every_delete_tool_is_marked_destructive() -> None:
    for name, spec in TOOL_ANNOTATIONS.items():
        if name.startswith("kumiho_delete_"):
            assert spec["destructiveHint"] is True, name
            assert spec["readOnlyHint"] is False, name


# ---------------------------------------------------------------------------
# Profile resolution
# ---------------------------------------------------------------------------


def test_profiles_are_full_and_connector() -> None:
    assert TOOL_PROFILES == ("full", "connector")


def test_no_profile_means_full(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KUMIHO_MCP_TOOL_PROFILE", raising=False)
    assert resolve_tool_profile(None) == "full"
    assert resolve_tool_profile("") == "full"
    assert resolve_tool_profile("  ") == "full"


def test_profile_falls_back_to_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KUMIHO_MCP_TOOL_PROFILE", "connector")
    assert resolve_tool_profile(None) == "connector"


def test_an_explicit_profile_beats_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KUMIHO_MCP_TOOL_PROFILE", "connector")
    assert resolve_tool_profile("full") == "full"


def test_profile_names_are_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KUMIHO_MCP_TOOL_PROFILE", raising=False)
    assert resolve_tool_profile("Connector") == "connector"
    assert resolve_tool_profile(" FULL ") == "full"


def test_an_empty_env_value_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KUMIHO_MCP_TOOL_PROFILE", "")
    assert resolve_tool_profile(None) == "full"


@pytest.mark.parametrize("bad", ["connectors", "readonly", "FULLL", "none"])
def test_an_unknown_profile_raises_and_names_the_valid_ones(bad: str) -> None:
    """Silently serving everything on a typo would publish every destructive
    tool to a public connector."""
    with pytest.raises(ValueError) as exc:
        resolve_tool_profile(bad)
    message = str(exc.value)
    assert repr(bad) in message
    for valid in TOOL_PROFILES:
        assert repr(valid) in message


def test_an_unknown_env_profile_raises_at_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KUMIHO_MCP_TOOL_PROFILE", "nope")
    with pytest.raises(ValueError):
        create_mcp_server()


# ---------------------------------------------------------------------------
# The connector tool list
# ---------------------------------------------------------------------------

#: The curated surface: the connector plan §2.2 table, less
#: ``kumiho_memory_dream_state`` (see the exclusion test below). The column
#: comments are the plan's, so ``kumiho_memory_space_profile`` sits under Read
#: here even though its own hints say otherwise — membership is what this pins.
SPEC_CONNECTOR_TOOLS = {
    # Read (11)
    "kumiho_memory_engage", "kumiho_memory_recall", "kumiho_memory_retrieve",
    "kumiho_memory_space_profile", "kumiho_chat_get", "kumiho_search_items",
    "kumiho_get_item", "kumiho_get_revision_by_tag", "kumiho_list_projects",
    "kumiho_get_spaces", "kumiho_get_provenance_summary",
    # Write (5)
    "kumiho_memory_reflect", "kumiho_memory_store", "kumiho_memory_consolidate",
    "kumiho_memory_decompose", "kumiho_create_space",
    # Destructive (2)
    "kumiho_deprecate_item", "kumiho_chat_clear",
}


def test_the_connector_profile_is_the_eighteen_specified_tools() -> None:
    assert len(CONNECTOR_PROFILE_TOOLS) == 18
    assert len(set(CONNECTOR_PROFILE_TOOLS)) == 18, "duplicate entry"
    assert set(CONNECTOR_PROFILE_TOOLS) == SPEC_CONNECTOR_TOOLS


def test_dream_state_is_withheld_from_the_connector_but_stays_annotated() -> None:
    """Listing it would publish a tool that cannot run.

    Its assessment pass needs an LLM key and hosted tenants are keyless (plan
    §1.10), so it would fail at call time — which directory review catches
    head-on, since it asks the submitter to confirm every listed tool has been
    run. The annotation stays because the full profile still serves it.
    """
    assert "kumiho_memory_dream_state" not in CONNECTOR_PROFILE_TOOLS
    assert "kumiho_memory_dream_state" in TOOL_ANNOTATIONS
    assert TOOL_ANNOTATIONS["kumiho_memory_dream_state"]["destructiveHint"] is True


def test_every_connector_tool_can_run_without_an_llm_key() -> None:
    """The keyless-core rule (plan §1.10), as a list rather than a habit.

    Every remaining connector tool is either a read or a keyless write — the
    agent does the reasoning and the tool just stores it. A tool that needs a
    summarizer belongs in the full profile until per-tenant metering exists.
    """
    needs_a_model = {
        "kumiho_memory_dream_state",  # LLM assessment pass
        "kumiho_code_ingest",         # batch-mines a commit range with a model
        "kumiho_code_mine_session",   # mines the transcript with a model
    }
    assert set(CONNECTOR_PROFILE_TOOLS) & needs_a_model == set()


def test_every_connector_tool_is_annotated() -> None:
    assert set(CONNECTOR_PROFILE_TOOLS) <= set(TOOL_ANNOTATIONS)


def test_the_connector_profile_exposes_no_delete_tool() -> None:
    """The two destructive entries are deliberate and narrow; nothing that
    removes a project, space, item or revision belongs on a public connector."""
    for name in CONNECTOR_PROFILE_TOOLS:
        assert not name.startswith("kumiho_delete_"), name


@pytest.fixture
def every_connector_tool_registered(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Stub any connector tool the installed kumiho-memory does not ship.

    The 18 names include tools that only exist in a current kumiho-memory
    (``kumiho_memory_space_profile``, ``kumiho_memory_decompose``). Without
    this, an exact-membership assertion would silently weaken into "whatever
    happens to be installed" — which is the assertion least worth making.
    """
    present = {t["name"] for t in mcp_server.TOOLS}
    stubs = [
        {"name": name, "description": f"stub: {name}", "inputSchema": {"type": "object"}}
        for name in CONNECTOR_PROFILE_TOOLS
        if name not in present
    ]
    monkeypatch.setattr(mcp_server, "TOOLS", list(mcp_server.TOOLS) + stubs)
    for stub in stubs:
        monkeypatch.setitem(
            mcp_server.TOOL_HANDLERS,
            stub["name"],
            lambda args, _n=stub["name"]: {"stub": _n},
        )
    return [s["name"] for s in stubs]


def test_tools_for_profile_filters_the_merged_list(
    every_connector_tool_registered: List[str],
) -> None:
    """Filtering happens against TOOLS at call time, so it sees the memory
    tools that were appended at import."""
    names = [t["name"] for t in tools_for_profile("connector")]
    assert set(names) == SPEC_CONNECTOR_TOOLS
    assert len(names) == 18


def test_the_full_profile_is_every_tool() -> None:
    assert [t["name"] for t in tools_for_profile("full")] == [
        t["name"] for t in mcp_server.TOOLS
    ]


# ---------------------------------------------------------------------------
# Server wiring: listing and dispatch
# ---------------------------------------------------------------------------


@pytest.fixture
def connector_server(every_connector_tool_registered: List[str]) -> Any:
    return create_mcp_server(profile="connector")


@pytest.fixture
def full_server(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.delenv("KUMIHO_MCP_TOOL_PROFILE", raising=False)
    return create_mcp_server()


def test_the_default_server_still_lists_every_tool(full_server: Any) -> None:
    """The stdio plugin path must not move: same tools, same count as today."""
    result = _dispatch(full_server, "tools/list")
    assert {t["name"] for t in result["tools"]} == {t["name"] for t in mcp_server.TOOLS}
    assert len(result["tools"]) == len(mcp_server.TOOLS)


def test_profile_none_and_full_agree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KUMIHO_MCP_TOOL_PROFILE", raising=False)
    default = _dispatch(create_mcp_server(), "tools/list")
    explicit = _dispatch(create_mcp_server(profile="full"), "tools/list")
    assert [t["name"] for t in default["tools"]] == [t["name"] for t in explicit["tools"]]


def test_the_connector_server_lists_exactly_the_eighteen(connector_server: Any) -> None:
    result = _dispatch(connector_server, "tools/list")
    assert {t["name"] for t in result["tools"]} == SPEC_CONNECTOR_TOOLS
    assert len(result["tools"]) == 18


def test_listed_tools_carry_their_annotations(connector_server: Any) -> None:
    if not mcp_server._TOOL_SUPPORTS_ANNOTATIONS:  # pragma: no cover
        pytest.skip("installed mcp has no ToolAnnotations")
    result = _dispatch(connector_server, "tools/list")
    for tool in result["tools"]:
        expected = TOOL_ANNOTATIONS[tool["name"]]
        annotations = tool["annotations"]
        assert annotations is not None, tool["name"]
        assert annotations["title"] == expected["title"]
        assert annotations["readOnlyHint"] is expected["readOnlyHint"]
        assert annotations["destructiveHint"] is expected["destructiveHint"]
        assert annotations["idempotentHint"] is expected["idempotentHint"]
        assert annotations["openWorldHint"] is False


def test_listed_tools_carry_a_title_when_the_sdk_has_the_field(
    connector_server: Any,
) -> None:
    if not mcp_server._TOOL_SUPPORTS_TITLE:  # pragma: no cover
        pytest.skip("installed mcp Tool has no title field")
    result = _dispatch(connector_server, "tools/list")
    for tool in result["tools"]:
        assert tool["title"] == TOOL_ANNOTATIONS[tool["name"]]["title"]


def test_the_full_profile_is_annotated_too(full_server: Any) -> None:
    """The plugin benefits from the hints as much as the directory does."""
    if not mcp_server._TOOL_SUPPORTS_ANNOTATIONS:  # pragma: no cover
        pytest.skip("installed mcp has no ToolAnnotations")
    result = _dispatch(full_server, "tools/list")
    assert all(t["annotations"] is not None for t in result["tools"])


def test_call_tool_refuses_a_tool_outside_the_profile(connector_server: Any) -> None:
    """Hiding a tool from the listing is not access control: a model that saw
    the full surface in another session will still ask for it by name."""
    result = _dispatch(
        connector_server,
        "tools/call",
        name="kumiho_delete_project",
        arguments={"project_name": "demo"},
    )
    payload = json.loads(result["content"][0]["text"])
    assert "not available" in payload["error"]
    assert "kumiho_delete_project" in payload["error"]
    assert payload["profile"] == "connector"


def test_the_refusal_beats_schema_validation(connector_server: Any) -> None:
    """Both majors must answer a hidden call the same way.

    mcp 2.x validates arguments before dispatch, so without care a hidden
    tool would come back as a schema complaint on 2.x and as a profile
    refusal on 1.x — for a tool that is not on offer either way.
    """
    result = _dispatch(
        connector_server, "tools/call", name="kumiho_delete_project", arguments={}
    )
    payload = json.loads(result["content"][0]["text"])
    assert payload.get("profile") == "connector"


def test_call_tool_still_dispatches_an_in_profile_tool(
    connector_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(
        mcp_server.TOOL_HANDLERS, "kumiho_list_projects", lambda args: {"ok": True}
    )
    result = _dispatch(
        connector_server, "tools/call", name="kumiho_list_projects", arguments={}
    )
    assert json.loads(result["content"][0]["text"]) == {"ok": True}


def test_the_full_profile_refuses_nothing(
    full_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(
        mcp_server.TOOL_HANDLERS, "kumiho_delete_project", lambda args: {"deleted": True}
    )
    result = _dispatch(
        full_server,
        "tools/call",
        name="kumiho_delete_project",
        arguments={"project_name": "demo"},
    )
    assert json.loads(result["content"][0]["text"]) == {"deleted": True}


def test_an_unknown_tool_is_still_reported_as_unknown(connector_server: Any) -> None:
    result = _dispatch(connector_server, "tools/call", name="not_a_tool", arguments={})
    assert "Unknown tool" in result["content"][0]["text"]


# ---------------------------------------------------------------------------
# Server instructions
# ---------------------------------------------------------------------------


def test_the_instructions_fit_the_budget() -> None:
    """They are spent from the user's context window on every conversation."""
    assert len(CONNECTOR_INSTRUCTIONS.split()) <= 700


@pytest.mark.parametrize(
    "fragment",
    [
        "kref://CognitiveMemory/personal/agent.instruction",
        "kumiho_memory_engage",
        "kumiho_memory_reflect",
        "kumiho_memory_consolidate",
        "kumiho_memory_decompose",
        "kumiho_deprecate_item",
        "kumiho_get_revision_by_tag",
        "space_hint",
        "session_id",
        "source_krefs",
    ],
)
def test_the_instructions_carry_the_protocol(fragment: str) -> None:
    """A remote connector has no skill and no hook: this text is the protocol."""
    assert fragment in CONNECTOR_INSTRUCTIONS


def test_the_instructions_only_name_tools_the_connector_exposes() -> None:
    """Instructing the model to call a tool the profile hides is a dead end."""
    # Word boundaries, not ``in``: every tool name is a prefix of some other
    # one (kumiho_get_revision / kumiho_get_revision_by_tag), so a substring
    # test reports names the text never mentions.
    mentioned = set(re.findall(r"kumiho_[a-z_]+", CONNECTOR_INSTRUCTIONS))
    named = mentioned & set(TOOL_ANNOTATIONS)
    assert named <= set(CONNECTOR_PROFILE_TOOLS)
    # And every mentioned kumiho_* token really is a tool, so a typo in the
    # instructions cannot send the model chasing a name that does not exist.
    assert mentioned <= set(TOOL_ANNOTATIONS)


def test_the_connector_server_carries_the_instructions(connector_server: Any) -> None:
    assert connector_server.instructions == CONNECTOR_INSTRUCTIONS


def test_the_default_server_carries_none(full_server: Any) -> None:
    """The plugin already ships the protocol as a skill; a second copy would
    spend the user's context twice."""
    assert not getattr(full_server, "instructions", None)


def test_explicit_instructions_win(every_connector_tool_registered: List[str]) -> None:
    server = create_mcp_server(profile="connector", instructions="custom text")
    assert server.instructions == "custom text"


def test_instructions_apply_to_the_full_profile_too() -> None:
    server = create_mcp_server(profile="full", instructions="custom text")
    assert server.instructions == "custom text"


def test_the_instructions_reach_the_initialization_options(
    connector_server: Any,
) -> None:
    """What ``initialize`` actually serves, not just what the object holds."""
    options = connector_server.create_initialization_options()
    assert getattr(options, "instructions", None) == CONNECTOR_INSTRUCTIONS


@pytest.mark.anyio
async def test_the_instructions_come_back_in_the_initialize_result(
    connector_server: Any,
) -> None:
    """End to end, over a real client/server pair.

    The in-memory pair is mcp 1.x's; on 2.x the shape of the helper differs,
    and the initialization-options assertion above carries the check instead.
    """
    if not _MCP_HAS_DECORATORS:  # pragma: no cover - depends on installed mcp
        pytest.skip("in-memory session helper targets the mcp 1.x Server")
    memory = pytest.importorskip("mcp.shared.memory")

    async with memory.create_connected_server_and_client_session(
        connector_server
    ) as client:
        result = await client.initialize()
        assert result.instructions == CONNECTOR_INSTRUCTIONS

        listed = await client.list_tools()
        assert {t.name for t in listed.tools} == SPEC_CONNECTOR_TOOLS

        if not mcp_server._TOOL_SUPPORTS_ANNOTATIONS:  # pragma: no cover
            return
        by_name = {t.name: t for t in listed.tools}
        engage = by_name["kumiho_memory_engage"]
        assert engage.annotations is not None
        assert engage.annotations.readOnlyHint is True
        forget = by_name["kumiho_deprecate_item"]
        assert forget.annotations.title == "Forget a memory"
        assert forget.annotations.destructiveHint is True


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


# ---------------------------------------------------------------------------
# Hosted mode: no process-global user state
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_caches() -> Any:
    """Restore the module caches around every test in this file."""
    snapshots = {
        "_project_cache": dict(mcp_server._project_cache),
        "_known_spaces": set(mcp_server._known_spaces),
        "_bundle_cache": dict(mcp_server._bundle_cache),
        "_space_registry_cache": dict(mcp_server._space_registry_cache),
    }
    yield
    mcp_server._project_cache.clear()
    mcp_server._project_cache.update(snapshots["_project_cache"])
    mcp_server._known_spaces.clear()
    mcp_server._known_spaces.update(snapshots["_known_spaces"])
    mcp_server._bundle_cache.clear()
    mcp_server._bundle_cache.update(snapshots["_bundle_cache"])
    mcp_server._space_registry_cache.clear()
    mcp_server._space_registry_cache.update(snapshots["_space_registry_cache"])


def _ctx(tenant: str) -> RequestContext:
    return RequestContext(
        tenant_id=tenant, user_id=f"user-of-{tenant}", auth_token=f"jwt-{tenant}"
    )


def test_the_auth_token_argument_is_ignored_in_hosted_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Publishing a caller-supplied token into os.environ swaps credentials
    for every other in-flight request, and outlives the call that did it."""
    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: True)
    monkeypatch.setattr(kumiho, "item_search", lambda **kwargs: [])

    with request_context(_ctx("tenant-a")):
        mcp_server.tool_search_items(auth_token="attacker-token")

    assert "KUMIHO_AUTH_TOKEN" not in os.environ


def test_the_auth_token_argument_still_works_locally(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Byte-for-byte behavior for the stdio plugin path."""
    monkeypatch.delenv("KUMIHO_MCP_HOSTED", raising=False)
    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: True)
    monkeypatch.setattr(kumiho, "item_search", lambda **kwargs: [])

    mcp_server.tool_search_items(auth_token="local-token")
    assert os.environ["KUMIHO_AUTH_TOKEN"] == "local-token"
    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)


def test_the_hosted_flag_alone_blocks_the_env_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hosted process must be defensive even between requests."""
    monkeypatch.setenv("KUMIHO_MCP_HOSTED", "1")
    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: True)
    monkeypatch.setattr(kumiho, "item_search", lambda **kwargs: [])

    mcp_server.tool_search_items(auth_token="whatever")
    assert "KUMIHO_AUTH_TOKEN" not in os.environ


def test_the_project_cache_is_keyed_by_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two tenants both have a project called CognitiveMemory. The cached
    value is a live handle bound to one tenant's client and credentials."""
    mcp_server._project_cache.clear()
    handles = {}

    def fake_get_project(name: str) -> Any:
        tenant = kumiho.current_request().tenant_id
        handle = handles.setdefault((tenant, name), object())
        return handle

    monkeypatch.setattr(kumiho, "get_project", fake_get_project)

    with request_context(_ctx("tenant-a")):
        a = mcp_server._get_project_cached("CognitiveMemory")
    with request_context(_ctx("tenant-b")):
        b = mcp_server._get_project_cached("CognitiveMemory")

    assert a is not b
    assert len(mcp_server._project_cache) == 2
    # And the cache still hits for a repeat within the same tenant.
    with request_context(_ctx("tenant-a")):
        assert mcp_server._get_project_cached("CognitiveMemory") is a
    assert len(mcp_server._project_cache) == 2


def test_the_space_registry_cache_is_keyed_by_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mcp_server._space_registry_cache.clear()

    class _Space:
        def __init__(self, path: str) -> None:
            self.path = path

    class _Project:
        name = "CognitiveMemory"

        def __init__(self, paths: List[str]) -> None:
            self._paths = paths

        def get_spaces(self, recursive: bool = False) -> List[Any]:
            return [_Space(p) for p in self._paths]

    with request_context(_ctx("tenant-a")):
        a = mcp_server._existing_space_paths(_Project(["/CognitiveMemory/a"]))
    with request_context(_ctx("tenant-b")):
        b = mcp_server._existing_space_paths(_Project(["/CognitiveMemory/b"]))

    assert a == {"/CognitiveMemory/a"}
    assert b == {"/CognitiveMemory/b"}
    assert len(mcp_server._space_registry_cache) == 2

    # Invalidation is scoped too: clearing A must not clear B.
    with request_context(_ctx("tenant-a")):
        mcp_server._invalidate_space_registry("CognitiveMemory")
    assert len(mcp_server._space_registry_cache) == 1


def test_the_known_spaces_set_is_keyed_by_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Otherwise tenant B's first store skips space creation because tenant A
    already made a space of that path — in a different graph."""
    mcp_server._known_spaces.clear()
    created: List[Any] = []

    class _Project:
        name = "CognitiveMemory"

        def create_space(self, segment: str, parent_path: str = "") -> None:
            created.append((kumiho.current_request().tenant_id, segment))

    monkeypatch.setattr(mcp_server, "_invalidate_space_registry", lambda name: None)

    for tenant in ("tenant-a", "tenant-b"):
        with request_context(_ctx(tenant)):
            mcp_server._ensure_space_path(_Project(), "personal")

    assert [t for t, _ in created] == ["tenant-a", "tenant-b"]
    assert len(mcp_server._known_spaces) == 2

    # Second call for the same tenant is served from the cache.
    with request_context(_ctx("tenant-a")):
        mcp_server._ensure_space_path(_Project(), "personal")
    assert len(created) == 2


def test_the_bundle_cache_is_keyed_by_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    mcp_server._bundle_cache.clear()

    class _Project:
        name = "CognitiveMemory"

        def create_bundle(self, name: str, parent_path: str = "") -> Any:
            return (kumiho.current_request().tenant_id, name)

    with request_context(_ctx("tenant-a")):
        a = mcp_server._get_or_create_bundle(_Project(), "/CognitiveMemory", "b")
    with request_context(_ctx("tenant-b")):
        b = mcp_server._get_or_create_bundle(_Project(), "/CognitiveMemory", "b")

    assert a == ("tenant-a", "b")
    assert b == ("tenant-b", "b")
    assert len(mcp_server._bundle_cache) == 2


def test_local_cache_keys_are_stable_without_a_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The stdio path gets one namespace, "local", and keeps its cache hits."""
    mcp_server._project_cache.clear()
    monkeypatch.setattr(kumiho, "get_project", lambda name: object())

    first = mcp_server._get_project_cached("CognitiveMemory")
    second = mcp_server._get_project_cached("CognitiveMemory")
    assert first is second
    assert list(mcp_server._project_cache) == ["local\x1fCognitiveMemory"]


def test_ensure_configured_refuses_local_credentials_when_hosted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Falling back would serve the operator's own graph to a remote caller."""
    called: List[int] = []
    monkeypatch.setattr(
        kumiho, "auto_configure_from_discovery", lambda *a, **k: called.append(1)
    )
    with request_context(_ctx("tenant-a")):
        with pytest.raises(RuntimeError, match="no request-scoped Kumiho client"):
            mcp_server._ensure_configured()
    assert called == []


def test_ensure_configured_is_satisfied_by_a_bound_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: List[int] = []
    monkeypatch.setattr(
        kumiho, "auto_configure_from_discovery", lambda *a, **k: called.append(1)
    )
    token = kumiho._client_context_var.set(object())
    try:
        with request_context(_ctx("tenant-a")):
            assert mcp_server._ensure_configured() is True
    finally:
        kumiho._client_context_var.reset(token)
    assert called == [], "hosted mode must never read ~/.kumiho"


def test_ensure_configured_is_unchanged_locally(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KUMIHO_MCP_HOSTED", raising=False)
    called: List[int] = []
    monkeypatch.setattr(
        kumiho, "auto_configure_from_discovery", lambda *a, **k: called.append(1)
    )
    assert mcp_server._ensure_configured() is True
    assert called == [1]


def test_memory_artifacts_are_not_written_when_hosted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    """The root is on the *server's* disk, shared by every tenant, and the
    path it records resolves for nobody."""
    monkeypatch.setenv("KUMIHO_MEMORY_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.setenv("KUMIHO_MCP_HOSTED", "1")

    location = mcp_server._write_memory_artifact(
        project="CognitiveMemory",
        space_path="/CognitiveMemory/personal",
        item_name="note",
        title="t",
        summary="s",
        user_text="u",
        assistant_text="a",
        memory_type="summary",
    )
    assert location == ""
    assert list(tmp_path.iterdir()) == []


def test_memory_artifacts_are_still_written_locally(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.delenv("KUMIHO_MCP_HOSTED", raising=False)
    monkeypatch.setenv("KUMIHO_MEMORY_ARTIFACT_ROOT", str(tmp_path))

    location = mcp_server._write_memory_artifact(
        project="CognitiveMemory",
        space_path="/CognitiveMemory/personal",
        item_name="note",
        title="t",
        summary="s",
        user_text="u",
        assistant_text="a",
        memory_type="summary",
    )
    assert location.endswith("note.md")
    assert "t" in open(location, encoding="utf-8").read()


def test_creating_a_server_starts_no_watchdog(monkeypatch: pytest.MonkeyPatch) -> None:
    """A hosted process builds these inside a long-lived web server, where the
    watchdog would watch the wrong parent and os._exit the whole service."""
    started: List[str] = []
    monkeypatch.setattr(
        mcp_server, "_start_orphan_watchdog", lambda: started.append("orphan")
    )
    monkeypatch.setattr(
        mcp_server, "_start_windows_watchdog", lambda: started.append("windows")
    )
    before = {t.name for t in threading.enumerate()}

    create_mcp_server(profile="connector")
    create_mcp_server()

    assert started == []
    assert {t.name for t in threading.enumerate()} - before == set()


def test_creating_a_server_touches_no_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction must be inert: the hosting layer builds one per process,
    before any request has an identity to configure a client with."""
    def _boom(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("create_mcp_server must not configure a client")

    monkeypatch.setattr(kumiho, "auto_configure_from_discovery", _boom)
    monkeypatch.setattr(kumiho, "get_projects", _boom)
    create_mcp_server(profile="connector")


# ---------------------------------------------------------------------------
# Context propagation into handlers
# ---------------------------------------------------------------------------


def test_a_tool_handler_runs_under_the_callers_request_context(
    full_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``asyncio.to_thread`` copies the context; a bare thread would not, and
    the handler would resolve the wrong tenant (or none)."""
    seen: Dict[str, Any] = {}

    def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        ctx = kumiho.current_request()
        seen["tenant"] = ctx.tenant_id if ctx else None
        seen["token"] = ctx.auth_token if ctx else None
        return {"ok": True}

    monkeypatch.setitem(mcp_server.TOOL_HANDLERS, "kumiho_list_projects", handler)

    with request_context(_ctx("tenant-a")):
        _dispatch(full_server, "tools/call", name="kumiho_list_projects", arguments={})

    assert seen == {"tenant": "tenant-a", "token": "jwt-tenant-a"}


def test_a_handler_that_opens_its_own_event_loop_still_sees_the_context(
    full_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The kumiho-memory handlers are sync bodies that ``asyncio.run`` inside.

    ``asyncio.run`` builds a Runner over a *copy* of the current context, so
    reads still resolve. Pinned here because the whole hosted design rests on
    it, and a future refactor to a shared executor would break it silently.
    """
    seen: Dict[str, Any] = {}

    def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        async def inner() -> str:
            ctx = kumiho.current_request()
            return ctx.tenant_id if ctx else "none"

        seen["tenant"] = asyncio.run(inner())
        return {"ok": True}

    monkeypatch.setitem(mcp_server.TOOL_HANDLERS, "kumiho_list_projects", handler)

    with request_context(_ctx("tenant-b")):
        _dispatch(full_server, "tools/call", name="kumiho_list_projects", arguments={})

    assert seen["tenant"] == "tenant-b"


def test_two_tenants_do_not_cross_talk_through_a_handler(
    full_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The end the hosted design is for: same process, same tool, two graphs."""
    mcp_server._project_cache.clear()
    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: True)
    monkeypatch.setattr(
        kumiho, "get_project", lambda name: (kumiho.current_request().tenant_id, name)
    )

    def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        return {"project": mcp_server._get_project_cached("CognitiveMemory")}

    monkeypatch.setitem(mcp_server.TOOL_HANDLERS, "kumiho_list_projects", handler)

    results = {}
    for tenant in ("tenant-a", "tenant-b"):
        with request_context(_ctx(tenant)):
            out = _dispatch(
                full_server, "tools/call", name="kumiho_list_projects", arguments={}
            )
            results[tenant] = json.loads(out["content"][0]["text"])["project"]

    assert results["tenant-a"] == ["tenant-a", "CognitiveMemory"]
    assert results["tenant-b"] == ["tenant-b", "CognitiveMemory"]
