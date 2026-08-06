# Use: Backend proxy router for Compliance Officer AI features (Triage & Regulatory Change).

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

    if "response_json" in result and isinstance(result["response_json"], dict):
        for k, v in result["response_json"].items():
            result.setdefault(k, v)

    result["assessment_summary"] = (
        result.get("assessment_summary")
        or result.get("summary")
        or result.get("justification")
        or result.get("response")
        or ""
    )

    recs = result.get("recommendations") or result.get("recommended_actions") or result.get("recommended_action")
    if isinstance(recs, list):
        recs = "\n".join(str(x) for x in recs)
    elif not isinstance(recs, str):
        citations = result.get("citations", [])
        recs = ", ".join(citations) if isinstance(citations, list) else ""
    result["recommendations"] = recs

    result["risk_level"] = result.get("risk_level") or result.get("priority") or result.get("severity") or None
    result["dpdp_compliant"] = result.get("dpdp_compliant") if isinstance(result.get("dpdp_compliant"), bool) else None
    return result

router = APIRouter(prefix="/compliance", tags=["AI Compliance"])


class TriageProxyRequest(BaseModel):
    conversation_id: str | None = None


class RegulatoryChangeProxyRequest(BaseModel):
    circular_text: str
    conversation_id: str | None = None


class ComplianceChatProxyRequest(BaseModel):
    query: str
    conversation_id: str | None = None


@router.post("/chat", summary="Compliance officer AI Q&A")
async def ai_compliance_chat(
    payload: ComplianceChatProxyRequest,
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
        "/compliance/chat",
        {"query": full_query, "conversation_id": conversation_id},
        authorization,
    )
    result = _normalize_ai_result(result)
    result["conversation_id"] = conversation_id
    return result


@router.post("/triage", summary="Run priority AI triage for compliance officer")
async def ai_compliance_triage(
    payload: TriageProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query database for open compliance gaps to build incident log context
    query = """
        select gap_id, control_id, framework_name, severity, title, remediation_status, description, created_at
        from compliance_gaps
        where institution_id = :inst_id
          and remediation_status in ('open', 'in_progress')
        order by case severity
            when 'critical' then 0
            when 'high' then 1
            when 'medium' then 2
            else 3
        end, created_at desc
        limit 20
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    
    if not rows:
        return {
            "response": "No open compliance gaps found for triage.",
            "citations": [],
            "query_type": "triage",
            "chunks_used": 0
        }

    # Format the gaps into a structured incident log
    lines = ["Outstanding compliance issues and gaps requiring priority triage:"]
    for idx, r in enumerate(rows, 1):
        lines.append(
            f"[{idx}] Control: {r['control_id'] or 'Unassigned'} | Framework: {r['framework_name']} | "
            f"Severity: {r['severity'].upper()} | Status: {r['remediation_status']}\n"
            f"Title: {r['title']}\n"
            f"Description: {r['description'] or 'No description provided.'}\n"
        )
    
    incident_log = "\n".join(lines)

    # Call AI service compliance triage
    ai_payload = {
        "incident_log": incident_log,
        "conversation_id": payload.conversation_id
    }
    
    res = await forward_to_ai_service("/compliance/triage", ai_payload, authorization)
    return _normalize_ai_result(res)


@router.post("/regulatory-change", summary="Analyze regulatory circular against compliance posture")
async def ai_regulatory_change(
    payload: RegulatoryChangeProxyRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    # Query current posture to inject as context
    stats_query = """
        select
            (select count(*) from control_assignments where institution_id = :inst_id) as total,
            (select count(*) from control_assignments where institution_id = :inst_id and status = 'compliant') as compliant,
            (select count(*) from compliance_gaps where institution_id = :inst_id and remediation_status in ('open', 'in_progress')) as active_gaps
    """
    stats_res = await session.execute(text(stats_query), {"inst_id": user_ctx.institution_id})
    stats_row = stats_res.mappings().first() or {}

    gaps_query = """
        select control_id, framework_name, severity, title
        from compliance_gaps
        where institution_id = :inst_id and remediation_status in ('open', 'in_progress')
        limit 10
    """
    gaps_res = await session.execute(text(gaps_query), {"inst_id": user_ctx.institution_id})
    gaps_rows = gaps_res.mappings().all()

    posture_summary = (
        f"Institution Compliance Stats:\n"
        f"- Total Controls: {stats_row.get('total', 0)}\n"
        f"- Compliant Controls: {stats_row.get('compliant', 0)}\n"
        f"- Active Gaps: {stats_row.get('active_gaps', 0)}\n\n"
        f"Active Compliance Gaps:\n"
    )
    for g in gaps_rows:
        posture_summary += f"- [{g['severity'].upper()}] Control {g['control_id']}: {g['title']} ({g['framework_name']})\n"

    # Prefix circular text with posture context
    circular_with_posture = (
        f"CURRENT INSTITUTION COMPLIANCE POSTURE:\n"
        f"{posture_summary}\n"
        f"NEW REGULATORY CIRCULAR TO ANALYZE:\n"
        f"{payload.circular_text}"
    )

    ai_payload = {
        "circular_text": circular_with_posture,
        "conversation_id": payload.conversation_id
    }

    res = await forward_to_ai_service("/compliance/regulatory-change", ai_payload, authorization)
    return _normalize_ai_result(res)
