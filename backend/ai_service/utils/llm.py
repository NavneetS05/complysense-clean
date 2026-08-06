# Use: Wrapper around Gemini LLM via langchain-google-genai with graceful fallbacks.

from typing import Any, Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class LLMService:
    """
    Lightweight wrapper that caches ChatGoogleGenerativeAI clients per-model and
    implements a simple fallback strategy when the configured model is unavailable
    to the account (common when moving between Google Cloud tiers or when new
    models are introduced).
    """

    # Ordered fallback models to try if the requested one fails
    _FALLBACK_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
    ]

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self._clients: dict[str, Any] = {}

    def get_client(self, model: str) -> ChatGoogleGenerativeAI:
        """Return a cached ChatGoogleGenerativeAI client for the requested model."""
        if model not in self._clients:
            self._clients[model] = ChatGoogleGenerativeAI(model=model, google_api_key=self.api_key)
        return self._clients[model]

    async def call(self, messages: List[Dict[str, str]], model: str = "gemini-2.5-flash") -> str:
        """
        Send messages to Gemini. If the chosen model fails due to availability
        (404 / model-not-found), attempt the configured fallback models in order.

        Returns the assistant text on success or raises the original exception if all
        fallbacks fail.
        """
        # Build langchain messages
        lc_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role in ("assistant", "model"):
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        # Prepare list of models to try (requested first, then fallbacks without duplicates)
        to_try = [model] + [m for m in self._FALLBACK_MODELS if m != model]

        last_exc: Exception | None = None
        for candidate in to_try:
            try:
                client = self.get_client(candidate)
                response = await client.ainvoke(lc_messages)
                return str(response.content)
            except Exception as exc:
                # Keep the last exception and try the next candidate
                last_exc = exc
                # If it's a clear 'model not found / unavailable' error, continue to fallback
                # Otherwise, continue as well but eventually re-raise so caller can handle it.
                # Logically we treat all exceptions here as retryable for the next candidate.
                continue

        # All attempts failed — raise the last exception so higher-level code can handle it
        if last_exc:
            raise last_exc
        # Defensive fallback (should not happen)
        raise RuntimeError("LLM call failed with no exception captured")

