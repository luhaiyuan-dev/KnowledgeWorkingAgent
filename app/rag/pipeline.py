from pathlib import Path

from app.core.config import Settings
from app.core.schemas import Citation, RetrievedChunk
from app.rag.embeddings import build_embeddings
from app.rag.loader import EnterpriseDocumentLoader
from app.rag.reranker import HybridReranker
from app.rag.splitter import EnterpriseTextSplitter
from app.rag.vector_store import LocalVectorStore


class RagPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        knowledge_path = settings.project_path(settings.rag.knowledge_base_dir)
        vector_path = settings.project_path(settings.rag.vector_store_path)
        self.loader = EnterpriseDocumentLoader(knowledge_path)
        self.splitter = EnterpriseTextSplitter(
            chunk_size=settings.rag.chunk_size,
            chunk_overlap=settings.rag.chunk_overlap,
        )
        self.vector_store = LocalVectorStore(build_embeddings(settings), vector_path)
        self.reranker = HybridReranker()

    def ingest(self) -> dict[str, int]:
        source_documents = self.loader.load_directory()
        chunks = self.splitter.split_documents(source_documents)
        self.vector_store.replace_documents(chunks)
        unique_sources = {document.metadata["source_name"] for document in source_documents}
        return {
            "files": len(unique_sources),
            "documents": len(source_documents),
            "chunks": len(chunks),
        }

    def ensure_index(self) -> dict[str, int] | None:
        if self.vector_store.count() == 0:
            return self.ingest()
        return None

    def retrieve(self, query: str, allowed_scopes: set[str]) -> list[RetrievedChunk]:
        candidates = self.vector_store.similarity_search_with_score(
            query=query,
            top_k=self.settings.rag.retrieval_top_k,
            allowed_scopes=allowed_scopes,
        )
        return self.reranker.rerank(
            query=query,
            candidates=candidates,
            top_n=self.settings.rag.rerank_top_n,
            minimum_score=self.settings.rag.minimum_score,
        )

    def build_context_and_citations(
        self, chunks: list[RetrievedChunk], query: str | None = None
    ) -> tuple[str, list[Citation]]:
        context_blocks: list[str] = []
        citations: list[Citation] = []
        for index, chunk in enumerate(chunks, start=1):
            source_id = f"S{index}"
            location = self._format_location(chunk.metadata)
            context_blocks.append(
                f"[{source_id}] 文件：{chunk.metadata.get('source_name')}；位置：{location}\n"
                f"{chunk.content}"
            )
            citations.append(
                Citation(
                    source_id=source_id,
                    file_name=str(chunk.metadata.get("source_name", "未知文件")),
                    location=location,
                    excerpt=self._focused_excerpt(chunk.content, query),
                    score=round(chunk.rerank_score, 4),
                )
            )
        return "\n\n".join(context_blocks), citations

    def _focused_excerpt(self, content: str, query: str | None, window_size: int = 260) -> str:
        normalized_content = content.replace("\n", " ")
        if len(normalized_content) <= window_size or not query:
            return normalized_content[:window_size]

        compact_query = "".join(query.lower().split())
        query_bigrams = {
            compact_query[index : index + 2] for index in range(max(0, len(compact_query) - 1))
        }
        best_start = 0
        best_score = -1
        step_size = max(40, window_size // 4)
        for start in range(0, len(normalized_content), step_size):
            window = normalized_content[start : start + window_size].lower()
            score = sum(1 for bigram in query_bigrams if bigram in window)
            if score > best_score:
                best_start = start
                best_score = score
        prefix = "…" if best_start > 0 else ""
        suffix = "…" if best_start + window_size < len(normalized_content) else ""
        return prefix + normalized_content[best_start : best_start + window_size] + suffix

    def load_named_file(self, file_name: str):
        return self.loader.load_file(Path(file_name))

    def _format_location(self, metadata: dict[str, object]) -> str:
        if "page" in metadata:
            return f"第 {metadata['page']} 页"
        if "sheet" in metadata:
            return f"工作表 {metadata['sheet']}"
        return f"分块 {metadata.get('chunk_index', 0)}"
