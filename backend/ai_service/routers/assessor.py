# Use: Assessor endpoints for Q&A and framework clause interpretation.
# Gated by permission USE_ASSESSOR_CHAT, isolation enforced on conversation history.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.assessor_agent import AssessorAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/assessor", tags=["Assessor"])


class AssessorChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = AssessorAgent()
_conv_mgr = ConversationManager()


@router.post("/chat", summary="Read-only assessor Q&A and framework clause verification")
async def chat_endpoint(
    payload: AssessorChatRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.USE_ASSESSOR_CHAT))],
) -> dict[str, Any]:
    """
    Conversational Q&A endpoint for read-only assessors.
    Restricted to frameworks permitted for the assessor role.
    """
    history = []
    if payload.conversation_id:
        try:
            history = await _conv_mgr.get_history(
                conversation_id=payload.conversation_id,
                user_id=str(user_ctx.user_id),
                institution_id=str(user_ctx.institution_id),
            )
        except ValueError:
            raise HTTPException(status_code=403, detail="Not authorized for this conversation.")

    result = await _agent.chat(
        query=payload.query,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        user_role=str(user_ctx.active_role_name),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="assessor_qa",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result
