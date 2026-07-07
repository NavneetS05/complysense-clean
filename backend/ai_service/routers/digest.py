# Use: Daily digest generation endpoint.
# Generates a compliance morning digest for the user's role and institution.

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.digest import DIGEST_TASK_PROMPT

router = APIRouter(prefix="/digest", tags=["Digest"])


class GenerateDigestRequest(BaseModel):
    context: str | None = None
    """
    Optional freeform context to focus the digest
    (e.g., "Focus on CERT-In deadlines this week").
    """
    conversation_id: str | None = None


_agent = BaseAgent(role="compliance_officer", endpoint_name="digest")


@router.post("/generate", summary="Generate a morning compliance digest")
async def generate_digest(
    payload: GenerateDigestRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Generates a role-appropriate compliance morning digest.
    Uses the active role's permitted frameworks to surface relevant deadlines,
    obligations and action items.
    """
    # Build a role-aware agent so framework gating applies correctly
    role_agent = BaseAgent(
        role=user_ctx.active_role_name.lower().replace(" ", "_"),
        endpoint_name="digest",
    )

    query = "Generate a compliance morning digest for today."
    if payload.context:
        query = f"{query} Focus: {payload.context}"

    result = await role_agent.execute(
        query=query,
        conversation_history=[],
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        task_prompt=DIGEST_TASK_PROMPT,
        endpoint_name="digest",
    )

    return result
