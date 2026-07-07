# Use: Vendor reviewer AI endpoints — contract/SOC2/DPA analysis.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from ai_service.agents.vendor_agent import VendorAgent
from ai_service.rag.generation.conversation import ConversationManager

router = APIRouter(prefix="/vendor", tags=["Vendor"])


class AnalyzeContractRequest(BaseModel):
    contract_text: str
    conversation_id: str | None = None


class VendorChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


_agent = VendorAgent()
_conv_mgr = ConversationManager()


@router.post("/analyze-contract", summary="Analyze a vendor contract or SOC2 report")
async def analyze_contract(
    payload: AnalyzeContractRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
) -> dict[str, Any]:
    """
    Analyzes a vendor contract or SOC2 report against DPDP Act 2023 and ISO 27001:2022.
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

    result = await _agent.analyze_contract(
        contract_text=payload.contract_text,
        conversation_history=history,
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )

    if payload.conversation_id and result.get("response"):
        await _conv_mgr.save_turn(
            conversation_id=payload.conversation_id,
            user_id=str(user_ctx.user_id),
            institution_id=str(user_ctx.institution_id),
            agent_type="analyze_contract",
            user_query=payload.contract_text[:200],
            assistant_response=result["response"],
        )

    return result


@router.post("/chat", summary="Vendor Q&A")
async def vendor_chat(
    payload: VendorChatRequest,
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
            agent_type="vendor_chat",
            user_query=payload.query,
            assistant_response=result["response"],
        )

    return result

