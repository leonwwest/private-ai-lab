import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.config import Settings, get_settings
from app.db import get_session
from app.dependencies import get_embedding_provider, get_llm_client
from app.schemas import ChatRequest, ChatResponse
from app.services.embeddings import EmbeddingProvider
from app.services.llm import LLMClient
from app.services.rag import answer_question

router = APIRouter(
    prefix="/v1/chat",
    tags=["chat"],
    dependencies=[Depends(require_api_key)],
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    llm: Annotated[LLMClient, Depends(get_llm_client)],
) -> ChatResponse:
    started = time.perf_counter()
    try:
        answer, sources = await answer_question(
            session=session,
            question=request.question,
            top_k=request.top_k or settings.rag_top_k,
            embeddings=embeddings,
            llm=llm,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        answer=answer,
        model=settings.llm_model,
        sources=sources,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
