from app.memory.store import InMemoryConversationStore


def test_memory_prunes_old_messages() -> None:
    memory = InMemoryConversationStore(max_messages=4, max_characters=1000)
    for index in range(4):
        memory.add_turn("session", f"question-{index}", f"answer-{index}")
    messages = memory.get_messages("session")
    assert len(messages) == 4
    assert "question-2" in str(messages[0].content)
