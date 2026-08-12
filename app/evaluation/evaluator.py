from pydantic import BaseModel

from app.core.schemas import AgentResponse


class EvaluationResult(BaseModel):
    citation_coverage: float
    has_answer: bool
    grounded_format_ok: bool
    notes: list[str]


class ResponseEvaluator:
    def evaluate(self, response: AgentResponse) -> EvaluationResult:
        notes: list[str] = []
        has_answer = bool(response.answer.strip())
        grounded_format_ok = True
        citation_coverage = 1.0

        if response.route in {"knowledge", "combo"}:
            if not response.citations:
                grounded_format_ok = "证据不足" in response.answer
                citation_coverage = 0.0
                notes.append("知识库回答没有返回引用")
            else:
                used_count = sum(
                    1
                    for citation in response.citations
                    if f"[{citation.source_id}]" in response.answer
                )
                citation_coverage = used_count / len(response.citations)
                grounded_format_ok = used_count > 0

        if not has_answer:
            notes.append("回答为空")
        return EvaluationResult(
            citation_coverage=round(citation_coverage, 4),
            has_answer=has_answer,
            grounded_format_ok=grounded_format_ok,
            notes=notes,
        )
