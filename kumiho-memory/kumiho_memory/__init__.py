"""Kumiho Memory - Universal memory provider for AI agents."""

__version__ = "0.3.5"

from kumiho_memory.redis_memory import RedisMemoryBuffer, _token_override_var as redis_token_override_var
from kumiho_memory.memory_manager import (
    AutoAssessFn,
    MemoryAssessResult,
    UniversalMemoryManager,
    get_memory_space,
)
from kumiho_memory.summarization import (
    AnthropicAdapter,
    EmbeddingAdapter,
    LLMAdapter,
    MemorySummarizer,
    OpenAICompatAdapter,
    OpenAICompatEmbeddingAdapter,
)
from kumiho_memory.privacy import PIIRedactor, CredentialDetectedError
from kumiho_memory.retry import RetryQueue
from kumiho_memory.dream_state import DreamState, MemoryAssessment, DreamStateStats
from kumiho_memory.graph_augmentation import GraphAugmentedRecall, GraphAugmentationConfig

__all__ = [
    "__version__",
    "LLMAdapter",
    "EmbeddingAdapter",
    "OpenAICompatAdapter",
    "OpenAICompatEmbeddingAdapter",
    "AnthropicAdapter",
    "RedisMemoryBuffer",
    "AutoAssessFn",
    "MemoryAssessResult",
    "UniversalMemoryManager",
    "get_memory_space",
    "MemorySummarizer",
    "PIIRedactor",
    "CredentialDetectedError",
    "RetryQueue",
    "DreamState",
    "MemoryAssessment",
    "DreamStateStats",
    "GraphAugmentedRecall",
    "GraphAugmentationConfig",
]
