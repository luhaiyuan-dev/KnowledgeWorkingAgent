from langchain_core.tools import BaseTool

from app.auth.policy import PolicyEngine
from app.core.schemas import UserContext


class ToolRegistry:
    def __init__(self, tools: list[BaseTool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def names(self) -> list[str]:
        return sorted(self._tools)

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"工具未注册：{name}")
        return self._tools[name]

    def allowed_for_user(self, user: UserContext, policy: PolicyEngine) -> list[BaseTool]:
        return [tool for tool in self._tools.values() if policy.can_use_tool(user, tool.name)]
