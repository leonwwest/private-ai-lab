from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_api_key
from app.config import get_settings
from app.main import create_app


def build_client() -> TestClient:
    get_settings.cache_clear()
    return TestClient(create_app())


def test_healthz_is_public() -> None:
    client = build_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def build_auth_client() -> TestClient:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_api_key)])
    def protected() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_protected_endpoint_requires_api_key() -> None:
    client = build_auth_client()

    response = client.get("/protected")

    assert response.status_code == 401


def test_protected_endpoint_accepts_bearer_api_key() -> None:
    client = build_auth_client()

    response = client.get("/protected", headers={"Authorization": "Bearer test-key"})

    assert response.status_code == 200
