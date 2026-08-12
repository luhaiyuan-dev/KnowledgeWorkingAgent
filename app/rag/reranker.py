import re

from langchain_core.documents import Document

from app.core.schemas import RetrievedChunk


class HybridReranker:
    def __init__(self, vector_weight: float = 0.7, lexical_weight: float = 0.3) -> None:
        if abs(vector_weight + lexical_weight - 1.0) > 0.0001:
            raise ValueError("重排权重之和必须为 1")
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight

    def rerank(
        self,
        query: str,
        candidates: list[tuple[Document, float]],
        top_n: int,
        minimum_score: float,
    ) -> list[RetrievedChunk]:
        query_tokens = self._tokens(query)
        ranked_chunks: list[RetrievedChunk] = []

        for document, vector_score in candidates:
            document_tokens = self._tokens(document.page_content)
            lexical_score = self._overlap_score(query_tokens, document_tokens)
            final_score = self.vector_weight * vector_score + self.lexical_weight * lexical_score
            if final_score >= minimum_score:
                ranked_chunks.append(
                    RetrievedChunk(
                        content=document.page_content,
                        metadata=document.metadata,
                        vector_score=vector_score,
                        rerank_score=min(1.0, final_score),
                    )
                )

        ranked_chunks.sort(key=lambda item: item.rerank_score, reverse=True)
        return ranked_chunks[:top_n]

    def _tokens(self, text: str) -> set[str]:
        normalized_text = re.sub(r"\s+", "", text.lower())
        chinese_bigrams = {
            normalized_text[index : index + 2] for index in range(max(0, len(normalized_text) - 1))
        }
        latin_words = set(re.findall(r"[a-z0-9_-]+", text.lower()))
        return chinese_bigrams | latin_words

    def _overlap_score(self, query_tokens: set[str], document_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        return len(query_tokens & document_tokens) / len(query_tokens)
