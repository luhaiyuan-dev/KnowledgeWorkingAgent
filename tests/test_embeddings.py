import numpy as np

from app.rag.embeddings import DeterministicHashEmbeddings


def test_hash_embeddings_are_deterministic_and_normalized() -> None:
    embeddings = DeterministicHashEmbeddings(dimensions=64)
    first = embeddings.embed_query("企业知识库")
    second = embeddings.embed_query("企业知识库")
    assert first == second
    assert len(first) == 64
    assert np.isclose(np.linalg.norm(first), 1.0)
