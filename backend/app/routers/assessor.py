# Use: Read-only assessor dashboard and conversation history endpoints.

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/assessor", tags=["assessor"])

SEVERITY_WEIGHT = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


@router.get("/dashboard-stats", summary="Read-only assessor dashboard aggregates")
async def get_dashboard_stats(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    inst_id = user_ctx.institution_id
    quarter_start = datetime.utcnow() - timedelta(days=90)
    trend_start = datetime.utcnow() - timedelta(days=180)

    overall_res = await session.execute(
        text(
            """
            select coalesce(round(avg(compliance_percentage)::numeric, 2), 0) as overall
            from compliance_results
            where institution_id = :inst_id
            """
        ),
        {"inst_id": inst_id},
    )
    overall = float(overall_res.scalar() or 0)

    framework_res = await session.execute(
        text(
            """
            select framework_name,
                   round(avg(compliance_percentage)::numeric, 2) as readiness,
                   count(distinct assessment_id) as assessment_count
            from compliance_results
            where institution_id = :inst_id
            group by framework_name
            order by framework_name asc
            """
        ),
        {"inst_id": inst_id},
    )
    frameworks = [
        {
            "framework": row["framework_name"] or "Unspecified",
            "readiness": float(row["readiness"] or 0),
            "assessment_count": int(row["assessment_count"] or 0),
        }
        for row in framework_res.mappings().all()
    ]

    gaps_res = await session.execute(
        text(
            """
            select severity, count(*) as count
            from compliance_gaps
            where institution_id = :inst_id
              and remediation_status in ('open', 'in_progress')
            group by severity
            """
        ),
        {"inst_id": inst_id},
    )
    gaps_by_severity = {row["severity"] or "unknown": int(row["count"] or 0) for row in gaps_res.mappings().all()}

    incident_res = await session.execute(
        text(
            """
            select
                count(*) filter (where status in ('resolved', 'closed')) as resolved,
                count(*) filter (where status not in ('resolved', 'closed')) as open
            from incidents
            where institution_id = :inst_id
              and coalesce(detected_at, created_at) >= :quarter_start
            """
        ),
        {"inst_id": inst_id, "quarter_start": quarter_start},
    )
    incident_row = incident_res.mappings().first() or {}

    trend_res = await session.execute(
        text(
            """
            select date_trunc('month', created_at) as month_start,
                   round(avg(compliance_percentage)::numeric, 2) as compliance
            from compliance_results
            where institution_id = :inst_id
              and created_at >= :trend_start
            group by month_start
            order by month_start asc
            """
        ),
        {"inst_id": inst_id, "trend_start": trend_start},
    )
    trend = [
        {
            "month": row["month_start"].strftime("%b") if row["month_start"] else None,
            "compliance": float(row["compliance"] or 0),
        }
        for row in trend_res.mappings().all()
    ]

    control_res = await session.execute(
        text(
            """
            select framework_name, status, count(*) as count
            from control_assignments
            where institution_id = :inst_id
            group by framework_name, status
            order by framework_name asc
            """
        ),
        {"inst_id": inst_id},
    )
    control_status = [
        {
            "framework": row["framework_name"] or "Unspecified",
            "status": row["status"] or "unknown",
            "count": int(row["count"] or 0),
        }
        for row in control_res.mappings().all()
    ]

    return {
        "overall_compliance": overall,
        "frameworks_assessed": len(frameworks),
        "framework_readiness": frameworks,
        "active_gaps_by_severity": gaps_by_severity,
        "incidents_this_quarter": {
            "resolved": int(incident_row.get("resolved") or 0),
            "open": int(incident_row.get("open") or 0),
        },
        "compliance_trend": trend,
        "control_status": control_status,
    }


@router.get("/top-risks", summary="Read-only assessor top risk areas")
async def get_top_risks(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            """
            select title, framework_name, severity, count(*) over (partition by framework_name, severity) as risk_count
            from compliance_gaps
            where institution_id = :inst_id
              and remediation_status in ('open', 'in_progress')
            """
        ),
        {"inst_id": user_ctx.institution_id},
    )
    rows = sorted(
        res.mappings().all(),
        key=lambda row: (SEVERITY_WEIGHT.get(str(row["severity"]).lower(), 0), int(row["risk_count"] or 0)),
        reverse=True,
    )
    return [
        {
            "title": row["title"] or "Untitled risk",
            "framework": row["framework_name"] or "Unspecified",
            "severity": row["severity"] or "unknown",
        }
        for row in rows[:5]
    ]


@router.get("/conversations", summary="List assessor Q&A conversations")
async def list_conversations(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.USE_ASSESSOR_CHAT))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            """
            select conversation_id, messages, created_at, updated_at
            from ai_conversations
            where institution_id = :inst_id
              and user_id = :user_id
              and agent_type = 'assessor_qa'
            order by updated_at desc
            limit 30
            """
        ),
        {"inst_id": user_ctx.institution_id, "user_id": user_ctx.user_id},
    )
    conversations = []
    for row in res.mappings().all():
        messages = row["messages"] or []
        first_user = next((m.get("content") for m in messages if m.get("role") == "user"), "Assessor Q&A")
        conversations.append(
            {
                "conversation_id": str(row["conversation_id"]),
                "title": first_user[:80],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            }
        )
    return conversations


@router.get("/conversations/{conversation_id}", summary="Load assessor Q&A conversation")
async def get_conversation(
    conversation_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.USE_ASSESSOR_CHAT))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    res = await session.execute(
        text(
            """
            select conversation_id, messages, created_at, updated_at
            from ai_conversations
            where conversation_id = :conversation_id
              and institution_id = :inst_id
              and user_id = :user_id
              and agent_type = 'assessor_qa'
            """
        ),
        {
            "conversation_id": conversation_id,
            "inst_id": user_ctx.institution_id,
            "user_id": user_ctx.user_id,
        },
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": str(row["conversation_id"]),
        "messages": row["messages"] or [],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }
