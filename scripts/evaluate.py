import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

QUESTIONS = [
    "星海智联的标准工单首次响应时间是多久？",
    "知识库支持哪些常见文件类型？",
    "计算 (1250 + 860) * 0.13",
]


def main() -> None:
    from app.agent.service import create_service
    from app.core.schemas import ChatRequest
    from app.evaluation.evaluator import ResponseEvaluator

    service = create_service()
    evaluator = ResponseEvaluator()
    for question in QUESTIONS:
        response = service.chat(ChatRequest(message=question, session_id="evaluation"))
        evaluation = evaluator.evaluate(response)
        print("=" * 80)
        print("问题：", question)
        print("回答：", response.answer)
        print("评估：", evaluation.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
