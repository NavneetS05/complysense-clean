# Use: Backend proxy router for Auditor AI features (Smart Sampling & Observation Drafter).

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

router = APIRouter(prefix="/audit", tags=["AI Audit"])


class SmartSampleProxyRequest(BaseModel):
    assessment_id: str
    conversation_id: str | None = None


class DraftObservationProxyRequest(BaseModel):
    control_id: str
    evidence_id: str | None = None
    partial_text: str | None = None
    conversation_id: str | None = None


class AuditChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="Auditor AI Q&A")
async def ai_audit_chat(
    payload: AuditChatProxyRequest,
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
        "/audit/chat",
        {"query": full_query, "conversation_id": conversation_id},
        authorization,
    )
    result = _normalize_ai_result(result)
    result["conversation_id"] = conversation_id
    return result


@router.post("/smart-sample", summary="Calculate smart evidence sample prioritization")
async def ai_smart_sample(
    payload: SmartSampleProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query assessment details
    assess_res = await session.execute(
        text("select framework_name, assessment_name from assessments where assessment_id = :assessment_id and institution_id = :inst_id"),
        {"assessment_id": payload.assessment_id, "inst_id": user_ctx.institution_id}
    )
    assess_row = assess_res.mappings().first()
    if not assess_row:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Query all controls for that assessment framework with evidence metadata and gap severity
    query = """
        select
            ca.control_id,
            ca.status,
            ca.due_date,
            (select count(*) from evidence_documents e where e.control_id = ca.control_id and e.institution_id = ca.institution_id) as evidence_count,
            (select max(uploaded_at) from evidence_documents e where e.control_id = ca.control_id and e.institution_id = ca.institution_id) as latest_upload,
            cg.severity as gap_severity
        from control_assignments ca
        left join compliance_gaps cg on cg.control_id = ca.control_id and cg.institution_id = ca.institution_id and cg.remediation_status in ('open', 'in_progress')
        where ca.framework_name = :framework_name
          and ca.institution_id = :inst_id
    """
    res = await session.execute(text(query), {"framework_name": assess_row["framework_name"], "inst_id": user_ctx.institution_id})
    rows = res.mappings().all()

    if not rows:
        return {
            "response": "No control assignments found for this assessment framework.",
            "citations": [],
            "query_type": "smart_sample",
            "chunks_used": 0
        }

    # Format the control details context for the AI service
    lines = [
        f"Assessment: {assess_row['assessment_name']} ({assess_row['framework_name']})",
        "Control assignments and evidence upload details:"
    ]
    for r in rows:
        due_str = r["due_date"].isoformat() if r["due_date"] else "No due date"
        latest_str = r["latest_upload"].isoformat() if r["latest_upload"] else "No uploads"
        gap_str = f" | Active Gap Severity: {r['gap_severity'].upper()}" if r["gap_severity"] else ""
        lines.append(
            f"- Control ID: {r['control_id']} | Status: {r['status']}{gap_str}\n"
            f"  Evidence Count: {r['evidence_count']} | Latest Upload: {latest_str} | Due: {due_str}"
        )
    
    control_details = "\n".join(lines)

    ai_payload = {
        "control_details": control_details,
        "conversation_id": payload.conversation_id
    }

    res = await forward_to_ai_service("/audit/smart-sample", ai_payload, authorization)
    normalized = _normalize_ai_result(res)

    ev_query = """
        select e.evidence_id
        from evidence_documents e
        join control_assignments ca on ca.control_id = e.control_id and ca.institution_id = e.institution_id
        where ca.framework_name = :framework_name and ca.institution_id = :inst_id
        order by e.uploaded_at desc
        limit 10
    """
    ev_res = await session.execute(text(ev_query), {"framework_name": assess_row["framework_name"], "inst_id": user_ctx.institution_id})
    ev_rows = ev_res.mappings().all()
    normalized["priority_evidence_ids"] = [str(r["evidence_id"]) for r in ev_rows]
    return normalized


@router.post("/draft-observation", summary="Draft a formal audit observation via AI")
async def ai_draft_observation(
    payload: DraftObservationProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query control assignment details
    control_res = await session.execute(
        text("select control_id, framework_name, status, due_date, notes from control_assignments where control_id = :control_id and institution_id = :inst_id"),
        {"control_id": payload.control_id, "inst_id": user_ctx.institution_id}
    )
    control_row = control_res.mappings().first()
    if not control_row:
        raise HTTPException(status_code=404, detail="Control assignment not found")

    # Query gap details if they exist
    gap_res = await session.execute(
        text("select title, description, severity from compliance_gaps where control_id = :control_id and institution_id = :inst_id and remediation_status in ('open', 'in_progress') limit 1"),
        {"control_id": payload.control_id, "inst_id": user_ctx.institution_id}
    )
    gap_row = gap_res.mappings().first()

    # Query evidence details if supplied
    evidence_desc = ""
    if payload.evidence_id:
        ev_res = await session.execute(
            text("select file_name, approval_status, description from evidence_documents where evidence_id = :evidence_id and institution_id = :inst_id"),
            {"evidence_id": payload.evidence_id, "inst_id": user_ctx.institution_id}
        )
        ev_row = ev_res.mappings().first()
        if ev_row:
            evidence_desc = (
                f"Evidence file attached: {ev_row['file_name']}\n"
                f"Evidence status: {ev_row['approval_status']}\n"
                f"Evidence description: {ev_row['description'] or 'No description provided.'}\n"
            )

    # Format the finding details context
    details = (
        f"CONTROL INFORMATION:\n"
        f"- Control ID: {control_row['control_id']}\n"
        f"- Framework: {control_row['framework_name']}\n"
        f"- Current status: {control_row['status']}\n"
        f"- Internal notes: {control_row['notes'] or 'None'}\n\n"
    )
    if gap_row:
        details += (
            f"COMPLIANCE GAP IDENTIFIED:\n"
            f"- Title: {gap_row['title']}\n"
            f"- Severity: {gap_row['severity'].upper()}\n"
            f"- Gap description: {gap_row['description'] or 'None'}\n\n"
        )
    if evidence_desc:
        details += f"EVIDENCE BEING EVALUATED:\n{evidence_desc}\n"
    if payload.partial_text:
        details += f"AUDITOR'S DRAFT / FIELD NOTES:\n{payload.partial_text}\n"

    ai_payload = {
        "finding_details": details,
        "conversation_id": payload.conversation_id
    }

    res = await forward_to_ai_service("/audit/draft-observation", ai_payload, authorization)
    return _normalize_ai_result(res)
