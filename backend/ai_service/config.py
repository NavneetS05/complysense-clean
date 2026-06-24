from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = None
    main_api_url: AnyHttpUrl = "http://localhost:8000"
    mongodb_uri: str | None = None
    mongodb_db: str = "complysense"
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    log_level: str = "INFO"


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()