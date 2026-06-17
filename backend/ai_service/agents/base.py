# Use: Sets up the base LangChain configurations, models, and shared chain setups.

from ai_service.config import get_ai_settings
from app.core.exceptions import AppError


class BaseAgent:
    def __init__(self) -> None:
        self.settings = get_ai_settings()

    def ensure_configured(self) -> None:
        if not self.settings.openai_api_key:
            raise AppError(503, "AI_NOT_CONFIGURED", "OPENAI_API_KEY is not configured")
