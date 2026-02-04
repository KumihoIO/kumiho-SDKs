# Kumiho Memory

Universal, pip-installable memory provider for AI agents built on
[Kumiho Cloud](https://kumiho.io). Provides working memory, long-term
consolidation, privacy-aware summarization, and scheduled memory maintenance.

## Features

| Module | Class | Description |
|--------|-------|-------------|
| `redis_memory` | `RedisMemoryBuffer` | Fast working memory backed by Redis / Upstash |
| `memory_manager` | `UniversalMemoryManager` | Orchestrates ingest, consolidation, recall, and tool-execution storage |
| `summarization` | `MemorySummarizer` | LLM-based conversation summarization (OpenAI, Anthropic, or custom) |
| `privacy` | `PIIRedactor` | PII detection and anonymization before storage |
| `retry` | `RetryQueue` | File-backed retry queue for resilient store operations |
| `dream_state` | `DreamState` | Scheduled memory consolidation ("Dream State") — deprecates, tags, and links memories |

## Install

```bash
pip install kumiho-memory

# With LLM provider extras
pip install kumiho-memory[openai]      # OpenAI / OpenAI-compatible
pip install kumiho-memory[anthropic]   # Anthropic Claude
pip install kumiho-memory[all]         # Both
```

Requires Python 3.10+.

## Quick Start

### Working Memory + Consolidation

```python
from kumiho_memory import RedisMemoryBuffer, UniversalMemoryManager

buffer = RedisMemoryBuffer()
manager = UniversalMemoryManager(redis_buffer=buffer)

# Ingest a user message
result = await manager.ingest_message(
    user_id="user-1",
    message="I prefer dark mode in all my editors.",
    context="personal",
)

# Add assistant response
await manager.add_assistant_response(
    session_id=result["session_id"],
    response="Noted -- I'll remember your dark mode preference.",
)

# Consolidate into long-term memory
report = await manager.consolidate_session(session_id=result["session_id"])
```

### Recall Memories

```python
results = await manager.recall_memories(
    "What are the user's UI preferences?",
    limit=5,
)
```

### Store Tool Executions

```python
result = await manager.store_tool_execution(
    task="git push origin main",
    status="failed",
    exit_code=128,
    stderr="Permission denied (publickey).",
    tools=["shell_exec"],
    topics=["git", "ssh"],
)
```

### Dream State (Scheduled Consolidation)

Dream State runs periodically (e.g. nightly) to consolidate the memory graph.
It replays new events, uses an LLM to assess each memory, and applies
deprecation, tagging, metadata enrichment, and relationship linking.

```python
from kumiho_memory import DreamState

ds = DreamState(project="CognitiveMemory")
report = await ds.run()

print(f"Events processed: {report['events_processed']}")
print(f"Deprecated: {report['deprecated']}")
print(f"Tags added: {report['tags_added']}")
print(f"Edges created: {report['edges_created']}")
```

Run as a cron job:

```bash
# Run nightly at 3 AM
0 3 * * * /usr/bin/python3 /path/to/run_dream_state.py
```

Key safety guards:
- Memories tagged `published` are never deprecated (immutable)
- Max 50% of assessed memories can be deprecated per run
- `dry_run=True` mode for previewing changes without mutations

## Environment

Set credentials so discovery can locate your regional Upstash Redis:

```
KUMIHO_AUTH_TOKEN=...
KUMIHO_CONTROL_PLANE_URL=https://control.kumiho.cloud
```

You can also explicitly set the Redis URL for local development:

```
UPSTASH_REDIS_URL=rediss://default:xxx@region-xxx.upstash.io:6379
```

If you want to keep the Redis password server-side, point the client at the
control-plane memory proxy instead:

```
KUMIHO_MEMORY_PROXY_URL=https://control.kumiho.cloud/api/memory/redis
```

`RedisMemoryBuffer()` will automatically use the cached tenant info created
by `kumiho-cli login` / `kumiho-cli refresh` for proper namespacing, so you
do not need to pass a tenant slug manually.

## LLM Configuration

`MemorySummarizer` auto-detects available providers from environment variables:

| Variable | Provider |
|----------|----------|
| `ANTHROPIC_API_KEY` | Anthropic Claude |
| `OPENAI_API_KEY` | OpenAI |

Or pass an adapter explicitly:

```python
from kumiho_memory import OpenAICompatAdapter, MemorySummarizer

adapter = OpenAICompatAdapter.create(
    api_key="sk-...",
    base_url="http://localhost:11434/v1",  # Ollama
)
summarizer = MemorySummarizer(adapter=adapter, model="llama3")
```

## License

MIT
