from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class EnterpriseAction(BaseModel):
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)
    confirmation_token: str | None = None


class EnterpriseToolAdapter(ABC):
    name: str
    risk_level: str = "high"

    def run(self, action: EnterpriseAction, confirmed_actions: list[str]) -> dict[str, Any]:
        if self.risk_level == "high" and action.operation not in confirmed_actions:
            return {
                "status": "confirmation_required",
                "tool": self.name,
                "operation": action.operation,
                "message": "该操作会修改外部业务系统，必须由用户明确确认后执行。",
            }
        return self.execute(action)

    @abstractmethod
    def execute(self, action: EnterpriseAction) -> dict[str, Any]:
        raise NotImplementedError


class CrmAdapter(EnterpriseToolAdapter):
    name = "crm"

    def execute(self, action: EnterpriseAction) -> dict[str, Any]:
        raise NotImplementedError("请在这里接入企业 CRM SDK 或内部 API")


class ErpAdapter(EnterpriseToolAdapter):
    name = "erp"

    def execute(self, action: EnterpriseAction) -> dict[str, Any]:
        raise NotImplementedError("请在这里接入企业 ERP SDK 或内部 API")


class EmailAdapter(EnterpriseToolAdapter):
    name = "email"

    def execute(self, action: EnterpriseAction) -> dict[str, Any]:
        raise NotImplementedError("请在这里接入企业邮件服务")


class CalendarAdapter(EnterpriseToolAdapter):
    name = "calendar"

    def execute(self, action: EnterpriseAction) -> dict[str, Any]:
        raise NotImplementedError("请在这里接入企业日历服务")
