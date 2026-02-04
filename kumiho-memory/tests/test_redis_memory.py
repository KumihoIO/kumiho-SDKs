import asyncio

from kumiho_memory.redis_memory import RedisMemoryBuffer

from fakes import FakeRedis


def test_add_get_clear_messages():
    fake = FakeRedis()
    buffer = RedisMemoryBuffer(client=fake, redis_url="redis://test")

    async def run():
        await buffer.add_message(
            project="TestProject",
            session_id="session-001",
            role="user",
            content="Hello",
        )
        await buffer.add_message(
            project="TestProject",
            session_id="session-001",
            role="assistant",
            content="Hi there",
        )
        result = await buffer.get_messages(
            project="TestProject",
            session_id="session-001",
            limit=10,
        )
        assert result["message_count"] == 2
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"

        cleared = await buffer.clear_session("TestProject", "session-001")
        assert cleared["cleared_count"] == 2

    asyncio.run(run())


def test_list_sessions_and_sequence():
    fake = FakeRedis()
    buffer = RedisMemoryBuffer(client=fake, redis_url="redis://test")

    async def run():
        await buffer.add_message(
            project="TestProject",
            session_id="session-a",
            role="user",
            content="One",
        )
        await buffer.add_message(
            project="TestProject",
            session_id="session-b",
            role="user",
            content="Two",
        )
        sessions = await buffer.list_sessions("TestProject")
        assert set(sessions["sessions"]) == {"session-a", "session-b"}

        seq1 = await buffer.next_session_sequence(
            user_canonical_id="user-1", date_str="20260203"
        )
        seq2 = await buffer.next_session_sequence(
            user_canonical_id="user-1", date_str="20260203"
        )
        assert seq1 == 1
        assert seq2 == 2

    asyncio.run(run())
