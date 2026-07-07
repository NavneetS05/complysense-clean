# Use: Auditor AI endpoints — smart evidence sampling, audit observation drafting.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.audit_agent import AuditAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/audit", tags=["Audit"])


class SmartSampleRequest(BaseModel):
    control_details: str
    conversation_id: str | None = None


class AuditObservationRequest(BaseModel):
    finding_details: str
    conversation_id: str | None = None


class AuditChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = AuditAgent()
_conv_mgr = ConversationManager()


@router.post("/smart-sample", summary="Calculate statistically valid audit sample sizes")
async def smart_sample(
    payload: SmartSampleRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Calculates recommended audit sample sizes for controls based on population and risk.
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

    result = await _agent.smart_sample(
        control_details=payload.control_details,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="smart_sample",
            user_query=payload.control_details[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/draft-observation", summary="Draft a formal audit observation")
async def draft_observation_endpoint(
    payload: AuditObservationRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Drafts a formal audit observation with Condition/Criteria/Cause/Effect/Recommendation.
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

    result = await _agent.draft_observation(
        finding_details=payload.finding_details,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="draft_observation",
            user_query=payload.finding_details[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/chat", summary="Auditor Q&A")
async def audit_chat(
    payload: AuditChatRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
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
            agent_type="audit_chat",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

