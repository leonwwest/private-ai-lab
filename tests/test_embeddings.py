import asyncio
from math import isclose, sqrt

from app.services.embeddings import HashEmbeddingProvider


def test_hash_embeddings_are_deterministic_and_normalized() -> None:
    provider = HashEmbeddingProvider(dimensions=32)

    first = asyncio.run(provider.embed(["Private AI Platform"]))
    second = asyncio.run(provider.embed(["Private AI Platform"]))

    assert first == second
    norm = sqrt(sum(value * value for value in first[0]))
    assert isclose(norm, 1.0)


def test_empty_text_returns_zero_vector() -> None:
    provider = HashEmbeddingProvider(dimensions=8)

    vector = asyncio.run(provider.embed(["   "]))[0]

    assert vector == [0.0] * 8
