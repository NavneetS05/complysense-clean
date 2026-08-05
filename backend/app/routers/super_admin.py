# Use: Super Admin-only platform management endpoints.
#
# POST /super-admin/rag/reindex
#   Proxies to the AI service's POST /admin/reindex endpoint, which re-chunks
#   and re-embeds the Supabase framework markdown knowledge base (DPDP, ISO 27001,
#   NIST CSF, etc.) without restarting the service.
#
#   Auth: requires MANAGE_INSTITUTIONS permission (Super Admin only).
#   The AI service itself is secured by X-Admin-Key; this proxy reads
#   AI_ADMIN_REINDEX_KEY from settings and forwards it automatically, so
#   the Super Admin user does NOT need to supply the key themselves.

from __future__ import annotations

from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.core.logging import logger
from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


@router.post(
    "/rag/reindex",
    summary="Trigger full RAG knowledge-base reindex (Super Admin only)",
)
async def trigger_rag_reindex(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INSTITUTIONS))],
) -> dict[str, Any]:
    """Force a full re-chunk and re-embed of the Supabase framework markdown files.

    Calls the AI service's POST /admin/reindex endpoint internally.
    The AI service atomically rebuilds and hot-reloads its in-memory indices —
    no service restart is required.

    MongoDB is NOT touched; it holds the dynamic operational data
    (control_library, uploaded documents) and is not part of the RAG corpus.

    Returns the AI service reindex result on success, or a 502/503 on failure.
    """
    settings = get_settings()
    ai_url = f"{settings.ai_service_url.rstrip('/')}/admin/reindex"

    # Read the admin key from settings (AI_ADMIN_REINDEX_KEY env var).
    # If not configured the AI service will return 503 — we surface that as-is.
    admin_key: str | None = getattr(settings, "ai_admin_reindex_key", None)

    headers: dict[str, str] = {}
    if admin_key:
        headers["X-Admin-Key"] = admin_key

    logger.info(
        "super_admin.rag_reindex.initiated",
        triggered_by=user_ctx.user_id,
        institution_id=user_ctx.institution_id,
    )

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                ai_url,
                params={"triggered_by": f"super_admin:{user_ctx.user_id}"},
                headers=headers,
            )

        if response.status_code == 503:
            raise HTTPException(
                status_code=503,
                detail=(
                    "AI service admin endpoints are disabled — "
                    "AI_ADMIN_REINDEX_KEY is not configured on the AI service."
                ),
            )
        if response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="AI service rejected the admin key. Check AI_ADMIN_REINDEX_KEY in .env.",
            )
        if response.status_code >= 500:
            body = {}
            try:
                body = response.json()
            except Exception:
                pass
            raise HTTPException(
                status_code=502,
                detail=body.get("detail", "AI service reindex failed — check AI service logs."),
            )

        result: dict[str, Any] = response.json()
        logger.info("super_admin.rag_reindex.complete", result=result)
        return result

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="RAG reindex timed out (>5 min). Check AI service logs for progress.",
        )
    except httpx.RequestError as exc:
        logger.error("super_admin.rag_reindex.connection_failed", error=str(exc))
        raise HTTPException(
            status_code=503,
            detail="AI service is unreachable. Ensure the AI service is running.",
        )
