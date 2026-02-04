"""LLM-based summarization for memory consolidation."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# LLM Adapter protocol — implement this to add any provider
# ---------------------------------------------------------------------------


@runtime_checkable
class LLMAdapter(Protocol):
    """Interface for LLM providers.

    Implement this protocol to plug in any LLM provider (Gemini, Mistral,
    Ollama, Cohere, etc.).  Built-in adapters are provided for
    OpenAI-compatible and Anthropic APIs.

    Example custom adapter::

        class MyAdapter:
            async def chat(self, *, messages, model, system="",
                           max_tokens=1024, json_mode=False) -> str:
                # call your LLM here
                return response_text
    """

    async def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        model: str,
        system: str = "",
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> str:
        """Send a chat request and return the raw response text."""
        ...


# ---------------------------------------------------------------------------
# Built-in adapters
# ---------------------------------------------------------------------------


class OpenAICompatAdapter:
    """Adapter for OpenAI and any OpenAI-compatible API.

    Works with: OpenAI, Azure OpenAI, Google Gemini (via OpenAI compat),
    Ollama, vLLM, LiteLLM, Together, Groq, Mistral, and others.

    Usage::

        # Standard OpenAI
        adapter = OpenAICompatAdapter.create(api_key="sk-...")

        # Gemini via OpenAI-compatible endpoint
        adapter = OpenAICompatAdapter.create(
            api_key="your-gemini-key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        # Local Ollama
        adapter = OpenAICompatAdapter.create(
            base_url="http://localhost:11434/v1",
        )
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def create(
        cls,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> "OpenAICompatAdapter":
        try:
            from openai import AsyncOpenAI  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "openai package is required: pip install kumiho-memory[openai]"
            ) from exc

        kwargs: Dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        return cls(AsyncOpenAI(**kwargs))

    async def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        model: str,
        system: str = "",
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> str:
        full_messages: List[Dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": full_messages,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""


class AnthropicAdapter:
    """Adapter for the Anthropic Messages API."""

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def create(cls, *, api_key: Optional[str] = None) -> "AnthropicAdapter":
        try:
            from anthropic import AsyncAnthropic  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required: pip install kumiho-memory[anthropic]"
            ) from exc

        kwargs: Dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        return cls(AsyncAnthropic(**kwargs))

    async def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        model: str,
        system: str = "",
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> str:
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""


# ---------------------------------------------------------------------------
# Provider / model defaults
# ---------------------------------------------------------------------------

PROVIDER_DEFAULTS: Dict[str, Dict[str, str]] = {
    "openai": {
        "model": "gpt-4o",
        "light_model": "gpt-4o-mini",
    },
    "anthropic": {
        "model": "claude-sonnet-4-5-20241022",
        "light_model": "claude-haiku-4-20250414",
    },
}

# Key-prefix heuristics used when the caller only supplies an API key.
_KEY_PREFIX_MAP = {
    "sk-": "openai",
}


def _detect_provider(api_key: str) -> str:
    """Best-effort provider detection from API key prefix."""
    for prefix, provider in _KEY_PREFIX_MAP.items():
        if api_key.startswith(prefix):
            return provider
    # Anthropic keys don't have a stable prefix; default to openai if unsure.
    return "openai"


class MemorySummarizer:
    """Summarize conversations into structured memory.

    Supports any LLM provider through the adapter pattern:

    1. **Built-in providers** (``provider="openai"`` or ``"anthropic"``):
       Auto-configured from env vars or explicit arguments.

    2. **OpenAI-compatible APIs** (Gemini, Ollama, Groq, Together, vLLM…):
       Set ``base_url`` to point at the compatible endpoint.

    3. **Fully custom providers**: Pass any object implementing the
       ``LLMAdapter`` protocol via the ``adapter`` parameter.

    Configuration priority (highest → lowest):

    1. Explicit ``adapter`` — bypasses all other config.
    2. Constructor arguments (``api_key``, ``provider``, ``model``,
       ``base_url``).
    3. Unified env vars: ``KUMIHO_LLM_API_KEY``, ``KUMIHO_LLM_PROVIDER``,
       ``KUMIHO_LLM_MODEL``, ``KUMIHO_LLM_BASE_URL``.
    4. Provider-specific env vars: ``OPENAI_API_KEY`` / ``ANTHROPIC_API_KEY``.
    5. Built-in defaults per provider.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        light_model: Optional[str] = None,
        base_url: Optional[str] = None,
        adapter: Optional[LLMAdapter] = None,
        client: Optional[Any] = None,
    ) -> None:
        # --- Fast path: caller provides a ready adapter ---
        if adapter is not None:
            self.adapter: LLMAdapter = adapter
            self.provider = provider or "custom"
            self.model = model or "default"
            self.light_model = light_model or model or "default"
            self.api_key = api_key
            return

        # --- Resolve configuration ---
        resolved_key = api_key or os.getenv("KUMIHO_LLM_API_KEY")

        resolved_base_url = (
            base_url
            or os.getenv("KUMIHO_LLM_BASE_URL", "").strip()
            or None
        )

        resolved_provider = (
            (provider or "").strip().lower()
            or os.getenv("KUMIHO_LLM_PROVIDER", "").strip().lower()
            or self._provider_from_env_keys()
            or (_detect_provider(resolved_key) if resolved_key else "openai")
        )

        defaults = PROVIDER_DEFAULTS.get(resolved_provider, {})

        self.provider = resolved_provider
        self.api_key = resolved_key
        self.model = (
            model
            or os.getenv("KUMIHO_LLM_MODEL", "").strip()
            or defaults.get("model", "gpt-4o")
        )
        self.light_model = (
            light_model
            or os.getenv("KUMIHO_LLM_LIGHT_MODEL", "").strip()
            or defaults.get("light_model", self.model)
        )

        # --- Build adapter ---
        if client is not None:
            # Backward compat: wrap a raw SDK client object
            if resolved_provider == "anthropic":
                self.adapter = AnthropicAdapter(client)
            else:
                self.adapter = OpenAICompatAdapter(client)
        else:
            self.adapter = self._build_adapter(
                resolved_provider, resolved_key, resolved_base_url,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def summarize_conversation(
        self,
        messages: List[Dict[str, Any]],
        *,
        context: Optional[str] = None,
        strict: bool = False,
    ) -> Dict[str, Any]:
        """Summarize conversation into structured memory."""

        system_prompt = self._system_prompt()
        conversation_text = self._format_messages(messages)
        user_prompt = self._user_prompt(conversation_text, context=context)

        try:
            raw = await self.adapter.chat(
                messages=[{"role": "user", "content": user_prompt}],
                model=self.model,
                system=system_prompt,
                max_tokens=1024,
                json_mode=True,
            )
            result = self._parse_json(raw)
        except Exception as exc:
            if strict:
                raise
            return self._fallback_summary(messages, error=str(exc))

        return self._normalize_summary(result, fallback_messages=messages)

    async def extract_topics(self, text: str) -> List[str]:
        """Extract topic keywords from text."""
        prompt = (
            "Extract 3-5 concise topic keywords from this text.\n\n"
            f"{text}\n\nTopics (comma-separated):"
        )
        response = await self.adapter.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.light_model,
            max_tokens=60,
        )
        topics = [item.strip().lower() for item in response.split(",") if item.strip()]
        return topics

    # ------------------------------------------------------------------
    # Adapter construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_adapter(
        provider: str,
        api_key: Optional[str],
        base_url: Optional[str],
    ) -> LLMAdapter:
        if provider == "anthropic" and not base_url:
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            return AnthropicAdapter.create(api_key=key)

        # Default to OpenAI-compatible (covers openai, gemini, ollama, etc.)
        key = api_key or os.getenv("OPENAI_API_KEY")
        return OpenAICompatAdapter.create(api_key=key, base_url=base_url)

    @staticmethod
    def _provider_from_env_keys() -> str:
        """Detect provider from which provider-specific env var is set."""
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        return ""

    # ------------------------------------------------------------------
    # Prompt templates
    # ------------------------------------------------------------------

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a memory extraction AI. Analyze conversations and extract structured knowledge.\n"
            "Output JSON in this exact schema:\n"
            "{\n"
            '  "type": "summary | fact | decision | action | reflection | error",\n'
            '  "title": "One-line summary (max 10 words)",\n'
            '  "summary": "1-2 sentence distilled understanding",\n'
            '  "knowledge": {\n'
            '    "facts": [{"claim": "...", "certainty": "low | medium | high"}],\n'
            '    "decisions": [{"decision": "...", "reason": "..."}],\n'
            '    "actions": [{"task": "...", "status": "open | done | blocked"}],\n'
            '    "open_questions": ["..."]\n'
            "  },\n"
            '  "classification": {\n'
            '    "topics": ["topic1", "topic2"],\n'
            '    "entities": ["person1", "project1"]\n'
            "  }\n"
            "}\n"
            "Rules:\n"
            "- Be concise\n"
            "- Extract only significant facts/decisions\n"
            "- Redact PII using placeholders like [EMAIL], [PHONE]\n"
            "- Focus on knowledge, not verbatim quotes"
        )

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        lines = []
        for msg in messages:
            role = str(msg.get("role", "unknown"))
            content = str(msg.get("content", ""))
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines)

    @staticmethod
    def _user_prompt(conversation_text: str, *, context: Optional[str]) -> str:
        context_line = f"\nContext: {context}\n" if context else ""
        return (
            "Conversation to summarize:\n\n"
            f"{conversation_text}\n"
            f"{context_line}\n"
            "Extract structured knowledge in JSON format."
        )

    # ------------------------------------------------------------------
    # JSON parsing & fallbacks
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        raise ValueError("No valid JSON found in summarizer response")

    @staticmethod
    def _normalize_summary(result: Dict[str, Any], *, fallback_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary = dict(result)
        summary.setdefault("type", "summary")
        summary.setdefault("title", "Conversation summary")
        summary.setdefault("summary", MemorySummarizer._fallback_summary_text(fallback_messages))
        summary.setdefault("knowledge", {})
        summary.setdefault("classification", {})
        summary["knowledge"].setdefault("facts", [])
        summary["knowledge"].setdefault("decisions", [])
        summary["knowledge"].setdefault("actions", [])
        summary["knowledge"].setdefault("open_questions", [])
        summary["classification"].setdefault("topics", [])
        summary["classification"].setdefault("entities", [])
        return summary

    @staticmethod
    def _fallback_summary(messages: List[Dict[str, Any]], *, error: str) -> Dict[str, Any]:
        text = MemorySummarizer._fallback_summary_text(messages)
        return {
            "type": "summary",
            "title": "Conversation summary",
            "summary": text,
            "knowledge": {"facts": [], "decisions": [], "actions": [], "open_questions": []},
            "classification": {"topics": [], "entities": []},
            "error": error,
        }

    @staticmethod
    def _fallback_summary_text(messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return "No conversation content available."
        last = messages[-1].get("content") or ""
        snippet = str(last).strip()
        if len(snippet) > 180:
            snippet = f"{snippet[:177]}..."
        return snippet or "Conversation summary unavailable."
