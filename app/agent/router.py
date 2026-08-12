import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.schemas import ChatRequest, RouteDecision
from app.prompts.manager import PromptManager


class TaskRouter:
    def __init__(self, model: BaseChatModel | None, prompts: PromptManager) -> None:
        self.model = model
        self.prompts = prompts

    def route(self, request: ChatRequest) -> RouteDecision:
        if request.mode != "auto":
            route_name = "tools" if request.mode == "tools" else request.mode
            return RouteDecision(route=route_name, reason=f"用户手动选择 {request.mode} 模式")

        if self.model is not None:
            try:
                structured_model = self.model.with_structured_output(RouteDecision)
                decision = structured_model.invoke(
                    [
                        SystemMessage(content=self.prompts.get("router_system")),
                        HumanMessage(content=request.message),
                    ]
                )
                return RouteDecision.model_validate(decision)
            except Exception:
                pass

        return self._heuristic_route(request.message)

    def _heuristic_route(self, message: str) -> RouteDecision:
        normalized = message.lower()
        selected_tools: list[str] = []

        if self._looks_like_calculation(normalized):
            selected_tools.append("calculator")
        if any(word in normalized for word in ["联网", "网页", "最新", "web", "互联网搜索"]):
            selected_tools.append("web_search")
        if any(
            word in normalized for word in ["excel", "销售数据", "数据表", "工作表", "查询数据"]
        ):
            selected_tools.append("data_query")
        if any(word in normalized for word in ["读取文件", "打开文件", "文件内容"]):
            selected_tools.append("file_reader")
        if any(word in normalized for word in ["分析文档", "分析报告", "文档摘要"]):
            selected_tools.append("document_analysis")

        knowledge_keywords = [
            "公司",
            "制度",
            "政策",
            "报销",
            "产品",
            "服务",
            "员工",
            "知识库",
            "手册",
            "faq",
            "根据文档",
            "标准工单",
            "响应时间",
        ]
        needs_knowledge = any(keyword in normalized for keyword in knowledge_keywords)

        if selected_tools and needs_knowledge:
            return RouteDecision(
                route="combo",
                tools=selected_tools,
                reason="问题同时包含企业知识与工具执行意图",
            )
        if selected_tools:
            return RouteDecision(route="tools", tools=selected_tools, reason="识别到明确工具任务")
        if needs_knowledge:
            return RouteDecision(route="knowledge", reason="问题需要企业知识库证据")
        return RouteDecision(route="chat", reason="未发现知识库或工具依赖，按普通对话处理")

    def _looks_like_calculation(self, message: str) -> bool:
        has_math_word = any(word in message for word in ["计算", "等于多少", "算一下"])
        has_expression = bool(re.search(r"\d\s*[+\-*/%]\s*\d", message))
        return has_math_word or has_expression
