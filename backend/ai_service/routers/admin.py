# Use: Admin endpoints — RAG reindex trigger and AI diagnostics.
# Secured by X-Admin-Key header (value must match AI_ADMIN_REINDEX_KEY env var).
# These endpoints are internal-only and should not be exposed to the public internet.

from typing import Any

from fastapi import APIRouter, Header, HTTPException

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.routers.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


def _verify_admin_key(x_admin_key: str | None) -> None:
    """Validates the X-Admin-Key header against the configured secret."""
    settings = get_ai_settings()
    expected = settings.admin_reindex_key
    if not expected:
        # No key configured — block all requests with a clear message
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are disabled: ADMIN_REINDEX_KEY is not configured.",
        )
    if x_admin_key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing admin key.")


@router.post("/reindex", summary="Force full RAG index rebuild")
async def trigger_reindex(
    triggered_by: str = "admin_api",
    x_admin_key: str | None = Header(default=None),
) -> dict[str, Any]:
    """
    Forces a full re-index of the RAG knowledge base.
    Atomically rebuilds and reloads indices into memory without restarting the service.

    Requires X-Admin-Key header matching ADMIN_REINDEX_KEY env variable.
    """
    _verify_admin_key(x_admin_key)

    try:
        from ai_service.rag.indexing.index_builder import IndexBuilder
        from ai_service.agents.base import _get_retriever
        import ai_service.main as _main

        builder = IndexBuilder()
        result = await builder.run_reindex_pipeline(triggered_by=triggered_by)

        # Reload in-memory indices without restart
        retriever = _get_retriever()
        retriever.reload_indices()
        _main._index_ready = True

        logger.info("admin.reindex_complete", result=result)

        return {
            "status": "success",
            "message": "RAG index rebuilt and reloaded successfully.",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("admin.reindex_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Re-indexing failed: {exc}")


@router.get("/diagnostics", summary="AI service diagnostics")
async def ai_diagnostics(
    x_admin_key: str | None = Header(default=None),
) -> dict[str, Any]:
    """
    Returns diagnostic information about the AI service index health.
    Requires X-Admin-Key header.
    """
    _verify_admin_key(x_admin_key)

    import ai_service.main as _main
    from ai_service.rag.indexing.index_builder import IndexBuilder

    builder = IndexBuilder()
    settings = get_ai_settings()

    return {
        "status": "ok",
        "index_ready": _main._index_ready,
        "vectorstore_exists_on_disk": builder.is_built(),
        "vectorstore_path": str(builder.vs_path),
        "embeddings_model": settings.embeddings_model,
        "llm_model": settings.llm_model,
        "supabase_configured": bool(settings.supabase_url and settings.supabase_service_key),
        "mongodb_configured": bool(settings.mongodb_uri),
        "database_configured": bool(settings.database_url),
    }
