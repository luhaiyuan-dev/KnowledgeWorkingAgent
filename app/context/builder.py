from langchain_core.messages import BaseMessage

from app.core.schemas import UserContext


class ContextBuilder:
    def __init__(self, max_characters: int = 16000) -> None:
        self.max_characters = max_characters

    def format_history(self, messages: list[BaseMessage]) -> str:
        lines: list[str] = []
        for message in messages:
            role_name = "用户" if message.type == "human" else "助手"
            lines.append(f"{role_name}：{message.content}")
        history = "\n".join(lines)
        return history[-self.max_characters :]

    def build_system_context(self, user: UserContext) -> str:
        role_text = "、".join(user.roles)
        department_text = user.department or "未设置"
        return (
            f"当前用户：{user.display_name}（{user.user_id}）\n"
            f"角色：{role_text}\n"
            f"部门：{department_text}"
        )
