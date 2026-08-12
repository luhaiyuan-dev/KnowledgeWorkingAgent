from pathlib import Path

import yaml

from app.core.config import PROJECT_ROOT
from app.core.schemas import UserContext


class PolicyEngine:
    def __init__(self, policy_path: str | Path | None = None) -> None:
        selected_path = (
            Path(policy_path) if policy_path else PROJECT_ROOT / "configs/permissions.yaml"
        )
        with selected_path.open("r", encoding="utf-8") as policy_file:
            self._policy = yaml.safe_load(policy_file)

    def allowed_tools(self, user: UserContext) -> set[str]:
        allowed: set[str] = set()
        for role in user.roles:
            role_policy = self._policy["roles"].get(role, {})
            allowed.update(role_policy.get("tools", []))
        return allowed

    def allowed_document_scopes(self, user: UserContext) -> set[str]:
        allowed: set[str] = set()
        for role in user.roles:
            role_policy = self._policy["roles"].get(role, {})
            allowed.update(role_policy.get("document_scopes", []))
        return allowed

    def can_use_tool(self, user: UserContext, tool_name: str) -> bool:
        allowed = self.allowed_tools(user)
        return "*" in allowed or tool_name in allowed

    def is_high_risk_tool(self, tool_name: str) -> bool:
        return tool_name in set(self._policy.get("high_risk_tools", []))
