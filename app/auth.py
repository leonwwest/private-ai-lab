from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    provided = request.headers.get("x-api-key")
    if credentials and credentials.scheme.lower() == "bearer":
        provided = credentials.credentials

    if provided and compare_digest(provided, settings.api_key):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key",
    )
