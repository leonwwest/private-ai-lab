from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class ReadyResponse(BaseModel):
    status: str
    database: str


class DocumentRead(BaseModel):
    id: str
    filename: str
    content_sha256: str
    byte_size: int
    created_at: datetime
    chunk_count: int


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    already_exists: bool = False


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    score: float
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    model: str
    sources: list[Source]
    duration_ms: int
