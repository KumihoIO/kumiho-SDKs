
import asyncio
from kumiho_memory import RedisMemoryBuffer, MemorySummarizer, PIIRedactor

async def test_summarization():
    memory = RedisMemoryBuffer()
    summarizer = MemorySummarizer()  # defaults to provider="openai", model="gpt-4-turbo"
    redactor = PIIRedactor()

    # 1. Ingest some test messages
    session_id = "test-summarize-001"
    messages = [
        ("user", "I'm working on a Rust gRPC server for asset management"),
        ("assistant", "That sounds like an interesting project. What kind of assets?"),
        ("user", "Creative assets - 3D models, textures, images. We use Neo4j for the graph"),
        ("assistant", "Graph databases are great for tracking relationships between assets"),
        ("user", "Exactly. We also need to track version lineage and AI-generated derivatives"),
    ]

    for role, content in messages:
        await memory.add_message(
            project="CognitiveMemory",
            session_id=session_id,
            role=role,
            content=content,
        )

    # 2. Retrieve messages
    result = await memory.get_messages(
        project="CognitiveMemory",
        session_id=session_id,
        limit=10,
    )
    print(f"Messages stored: {result['message_count']}")

    # 3. Summarize with OpenAI
    summary = await summarizer.summarize_conversation(result["messages"])
    print(f"\nSummary type: {summary['type']}")
    print(f"Title: {summary['title']}")
    print(f"Summary: {summary['summary']}")
    print(f"Topics: {summary['classification']['topics']}")
    print(f"Knowledge: {summary['knowledge']}")

    # 4. PII redaction test
    pii_text = "Contact alice@example.com or call 555-123-4567 for details"
    redacted = redactor.anonymize_summary(pii_text)
    print(f"\nPII test: {pii_text}")
    print(f"Redacted: {redacted}")

    # 5. Clean up
    await memory.clear_session("CognitiveMemory", session_id)
    print("\nSession cleared.")

asyncio.run(test_summarization())