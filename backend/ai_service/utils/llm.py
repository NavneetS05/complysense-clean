# Use: Wrapper around Gemini 2.5 Flash LLM via langchain-google-genai.

from typing import Any, Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self._clients: dict[str, Any] = {}

    def get_client(self, model: str = "gemini-2.5-flash") -> ChatGoogleGenerativeAI:
        """
        Returns a cached ChatGoogleGenerativeAI client for the given model.
        Use "gemini-2.5-flash" for most tasks.
        Use "gemini-2.5-pro" for complex multi-step reasoning if needed in future.
        """
        if model not in self._clients:
            self._clients[model] = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.api_key,
            )
        return self._clients[model]

    async def call(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-2.5-flash",
    ) -> str:
        """
        Sends a list of role/content messages to Gemini and returns the response text.

        Message format:  [{"role": "system"|"user"|"assistant", "content": "..."}]

        Model routing:
          - "gemini-2.5-flash"  → default for Q&A, translation, digest, triage
          - "gemini-2.5-pro"    → reserved for future heavy reasoning if needed
        """
        client = self.get_client(model)
        # Placeholder: convert messages → LangChain format and invoke
        return ""
