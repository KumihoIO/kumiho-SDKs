# Release Notes — kumiho-memory v0.1.0

**Release Date:** 2026-02-04

This is the initial public release of `kumiho-memory`, a universal memory
provider for AI agents built on Kumiho Cloud.

---

## Highlights

### Dream State — Scheduled Memory Consolidation

The headline feature of this release is **Dream State**, an automated memory
maintenance system inspired by how the human brain consolidates memories during
sleep. When run on a schedule (e.g. nightly at 3 AM), Dream State:

- Replays all new memory events since the last run
- Fetches full revision data and inspects bundle groupings
- Sends memories to an LLM for assessment in configurable batches
- Applies recommendations: deprecation, tag enrichment, metadata updates, and
  relationship linking
- Persists a cursor for incremental processing and generates a detailed
  Markdown report

Safety guards ensure responsible automated consolidation:

- **Published protection** — memories tagged `published` are never deprecated,
  preserving thought processes and execution decisions as immutable records
- **Deprecation circuit breaker** — at most 50% of assessed memories can be
  deprecated in a single run
- **Dry run mode** — preview assessments without applying any mutations
- **Error isolation** — individual action failures do not halt the run

### Universal Memory Manager

Full lifecycle orchestration for AI agent memory:

- **Ingest** — buffer user/assistant messages in Redis with automatic session
  tracking
- **Consolidate** — summarize conversations with LLM, redact PII, write local
  artifacts, and store to Kumiho's graph
- **Recall** — retrieve relevant long-term memories by semantic query with
  optional space path and memory type filters
- **Tool execution storage** — structured capture of tool/command results as
  `action` or `error` memory types with execution logs

### Resilient Storage

- Exponential backoff retry with configurable max attempts
- File-backed retry queue for offline persistence when the server is
  unreachable
- Queue flush replays failed payloads on next available connection

### Privacy

- `PIIRedactor` detects and anonymizes personally identifiable information
  before summaries are stored

---

## Modules

| Module | Public API |
|--------|------------|
| `memory_manager` | `UniversalMemoryManager`, `get_memory_space` |
| `redis_memory` | `RedisMemoryBuffer` |
| `summarization` | `MemorySummarizer`, `LLMAdapter`, `OpenAICompatAdapter`, `AnthropicAdapter` |
| `privacy` | `PIIRedactor` |
| `retry` | `RetryQueue` |
| `dream_state` | `DreamState`, `MemoryAssessment`, `DreamStateStats` |

---

## LLM Provider Support

Summarization and Dream State assessment work with any OpenAI-compatible API
out of the box:

- **OpenAI** — GPT-4o, GPT-4, etc.
- **Anthropic** — Claude Sonnet, Opus, Haiku
- **Self-hosted** — Ollama, vLLM, or any OpenAI-compatible endpoint

Auto-detection from environment variables (`OPENAI_API_KEY`,
`ANTHROPIC_API_KEY`) or explicit adapter injection.

---

## Test Coverage

59 tests covering the full package:

- 15 Dream State tests (empty stream, full pipeline, cursor round-trip,
  deprecation, tagging, relationships, dry run, published protection,
  circuit breaker, report generation, bundle context, JSON parsing)
- 28 memory manager tests (consolidation, recall, attachments, tool execution,
  space paths, memory types, retry, queue)
- 6 retry tests (backoff, queue drain, flush, partial failure)
- 5 Redis buffer tests
- 3 summarization tests
- 2 privacy tests

---

## Requirements

- Python >= 3.10
- `kumiho` >= 0.9.0
- `redis[hiredis]` >= 5.0.0
- `requests` >= 2.31.0

Optional extras: `kumiho-memory[openai]`, `kumiho-memory[anthropic]`,
`kumiho-memory[all]`.

---

## Getting Started

```bash
pip install kumiho-memory[all]
```

```python
from kumiho_memory import (
    RedisMemoryBuffer,
    UniversalMemoryManager,
    DreamState,
)

# Working memory + consolidation
buffer = RedisMemoryBuffer()
manager = UniversalMemoryManager(redis_buffer=buffer)

# Scheduled memory maintenance
ds = DreamState(project="CognitiveMemory")
report = await ds.run()
```

See the [README](README.md) for full usage examples and environment
configuration.
