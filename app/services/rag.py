from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Chunk, Document
from app.schemas import Source
from app.services.chunking import chunk_text
from app.services.embeddings import EmbeddingProvider
from app.services.llm import LLMClient


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    filename: str
    chunk_index: int
    content: str
    score: float


async def ingest_text_document(
    session: Session,
    filename: str,
    raw_bytes: bytes,
    text: str,
    settings: Settings,
    embeddings: EmbeddingProvider,
) -> tuple[Document, int, bool]:
    content_hash = sha256(raw_bytes).hexdigest()
    existing = session.scalar(
        select(Document).where(Document.content_sha256 == content_hash)
    )
    if existing:
        chunk_count = session.scalar(
            select(func.count(Chunk.id)).where(Chunk.document_id == existing.id)
        )
        return existing, int(chunk_count or 0), True

    text_chunks = chunk_text(
        text,
        max_tokens=settings.max_chunk_tokens,
        overlap_tokens=settings.chunk_overlap_tokens,
    )
    if not text_chunks:
        raise ValueError("Document contains no usable text chunks")

    vectors = await embeddings.embed([chunk.content for chunk in text_chunks])
    document = Document(
        filename=filename,
        content_sha256=content_hash,
        byte_size=len(raw_bytes),
    )
    session.add(document)
    session.flush()

    for text_chunk, vector in zip(text_chunks, vectors, strict=True):
        session.add(
            Chunk(
                document_id=document.id,
                chunk_index=text_chunk.index,
                content=text_chunk.content,
                token_count=text_chunk.token_count,
                embedding=vector,
            )
        )

    session.commit()
    session.refresh(document)
    return document, len(text_chunks), False


def list_documents(session: Session) -> list[tuple[Document, int]]:
    statement = (
        select(Document, func.count(Chunk.id).label("chunk_count"))
        .outerjoin(Chunk)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    return [
        (document, int(chunk_count))
        for document, chunk_count in session.execute(statement)
    ]


def retrieve_chunks(
    session: Session,
    query_vector: list[float],
    top_k: int,
) -> list[RetrievedChunk]:
    distance = Chunk.embedding.cosine_distance(query_vector)
    statement = (
        select(Chunk, Document, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .order_by(distance)
        .limit(top_k)
    )

    results: list[RetrievedChunk] = []
    for chunk, document, raw_distance in session.execute(statement):
        distance_value = float(raw_distance)
        results.append(
            RetrievedChunk(
                document_id=document.id,
                filename=document.filename,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=max(0.0, 1.0 - distance_value),
            )
        )
    return results


async def answer_question(
    session: Session,
    question: str,
    top_k: int,
    embeddings: EmbeddingProvider,
    llm: LLMClient,
) -> tuple[str, list[Source]]:
    query_vector = (await embeddings.embed([question]))[0]
    retrieved = retrieve_chunks(session, query_vector=query_vector, top_k=top_k)
    context_blocks = [
        f"[{index}] {chunk.filename} / Abschnitt {chunk.chunk_index}\n{chunk.content}"
        for index, chunk in enumerate(retrieved, start=1)
    ]
    answer = await llm.answer(question=question, context_blocks=context_blocks)
    sources = [
        Source(
            document_id=chunk.document_id,
            filename=chunk.filename,
            chunk_index=chunk.chunk_index,
            score=round(chunk.score, 4),
            excerpt=chunk.content[:360],
        )
        for chunk in retrieved
    ]
    return answer, sources
