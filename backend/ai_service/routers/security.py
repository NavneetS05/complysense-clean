# Use: IT Security officer AI endpoints — CERT-In report drafting, incident analysis.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.security_agent import SecurityAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/security", tags=["Security"])


class CertInDraftRequest(BaseModel):
    incident_details: str
    conversation_id: str | None = None


class SecurityChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = SecurityAgent()
_conv_mgr = ConversationManager()


@router.post("/cert-in-draft", summary="Draft a formal CERT-In cybersecurity incident report")
async def draft_certin_report(
    payload: CertInDraftRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INSTITUTIONS))],
) -> dict[str, Any]:
    """
    Drafts a structured CERT-In cybersecurity incident report from incident log text.
    Cites relevant CERT-In 2022 sections.
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

    result = await _agent.cert_in_draft(
        incident_details=payload.incident_details,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="cert_in_draft",
            user_query=payload.incident_details[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/chat", summary="Security Q&A and technical guidance")
async def security_chat(
    payload: SecurityChatRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Conversational Q&A for IT security officers.
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

    result = await _agent.execute(
        query=payload.query,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        endpoint_name="chat",
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="security_chat",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

