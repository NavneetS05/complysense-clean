# Use: Backend proxy router for Department Reviewer AI features (Translate Control & Pre-flight Check).

import time
from typing import Annotated, Any, Dict, Tuple
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from app.routers.ai.proxy import forward_to_ai_service

router = APIRouter(prefix="/dept", tags=["AI Department"])


# Simple in-memory Redis-like TTL cache fallback
class InMemoryTTLCache:
    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]  # Expired
        return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._cache[key] = (value, time.time() + ttl_seconds)


# Initialize cache singleton
_translation_cache = InMemoryTTLCache()


class PreflightCheckProxyRequest(BaseModel):
    control_id: str
    file_name: str
    file_size_kb: int
    mime_type: str
    file_content_preview: str
    conversation_id: str | None = None


class DeptChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="Department reviewer AI Q&A")
async def ai_dept_chat(
    payload: DeptChatProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    conversation_id = payload.conversation_id or str(uuid4())
    result = await forward_to_ai_service(
        "/dept/chat",
        {"query": payload.query, "conversation_id": conversation_id},
        authorization,
    )
    result["conversation_id"] = conversation_id
    return result


@router.get("/translate/{control_id}", summary="Translate control requirement into plain English")
async def ai_translate_control(
    control_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    cache_key = f"translate:{control_id}:en"
    
    # Try fetching from cache
    cached_val = _translation_cache.get(cache_key)
    if cached_val is not None:
        return cached_val

    # Query PostgreSQL control assignments to fetch the raw text
    control_res = await session.execute(
        text("select control_id, notes, framework_name from control_assignments where control_id = :control_id and institution_id = :inst_id"),
        {"control_id": control_id, "inst_id": user_ctx.institution_id}
    )
    control_row = control_res.mappings().first()
    if not control_row:
        raise HTTPException(status_code=404, detail="Control assignment not found")

    control_text = control_row["notes"] or f"Regulatory control requirement for {control_row['framework_name']} {control_row['control_id']}"

    ai_payload = {
        "control_text": control_text,
        "conversation_id": None
    }

    # Forward to AI service translate control
    res = await forward_to_ai_service("/dept/translate-control", ai_payload, authorization)

    # Cache response for 7 days (604,800 seconds)
    _translation_cache.set(cache_key, res, ttl_seconds=604800)

    return res


@router.post("/preflight-check", summary="Run pre-flight check on evidence document")
async def ai_preflight_check(
    payload: PreflightCheckProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query PostgreSQL control assignments to fetch context
    control_res = await session.execute(
        text("select control_id, notes, framework_name from control_assignments where control_id = :control_id and institution_id = :inst_id"),
        {"control_id": payload.control_id, "inst_id": user_ctx.institution_id}
    )
    control_row = control_res.mappings().first()
    if not control_row:
        raise HTTPException(status_code=404, detail="Control assignment not found")

    control_text = control_row["notes"] or f"Control requirement for {control_row['framework_name']} {control_row['control_id']}"

    # Assemble document content string
    document_text = (
        f"File Metadata:\n"
        f"- Filename: {payload.file_name}\n"
        f"- Size: {payload.file_size_kb} KB\n"
        f"- Mime: {payload.mime_type}\n\n"
        f"Content Extract / Preview:\n"
        f"{payload.file_content_preview}"
    )

    ai_payload = {
        "document_text": document_text,
        "control_requirement": control_text,
        "conversation_id": payload.conversation_id
    }

    return await forward_to_ai_service("/dept/preflight-check", ai_payload, authorization)
