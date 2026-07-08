from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.config import Settings, get_settings
from app.db import get_session
from app.dependencies import get_embedding_provider
from app.schemas import DocumentRead, IngestResponse
from app.services.embeddings import EmbeddingProvider
from app.services.pdf_loader import extract_pdf_text
from app.services.rag import ingest_text_document, list_documents

router = APIRouter(
    prefix="/v1/documents",
    tags=["documents"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[DocumentRead])
def documents(session: Annotated[Session, Depends(get_session)]) -> list[DocumentRead]:
    return [
        DocumentRead(
            id=document.id,
            filename=document.filename,
            content_sha256=document.content_sha256,
            byte_size=document.byte_size,
            created_at=document.created_at,
            chunk_count=chunk_count,
        )
        for document, chunk_count in list_documents(session)
    ]


@router.post("/upload", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
) -> IngestResponse:
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    raw_pdf = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(raw_pdf) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds max upload size of {settings.max_upload_mb} MB",
        )

    try:
        text = extract_pdf_text(raw_pdf)
        document, chunk_count, already_exists = await ingest_text_document(
            session=session,
            filename=filename,
            raw_bytes=raw_pdf,
            text=text,
            settings=settings,
            embeddings=embeddings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IngestResponse(
        document_id=document.id,
        filename=document.filename,
        chunk_count=chunk_count,
        already_exists=already_exists,
    )
