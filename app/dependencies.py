from functools import lru_cache

from app.config import get_settings
from app.services.embeddings import EmbeddingProvider, build_embedding_provider
from app.services.llm import LLMClient


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    return build_embedding_provider(get_settings())


@lru_cache
def get_llm_client() -> LLMClient:
    return LLMClient(get_settings())
