"""Universal memory manager for AI agents."""

from __future__ import annotations

import asyncio
import inspect
import hashlib
import logging
import mimetypes
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from kumiho_memory.privacy import PIIRedactor
from kumiho_memory.redis_memory import RedisMemoryBuffer
from kumiho_memory.retry import RetryQueue, retry_with_backoff
from kumiho_memory.summarization import LLMAdapter, MemorySummarizer

logger = logging.getLogger(__name__)


StoreCallable = Callable[..., Any]
RetrieveCallable = Callable[..., Any]


class UniversalMemoryManager:
    """Orchestrates working memory, summarization, and long-term storage.

    For agent frameworks (OpenClaw, LangChain, etc.) that already have a
    configured LLM, pass the ``llm_adapter`` parameter to reuse it::

        manager = UniversalMemoryManager(llm_adapter=my_agent_adapter)

    This avoids separate LLM configuration for the memory subsystem.
    """

    def __init__(
        self,
        *,
        project: str = "CognitiveMemory",
        consolidation_threshold: int = 50,
        artifact_root: Optional[str] = None,
        llm_adapter: Optional[LLMAdapter] = None,
        redis_buffer: Optional[RedisMemoryBuffer] = None,
        summarizer: Optional[MemorySummarizer] = None,
        pii_redactor: Optional[PIIRedactor] = None,
        memory_store: Optional[StoreCallable] = None,
        memory_retrieve: Optional[RetrieveCallable] = None,
        redis_url: Optional[str] = None,
        tenant_hint: Optional[str] = None,
        retry_queue: Optional[RetryQueue] = None,
        store_max_retries: int = 3,
    ) -> None:
        self.project = project
        self.consolidation_threshold = consolidation_threshold
        self.artifact_root = artifact_root or os.getenv(
            "KUMIHO_MEMORY_ARTIFACT_ROOT",
            os.path.join(os.path.expanduser("~"), ".kumiho", "artifacts"),
        )

        self.redis_buffer = redis_buffer or RedisMemoryBuffer(
            redis_url=redis_url,
            tenant_hint=tenant_hint,
        )
        if summarizer is not None:
            self.summarizer = summarizer
        elif llm_adapter is not None:
            self.summarizer = MemorySummarizer(adapter=llm_adapter)
        else:
            self.summarizer = MemorySummarizer()
        self.pii_redactor = pii_redactor or PIIRedactor()

        self.memory_store = memory_store if memory_store is not None else _load_default_store()
        self.memory_retrieve = (
            memory_retrieve if memory_retrieve is not None else _load_default_retrieve()
        )
        self.retry_queue = retry_queue
        self.store_max_retries = store_max_retries

    async def ingest_message(
        self,
        *,
        user_id: str,
        message: str,
        role: str = "user",
        channel: str = "unknown",
        context: str = "personal",
        session_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        resolved_session_id = session_id or await self._generate_session_id(user_id, context)

        metadata: Dict[str, Any] = {
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if attachments:
            artifact_pointers: List[Dict[str, Any]] = []
            for attachment in attachments:
                pointer = self._store_attachment(attachment, context=context)
                artifact_pointers.append(pointer)
            metadata["attachments"] = artifact_pointers

        result = await self.redis_buffer.add_message(
            project=self.project,
            session_id=resolved_session_id,
            role=role,
            content=message,
            metadata=metadata,
        )
        return {
            "success": True,
            "session_id": resolved_session_id,
            "message_count": result["message_count"],
            "attachments": metadata.get("attachments", []),
        }

    async def add_assistant_response(
        self,
        *,
        session_id: str,
        response: str,
        channel: str = "unknown",
    ) -> Dict[str, Any]:
        result = await self.redis_buffer.add_message(
            project=self.project,
            session_id=session_id,
            role="assistant",
            content=response,
            metadata={
                "channel": channel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        return {
            "success": True,
            "message_count": result["message_count"],
        }

    async def handle_user_message(
        self,
        *,
        user_id: str,
        message: str,
        channel: str = "unknown",
        context: str = "personal",
        session_id: Optional[str] = None,
        working_memory_limit: int = 10,
        recall_limit: int = 5,
    ) -> Dict[str, Any]:
        ingest_result = await self.ingest_message(
            user_id=user_id,
            message=message,
            role="user",
            channel=channel,
            context=context,
            session_id=session_id,
        )
        session_id = ingest_result["session_id"]

        working_memory_result = await self.redis_buffer.get_messages(
            project=self.project,
            session_id=session_id,
            limit=working_memory_limit,
        )

        long_term_memory = await self.recall_memories(message, limit=recall_limit)

        should_consolidate = (
            working_memory_result["message_count"] >= self.consolidation_threshold
        )

        return {
            "session_id": session_id,
            "working_memory": working_memory_result["messages"],
            "long_term_memory": long_term_memory,
            "should_consolidate": should_consolidate,
        }

    async def consolidate_session(self, *, session_id: str) -> Dict[str, Any]:
        messages_result = await self.redis_buffer.get_messages(
            project=self.project,
            session_id=session_id,
            limit=1000,
        )
        messages = messages_result["messages"]

        if not messages:
            return {"success": False, "error": "No messages to consolidate"}

        summary_result = await self.summarizer.summarize_conversation(messages)
        redacted_summary = self.pii_redactor.anonymize_summary(summary_result.get("summary", ""))

        # Reject credentials before sending to cloud graph (spec §10.4.5)
        self.pii_redactor.reject_credentials(redacted_summary)

        store_result: Dict[str, Any] = {}
        if self.memory_store:
            topics = summary_result.get("classification", {}).get("topics", [])
            user_lines: List[str] = []
            assistant_lines: List[str] = []

            title = summary_result.get("title", "Conversation")
            conversation_markdown = self._build_conversation_markdown(
                messages=messages,
                title=title,
                session_id=session_id,
                summary=redacted_summary,
                topics=topics,
                user_lines_out=user_lines,
                assistant_lines_out=assistant_lines,
            )

            space_hint = "/".join(topics[:2]) if topics else ""
            artifact_path = self._write_artifact(
                session_id=session_id,
                content=conversation_markdown,
                space_hint=space_hint,
            )

            # Collect attachment pointers from all messages in the session
            all_attachments: List[Dict[str, Any]] = []
            for msg in messages:
                msg_attachments = (msg.get("metadata") or {}).get("attachments", [])
                all_attachments.extend(msg_attachments)

            payload: Dict[str, Any] = {
                "project": self.project,
                "memory_type": summary_result.get("type", "summary"),
                "title": title,
                "summary": redacted_summary,
                "user_text": "\n".join(user_lines),
                "assistant_text": "\n".join(assistant_lines),
                "artifact_location": artifact_path,
                "artifact_name": "conversation",
                "bundle_name": topics[0] if topics else "",
                "space_hint": space_hint,
                "tags": ["summarized", "published"],
                "metadata": {
                    "session_id": session_id,
                    "message_count": str(len(messages)),
                    "topics": ",".join(topics),
                },
            }
            if all_attachments:
                payload["metadata"]["attachments"] = all_attachments

            store_result = await self._store_with_retry(**payload)

        await self.redis_buffer.clear_session(self.project, session_id)

        return {
            "success": True,
            "summary": redacted_summary,
            "store_result": store_result,
        }

    async def store_tool_execution(
        self,
        *,
        task: str,
        status: str = "done",
        exit_code: Optional[int] = None,
        duration_ms: Optional[int] = None,
        stdout: str = "",
        stderr: str = "",
        tools: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        space_hint: str = "",
        open_questions: Optional[List[str]] = None,
        derived_from: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Store a tool execution result as a structured memory.

        For successful executions, stores as ``type: action``.
        For failures (non-zero exit code or ``status`` in
        ``{"failed", "error", "blocked"}``), stores as ``type: error``.

        Parameters
        ----------
        task:
            Description of what was executed (e.g. ``"git push origin main"``).
        status:
            Execution outcome: ``"done"``, ``"failed"``, ``"error"``,
            ``"blocked"``.
        exit_code:
            Process exit code (0 = success).
        duration_ms:
            Execution duration in milliseconds.
        stdout / stderr:
            Captured output (stored locally as artifact, not uploaded).
        tools:
            Tool names used (e.g. ``["shell_exec"]``).
        topics:
            Classification topics (e.g. ``["git", "deployment"]``).
        space_hint:
            Space path hint for organising the memory.
        open_questions:
            Unresolved questions from failed executions.
        derived_from:
            Krefs this execution was derived from.
        """
        if not self.memory_store:
            return {"success": False, "error": "No memory_store configured"}

        is_error = status in ("failed", "error", "blocked") or (
            exit_code is not None and exit_code != 0
        )
        memory_type = "error" if is_error else "action"

        # Build title from task description
        prefix = "Failed" if is_error else "Successfully executed"
        title = f"{prefix}: {task[:60]}"

        # Build summary
        if is_error and stderr:
            summary = f"Attempted '{task}' but failed: {stderr[:200]}"
        elif is_error:
            summary = f"Attempted '{task}' but failed with status '{status}'"
        else:
            summary = f"Executed '{task}' successfully"

        summary = self.pii_redactor.anonymize_summary(summary)

        # Reject credentials before sending to cloud graph (spec §10.4.5)
        self.pii_redactor.reject_credentials(summary)

        # Write execution log as local artifact
        log_content = (
            f"# Tool Execution: {task}\n\n"
            f"**Status:** {status}  \n"
            f"**Exit code:** {exit_code}  \n"
            f"**Duration:** {duration_ms}ms  \n\n"
        )
        if stdout:
            log_content += f"## stdout\n\n```\n{stdout}\n```\n\n"
        if stderr:
            log_content += f"## stderr\n\n```\n{stderr}\n```\n\n"

        safe_name = task.replace(" ", "_").replace("/", "_")[:40]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        artifact_path = self._write_artifact(
            session_id=f"exec_{timestamp}_{safe_name}",
            content=log_content,
            space_hint=space_hint,
        )

        resolved_topics = topics or []
        knowledge: Dict[str, Any] = {
            "actions": [{
                "task": task,
                "status": status,
                "exit_code": exit_code,
                "duration_ms": duration_ms,
            }],
            "facts": [],
            "decisions": [],
            "open_questions": open_questions or [],
        }

        if is_error and stderr:
            knowledge["facts"].append({
                "claim": stderr[:200],
                "certainty": "high",
            })

        payload: Dict[str, Any] = {
            "project": self.project,
            "memory_type": memory_type,
            "title": title,
            "summary": summary,
            "user_text": task,
            "assistant_text": stdout[:500] if stdout else "",
            "artifact_location": artifact_path,
            "artifact_name": "execution_log",
            "bundle_name": resolved_topics[0] if resolved_topics else "",
            "space_hint": space_hint,
            "tags": [memory_type, status, "published"],
            "metadata": {
                "memory_type": memory_type,
                "exit_code": str(exit_code) if exit_code is not None else "",
                "duration_ms": str(duration_ms) if duration_ms is not None else "",
                "topics": ",".join(resolved_topics),
                "tools": ",".join(tools or []),
            },
        }
        if derived_from:
            payload["metadata"]["derived_from"] = derived_from

        store_result = await self._store_with_retry(**payload)
        return {"success": True, "memory_type": memory_type, "store_result": store_result}

    async def _store_with_retry(self, **payload: Any) -> Dict[str, Any]:
        """Call ``memory_store`` with retry + queue fallback.

        1. Try up to ``store_max_retries`` with exponential backoff.
        2. If all retries fail and a ``retry_queue`` is configured,
           enqueue the payload for later replay.
        3. If no queue is configured, raise the exception.
        """
        if not self.memory_store:
            return {}

        try:
            return await retry_with_backoff(
                self.memory_store,
                max_retries=self.store_max_retries,
                **payload,
            )
        except Exception as exc:
            if self.retry_queue is not None:
                self.retry_queue.enqueue(payload)
                logger.warning(
                    "memory_store failed after %d retries — queued for later: %s",
                    self.store_max_retries,
                    exc,
                )
                return {"queued": True, "error": str(exc)}
            raise

    async def flush_retry_queue(self) -> Dict[str, int]:
        """Replay queued ``memory_store`` calls that previously failed.

        Returns ``{"succeeded": N, "failed": M}``.  Items that still
        fail remain in the queue for the next flush attempt.
        """
        if not self.retry_queue or not self.memory_store:
            return {"succeeded": 0, "failed": 0}
        return await self.retry_queue.flush(self.memory_store)

    @staticmethod
    def _build_conversation_markdown(
        *,
        messages: List[Dict[str, Any]],
        title: str,
        session_id: str,
        summary: str,
        topics: List[str],
        user_lines_out: List[str],
        assistant_lines_out: List[str],
    ) -> str:
        """Build a Markdown document from the full interleaved conversation."""
        parts: List[str] = [
            f"# {title}",
            "",
            f"**Session:** `{session_id}`  ",
            f"**Messages:** {len(messages)}  ",
        ]
        if topics:
            parts.append(f"**Topics:** {', '.join(topics)}  ")
        parts.append(f"**Summary:** {summary}")
        parts.extend(["", "---", ""])

        for msg in messages:
            role = msg.get("role", "unknown")
            text = msg.get("content", "")
            timestamp = (
                msg.get("timestamp", "")
                or msg.get("metadata", {}).get("timestamp", "")
            )

            if role == "assistant":
                assistant_lines_out.append(text)
            else:
                user_lines_out.append(text)

            header = f"### {role.capitalize()}"
            if timestamp:
                header += f"  \n<sub>{timestamp}</sub>"
            parts.extend([header, "", text, ""])

        return "\n".join(parts)

    def _store_attachment(
        self, attachment: Dict[str, Any], *, context: str = ""
    ) -> Dict[str, Any]:
        """Copy an attached file into the artifact directory and return a pointer.

        Parameters
        ----------
        attachment:
            Must contain ``path`` (source file).  Optional keys:
            ``content_type`` (MIME), ``description``.
        context:
            Space hint for organising the file inside the artifact tree.

        Returns
        -------
        Artifact pointer dict with ``location``, ``hash``, ``size_bytes``,
        ``content_type``, ``original_name``, and ``description``.
        """
        source = Path(attachment["path"])
        if not source.is_file():
            raise FileNotFoundError(f"Attachment not found: {source}")

        # Determine MIME type
        content_type = attachment.get("content_type")
        if not content_type:
            content_type, _ = mimetypes.guess_type(source.name)
            content_type = content_type or "application/octet-stream"

        # Target directory: {artifact_root}/{project}/attachments/{context}/
        target_dir = Path(self.artifact_root) / self.project / "attachments"
        if context:
            target_dir = target_dir / context
        target_dir.mkdir(parents=True, exist_ok=True)

        # Compute hash before copying (stream-friendly)
        sha = hashlib.sha256()
        size = 0
        with open(source, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                sha.update(chunk)
                size += len(chunk)
        file_hash = sha.hexdigest()

        # Copy with hash prefix to avoid collisions
        dest = target_dir / f"{file_hash[:12]}_{source.name}"
        shutil.copy2(source, dest)

        return {
            "type": "attachment",
            "original_name": source.name,
            "storage": "local",
            "location": dest.as_uri(),
            "hash": f"sha256:{file_hash}",
            "size_bytes": size,
            "content_type": content_type,
            "description": attachment.get("description", ""),
        }

    def _write_artifact(
        self, *, session_id: str, content: str, space_hint: str = ""
    ) -> str:
        """Write conversation Markdown and return the path.

        Directory layout::

            {artifact_root}/{project}/{space_segments...}/{session}.md
        """
        safe_name = session_id.replace(":", "_").replace("/", "_")
        target_dir = Path(self.artifact_root) / self.project
        if space_hint:
            segments = [seg for seg in space_hint.split("/") if seg.strip()]
            target_dir = target_dir.joinpath(*segments)
        target_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = target_dir / f"{safe_name}.md"
        artifact_path.write_text(content, encoding="utf-8")
        return str(artifact_path)

    async def recall_memories(
        self,
        query: str,
        *,
        limit: int = 5,
        space_paths: Optional[List[str]] = None,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve long-term memories by semantic query.

        Parameters
        ----------
        query:
            Natural-language search query.
        limit:
            Maximum number of results.
        space_paths:
            Restrict search to these space paths (e.g.
            ``["CognitiveMemory/personal"]``).  When ``None``, searches
            all spaces in the project.
        memory_types:
            Filter by memory type (e.g. ``["error"]`` to find past
            mistakes, ``["action", "error"]`` for all tool executions).
            When ``None``, returns all types.
        """
        if not self.memory_retrieve:
            return []

        kwargs: Dict[str, Any] = {
            "project": self.project,
            "query": query,
            "limit": limit,
        }
        if space_paths:
            kwargs["space_paths"] = space_paths
        if memory_types:
            kwargs["memory_types"] = memory_types

        result = await _maybe_await(self.memory_retrieve, **kwargs)

        if isinstance(result, dict) and "revision_krefs" in result:
            revision_krefs = result.get("revision_krefs", [])
            scores = result.get("scores", [])

            # Fetch revision metadata concurrently so the LLM gets
            # usable content (title, summary, type) instead of bare krefs.
            meta_tasks = [
                self._fetch_revision_metadata(kref) for kref in revision_krefs
            ]
            meta_results = await asyncio.gather(*meta_tasks)

            enriched: List[Dict[str, Any]] = []
            for i, (kref, meta) in enumerate(zip(revision_krefs, meta_results)):
                entry: Dict[str, Any] = {"kref": kref}
                if i < len(scores):
                    entry["score"] = scores[i]
                entry.update(meta)
                enriched.append(entry)
            return enriched
        if isinstance(result, list):
            return result
        return []

    async def _fetch_revision_metadata(self, kref: str) -> Dict[str, Any]:
        """Fetch revision metadata and raw artifact content.

        The revision metadata contains redacted/sanitized fields (title,
        summary, type).  The source of truth for the full conversation is
        the raw Markdown artifact stored locally.  This method reads both
        so the LLM gets usable context for recall.
        """
        try:
            import kumiho

            revision = await asyncio.to_thread(kumiho.get_revision, kref)
            meta = revision.metadata or {}
            entry: Dict[str, Any] = {
                "title": meta.get("title", ""),
                "summary": meta.get("summary", ""),
                "type": meta.get("type", ""),
                "space": meta.get("space", ""),
                "created_at": getattr(revision, "created_at", ""),
                "tags": getattr(revision, "tags", []),
            }

            # Read the raw conversation from the local artifact file.
            try:
                artifacts = await asyncio.to_thread(revision.get_artifacts)
                for artifact in artifacts:
                    location = getattr(artifact, "location", "")
                    if not location:
                        continue
                    content = await self._read_artifact_content(location)
                    if content:
                        entry["artifact_name"] = getattr(artifact, "name", "")
                        entry["artifact_location"] = location
                        entry["content"] = content
                        break  # use the first readable artifact
            except Exception as exc:
                logger.debug("Failed to fetch artifacts for %s: %s", kref, exc)

            return entry
        except Exception as exc:
            logger.debug("Failed to fetch revision %s: %s", kref, exc)
            return {}

    @staticmethod
    async def _read_artifact_content(location: str) -> str:
        """Read a local artifact file and return its text content."""
        path = Path(location)
        if not path.is_file():
            return ""
        try:
            return await asyncio.to_thread(
                path.read_text, "utf-8",
            )
        except Exception:
            return ""

    async def close(self) -> None:
        await self.redis_buffer.close()

    async def _generate_session_id(self, user_canonical_id: str, context: str) -> str:
        user_hash = hashlib.sha256(user_canonical_id.encode()).hexdigest()[:10]
        date = datetime.now(timezone.utc).strftime("%Y%m%d")

        sequence = 1
        if hasattr(self.redis_buffer, "next_session_sequence"):
            try:
                sequence = await self.redis_buffer.next_session_sequence(
                    user_canonical_id=user_canonical_id,
                    date_str=date,
                )
            except Exception:
                sequence = 1

        return f"{context}:user-{user_hash}:{date}:{sequence:03d}"


def get_memory_space(
    channel_type: str,
    *,
    project: str = "CognitiveMemory",
    team_slug: str = "",
    group_id: str = "",
) -> str:
    """Map a channel type to a Kumiho memory space path.

    This enforces session sandboxing so that memories from different
    contexts (personal DMs, team channels, group chats) don't leak
    across boundaries.

    Parameters
    ----------
    channel_type:
        One of ``"personal_dm"``, ``"team_channel"``, ``"group_dm"``.
        Unknown types default to ``"personal"``.
    project:
        Kumiho project name (default ``"CognitiveMemory"``).
    team_slug:
        Team identifier, required when ``channel_type`` is
        ``"team_channel"``.
    group_id:
        Group identifier, required when ``channel_type`` is
        ``"group_dm"``.

    Returns
    -------
    Space path string, e.g. ``"CognitiveMemory/work/team-alpha"``.
    """
    if channel_type == "team_channel":
        slug = team_slug or "default"
        return f"{project}/work/{slug}"
    if channel_type == "group_dm":
        gid = group_id or "default"
        return f"{project}/groups/{gid}"
    # personal_dm and any unknown type
    return f"{project}/personal"


def _load_default_store() -> Optional[StoreCallable]:
    try:
        from kumiho.mcp_server import tool_memory_store  # type: ignore

        return tool_memory_store
    except Exception:
        return None


def _load_default_retrieve() -> Optional[RetrieveCallable]:
    try:
        from kumiho.mcp_server import tool_memory_retrieve  # type: ignore

        return tool_memory_retrieve
    except Exception:
        return None


async def _maybe_await(func: Callable[..., Any], **kwargs: Any) -> Any:
    result = func(**kwargs)
    if inspect.isawaitable(result):
        return await result
    return result
