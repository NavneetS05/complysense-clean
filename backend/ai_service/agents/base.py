from __future__ import annotations

from typing import Any

from ai_service.config import get_ai_settings
from ai_service.prompts import assemble_prompt
from ai_service.security import sanitize_input, validate_response
from app.core.exceptions import AppError


class BaseAgent:
    def __init__(self, *, role: str, task: str) -> None:
        self.settings = get_ai_settings()
        self.role = role
        self.task = task

    def ensure_configured(self) -> None:
        if not self.settings.openai_api_key:
            raise AppError(503, "AI_NOT_CONFIGURED", "OPENAI_API_KEY is not configured")

    async def run(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        self.ensure_configured()
        sanitized_input = sanitize_input(user_input)
        prompt = assemble_prompt(role=self.role, task=self.task, user_input=sanitized_input, context=context)
        response = await self.call_model(prompt)
        return validate_response(response, context)

    async def call_model(self, prompt: str) -> str:
        raise NotImplementedError("call_model must be implemented by subclasses")
