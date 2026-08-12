from app.agent.service import EnterpriseAgentService
from app.core.config import load_settings
from app.core.schemas import ChatRequest


def build_demo_service(tmp_path) -> EnterpriseAgentService:
    settings = load_settings().model_copy(deep=True)
    settings.app.demo_mode = True
    settings.rag.vector_store_path = str(tmp_path / "service-index.json")
    return EnterpriseAgentService(settings)


def test_demo_service_returns_rag_citations(tmp_path) -> None:
    service = build_demo_service(tmp_path)
    response = service.chat(ChatRequest(message="公司标准工单首次响应时间是多久？"))
    assert response.route == "knowledge"
    assert response.citations
    assert "[S1]" in response.answer
    assert "4 个工作小时" in response.answer
    assert len(response.answer) < 800


def test_demo_service_executes_calculator(tmp_path) -> None:
    service = build_demo_service(tmp_path)
    response = service.chat(ChatRequest(message="请计算 (1250 + 860) * 0.13"))
    assert response.route == "tools"
    assert "calculator" in response.used_tools
    assert "274.3" in response.answer


def test_demo_service_extracts_factual_sentence_instead_of_question_heading(tmp_path) -> None:
    service = build_demo_service(tmp_path)
    response = service.chat(ChatRequest(message="知识库支持哪些常见文件类型？"))
    assert "支持 PDF、Word、Excel" in response.answer
    assert "## Q2" not in response.answer
