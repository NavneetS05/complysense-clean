# Use: Manages knowledge base documents used in RAG and search.

from fastapi import HTTPException
from app.config import get_settings
from app.supabase_client import get_supabase_client


class KnowledgeBaseStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_client(self):
        client = get_supabase_client()
        if client is None:
            raise HTTPException(status_code=503, detail="Supabase storage service is currently unavailable")
        return client

    def list_objects(self, prefix: str = "") -> list[str]:
        client = self._get_client()
        objects = client.storage.from_(self.settings.supabase_knowledge_bucket).list(prefix)
        return [item["name"] for item in objects]

    def signed_url(self, path: str, expires_in: int = 3600) -> str:
        client = self._get_client()
        response = client.storage.from_(self.settings.supabase_knowledge_bucket).create_signed_url(
            path, expires_in
        )
        return str(response["signedURL"])
