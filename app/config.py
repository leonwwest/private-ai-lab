from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Private AI Lab"
    environment: str = "local"
    api_key: str = Field(default="dev-private-ai-lab-key")

    database_url: str = (
        "postgresql+psycopg://private_ai:private_ai@postgres:5432/private_ai"
    )
    init_db_on_startup: bool = True

    upload_dir: str = "/data/uploads"
    max_upload_mb: int = 15
    max_chunk_tokens: int = 260
    chunk_overlap_tokens: int = 40
    rag_top_k: int = 4

    embedding_provider: Literal["hash", "openai"] = "hash"
    embedding_dimensions: int = 384
    embedding_base_url: str = "http://ollama:11434/v1"
    embedding_api_key: str = "ollama"
    embedding_model: str = "text-embedding-3-small"
    embedding_timeout_seconds: int = 60

    llm_base_url: str = "http://ollama:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.2:3b"
    llm_timeout_seconds: int = 90

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
