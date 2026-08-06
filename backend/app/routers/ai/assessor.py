# Use: Main API proxy for Read-Only Assessor AI chat.

from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.routers.ai.proxy import forward_to_ai_service
from app.schemas.auth import UserContext
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assessor", tags=["AI Assessor"])


class AssessorChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="Read-only assessor AI Q&A")
async def ai_assessor_chat(
    payload: AssessorChatProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.USE_ASSESSOR_CHAT))],
    session: AsyncSession = Depends(get_db_session),
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    from app.routers.ai.operational_context import build_institution_operational_context

    conversation_id = payload.conversation_id or str(uuid4())
    op_context = await build_institution_operational_context(session, user_ctx.institution_id)

    full_query = (
        f"LIVE INSTITUTION DATABASE CONTEXT:\n{op_context}\n\n"
        f"USER QUERY:\n{payload.query}"
    ) if op_context else payload.query

    result = await forward_to_ai_service(
        "/assessor/chat",
        {"query": full_query, "conversation_id": conversation_id},
        authorization,
    )
    result["conversation_id"] = conversation_id
    return result
