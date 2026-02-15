"""Kumiho Memory - Universal memory provider for AI agents."""

__version__ = "0.2.0"

from kumiho_memory.redis_memory import RedisMemoryBuffer
from kumiho_memory.memory_manager import UniversalMemoryManager, get_memory_space
from kumiho_memory.summarization import (
    AnthropicAdapter,
    LLMAdapter,
    MemorySummarizer,
    OpenAICompatAdapter,
)
from kumiho_memory.privacy import PIIRedactor, CredentialDetectedError
from kumiho_memory.retry import RetryQueue
from kumiho_memory.dream_state import DreamState, MemoryAssessment, DreamStateStats

__all__ = [
    "__version__",
    "LLMAdapter",
    "OpenAICompatAdapter",
    "AnthropicAdapter",
    "RedisMemoryBuffer",
    "UniversalMemoryManager",
    "get_memory_space",
    "MemorySummarizer",
    "PIIRedactor",
    "CredentialDetectedError",
    "RetryQueue",
    "DreamState",
    "MemoryAssessment",
    "DreamStateStats",
]
