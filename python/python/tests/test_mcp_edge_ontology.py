"""The MCP edge tools' advertised vocabulary, pinned against ``EdgeType``.

``kumiho_create_edge`` and ``kumiho_delete_edge`` carry the edge vocabulary a
second time, as a JSON-Schema ``enum``. That copy drifted: it listed 8 of the
10 ``EdgeType`` members. The enum is enforced -- ``_dispatch`` runs
``jsonschema.validate`` against it -- so an omitted type is not cosmetic, it is
unreachable.

The fix is not to hardcode the missing names a third time. These tests derive
the expected sets from ``EdgeType`` itself, so the schema cannot drift from the
ontology again without failing here.

The two tools are deliberately NOT symmetric, and neither exposes the whole
ontology. See the constants below for why.
"""

from __future__ import annotations

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

from kumiho.edge import EdgeType
from kumiho.mcp_server import TOOLS


#: Every edge type the SDK defines, read off the class rather than retyped.
ONTOLOGY = {
    value
    for name, value in vars(EdgeType).items()
    if name.isupper() and isinstance(value, str)
}

#: Belief revision is a protocol, not a lone edge. Its in-system producers pair
#: the edge with a status demotion on the superseded revision and a
#: grounding-staleness ripple to whatever depended on it. A bare edge write
#: performs only the first third, which silently restores the state
#: ``grounding.py`` exists to prevent, so SUPERSEDES is not offered by either
#: tool. Explicit, agent-supplied belief revision belongs in the memory layer,
#: where the companions run.
BELIEF_REVISION = {EdgeType.SUPERSEDES}

#: Deleting an edge has no repair path anywhere in the memory layer. The tool
#: keeps the vocabulary it shipped with; SUPPORTS is create-only for now.
NOT_DELETABLE = BELIEF_REVISION | {EdgeType.SUPPORTS}


def _advertised(tool_name: str) -> set[str]:
    schemas = {tool["name"]: tool["inputSchema"] for tool in TOOLS}
    return set(schemas[tool_name]["properties"]["edge_type"]["enum"])


def test_ontology_has_ten_members() -> None:
    """A guard on the guard: the derivation must not silently collapse."""
    assert len(ONTOLOGY) == 10


def test_create_edge_advertises_everything_but_belief_revision() -> None:
    assert _advertised("kumiho_create_edge") == ONTOLOGY - BELIEF_REVISION


def test_delete_edge_withholds_belief_revision_and_supports() -> None:
    assert _advertised("kumiho_delete_edge") == ONTOLOGY - NOT_DELETABLE


def test_creative_provenance_types_stay_advertised() -> None:
    """The regression this file's ancestor guarded, kept intact."""
    provenance = {"CREATED_FROM", "PRODUCED_BY", "DERIVED_FROM", "MIGRATED_FROM"}
    for tool_name in ("kumiho_create_edge", "kumiho_delete_edge"):
        assert provenance <= _advertised(tool_name)
