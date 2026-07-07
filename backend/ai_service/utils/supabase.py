# Use: Decoupled Supabase storage client for the AI service.
# Initialized from AISettings (loaded from .env) — does NOT import from app.*

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.utils.supabase")

_supabase_client = None


def get_supabase_client():
    """
    Returns a lazy-initialized Supabase client.
    Returns None if credentials are not configured (graceful degradation).
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    settings = get_ai_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        logger.warning(
            "supabase.not_configured",
            detail="SUPABASE_URL or SUPABASE_SERVICE_KEY is missing. Knowledge base downloads from Supabase will be skipped.",
        )
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(
            str(settings.supabase_url),
            settings.supabase_service_key,
        )
        logger.info("supabase.connected", bucket=settings.supabase_knowledge_bucket)
        return _supabase_client
    except Exception as exc:
        logger.error("supabase.connection_failed", error=str(exc))
        return None


def download_file_from_bucket(bucket: str, path_in_bucket: str) -> bytes | None:
    """
    Downloads a file from Supabase Storage.
    Returns raw bytes, or None if Supabase is unavailable.
    """
    client = get_supabase_client()
    if client is None:
        return None

    try:
        return client.storage.from_(bucket).download(path_in_bucket)
    except Exception as exc:
        logger.error(
            "supabase.download_failed",
            bucket=bucket,
            path=path_in_bucket,
            error=str(exc),
        )
        return None
