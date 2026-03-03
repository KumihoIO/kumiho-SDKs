import asyncio
from kumiho_memory import UniversalMemoryManager, RedisMemoryBuffer, MemorySummarizer, PIIRedactor

async def test_consolidation():
    memory = RedisMemoryBuffer()
    manager = UniversalMemoryManager(
        redis_buffer=memory,
        summarizer=MemorySummarizer(),  # Uses OPENAI_API_KEY
        pii_redactor=PIIRedactor(),
        consolidation_threshold=3,      # Low threshold for testing
    )

    session_id = "consolidation-test-001"

    # 1. Ingest messages
    conversations = [
        ("user", "I'm building a graph-based asset manager called Kumiho"),
        ("assistant", "Interesting! What technology stack are you using?"),
        ("user", "Rust for the gRPC server, Neo4j for the graph, and Redis for caching"),
        ("assistant", "That's a solid stack. How do you handle versioning?"),
        ("user", "Each asset has revisions tracked in Neo4j with DERIVED_FROM edges"),
    ]

    for role, content in conversations:
        result = await manager.ingest_message(
            user_id="test-user",
            message=content,
            role=role,
            channel="test",
            session_id=session_id,
        )
        print(f"Ingested {result['message_count']} messages")

    # 2. Consolidate (summarize + PII redact + store to Neo4j)
    print("\nConsolidating session...")
    consolidation = await manager.consolidate_session(session_id=session_id)

    print(f"Success: {consolidation['success']}")
    print(f"Summary: {consolidation['summary']}")
    print(f"Store result: {consolidation['store_result']}")

    # 3. Verify session cleared
    remaining = await memory.get_messages(
        project="CognitiveMemory",
        session_id=session_id,
        limit=10,
    )
    print(f"\nMessages after consolidation: {remaining['message_count']}")

    await manager.close()

asyncio.run(test_consolidation())
