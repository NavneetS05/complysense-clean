# Use: Policy approver AI endpoints — conflict detection, executive summary.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.policy_agent import PolicyAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/policy", tags=["Policy"])


class PolicyConflictRequest(BaseModel):
    policy_text: str
    conversation_id: str | None = None


class ExecutiveSummaryRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = PolicyAgent()
_conv_mgr = ConversationManager()


@router.post("/conflict-detect", summary="Detect conflicts and gaps in a policy document")
async def detect_policy_conflicts(
    payload: PolicyConflictRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
) -> dict[str, Any]:
    """
    Validates a policy draft against regulatory frameworks.
    Returns list of conflicts, missing mandatory clauses, and an approval verdict.
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

    result = await _agent.conflict_detect(
        policy_text=payload.policy_text,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="conflict_detect",
            user_query=payload.policy_text[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/executive-summary", summary="Generate an executive compliance briefing")
async def executive_summary(
    payload: ExecutiveSummaryRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
) -> dict[str, Any]:
    """
    Generates a leadership-ready compliance summary briefing.
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

    result = await _agent.executive_summary(
        query=payload.query,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="executive_summary",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

