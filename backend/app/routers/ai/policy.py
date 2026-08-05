# Use: Backend proxy router for Policy Approver AI features (Conflict Detection & Executive Summary).

import asyncio
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from app.routers.ai.proxy import forward_to_ai_service

router = APIRouter(prefix="/policy", tags=["AI Policy"])


class PolicyAnalyzeProxyRequest(BaseModel):
    conversation_id: str | None = None


class PolicyConflictProxyRequest(BaseModel):
    policy_text: str
    conversation_id: str | None = None


class ExecutiveSummaryProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/conflict-detect", summary="Detect conflicts and gaps in a policy document")
async def ai_policy_conflict_detect(
    payload: PolicyConflictProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.APPROVE_POLICIES))],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    return await forward_to_ai_service(
        "/policy/conflict-detect",
        {"policy_text": payload.policy_text, "conversation_id": payload.conversation_id},
        authorization,
    )


@router.post("/executive-summary", summary="Generate an executive compliance briefing")
async def ai_policy_executive_summary(
    payload: ExecutiveSummaryProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.APPROVE_POLICIES))],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    return await forward_to_ai_service(
        "/policy/executive-summary",
        {"query": payload.query, "conversation_id": payload.conversation_id},
        authorization,
    )


@router.post("/analyze/{policy_id}", summary="Analyze a policy for conflicts and generate executive summary")
async def ai_policy_analyze(
    policy_id: str,
    payload: PolicyAnalyzeProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.APPROVE_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query complete policy draft details
    policy_query = """
        select policy_id, policy_name, policy_content, version_number, related_control_id
        from generated_policies
        where policy_id = :policy_id and institution_id = :inst_id
    """
    res = await session.execute(text(policy_query), {"policy_id": policy_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy_content = row["policy_content"] or ""
    policy_name = row["policy_name"]

    if not policy_content.strip():
        return {
            "executive_summary": {
                "response": "Policy document is empty. Cannot generate summary.",
                "citations": []
            },
            "conflicts": {
                "response": "Policy document is empty. No conflicts analyzed.",
                "citations": []
            }
        }

    # Parallel execution using asyncio.gather
    async def get_conflicts():
        conflict_payload = {
            "policy_text": policy_content,
            "conversation_id": payload.conversation_id
        }
        try:
            return await forward_to_ai_service("/policy/conflict-detect", conflict_payload, authorization)
        except Exception as e:
            return {"response": f"Failed to detect conflicts: {e}", "citations": [], "error": str(e)}

    async def get_summary():
        summary_query = f"Summarize changes, who is affected, and the regulatory basis for the policy named '{policy_name}'.\n\nContent:\n{policy_content}"
        summary_payload = {
            "query": summary_query,
            "conversation_id": payload.conversation_id
        }
        try:
            return await forward_to_ai_service("/policy/executive-summary", summary_payload, authorization)
        except Exception as e:
            return {"response": f"Failed to generate summary: {e}", "citations": [], "error": str(e)}

    conflicts_res, summary_res = await asyncio.gather(
        get_conflicts(),
        get_summary()
    )

    # Normalize nested responses to stable keys
    summary_res = summary_res or {}
    conflicts_res = conflicts_res or {}
    summary_res["assessment_summary"] = summary_res.get("assessment_summary") or summary_res.get("response") or ""
    summary_res["recommendations"] = summary_res.get("recommendations") or ""
    conflicts_res["assessment_summary"] = conflicts_res.get("assessment_summary") or conflicts_res.get("response") or ""
    conflicts_res["recommendations"] = conflicts_res.get("recommendations") or ""

    return {
        "executive_summary": summary_res,
        "conflicts": conflicts_res
    }
