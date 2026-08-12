from app.agent.router import TaskRouter
from app.core.schemas import ChatRequest
from app.prompts.manager import PromptManager


def test_router_detects_knowledge_question() -> None:
    router = TaskRouter(model=None, prompts=PromptManager())
    decision = router.route(ChatRequest(message="星海智联的标准工单首次响应时间是多久？"))
    assert decision.route == "knowledge"


def test_router_detects_calculator() -> None:
    router = TaskRouter(model=None, prompts=PromptManager())
    decision = router.route(ChatRequest(message="请计算 (20 + 5) * 3"))
    assert decision.route == "tools"
    assert "calculator" in decision.tools
