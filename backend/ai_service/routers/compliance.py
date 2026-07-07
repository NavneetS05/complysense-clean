# Use: Compliance officer AI endpoints — priority triage, regulatory change analysis.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.compliance_agent import ComplianceAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/compliance", tags=["Compliance"])


class TriageRequest(BaseModel):
    incident_log: str
    conversation_id: str | None = None


class RegulatoryChangeRequest(BaseModel):
    circular_text: str
    conversation_id: str | None = None


class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = ComplianceAgent()
_conv_mgr = ConversationManager()


@router.post("/triage", summary="Priority-triage an incident log against ISO 27001 and CERT-In")
async def compliance_triage(
    payload: TriageRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INSTITUTIONS))],
) -> dict[str, Any]:
    """
    Triages a security incident log and classifies priority.
    Returns JSON with priority, cert_in_trigger flag, and mapped ISO controls.
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

    result = await _agent.triage(
        incident_log=payload.incident_log,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="compliance_triage",
            user_query=payload.incident_log[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/regulatory-change", summary="Analyze a new regulatory circular for gaps")
async def regulatory_change(
    payload: RegulatoryChangeRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INSTITUTIONS))],
) -> dict[str, Any]:
    """
    Compares new regulatory circular against existing compliance posture and maps gaps.
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

    result = await _agent.regulatory_change(
        circular_text=payload.circular_text,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="regulatory_change",
            user_query=payload.circular_text[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/chat", summary="General compliance Q&A")
async def compliance_chat(
    payload: ChatRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Conversational Q&A endpoint for compliance officers.
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
            agent_type="compliance_chat",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

