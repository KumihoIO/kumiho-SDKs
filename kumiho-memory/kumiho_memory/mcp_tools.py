"""MCP tool definitions for kumiho-memory.

This module exposes kumiho-memory functionality as MCP tools.  It is
**auto-discovered** by the core Kumiho MCP server (``kumiho.mcp_server``)
when ``kumiho-memory`` is installed — no manual registration required.

The plugin hook in ``mcp_server.py`` does::

    try:
        from kumiho_memory.mcp_tools import MEMORY_TOOLS, MEMORY_TOOL_HANDLERS
        TOOLS.extend(MEMORY_TOOLS)
        TOOL_HANDLERS.update(MEMORY_TOOL_HANDLERS)
    except ImportError:
        pass

All tool handlers are **synchronous** functions.  The MCP server dispatches
them via ``asyncio.to_thread(handler, args)``, so they run in a thread pool
with no active event loop — ``asyncio.run()`` is safe to use inside them.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton manager
# ---------------------------------------------------------------------------

_manager: Optional[Any] = None


def _get_manager():
    """Lazily create and return a shared ``UniversalMemoryManager``."""
    global _manager
    if _manager is not None:
        return _manager

    from kumiho_memory import (
        RedisMemoryBuffer,
        UniversalMemoryManager,
        MemorySummarizer,
        PIIRedactor,
    )

    graph_config = None
    if os.environ.get("KUMIHO_GRAPH_AUGMENTED_RECALL", "").strip() in ("1", "true"):
        try:
            from kumiho_memory.graph_augmentation import GraphAugmentationConfig
            graph_config = GraphAugmentationConfig()
        except Exception as exc:
            logger.warning(
                "Graph-augmented recall requested but configuration failed: %s. "
                "Falling back to standard recall.",
                exc,
            )

    buffer = RedisMemoryBuffer()
    _manager = UniversalMemoryManager(
        redis_buffer=buffer,
        summarizer=MemorySummarizer(),
        pii_redactor=PIIRedactor(),
        graph_augmentation=graph_config,
    )
    return _manager


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


def tool_chat_add(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a message to Redis working memory."""
    manager = _get_manager()
    return asyncio.run(
        manager.redis_buffer.add_message(
            project=manager.project,
            session_id=args["session_id"],
            role=args.get("role", "user"),
            content=args["message"],
            metadata=args.get("metadata"),
        )
    )


def tool_chat_get(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get messages from Redis working memory."""
    manager = _get_manager()
    return asyncio.run(
        manager.redis_buffer.get_messages(
            project=manager.project,
            session_id=args["session_id"],
            limit=args.get("limit", 50),
        )
    )


def tool_chat_clear(args: Dict[str, Any]) -> Dict[str, Any]:
    """Clear a session's working memory."""
    manager = _get_manager()
    return asyncio.run(
        manager.redis_buffer.clear_session(
            manager.project,
            args["session_id"],
        )
    )


def tool_memory_ingest(args: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest a user message — buffers in Redis and returns context."""
    manager = _get_manager()
    return asyncio.run(
        manager.handle_user_message(
            user_id=args["user_id"],
            message=args["message"],
            context=args.get("context", "personal"),
            session_id=args.get("session_id"),
            working_memory_limit=args.get("working_memory_limit", 10),
            recall_limit=args.get("recall_limit", 5),
        )
    )


def tool_memory_add_response(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add an assistant response to the session buffer."""
    manager = _get_manager()
    return asyncio.run(
        manager.add_assistant_response(
            session_id=args["session_id"],
            response=args["response"],
        )
    )


def tool_memory_consolidate(args: Dict[str, Any]) -> Dict[str, Any]:
    """Consolidate a session — summarize, redact PII, store to graph."""
    manager = _get_manager()
    return asyncio.run(
        manager.consolidate_session(session_id=args["session_id"])
    )


def tool_memory_recall(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search long-term memories by semantic query."""
    manager = _get_manager()
    results = asyncio.run(
        manager.recall_memories(
            args["query"],
            limit=args.get("limit", 5),
            space_paths=args.get("space_paths"),
            memory_types=args.get("memory_types"),
            graph_augmented=args.get("graph_augmented", False),
        )
    )
    return {"results": results, "count": len(results)}


def tool_memory_store_execution(args: Dict[str, Any]) -> Dict[str, Any]:
    """Store a tool/command execution result as memory."""
    manager = _get_manager()
    return asyncio.run(
        manager.store_tool_execution(
            task=args["task"],
            status=args.get("status", "done"),
            exit_code=args.get("exit_code"),
            duration_ms=args.get("duration_ms"),
            stdout=args.get("stdout", ""),
            stderr=args.get("stderr", ""),
            tools=args.get("tools"),
            topics=args.get("topics"),
            space_hint=args.get("space_hint", ""),
        )
    )


def tool_memory_dream_state(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a Dream State memory consolidation cycle."""
    from kumiho_memory import DreamState

    ds = DreamState(
        project=args.get("project", "CognitiveMemory"),
        batch_size=args.get("batch_size", 20),
        dry_run=args.get("dry_run", False),
        max_deprecation_ratio=args.get("max_deprecation_ratio", 0.5),
        allow_published_deprecation=args.get("allow_published_deprecation", False),
    )
    return asyncio.run(ds.run())


def tool_memory_discover_edges(args: Dict[str, Any]) -> Dict[str, Any]:
    """Discover and create edges from a memory to related existing memories."""
    manager = _get_manager()
    edges = asyncio.run(
        manager.discover_edges_post_consolidation(
            revision_kref=args["revision_kref"],
            summary=args["summary"],
            max_queries=args.get("max_queries", 5),
            max_edges=args.get("max_edges", 3),
            min_score=args.get("min_score", 0.3),
            edge_type=args.get("edge_type", "REFERENCED"),
            space_paths=args.get("space_paths"),
        )
    )
    return {"edges": edges, "count": len(edges)}


# ---------------------------------------------------------------------------
# Tool definitions (JSON Schema)
# ---------------------------------------------------------------------------

MEMORY_TOOLS: List[Dict[str, Any]] = [
    # ── Chat memory (Redis working memory) ────────────────────
    {
        "name": "kumiho_chat_add",
        "description": (
            "Add a user or assistant message to Redis working memory for a "
            "conversation session. Returns the current message count."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier.",
                },
                "message": {
                    "type": "string",
                    "description": "Message content.",
                },
                "role": {
                    "type": "string",
                    "enum": ["user", "assistant"],
                    "default": "user",
                    "description": "Message role.",
                },
            },
            "required": ["session_id", "message"],
        },
    },
    {
        "name": "kumiho_chat_get",
        "description": (
            "Retrieve recent messages from Redis working memory for a "
            "session. Returns messages, count, and TTL."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier.",
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Max messages to return.",
                },
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "kumiho_chat_clear",
        "description": "Clear all working memory for a conversation session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier.",
                },
            },
            "required": ["session_id"],
        },
    },
    # ── Memory lifecycle (orchestrated) ───────────────────────
    {
        "name": "kumiho_memory_ingest",
        "description": (
            "Ingest a user message into AI cognitive memory. Buffers the "
            "message in Redis, recalls relevant long-term memories, and "
            "returns working memory + long-term context. This is the main "
            "entry point for AI agents handling user messages."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Stable user identifier.",
                },
                "message": {
                    "type": "string",
                    "description": "User message text.",
                },
                "context": {
                    "type": "string",
                    "default": "personal",
                    "description": (
                        "Memory context: personal, work, etc."
                    ),
                },
                "session_id": {
                    "type": "string",
                    "description": (
                        "Existing session ID. Auto-generated if omitted."
                    ),
                },
                "working_memory_limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max working memory messages to return.",
                },
                "recall_limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Max long-term memories to recall.",
                },
            },
            "required": ["user_id", "message"],
        },
    },
    {
        "name": "kumiho_memory_add_response",
        "description": (
            "Add an assistant response to the session buffer in Redis "
            "working memory. Call this after generating your response."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier from ingest.",
                },
                "response": {
                    "type": "string",
                    "description": "Assistant response text.",
                },
            },
            "required": ["session_id", "response"],
        },
    },
    {
        "name": "kumiho_memory_consolidate",
        "description": (
            "Consolidate a conversation session into long-term memory. "
            "Summarizes the conversation with an LLM, redacts PII, writes "
            "a local artifact, and stores the summary to the Kumiho graph. "
            "The session's working memory is cleared after consolidation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier to consolidate.",
                },
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "kumiho_memory_recall",
        "description": (
            "Search long-term memories by semantic query. Returns matching "
            "memories from the Kumiho graph with optional filtering by "
            "space paths and memory types."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language search query.",
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Max results to return.",
                },
                "space_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Restrict search to these space paths "
                        "(e.g. ['CognitiveMemory/personal'])."
                    ),
                },
                "memory_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Filter by memory type "
                        "(e.g. ['error'], ['action', 'summary'])."
                    ),
                },
                "graph_augmented": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Enable graph-augmented recall: multi-query "
                        "reformulation + edge traversal to discover "
                        "connected memories that vector search alone misses. "
                        "Requires KUMIHO_GRAPH_AUGMENTED_RECALL=1 env var."
                    ),
                },
            },
            "required": ["query"],
        },
    },
    # ── Edge discovery ─────────────────────────────────────────
    {
        "name": "kumiho_memory_discover_edges",
        "description": (
            "Discover and create edges from a newly stored memory to "
            "related existing memories. Uses the LLM to generate "
            "'implication queries' (future scenarios where the memory "
            "would be relevant) and links to matching memories. "
            "Best used after kumiho_memory_consolidate or "
            "kumiho_memory_store."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "revision_kref": {
                    "type": "string",
                    "description": (
                        "The kref URI of the revision to discover "
                        "edges for."
                    ),
                },
                "summary": {
                    "type": "string",
                    "description": (
                        "Summary text of the memory (used to generate "
                        "implication queries)."
                    ),
                },
                "max_queries": {
                    "type": "integer",
                    "default": 5,
                    "description": "Max implication queries to generate.",
                },
                "max_edges": {
                    "type": "integer",
                    "default": 3,
                    "description": "Max edges to create.",
                },
                "min_score": {
                    "type": "number",
                    "default": 0.3,
                    "description": (
                        "Minimum similarity score for edge candidates."
                    ),
                },
                "edge_type": {
                    "type": "string",
                    "default": "REFERENCED",
                    "description": "Edge type to create (default: REFERENCED).",
                },
                "space_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Restrict search to these space paths. "
                        "Auto-derived from revision_kref if omitted."
                    ),
                },
            },
            "required": ["revision_kref", "summary"],
        },
    },
    # ── Tool execution ────────────────────────────────────────
    {
        "name": "kumiho_memory_store_execution",
        "description": (
            "Store a tool or command execution result as a structured "
            "memory. Successful executions are stored as 'action' type; "
            "failures as 'error' type. Includes stdout/stderr as artifacts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": (
                        "Description of what was executed "
                        "(e.g. 'git push origin main')."
                    ),
                },
                "status": {
                    "type": "string",
                    "default": "done",
                    "enum": ["done", "failed", "error", "blocked"],
                    "description": "Execution outcome.",
                },
                "exit_code": {
                    "type": "integer",
                    "description": "Process exit code (0 = success).",
                },
                "duration_ms": {
                    "type": "integer",
                    "description": "Execution duration in milliseconds.",
                },
                "stdout": {
                    "type": "string",
                    "description": "Captured standard output.",
                },
                "stderr": {
                    "type": "string",
                    "description": "Captured standard error.",
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tool names used.",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Classification topics.",
                },
                "space_hint": {
                    "type": "string",
                    "description": "Space path hint for organisation.",
                },
            },
            "required": ["task"],
        },
    },
    # ── Maintenance ───────────────────────────────────────────
    {
        "name": "kumiho_memory_dream_state",
        "description": (
            "Run a Dream State memory consolidation cycle. Replays new "
            "events, assesses memories with an LLM, and applies "
            "deprecation, tagging, metadata enrichment, and relationship "
            "linking. Use dry_run=true to preview without mutations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "default": "CognitiveMemory",
                    "description": "Kumiho project to process.",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": "Preview changes without applying.",
                },
                "batch_size": {
                    "type": "integer",
                    "default": 20,
                    "description": "Memories per LLM assessment batch.",
                },
                "max_deprecation_ratio": {
                    "type": "number",
                    "default": 0.5,
                    "minimum": 0.1,
                    "maximum": 0.9,
                    "description": "Max fraction of memories to deprecate per run (0.1-0.9).",
                },
                "allow_published_deprecation": {
                    "type": "boolean",
                    "default": False,
                    "description": "Allow deprecation of published items (use with caution).",
                },
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool handler mapping
# ---------------------------------------------------------------------------

MEMORY_TOOL_HANDLERS: Dict[str, Any] = {
    "kumiho_chat_add": tool_chat_add,
    "kumiho_chat_get": tool_chat_get,
    "kumiho_chat_clear": tool_chat_clear,
    "kumiho_memory_ingest": tool_memory_ingest,
    "kumiho_memory_add_response": tool_memory_add_response,
    "kumiho_memory_consolidate": tool_memory_consolidate,
    "kumiho_memory_recall": tool_memory_recall,
    "kumiho_memory_discover_edges": tool_memory_discover_edges,
    "kumiho_memory_store_execution": tool_memory_store_execution,
    "kumiho_memory_dream_state": tool_memory_dream_state,
}
