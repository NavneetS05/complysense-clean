# Use: Centralized AI configuration (LLM, embeddings, FAISS, BM25, Supabase, token budgets, thresholds).

from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


AI_SERVICE_ROOT = Path(__file__).resolve().parent


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini API Key & Model (free tier available at aistudio.google.com)
    gemini_api_key: str | None = None
    llm_model: str = "gemini-2.5-flash-lite"

    # Optional admin key to secure the /admin/reindex endpoint
    admin_reindex_key: str | None = None

    # Service URLs
    main_api_url: AnyHttpUrl = "http://127.0.0.1:8000"

    # PostgreSQL (same shared DB as main app — AI service only writes audit logs)
    # Env variable: DATABASE_URL
    database_url: str | None = None

    # MongoDB Atlas — documents collection for user-uploaded evidence indexing
    mongodb_uri: str | None = None
    mongodb_database: str = "complysense"
    mongodb_documents_collection: str = "documents"

    # Supabase — knowledge base bucket for RAG markdown files
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    supabase_knowledge_bucket: str = "knowledge-base"

    # Logging & Env
    log_level: str = "DEBUG"
    environment: str = "development"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    # Token Budgets
    max_input_tokens: int = 3200
    max_output_tokens: int = 1500

    # Retrieval Thresholds
    similarity_threshold: float = 0.35

    # Vectorstore persistence path (resolved relative to the AI service root)
    vectorstore_path: str = str((AI_SERVICE_ROOT / "vectorstore").resolve())

    # Embeddings model (local, free via sentence-transformers)
    embeddings_model: str = "BAAI/bge-m3"

    # LLM model
    # Use a models/* name compatible with Google's Generative Language API. Default to a modern Gemini flash model.
    llm_model: str = "gemini-1.5-flash"

    @field_validator("vectorstore_path", mode="before")
    @classmethod
    def resolve_vectorstore_path(cls, value: str | None) -> str:
        if value in (None, ""):
            return str((AI_SERVICE_ROOT / "vectorstore").resolve())

        path = Path(value).expanduser()
        if path.is_absolute():
            return str(path.resolve())
        return str((AI_SERVICE_ROOT / path).resolve())


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()
