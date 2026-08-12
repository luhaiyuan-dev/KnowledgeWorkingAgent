from app.core.config import load_settings
from app.rag.pipeline import RagPipeline


def test_rag_pipeline_ingests_and_cites_sources(tmp_path) -> None:
    settings = load_settings().model_copy(deep=True)
    settings.rag.vector_store_path = str(tmp_path / "index.json")
    rag = RagPipeline(settings)
    statistics = rag.ingest()
    chunks = rag.retrieve("标准工单首次响应时间", {"internal"})
    context, citations = rag.build_context_and_citations(chunks, query="标准工单首次响应时间")
    assert statistics["files"] == 5
    assert chunks
    assert citations
    assert "[S1]" in context
    assert any(
        "FAQ" in citation.file_name or "公司简介" in citation.file_name for citation in citations
    )
    assert any("4 个工作小时" in citation.excerpt for citation in citations)
