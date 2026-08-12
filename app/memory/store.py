import threading

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class InMemoryConversationStore:
    def __init__(self, max_messages: int = 12, max_characters: int = 12000) -> None:
        self.max_messages = max_messages
        self.max_characters = max_characters
        self._sessions: dict[str, list[BaseMessage]] = {}
        self._lock = threading.RLock()

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def add_turn(self, session_id: str, user_message: str, assistant_message: str) -> None:
        with self._lock:
            messages = self._sessions.setdefault(session_id, [])
            messages.append(HumanMessage(content=user_message))
            messages.append(AIMessage(content=assistant_message))
            self._sessions[session_id] = self._prune(messages)

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def _prune(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        limited_messages = list(messages[-self.max_messages :])
        while limited_messages and self._character_count(limited_messages) > self.max_characters:
            limited_messages.pop(0)
        return limited_messages

    def _character_count(self, messages: list[BaseMessage]) -> int:
        return sum(len(str(message.content)) for message in messages)
