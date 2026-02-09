# Release Notes — kumiho-memory

## v0.1.2

**Release Date:** 2026-02-09

`v0.1.2` is a documentation-focused patch release.

### Highlights

- Updated `README.md` status block with latest patch metadata
- Corrected README heading formatting
- Synced package version metadata across `pyproject.toml` and `kumiho_memory.__version__`
- Corrected project changelog URL to point to `RELEASE_NOTES.md`

No breaking API changes are introduced in this release.

---

## v0.1.1

**Release Date:** 2026-02-08

`v0.1.1` is a patch release focused on MCP integration, Redis proxy/auth
hardening, and test expansion.

---

## Highlights

### MCP Tool Integration (New)

Added `kumiho_memory.mcp_tools` with **9 MCP tool wrappers** that are
auto-discovered by the core `kumiho` MCP server when `kumiho-memory` is
installed.

Available tools:

- `kumiho_chat_add`
- `kumiho_chat_get`
- `kumiho_chat_clear`
- `kumiho_memory_ingest`
- `kumiho_memory_add_response`
- `kumiho_memory_consolidate`
- `kumiho_memory_recall`
- `kumiho_memory_store_execution`
- `kumiho_memory_dream_state`

### Redis Proxy + Auth Resilience

Improved memory proxy reliability in `RedisMemoryBuffer`:

- Better handling of Firebase token vs control-plane token flows
- Automatic token refresh and retry on proxy auth failures (401/403)
- Cleaner fallback path between discovery, direct URL, and proxy mode

### Documentation Updates

- Expanded README with onboarding/initialization guidance
- Added MCP integration setup and tool reference
- Refreshed usage examples for working memory and Dream State

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
| `mcp_tools` | `MEMORY_TOOLS`, `MEMORY_TOOL_HANDLERS` |

---

## Test Coverage

82 tests total:

- 16 MCP tool tests
- 15 Dream State tests
- 28 memory manager tests
- 10 retry tests
- 9 Redis buffer tests
- 3 summarization tests
- 1 privacy test

---

## Requirements

- Python >= 3.10
- `kumiho` >= 0.9.0
- `redis[hiredis]` >= 5.0.0
- `requests` >= 2.31.0

Optional extras:

- `kumiho-memory[openai]`
- `kumiho-memory[anthropic]`
- `kumiho-memory[all]`

---

## Upgrade

```bash
pip install -U kumiho-memory[all]
```

No breaking API changes from `v0.1.0` are introduced in this release.
