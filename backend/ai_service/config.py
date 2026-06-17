# Use: AI service configuration and settings management.

from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None
    main_api_url: AnyUrl = "http://localhost:8000"
    log_level: str = "INFO"


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()
