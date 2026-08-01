"""Construction and dispatch tests for the MCP server, on both mcp majors.

Nothing called ``create_mcp_server()`` before these tests, which is why mcp
2.0.0 reached users as a server that raised on its first decorator
(kumiho-SDKs#145). ``run_server`` logs "Starting Kumiho MCP server..." *before*
calling it, so a log-greping smoke test reports a healthy start either way —
the server has to actually be built, and its handlers actually driven.

Every assertion here runs against whichever mcp is installed. The two majors
register handlers differently (decorators vs ``Server(on_*=...)``) and renamed
the model fields camelCase to snake_case, so dispatch goes through
:func:`_dispatch` and results are read through ``model_dump(by_alias=True)`` —
the wire shape, which is identical across both.

Covers:
- kumiho-SDKs#145 construction, and the input validation mcp 2.0 stopped doing
- kumiho-SDKs#146 ``resources/read`` receiving an ``AnyUrl`` rather than a str
- kumiho-SDKs#147 ``serverInfo.version`` reporting kumiho's own version
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

import mcp.types as types  # noqa: E402

import kumiho  # noqa: E402
from kumiho import mcp_server  # noqa: E402
from kumiho.mcp_server import _MCP_HAS_DECORATORS, create_mcp_server  # noqa: E402

# method -> (1.x Request class name, params class name or None). The list
# methods take no params on either major.
_METHODS = {
    "tools/list": ("ListToolsRequest", None),
    "tools/call": ("CallToolRequest", "CallToolRequestParams"),
    "resources/list": ("ListResourcesRequest", None),
    "resources/read": ("ReadResourceRequest", "ReadResourceRequestParams"),
    "prompts/list": ("ListPromptsRequest", None),
    "prompts/get": ("GetPromptRequest", "GetPromptRequestParams"),
}


def _dispatch(server: Any, method: str, **params: Any) -> dict:
    """Invoke a registered handler and return its result as a wire-shaped dict.

    mcp 1.x keys handlers by Request type and hands them a whole Request,
    returning a ``ServerResult`` wrapper; mcp 2.x keys them by method string and
    hands them ``(ctx, params)``, returning the result model directly. Kumiho's
    handlers ignore ``ctx``, so tests pass ``None`` for it.
    """
    request_name, params_name = _METHODS[method]
    params_type = getattr(types, params_name) if params_name else None

    if _MCP_HAS_DECORATORS:
        request_type = getattr(types, request_name)
        handler = server.request_handlers[request_type]
        request = (
            request_type(method=method, params=params_type(**params))
            if params_type
            else request_type(method=method)
        )
        result = asyncio.run(handler(request)).root
    else:
        entry = server.get_request_handler(method)
        assert entry is not None, f"no handler registered for {method}"
        result = asyncio.run(
            entry.handler(None, params_type(**params) if params_type else None)
        )

    # by_alias gives the camelCase wire names on both majors, so assertions
    # below never depend on which one is installed.
    return result.model_dump(by_alias=True)


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> Any:
    """A server whose backend calls are stubbed, so no live gRPC is needed."""

    class _Project:
        name = "demo"
        description = "Demo project"

    monkeypatch.setattr(mcp_server, "_ensure_configured", lambda: None)
    monkeypatch.setattr(kumiho, "get_projects", lambda: [_Project()])
    monkeypatch.setattr(
        mcp_server, "tool_get_project", lambda name: {"name": name, "kind": "project"}
    )
    return create_mcp_server()


def test_create_mcp_server_constructs() -> None:
    """The regression itself: mcp 2.0.0 raised here, at the first decorator."""
    assert create_mcp_server() is not None


def test_all_six_methods_are_registered(server: Any) -> None:
    """A partial port would still construct — check every handler landed."""
    for method, (request_name, _) in _METHODS.items():
        if _MCP_HAS_DECORATORS:
            assert getattr(types, request_name) in server.request_handlers, method
        else:
            assert server.get_request_handler(method) is not None, method


def test_capabilities_advertise_tools_resources_and_prompts(server: Any) -> None:
    """Capabilities are derived from what is registered; all three must survive."""
    caps = server.create_initialization_options().capabilities
    assert caps.tools is not None
    assert caps.resources is not None
    assert caps.prompts is not None


def test_server_info_reports_kumiho_version(server: Any) -> None:
    """kumiho-SDKs#147: without version=, 1.x reports mcp's and 2.0 reports ''."""
    options = server.create_initialization_options()
    assert options.server_name == "kumiho-mcp"
    assert options.server_version == kumiho.__version__


def test_list_tools_returns_every_tool_with_a_camelcase_schema(server: Any) -> None:
    result = _dispatch(server, "tools/list")
    assert len(result["tools"]) == len(mcp_server.TOOLS)
    # inputSchema, not input_schema: mcp 2.0 renamed the field but kept the alias.
    assert all(t["inputSchema"] for t in result["tools"])
    assert {t["name"] for t in result["tools"]} == {
        t["name"] for t in mcp_server.TOOLS
    }


def test_call_tool_dispatches_to_the_handler(
    server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(
        mcp_server.TOOL_HANDLERS, "kumiho_get_project", lambda args: {"echoed": args}
    )
    result = _dispatch(
        server, "tools/call", name="kumiho_get_project", arguments={"name": "demo"}
    )
    assert not result["isError"]
    assert json.loads(result["content"][0]["text"]) == {"echoed": {"name": "demo"}}


def test_call_tool_rejects_input_that_violates_the_schema(server: Any) -> None:
    """The silent regression a naive mcp 2.0 port introduces.

    mcp 1.x's ``@server.call_tool()`` validated arguments against each tool's
    inputSchema for free; mcp 2.0's low-level path does not. A port that drops
    the check still compiles, connects and serves — it just stops validating.
    ``kumiho_get_project`` requires ``name``, so an empty argument object must
    come back as an error rather than reaching the handler.
    """
    result = _dispatch(server, "tools/call", name="kumiho_get_project", arguments={})
    assert result["isError"] is True
    assert "validation error" in result["content"][0]["text"].lower()


def test_call_tool_reports_unknown_tools(server: Any) -> None:
    result = _dispatch(server, "tools/call", name="not_a_tool", arguments={})
    assert "Unknown tool" in result["content"][0]["text"]


def test_list_resources_maps_projects(server: Any) -> None:
    result = _dispatch(server, "resources/list")
    # str(): model_dump leaves uri as an AnyUrl on mcp 1.x and stringifies it
    # on 2.x. Both serialize identically on the wire.
    assert str(result["resources"][0]["uri"]) == "kumiho://project/demo"
    assert result["resources"][0]["mimeType"] == "application/json"


def test_read_resource_accepts_the_anyurl_mcp_actually_passes(server: Any) -> None:
    """kumiho-SDKs#146: the handler was annotated ``uri: str`` but mcp passes an
    ``AnyUrl``, which has no ``.startswith`` — so every read raised.

    Passing the URI through ``ReadResourceRequestParams`` is what makes this a
    real regression test: pydantic coerces it to ``AnyUrl`` exactly as the SDK
    does, so a handler that assumes ``str`` fails here.
    """
    result = _dispatch(server, "resources/read", uri="kumiho://project/demo")
    contents = result["contents"][0]
    assert json.loads(contents["text"]) == {"name": "demo", "kind": "project"}
    # A bare str return would have been served as text/plain despite the
    # resource listing advertising JSON.
    assert contents["mimeType"] == "application/json"


def test_read_resource_rejects_an_unknown_uri(server: Any) -> None:
    with pytest.raises(ValueError, match="Unknown resource URI"):
        _dispatch(server, "resources/read", uri="kumiho://nope/demo")


def test_list_prompts(server: Any) -> None:
    result = _dispatch(server, "prompts/list")
    assert {p["name"] for p in result["prompts"]} == {"analyze_asset", "find_assets"}


def test_get_prompt_renders_its_argument(server: Any) -> None:
    result = _dispatch(
        server,
        "prompts/get",
        name="analyze_asset",
        arguments={"kref": "kref://demo/asset"},
    )
    assert "kref://demo/asset" in result["messages"][0]["content"]["text"]


def test_get_prompt_rejects_an_unknown_prompt(server: Any) -> None:
    with pytest.raises(ValueError, match="Unknown prompt"):
        _dispatch(server, "prompts/get", name="not_a_prompt", arguments={})
