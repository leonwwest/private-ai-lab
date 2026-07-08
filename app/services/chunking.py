import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str
    token_count: int


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(
    text: str,
    max_tokens: int = 260,
    overlap_tokens: int = 40,
) -> list[TextChunk]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens must not be negative")
    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be smaller than max_tokens")

    words = normalize_text(text).split()
    if not words:
        return []

    chunks: list[TextChunk] = []
    step = max_tokens - overlap_tokens
    start = 0

    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunk_words = words[start:end]
        chunks.append(
            TextChunk(
                index=len(chunks),
                content=" ".join(chunk_words),
                token_count=len(chunk_words),
            )
        )
        if end == len(words):
            break
        start += step

    return chunks
