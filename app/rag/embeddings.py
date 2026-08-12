import hashlib
import math
import os
import re

from langchain_core.embeddings import Embeddings

from app.core.config import Settings


class DeterministicHashEmbeddings(Embeddings):
    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_text(text)

    def _embed_text(self, text: str) -> list[float]:
        normalized_text = re.sub(r"\s+", "", text.lower())
        tokens = self._make_tokens(normalized_text)
        vector = [0.0] * self.dimensions

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        length = math.sqrt(sum(value * value for value in vector))
        if length == 0:
            return vector
        return [value / length for value in vector]

    def _make_tokens(self, text: str) -> list[str]:
        if not text:
            return []
        characters = list(text)
        single_characters = characters
        bigrams = [text[index : index + 2] for index in range(len(text) - 1)]
        return single_characters + bigrams


def build_embeddings(settings: Settings) -> Embeddings:
    provider = settings.embedding.provider.lower()
    if provider == "hash":
        return DeterministicHashEmbeddings(settings.embedding.dimensions)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("使用 OpenAI Embedding 时必须配置 OPENAI_API_KEY")
        return OpenAIEmbeddings(model=settings.embedding.model, api_key=api_key)

    if provider == "huggingface":
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError as error:
            raise RuntimeError(
                "HuggingFace 模式需要额外安装 langchain-huggingface 和 sentence-transformers"
            ) from error
        return HuggingFaceEmbeddings(
            model_name=settings.embedding.model,
            encode_kwargs={"normalize_embeddings": True},
        )

    raise ValueError(f"未知 Embedding 提供商：{provider}")
