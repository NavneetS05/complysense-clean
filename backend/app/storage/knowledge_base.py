# Use: Manages knowledge base documents used in RAG and search.

from app.config import get_settings
from app.supabase_client import supabase


class KnowledgeBaseStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def list_objects(self, prefix: str = "") -> list[str]:
        objects = supabase.storage.from_(self.settings.supabase_knowledge_bucket).list(prefix)
        return [item["name"] for item in objects]

    def signed_url(self, path: str, expires_in: int = 3600) -> str:
        response = supabase.storage.from_(self.settings.supabase_knowledge_bucket).create_signed_url(
            path, expires_in
        )
        return str(response["signedURL"])
