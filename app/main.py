import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, make_asgi_app

from app.config import Settings, get_settings
from app.db import init_db
from app.logging_config import configure_logging, get_logger
from app.routers import chat, documents, health

REQUEST_COUNT = Counter(
    "private_ai_lab_http_requests_total",
    "HTTP requests by method, path and status.",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "private_ai_lab_http_request_duration_seconds",
    "HTTP request latency by method and path.",
    ["method", "path"],
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.init_db_on_startup:
            init_db()
            logger.info("database.initialized")
        yield

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Local/private AI platform with RAG, auth and observability.",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def observe_requests(request: Request, call_next):
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - started
            path = request.url.path
            if not path.startswith("/metrics"):
                REQUEST_COUNT.labels(
                    method=request.method,
                    path=path,
                    status=str(status_code),
                ).inc()
                REQUEST_LATENCY.labels(
                    method=request.method,
                    path=path,
                ).observe(duration)
                logger.info(
                    "request.complete",
                    method=request.method,
                    path=path,
                    status=status_code,
                    duration_ms=round(duration * 1000, 2),
                )

    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.mount("/metrics", make_asgi_app())
    return app


app = create_app()
