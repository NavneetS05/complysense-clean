# Use: Initializes and configures the Supabase Storage client integration with fault tolerance.

from typing import Any
from supabase import Client, create_client
from app.config import get_settings
from app.core.logging import logger

_supabase_client: Client | None = None
_supabase_init_attempted: bool = False


def get_supabase_client() -> Client | None:
    global _supabase_client, _supabase_init_attempted
    if _supabase_client is None and not _supabase_init_attempted:
        _supabase_init_attempted = True
        try:
            settings = get_settings()
            _supabase_client = create_client(str(settings.supabase_url), settings.supabase_service_key)
        except Exception as exc:
            logger.error("supabase.init_failed", error=str(exc))
            _supabase_client = None
    return _supabase_client


def check_supabase_sync() -> dict[str, Any]:
    client = get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase client failed to initialize or is unavailable")
    settings = get_settings()
    client.storage.get_bucket(settings.supabase_knowledge_bucket)
    return {"ok": True}
