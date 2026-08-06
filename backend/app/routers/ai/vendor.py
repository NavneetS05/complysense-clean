# Use: Backend proxy router for Vendor Reviewer AI features (Contract Analyzer).

import json
from datetime import datetime
from typing import Annotated, Any
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.repositories.audit import AuditLogRepository
from app.schemas.auth import UserContext
from app.routers.ai.proxy import forward_to_ai_service
from app.mongodb import get_mongo_database

router = APIRouter(prefix="/vendor", tags=["AI Vendor"])


class AnalyzeContractProxyRequest(BaseModel):
    vendor_id: str
    contract_text: str
    conversation_id: str | None = None


class VendorChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def _extract_risk_level(result: dict[str, Any]) -> str | None:
    risk_level = result.get("risk_level") or result.get("severity")
    if isinstance(risk_level, str):
        normalized = risk_level.lower()
        for level in ("critical", "high", "medium", "low"):
            if level in normalized:
                return level

    response = str(result.get("response") or result.get("assessment_summary") or "").lower()
    for level in ("critical", "high", "medium", "low"):
        if f"{level} risk" in response or f"risk level: {level}" in response:
            return level
    return None


def _extract_dpdp_compliant(result: dict[str, Any]) -> bool | None:
    value = result.get("dpdp_compliant")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "compliant"}:
            return True
        if normalized in {"false", "no", "non-compliant", "noncompliant"}:
            return False
    return None


@router.post("/chat", summary="Vendor reviewer AI Q&A")
async def ai_vendor_chat(
    payload: VendorChatProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_VENDORS))],
    session: AsyncSession = Depends(get_db_session),
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    from app.routers.ai.operational_context import build_institution_operational_context

    conversation_id = payload.conversation_id or str(uuid4())
    op_context = await build_institution_operational_context(session, user_ctx.institution_id)

    full_query = (
        f"LIVE INSTITUTION DATABASE CONTEXT:\n{op_context}\n\n"
        f"USER QUERY:\n{payload.query}"
    ) if op_context else payload.query

    result = await forward_to_ai_service(
        "/vendor/chat",
        {"query": full_query, "conversation_id": conversation_id},
        authorization,
    )
    result["conversation_id"] = conversation_id
    return result


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
        logger.warning("mongodb.vendor_contract_write_failed", vendor_id=payload.vendor_id, error=str(exc))

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

    result = await forward_to_ai_service("/vendor/analyze-contract", ai_payload, authorization)
    # Normalize returned AI payload to stable keys used by frontend
    assessment_summary = result.get("assessment_summary") or result.get("summary") or result.get("response") or ""
    recommendations = result.get("recommendations") or result.get("recommended_actions") or result.get("citations") or ""
    result["assessment_summary"] = assessment_summary
    result["recommendations"] = recommendations
    result["risk_level"] = _extract_risk_level(result)
    result["dpdp_compliant"] = _extract_dpdp_compliant(result)

    assessment_res = await session.execute(
        text(
            """
            insert into vendor_risk_assessments (
                vendor_id, institution_id, risk_level, assessment_summary,
                recommendations, dpdp_compliant, assessed_by, created_at
            ) values (
                :vendor_id, :institution_id, :risk_level, :assessment_summary,
                :recommendations, :dpdp_compliant, :assessed_by, now()
            ) returning vendor_risk_id
            """
        ),
        {
            "vendor_id": payload.vendor_id,
            "institution_id": user_ctx.institution_id,
            "risk_level": _extract_risk_level(result),
            "assessment_summary": _as_text(assessment_summary),
            "recommendations": _as_text(recommendations),
            "dpdp_compliant": _extract_dpdp_compliant(result),
            "assessed_by": user_ctx.user_id,
        },
    )
    assessment_row = assessment_res.mappings().first()
    if not assessment_row:
        raise HTTPException(status_code=500, detail="Failed to save vendor risk assessment")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="vendor_risk_assessment_created",
        entity_type="vendor_risk_assessment",
        entity_id=str(assessment_row["vendor_risk_id"]),
        action_details={"vendor_id": payload.vendor_id, "source": "ai_contract_analysis"},
    )
    await session.commit()

    result["vendor_risk_id"] = str(assessment_row["vendor_risk_id"])
    return result
