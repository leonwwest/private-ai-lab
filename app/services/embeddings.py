from __future__ import annotations

import re
from hashlib import sha256
from math import sqrt
from typing import Protocol

import httpx

from app.config import Settings

TOKEN_RE = re.compile(r"[\w.-]+", re.UNICODE)


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class HashEmbeddingProvider:
    """Small deterministic embedding provider for offline demos and tests."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (len(token) % 5) / 5.0
            vector[index] += sign * weight

        norm = sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class OpenAICompatibleEmbeddingProvider:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        dimensions: int,
        timeout_seconds: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.timeout_seconds = timeout_seconds

    async def embed(self, texts: list[str]) -> list[list[float]]:
        payload: dict[str, object] = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        data = response.json()["data"]
        vectors = [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]
        for vector in vectors:
            if len(vector) != self.dimensions:
                raise RuntimeError(
                    "Embedding dimension mismatch: "
                    f"expected {self.dimensions}, got {len(vector)}"
                )
        return vectors


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        return OpenAICompatibleEmbeddingProvider(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
    return HashEmbeddingProvider(dimensions=settings.embedding_dimensions)
