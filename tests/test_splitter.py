from langchain_core.documents import Document

from app.rag.splitter import EnterpriseTextSplitter


def test_chinese_splitter_keeps_chunk_size_bounded() -> None:
    content = "第一段介绍企业制度。\n\n" + "报销申请必须经过审批。" * 100
    splitter = EnterpriseTextSplitter(chunk_size=120, chunk_overlap=20)
    chunks = splitter.split_documents([Document(page_content=content, metadata={})])
    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 120 for chunk in chunks)
    assert all("chunk_index" in chunk.metadata for chunk in chunks)
