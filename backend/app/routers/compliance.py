# Use: Aggregated dashboard and triage endpoints for the Compliance Officer workspace.

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get(
    "/dashboard",
    summary="Get compliance officer dashboard data from seeded operational records",
)
async def get_compliance_dashboard(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    try:
        stats_res = await session.execute(
            text(
                """
                select
                    (select count(*) from control_assignments where institution_id = :inst_id) as total_controls,
                    (select count(*) from control_assignments where institution_id = :inst_id and status = 'compliant') as compliant_controls,
                    (select count(*) from control_assignments where institution_id = :inst_id and status = 'non_compliant') as non_compliant_controls,
                    (select count(*) from compliance_gaps where institution_id = :inst_id and remediation_status in ('open', 'in_progress')) as active_gaps,
                    (select count(*) from compliance_gaps where institution_id = :inst_id and severity = 'critical' and remediation_status in ('open', 'in_progress')) as critical_gaps,
                    (select count(*) from compliance_gaps where institution_id = :inst_id and severity = 'high' and remediation_status in ('open', 'in_progress')) as high_gaps,
                    (select count(*) from evidence_documents where institution_id = :inst_id and approval_status = 'pending') as pending_evidence,
                    (select count(*) from mitigation_tasks where institution_id = :inst_id and task_status not in ('completed', 'cancelled') and due_date < now()) as overdue_tasks,
                    (select count(*) from assessments where institution_id = :inst_id and assessment_status in ('draft', 'in_progress')) as active_assessments
                """
            ),
            {"inst_id": user_ctx.institution_id},
        )
        stats_row = stats_res.mappings().first() or {}

        overdue_controls_res = await session.execute(
            text(
                """
                select assignment_id, control_id, framework_name, due_date, status
                from control_assignments
                where institution_id = :inst_id
                  and due_date is not null
                  and due_date < now()
                  and status not in ('compliant', 'submitted', 'na')
                order by due_date asc
                limit 5
                """
            ),
            {"inst_id": user_ctx.institution_id},
        )
        overdue_controls = [
            {
                "assignment_id": str(row[0]),
                "control_id": row[1],
                "framework_name": row[2],
                "due_date": row[3].isoformat() if row[3] else None,
                "status": row[4],
            }
            for row in overdue_controls_res.fetchall()
        ]

        evidence_res = await session.execute(
            text(
                """
                select evidence_id, file_name, control_id, approval_status, uploaded_at
                from evidence_documents
                where institution_id = :inst_id
                  and approval_status = 'pending'
                order by uploaded_at desc
                limit 5
                """
            ),
            {"inst_id": user_ctx.institution_id},
        )
        evidence_queue = [
            {
                "evidence_id": str(row[0]),
                "file_name": row[1],
                "control_id": row[2],
                "approval_status": row[3],
                "uploaded_at": row[4].isoformat() if row[4] else None,
            }
            for row in evidence_res.fetchall()
        ]

        triage_res = await session.execute(
            text(
                """
                select title, severity, framework_name, control_id, remediation_status
                from compliance_gaps
                where institution_id = :inst_id
                  and remediation_status in ('open', 'in_progress')
                order by case severity
                    when 'critical' then 0
                    when 'high' then 1
                    when 'medium' then 2
                    else 3
                end, created_at desc
                limit 8
                """
            ),
            {"inst_id": user_ctx.institution_id},
        )
        triage = [
            {
                "title": row[0],
                "severity": row[1],
                "framework_name": row[2],
                "control_id": row[3],
                "remediation_status": row[4],
            }
            for row in triage_res.fetchall()
        ]

        today_actions = []
        if int(stats_row.get("pending_evidence") or 0) > 0:
            today_actions.append(
                {
                    "title": f"Review {stats_row.get('pending_evidence')} pending evidence submissions",
                    "href": "/compliance/evidence-queue",
                }
            )
        if int(stats_row.get("active_assessments") or 0) > 0:
            today_actions.append(
                {
                    "title": f"Complete {stats_row.get('active_assessments')} active assessment(s)",
                    "href": "/compliance/assessments",
                }
            )
        if int(stats_row.get("active_gaps") or 0) > 0:
            today_actions.append(
                {
                    "title": f"Assign tasks for {stats_row.get('active_gaps')} open gaps",
                    "href": "/compliance/gaps",
                }
            )
        if int(stats_row.get("overdue_tasks") or 0) > 0:
            today_actions.append(
                {
                    "title": f"Follow up on {stats_row.get('overdue_tasks')} overdue tasks",
                    "href": "/compliance/tasks",
                }
            )

        return {
            "stats": {
                "total_controls": int(stats_row.get("total_controls") or 0),
                "compliant_controls": int(stats_row.get("compliant_controls") or 0),
                "non_compliant_controls": int(stats_row.get("non_compliant_controls") or 0),
                "active_gaps": int(stats_row.get("active_gaps") or 0),
                "critical_gaps": int(stats_row.get("critical_gaps") or 0),
                "high_gaps": int(stats_row.get("high_gaps") or 0),
                "pending_evidence": int(stats_row.get("pending_evidence") or 0),
                "overdue_tasks": int(stats_row.get("overdue_tasks") or 0),
                "active_assessments": int(stats_row.get("active_assessments") or 0),
            },
            "triage": triage,
            "today_actions": today_actions,
            "evidence_queue": evidence_queue,
            "overdue_controls": overdue_controls,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/triage-context",
    summary="Get triage context for AI prioritization",
)
async def get_triage_context(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    return await get_compliance_dashboard(user_ctx, session)
