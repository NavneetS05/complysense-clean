# Use: Backend proxy router for IT Security Officer AI features (CERT-In Report Drafter).

from typing import Annotated, Any
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from app.routers.ai.proxy import forward_to_ai_service


def _normalize_ai_result(result: dict[str, Any] | None) -> dict[str, Any]:
    if result is None:
        result = {}
    result["assessment_summary"] = result.get("assessment_summary") or result.get("summary") or result.get("response") or ""
    result["recommendations"] = result.get("recommendations") or result.get("recommended_actions") or result.get("citations") or ""
    result["risk_level"] = result.get("risk_level") or result.get("severity") or None
    result["dpdp_compliant"] = result.get("dpdp_compliant") if isinstance(result.get("dpdp_compliant"), bool) else None
    return result

router = APIRouter(prefix="/security", tags=["AI Security"])


class CertInDraftProxyRequest(BaseModel):
    conversation_id: str | None = None


class SecurityChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="IT security AI Q&A")
async def ai_security_chat(
    payload: SecurityChatProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
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
        "/security/chat",
        {"query": full_query, "conversation_id": conversation_id},
        authorization,
    )
    result = _normalize_ai_result(result)
    result["conversation_id"] = conversation_id
    return result


@router.post("/cert-in-draft/{incident_id}", summary="Draft a CERT-In incident report via AI")
async def ai_cert_in_draft(
    incident_id: str,
    payload: CertInDraftProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query complete incident details with joins
    incident_query = """
        select 
            i.incident_id, i.title, i.description, i.incident_type, i.severity, i.status,
            i.occurred_at, i.detected_at, i.cert_in_deadline, i.cert_in_reported,
            i.dpdp_notification_required, i.affected_systems, i.affected_data_categories,
            u.full_name as assigned_name, u.email as assigned_email, u.phone as assigned_phone, u.designation as assigned_designation,
            inst.name as institution_name
        from incidents i
        left join users u on i.assigned_to = u.user_id
        join institutions inst on i.institution_id = inst.institution_id
        where i.incident_id = :incident_id and i.institution_id = :inst_id
    """
    res = await session.execute(text(incident_query), {"incident_id": incident_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Fetch incident timeline entries
    timeline_query = """
        select t.action_taken, t.action_at, u.full_name as action_by_name
        from incident_timeline t
        left join users u on t.action_by = u.user_id
        where t.incident_id = :incident_id
        order by t.action_at asc
    """
    t_res = await session.execute(text(timeline_query), {"incident_id": incident_id})
    timeline_rows = t_res.mappings().all()

    # Format values for representation
    occurred_str = row["occurred_at"].isoformat() if row["occurred_at"] else "[FILL IN: Occurred Date/Time]"
    detected_str = row["detected_at"].isoformat() if row["detected_at"] else "[FILL IN: Detected Date/Time]"
    timeline_entries = []
    for r in timeline_rows:
        time_str = r["action_at"].isoformat() if r["action_at"] else ""
        timeline_entries.append(f"- [{time_str}] {r['action_taken']} (By: {r['action_by_name'] or 'System'})")
    timeline_str = "\n".join(timeline_entries) if timeline_entries else "[FILL IN: Steps Taken / Timeline]"

    # Assemble structured text prompt context
    details = (
        f"Organization Name: {row['institution_name']}\n"
        f"Contact Person: {row['assigned_name'] or '[FILL IN: Assigned Contact Person]'}\n"
        f"Designation: {row['assigned_designation'] or '[FILL IN: Designation]'}\n"
        f"Email: {row['assigned_email'] or '[FILL IN: Email]'}\n"
        f"Phone: {row['assigned_phone'] or '[FILL IN: Phone]'}\n\n"
        f"Incident Title: {row['title']}\n"
        f"Incident Description: {row['description'] or 'No description provided.'}\n"
        f"Incident Type: {row['incident_type'] or 'unknown'}\n"
        f"Severity: {row['severity'].upper() if row['severity'] else 'UNKNOWN'}\n"
        f"Occurred At: {occurred_str}\n"
        f"Detected At: {detected_str}\n"
        f"Affected Systems: {row['affected_systems'] or '[FILL IN: List affected hostnames, systems, IPs]'}\n"
        f"Affected Data Categories: {row['affected_data_categories'] or '[FILL IN: Categories of data affected]'}\n"
        f"DPDP Notification Required: {row['dpdp_notification_required']}\n\n"
        f"Action Timeline:\n{timeline_str}"
    )

    ai_payload = {
        "incident_details": details,
        "conversation_id": payload.conversation_id
    }
    res = await forward_to_ai_service("/security/cert-in-draft", ai_payload, authorization)
    return _normalize_ai_result(res)
