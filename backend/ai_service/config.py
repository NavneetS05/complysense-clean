# Use: Centralized AI configuration (LLM, embeddings, FAISS, BM25, Supabase, token budgets, thresholds).

from functools import lru_cache
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini API Key (free tier available at aistudio.google.com)
    gemini_api_key: str | None = None

    # Optional admin key to secure the /admin/reindex endpoint
    admin_reindex_key: str | None = None

    # Service URLs
    main_api_url: AnyHttpUrl = "http://localhost:8000"

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
    log_level: str = "INFO"
    environment: str = "development"

    # Token Budgets
    max_input_tokens: int = 3200
    max_output_tokens: int = 1500

    # Retrieval Thresholds
    similarity_threshold: float = 0.35

    # Vectorstore persistence path (relative to backend/ working dir)
    vectorstore_path: str = "ai_service/rag/vectorstore/"

    # Embeddings model (local, free via sentence-transformers)
    embeddings_model: str = "BAAI/bge-m3"

    # LLM model
    llm_model: str = "gemini-2.5-flash"


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()