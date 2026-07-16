# Use: Main API proxy for Read-Only Assessor AI chat.

from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.routers.ai.proxy import forward_to_ai_service
from app.schemas.auth import UserContext

router = APIRouter(prefix="/assessor", tags=["AI Assessor"])


class AssessorChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="Read-only assessor AI Q&A")
async def ai_assessor_chat(
    payload: AssessorChatProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.USE_ASSESSOR_CHAT))],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    conversation_id = payload.conversation_id or str(uuid4())
    result = await forward_to_ai_service(
        "/assessor/chat",
        {"query": payload.query, "conversation_id": conversation_id},
        authorization,
    )
    result["conversation_id"] = conversation_id
    return result
