# Use: Department reviewer AI endpoints — control translation, pre-flight evidence checks.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.base import BaseAgent
from ai_service.rag.generation.conversation import ConversationManager
from ai_service.prompts.tasks.dept import DEPT_TRANSLATE_PROMPT, DEPT_PREFLIGHT_PROMPT

router = APIRouter(prefix="/dept", tags=["Department"])


class TranslateControlRequest(BaseModel):
    control_text: str
    conversation_id: str | None = None


class PreflightCheckRequest(BaseModel):
    document_text: str
    control_requirement: str
    conversation_id: str | None = None


class DeptChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = BaseAgent(role="dept_reviewer", endpoint_name="translate_control")
_conv_mgr = ConversationManager()


@router.post("/translate-control", summary="Translate a complex regulatory control into plain English steps")
async def translate_control(
    payload: TranslateControlRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Converts complex framework control text into simple, action-oriented step-by-step instructions.
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
        query="Translate this regulatory control text into plain English action steps.",
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        user_role=str(user_ctx.active_role_name),
        task_prompt=DEPT_TRANSLATE_PROMPT,
        extra_context=payload.control_text,
        endpoint_name="translate_control",
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="translate_control",
            user_query=payload.control_text[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/preflight-check", summary="Pre-flight evidence compliance check")
async def preflight_check(
    payload: PreflightCheckRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Verifies whether an uploaded document provides sufficient evidence for the control requirement.
    Returns JSON with status (pass/fail), confidence, missing_elements, and feedback.
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

    combined_content = f"CONTROL REQUIREMENT:\n{payload.control_requirement}\n\nSUBMITTED DOCUMENT:\n{payload.document_text}"

    result = await _agent.execute(
        query=f"Pre-flight check this document against the control requirement: {payload.control_requirement[:100]}",
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        user_role=str(user_ctx.active_role_name),
        task_prompt=DEPT_PREFLIGHT_PROMPT,
        extra_context=combined_content,
        endpoint_name="preflight_check",
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="preflight_check",
            user_query=payload.control_requirement[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/chat", summary="Department Q&A")
async def dept_chat(
    payload: DeptChatRequest,
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
        user_role=str(user_ctx.active_role_name),
        endpoint_name="chat",
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="dept_chat",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

