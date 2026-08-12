import json
import threading
from pathlib import Path

import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class LocalVectorStore:
    def __init__(self, embeddings: Embeddings, persist_path: str | Path) -> None:
        self.embeddings = embeddings
        self.persist_path = Path(persist_path)
        self.documents: list[Document] = []
        self.vectors = np.empty((0, 0), dtype=np.float32)
        self._lock = threading.RLock()
        if self.persist_path.exists():
            self.load()

    def replace_documents(self, documents: list[Document]) -> None:
        texts = [document.page_content for document in documents]
        vectors = self.embeddings.embed_documents(texts)
        vector_array = np.asarray(vectors, dtype=np.float32)
        vector_array = self._normalize_rows(vector_array)
        with self._lock:
            self.documents = documents
            self.vectors = vector_array
            self.persist()

    def similarity_search_with_score(
        self,
        query: str,
        top_k: int,
        allowed_scopes: set[str] | None = None,
    ) -> list[tuple[Document, float]]:
        with self._lock:
            if not self.documents or self.vectors.size == 0:
                return []
            query_vector = np.asarray(self.embeddings.embed_query(query), dtype=np.float32)
            query_length = float(np.linalg.norm(query_vector))
            if query_length == 0:
                return []
            query_vector = query_vector / query_length
            scores = self.vectors @ query_vector

            candidates: list[tuple[Document, float]] = []
            for index, score in enumerate(scores.tolist()):
                document = self.documents[index]
                document_scope = str(document.metadata.get("access_scope", "internal"))
                if (
                    allowed_scopes
                    and "*" not in allowed_scopes
                    and document_scope not in allowed_scopes
                ):
                    continue
                normalized_score = max(0.0, min(1.0, (float(score) + 1.0) / 2.0))
                candidates.append((document, normalized_score))

            candidates.sort(key=lambda item: item[1], reverse=True)
            return candidates[:top_k]

    def persist(self) -> None:
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "documents": [
                {"page_content": document.page_content, "metadata": document.metadata}
                for document in self.documents
            ],
            "vectors": self.vectors.tolist(),
        }
        temporary_path = self.persist_path.with_suffix(self.persist_path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        temporary_path.replace(self.persist_path)

    def load(self) -> None:
        payload = json.loads(self.persist_path.read_text(encoding="utf-8"))
        self.documents = [Document(**item) for item in payload.get("documents", [])]
        self.vectors = np.asarray(payload.get("vectors", []), dtype=np.float32)
        if self.vectors.size and self.vectors.ndim == 1:
            self.vectors = self.vectors.reshape(1, -1)

    def count(self) -> int:
        return len(self.documents)

    def _normalize_rows(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.size == 0:
            return vectors
        lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
        lengths[lengths == 0] = 1.0
        return vectors / lengths
