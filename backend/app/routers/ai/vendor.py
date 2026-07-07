# Use: Backend proxy router for Vendor Reviewer AI features (Contract Analyzer).

from datetime import datetime
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
from app.mongodb import get_mongo_database

router = APIRouter(prefix="/vendor", tags=["AI Vendor"])


class AnalyzeContractProxyRequest(BaseModel):
    vendor_id: str
    contract_text: str
    conversation_id: str | None = None


@router.post("/analyze-contract", summary="Analyze vendor contract with compliance checks")
async def ai_analyze_contract(
    payload: AnalyzeContractProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_VENDORS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query vendor details from PostgreSQL for context
    vendor_res = await session.execute(
        text("select vendor_name, product_name, vendor_category, processing_location, dpa_available from vendors where vendor_id = :vendor_id and institution_id = :inst_id"),
        {"vendor_id": payload.vendor_id, "inst_id": user_ctx.institution_id}
    )
    vendor_row = vendor_res.mappings().first()
    if not vendor_row:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Persist contract analysis query in MongoDB vendor_contracts collection
    try:
        db = get_mongo_database()
        await db["vendor_contracts"].insert_one({
            "vendor_id": payload.vendor_id,
            "institution_id": str(user_ctx.institution_id),
            "contract_text": payload.contract_text,
            "analyzed_at": datetime.utcnow(),
            "analyzed_by": str(user_ctx.user_id)
        })
    except Exception as exc:
        # Log error, but proceed as non-fatal to ensure contract analysis functions
        import logging
        logging.getLogger("app.routers.ai.vendor").warning(f"MongoDB write failed: {exc}")

    # Build vendor contextual prompt suffix
    vendor_context = (
        f"Vendor Name: {vendor_row['vendor_name']}\n"
        f"Product: {vendor_row['product_name'] or 'N/A'}\n"
        f"Category: {vendor_row['vendor_category'] or 'N/A'}\n"
        f"Processing Location: {vendor_row['processing_location'] or 'Unknown'}\n"
        f"DPA Available: {vendor_row['dpa_available']}\n\n"
        f"CONTRACT TEXT:\n{payload.contract_text}"
    )

    ai_payload = {
        "contract_text": vendor_context,
        "conversation_id": payload.conversation_id
    }

    return await forward_to_ai_service("/vendor/analyze-contract", ai_payload, authorization)
