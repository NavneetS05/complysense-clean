# Use: App configuration module using Pydantic settings. Reads environment variables from the .env file.

from functools import lru_cache

from pydantic import AnyUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_version: str = "v1"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: PostgresDsn

    mongodb_uri: str
    mongodb_database: str = "complysense"
    mongodb_documents_collection: str = "documents"
    mongodb_control_library_collection: str = "control_library"

    supabase_url: AnyUrl
    supabase_service_key: str
    supabase_knowledge_bucket: str = "knowledge-base"

    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    refresh_cookie_name: str = "complysense_refresh"
    refresh_cookie_secure: bool = True
    refresh_cookie_samesite: str = "lax"
    jwt_algorithm: str = "HS256"

    # SMTP — Gmail address and App Password only.
    # Leave blank to disable email delivery (forgot-password falls back to inline redirect).
    smtp_user: str | None = None
    smtp_password: str | None = None

    main_api_url: str = "http://localhost:8000"
    ai_service_url: str = "http://localhost:8001"
    openai_api_key: str | None = None

    frontend_url: str = "http://localhost:5173"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
