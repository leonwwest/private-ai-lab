from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.environment,
    )


@router.get("/readyz", response_model=ReadyResponse)
def ready(session: Annotated[Session, Depends(get_session)]) -> ReadyResponse:
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc
    return ReadyResponse(status="ok", database="ok")
