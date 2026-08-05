# Use: Router for querying and retrieving the central audit trail logs and auditor workspace data.

from __future__ import annotations

import csv
import io
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.schemas.auth import UserContext

router = APIRouter(prefix="/audit", tags=["audit"])


class CreateObservationPayload(BaseModel):
    assessment_id: str
    control_id: str
    evidence_id: str | None = None
    observation_text: str = Field(min_length=10, max_length=4000)
    severity: str = "observation"


class UpdateObservationPayload(BaseModel):
    observation_text: str | None = None
    severity: str | None = None
    status: str | None = None


class DraftObservationPayload(BaseModel):
    control_id: str | None = None
    observation_text: str = ""


class SmartSamplePayload(BaseModel):
    assessment_id: str


from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Handle this function with safety
async def create_audit_report_entry(
    session: AsyncSession,
    *,
    institution_id: str,
    generated_by: str,
    report_name: str,
    report_type: str,
    file_path: str,
    assessment_id: str | None = None,
) -> Any:
    result = await session.execute(
        text(
            """
            INSERT INTO audit_reports (
                institution_id,
                assessment_id,
                report_name,
                report_type,
                file_path,
                generated_by
            )
            VALUES (
                :institution_id,
                :assessment_id,
                :report_name,
                :report_type,
                :file_path,
                :generated_by
            )
            RETURNING
                report_id,
                institution_id,
                assessment_id,
                report_name,
                report_type,
                file_path,
                generated_by,
                generated_at
            """
        ),
        {
            "institution_id": institution_id,
            "assessment_id": assessment_id,
            "report_name": report_name,
            "report_type": str(report_type),
            "file_path": file_path,
            "generated_by": generated_by,
        },
    )

    row = result.mappings().first()

    if row is None:
        raise RuntimeError("Failed to create audit report entry.")

    return row

@router.get(
    "/recent",
    summary="Get recent audit logs across the platform (Super Admin) or scoped to institution",
)
async def get_recent_audit(
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = Query(10),
) -> list[dict[str, Any]]:
    query = """
        select al.audit_log_id, al.institution_id, i.institution_name,
               al.user_id, u.full_name as user_name,
               al.action_type, al.entity_type, al.entity_id,
               al.action_details, al.ip_address, al.created_at
          from audit_logs al
          left join institutions i on i.institution_id = al.institution_id
          left join users u on u.user_id = al.user_id
    """
    params: dict[str, Any] = {"limit": limit}

    if user.active_role_name != RoleName.SUPER_ADMIN:
        query += " where al.institution_id = :inst_id"
        params["inst_id"] = user.institution_id

    query += " order by al.created_at desc limit :limit"

    try:
        res = await session.execute(text(query), params)
        rows = res.mappings().all()
        out: list[dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            d["audit_log_id"] = str(d.get("audit_log_id"))
            d["institution_id"] = str(d.get("institution_id")) if d.get("institution_id") else None
            d["user_id"] = str(d.get("user_id")) if d.get("user_id") else None
            d["entity_id"] = str(d.get("entity_id")) if d.get("entity_id") else None
            # Normalize timestamp
            if d.get("created_at"):
                try:
                    d["created_at"] = d["created_at"].isoformat()
                except Exception:
                    d["created_at"] = str(d["created_at"])
            out.append(d)
        return out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/logs",
    summary="Search, filter, and retrieve platform/institution audit logs",
)
async def get_audit_logs(
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    institution_id: str | None = Query(None),
    action_type: str | None = Query(None),
    user_search: str | None = Query(None),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    format: str | None = Query(None),
    page: int = Query(1),
    limit: int = Query(50),
) -> Any:
    if PermissionKey.VIEW_AUDIT_TRAIL.value not in user.permissions:
        raise HTTPException(status_code=403, detail="Missing permission: view_audit_trail")

    scope_inst_id = institution_id
    if user.active_role_name != RoleName.SUPER_ADMIN:
        scope_inst_id = user.institution_id

    query_select = """
        select al.audit_log_id, al.institution_id, i.institution_name,
               al.user_id, u.full_name as user_name, u.email as user_email,
               al.active_role_id, r.role_name as role_at_time,
               al.action_type, al.entity_type, al.entity_id,
               al.action_details, al.ip_address, al.created_at
          from audit_logs al
          left join institutions i on i.institution_id = al.institution_id
          left join users u on u.user_id = al.user_id
          left join roles r on r.role_id = al.active_role_id
         where 1=1
    """

    query_count = """
        select count(*)
          from audit_logs al
          left join users u on u.user_id = al.user_id
         where 1=1
    """

    where_clause = ""
    params: dict[str, Any] = {}

    if scope_inst_id and scope_inst_id != "All":
        where_clause += " and al.institution_id = :inst_id"
        params["inst_id"] = scope_inst_id

    if action_type and action_type != "All":
        where_clause += " and al.action_type = :action_type"
        params["action_type"] = action_type

    if user_search:
        where_clause += " and (lower(u.full_name) like lower(:user_search) or lower(u.email) like lower(:user_search))"
        params["user_search"] = f"%{user_search}%"

    if from_date:
        where_clause += " and al.created_at >= :from_date"
        params["from_date"] = f"{from_date} 00:00:00"

    if to_date:
        where_clause += " and al.created_at <= :to_date"
        params["to_date"] = f"{to_date} 23:59:59"

    if format == "csv":
        query_csv = f"{query_select} {where_clause} order by al.created_at desc"
        res = await session.execute(text(query_csv), params)
        rows = res.mappings().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Institution", "User Name", "User Email", "Role At Time", "Action Type", "Entity Type", "Entity ID", "IP Address", "Details"])

        for r in rows:
            writer.writerow([
                str(r["created_at"]),
                r["institution_name"] or "System",
                r["user_name"] or "System",
                r["user_email"] or "N/A",
                r["role_at_time"] or "N/A",
                r["action_type"],
                r["entity_type"] or "N/A",
                str(r["entity_id"]) if r["entity_id"] else "N/A",
                r["ip_address"] or "N/A",
                str(r["action_details"] or ""),
            ])

        csv_data = output.getvalue()
        output.close()

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_trail_export.csv"},
        )

    res_count = await session.execute(text(f"{query_count} {where_clause}"), params)
    total_count = res_count.scalar() or 0

    offset = (page - 1) * limit
    params["limit"] = limit
    params["offset"] = offset

    query_paginated = f"{query_select} {where_clause} order by al.created_at desc limit :limit offset :offset"
    res_logs = await session.execute(text(query_paginated), params)
    rows = res_logs.mappings().all()

    logs = []
    for r in rows:
        d = dict(r)
        d["audit_log_id"] = str(d["audit_log_id"])
        d["institution_id"] = str(d["institution_id"]) if d["institution_id"] else None
        d["user_id"] = str(d["user_id"]) if d["user_id"] else None
        d["active_role_id"] = str(d["active_role_id"]) if d["active_role_id"] else None
        d["entity_id"] = str(d["entity_id"]) if d["entity_id"] else None
        logs.append(d)

    return {"logs": logs, "total": total_count, "page": page, "limit": limit}


@router.get(
    "/observations",
    summary="List audit observations for the current institution",
)
async def list_observations(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    assessment_id: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    control_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    query = """
        select ao.observation_id, ao.assessment_id, ao.control_id, ao.evidence_id, ao.observation_text,
               ao.severity, ao.status, ao.created_at, ao.added_by, u.full_name as added_by_name,
               a.assessment_name, a.framework_name, ed.file_name
          from audit_observations ao
          left join assessments a on a.assessment_id = ao.assessment_id
          left join users u on u.user_id = ao.added_by
          left join evidence_documents ed on ed.evidence_id = ao.evidence_id
         where ao.institution_id = :inst_id
    """
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id}
    if assessment_id:
        query += " and ao.assessment_id = :assessment_id"
        params["assessment_id"] = assessment_id
    if severity:
        query += " and ao.severity = :severity"
        params["severity"] = severity
    if status:
        query += " and ao.status = :status"
        params["status"] = status
    if control_id:
        query += " and ao.control_id = :control_id"
        params["control_id"] = control_id
    query += " order by ao.created_at desc"

    res = await session.execute(text(query), params)
    rows = res.mappings().all()
    return [
        {
            "observation_id": str(row["observation_id"]),
            "assessment_id": str(row["assessment_id"]) if row["assessment_id"] else None,
            "assessment_name": row["assessment_name"],
            "framework_name": row["framework_name"],
            "control_id": row["control_id"],
            "evidence_id": str(row["evidence_id"]) if row["evidence_id"] else None,
            "evidence_file": row["file_name"],
            "observation_text": row["observation_text"],
            "severity": row["severity"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "added_by": str(row["added_by"]) if row["added_by"] else None,
            "added_by_name": row["added_by_name"],
        }
        for row in rows
    ]


@router.post(
    "/observations",
    status_code=201,
    summary="Create an audit observation for an assessment/control",
)
async def create_observation(
    payload: CreateObservationPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.ADD_AUDIT_OBSERVATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if user_ctx.active_role_name != RoleName.AUDITOR:
        raise HTTPException(status_code=403, detail="Only auditors can add observations")

    assessment_check = await session.execute(
        text("select assessment_id from assessments where assessment_id = :assessment_id and institution_id = :inst_id"),
        {"assessment_id": payload.assessment_id, "inst_id": user_ctx.institution_id},
    )
    if not assessment_check.mappings().first():
        raise HTTPException(status_code=404, detail="Assessment not found")

    if payload.evidence_id:
        evidence_check = await session.execute(
            text("select evidence_id from evidence_documents where evidence_id = :evidence_id and institution_id = :inst_id"),
            {"evidence_id": payload.evidence_id, "inst_id": user_ctx.institution_id},
        )
        if not evidence_check.mappings().first():
            raise HTTPException(status_code=404, detail="Evidence not found")

    res = await session.execute(
        text(
            """
            insert into audit_observations (
                institution_id, assessment_id, control_id, evidence_id, observation_text, severity, status, added_by
            ) values (
                :inst_id, :assessment_id, :control_id, :evidence_id, :observation_text, :severity, 'open', :added_by
            ) returning observation_id, created_at
            """
        ),
        {
            "inst_id": user_ctx.institution_id,
            "assessment_id": payload.assessment_id,
            "control_id": payload.control_id,
            "evidence_id": payload.evidence_id,
            "observation_text": payload.observation_text,
            "severity": payload.severity,
            "added_by": user_ctx.user_id,
        },
    )
    await session.execute(
        text(
            """
            insert into audit_logs (
                institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details
            ) values (
                :inst_id, :user_id, :active_role_id, 'observation_added', 'audit_observation', :entity_id, :details
            )
            """
        ),
        {
            "inst_id": user_ctx.institution_id,
            "user_id": user_ctx.user_id,
            "active_role_id": user_ctx.active_role_id,
            "entity_id": None,
            "details": f'{{"control_id":"{payload.control_id}"}}',
        },
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create observation")
    return {
        "observation_id": str(row["observation_id"]),
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


@router.patch("/observations/{observation_id}", summary="Update an observation owned by the current auditor")
async def update_observation(
    observation_id: str,
    payload: UpdateObservationPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.ADD_AUDIT_OBSERVATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if user_ctx.active_role_name != RoleName.AUDITOR:
        raise HTTPException(status_code=403, detail="Only auditors can edit observations")
    fields = []
    params: dict[str, Any] = {"observation_id": observation_id, "inst_id": user_ctx.institution_id, "user_id": user_ctx.user_id}
    if payload.observation_text is not None:
        fields.append("observation_text = :observation_text")
        params["observation_text"] = payload.observation_text
    if payload.severity is not None:
        fields.append("severity = :severity")
        params["severity"] = payload.severity
    if payload.status is not None:
        fields.append("status = :status")
        params["status"] = payload.status
    if not fields:
        raise HTTPException(status_code=400, detail="No update values provided")
    query = f"update audit_observations set {', '.join(fields)} where observation_id = :observation_id and institution_id = :inst_id and added_by = :user_id and status in ('open', 'acknowledged') returning observation_id"
    res = await session.execute(text(query), params)
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Observation not found or is not editable")
    return {"observation_id": str(row["observation_id"]), "updated": True}


@router.delete("/observations/{observation_id}", summary="Delete an observation owned by the current auditor")
async def delete_observation(
    observation_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.ADD_AUDIT_OBSERVATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if user_ctx.active_role_name != RoleName.AUDITOR:
        raise HTTPException(status_code=403, detail="Only auditors can delete observations")
    res = await session.execute(
        text(
            """
            delete from audit_observations
             where observation_id = :observation_id
               and institution_id = :inst_id
               and added_by = :user_id
               and status = 'open'
            returning observation_id
            """
        ),
        {"observation_id": observation_id, "inst_id": user_ctx.institution_id, "user_id": user_ctx.user_id},
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Observation not found or cannot be deleted")
    return {"observation_id": str(row["observation_id"]), "deleted": True}


@router.post("/observations/draft", summary="Generate a draft observation for the selected control")
async def draft_observation(
    payload: DraftObservationPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.ADD_AUDIT_OBSERVATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if user_ctx.active_role_name != RoleName.AUDITOR:
        raise HTTPException(status_code=403, detail="Only auditors can draft observations")
    base_text = payload.observation_text.strip()
    if not base_text:
        base_text = "Evidence submitted for this control should be reviewed for sufficiency."
    draft = (
        f"Potential gap noted for control {payload.control_id or 'the selected control'}: {base_text} "
        "Please confirm that the evidence is complete, current, and aligned with the stated requirement."
    )
    return {"draft": draft}


@router.post("/smart-sample", summary="Create a lightweight risk-priority sample of evidence items")
async def smart_sample(
    payload: SmartSamplePayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    if user_ctx.active_role_name != RoleName.AUDITOR:
        raise HTTPException(status_code=403, detail="Only auditors can use smart sampling")

    assessment_check = await session.execute(
        text("select assessment_id from assessments where assessment_id = :assessment_id and institution_id = :inst_id"),
        {"assessment_id": payload.assessment_id, "inst_id": user_ctx.institution_id},
    )
    if not assessment_check.mappings().first():
        raise HTTPException(status_code=404, detail="Assessment not found")

    res = await session.execute(
        text(
            """
            select evidence_id, control_id, file_name, approval_status
              from evidence_documents
             where institution_id = :inst_id
               and control_id is not null
             order by uploaded_at desc
            """
        ),
        {"inst_id": user_ctx.institution_id},
    )
    rows = res.mappings().all()

    samples = []
    for row in rows:
        reason = "Missing or pending evidence" if row["approval_status"] != "approved" else "Evidence present but should be reviewed"
        samples.append({
            "evidence_id": str(row["evidence_id"]),
            "control_id": row["control_id"],
            "file_name": row["file_name"],
            "reason": reason,
        })
    return samples[:8]


@router.get("/reports", summary="List audit reports for the current institution")
async def list_reports(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            """
            select report_id, assessment_id, report_name, report_type, file_path, generated_by, generated_at
              from audit_reports
             where institution_id = :inst_id
             order by generated_at desc
            """
        ),
        {"inst_id": user_ctx.institution_id},
    )
    rows = res.mappings().all()
    return [
        {
            "report_id": str(row["report_id"]),
            "assessment_id": str(row["assessment_id"]) if row["assessment_id"] else None,
            "report_name": row["report_name"],
            "report_type": row["report_type"],
            "file_path": row["file_path"],
            "generated_by": str(row["generated_by"]) if row["generated_by"] else None,
            "generated_at": row["generated_at"].isoformat() if row["generated_at"] else None,
        }
        for row in rows
    ]


@router.post("/reports/generate", status_code=201, summary="Generate a report entry from an assessment")
async def generate_report(
    payload: dict[str, Any],
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.GENERATE_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    assessment_id = payload.get("assessment_id")
    report_name = payload.get("report_name") or "Audit Report"
    report_type = payload.get("report_type") or "custom"
    sections = payload.get("sections") or []

    assessment_check = await session.execute(
        text("select assessment_id, assessment_name, framework_name from assessments where assessment_id = :assessment_id and institution_id = :inst_id"),
        {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id},
    )
    assessment = assessment_check.mappings().first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    res = await session.execute(
        text(
            """
            insert into audit_reports (
                institution_id, assessment_id, report_name, report_type, file_path, generated_by
            ) values (
                :inst_id, :assessment_id, :report_name, :report_type, :file_path, :generated_by
            ) returning report_id, generated_at
            """
        ),
        {
            "inst_id": user_ctx.institution_id,
            "assessment_id": assessment_id,
            "report_name": report_name,
            "report_type": report_type,
            "file_path": f"/reports/{report_name.lower().replace(' ', '-')}.html",
            "generated_by": user_ctx.user_id,
        },
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create report")

    observation_count = await session.execute(text("select count(*) from audit_observations where assessment_id = :assessment_id and institution_id = :inst_id"), {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id})
    gap_count = await session.execute(text("select count(*) from compliance_gaps where assessment_id = :assessment_id and institution_id = :inst_id"), {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id})
    evidence_count = await session.execute(text("select count(*) from evidence_documents where institution_id = :inst_id and control_id is not null"), {"inst_id": user_ctx.institution_id})

    return {
        "report_id": str(row["report_id"]),
        "generated_at": row["generated_at"].isoformat() if row["generated_at"] else None,
        "summary": {
            "assessment_name": assessment["assessment_name"],
            "framework_name": assessment["framework_name"],
            "sections": sections,
            "observation_count": observation_count.scalar() or 0,
            "gap_count": gap_count.scalar() or 0,
            "evidence_count": evidence_count.scalar() or 0,
        },
    }


@router.get("/reports/{report_id}", summary="Get a single audit report with assembled sections")
async def get_report(
    report_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    report_res = await session.execute(
        text("select report_id, assessment_id, report_name, report_type, file_path, generated_by, generated_at from audit_reports where report_id = :report_id and institution_id = :inst_id"),
        {"report_id": report_id, "inst_id": user_ctx.institution_id},
    )
    report = report_res.mappings().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    assessment_res = await session.execute(
        text("select assessment_id, assessment_name, framework_name, assessment_status from assessments where assessment_id = :assessment_id"),
        {"assessment_id": report["assessment_id"]},
    )
    assessment = assessment_res.mappings().first()

    observation_count = await session.execute(text("select count(*) from audit_observations where assessment_id = :assessment_id and institution_id = :inst_id"), {"assessment_id": report["assessment_id"], "inst_id": user_ctx.institution_id})
    gap_res = await session.execute(text("select gap_id, title, severity, remediation_status from compliance_gaps where assessment_id = :assessment_id and institution_id = :inst_id order by created_at desc"), {"assessment_id": report["assessment_id"], "inst_id": user_ctx.institution_id})
    observation_res = await session.execute(text("select observation_text, severity, status from audit_observations where assessment_id = :assessment_id and institution_id = :inst_id order by created_at desc"), {"assessment_id": report["assessment_id"], "inst_id": user_ctx.institution_id})

    return {
        "report_id": str(report["report_id"]),
        "report_name": report["report_name"],
        "report_type": report["report_type"],
        "generated_at": report["generated_at"].isoformat() if report["generated_at"] else None,
        "assessment": {
            "assessment_id": str(assessment["assessment_id"]) if assessment else None,
            "assessment_name": assessment["assessment_name"] if assessment else None,
            "framework_name": assessment["framework_name"] if assessment else None,
            "assessment_status": assessment["assessment_status"] if assessment else None,
        },
        "summary": {
            "observation_count": observation_count.scalar() or 0,
            "gaps": [
                {
                    **dict(r),
                    "created_at": r["created_at"].isoformat() if r.get("created_at") else None
                }
                for r in gap_res.mappings().all()
            ],
            "observations": [
                {
                    **dict(r),
                    "created_at": r["created_at"].isoformat() if r.get("created_at") else None
                }
                for r in observation_res.mappings().all()
            ],
        },
    }


@router.get("/reports/{report_id}/download", summary="Download a generated report as HTML")
async def download_report(
    report_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_AUDIT_REPORTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    report_res = await session.execute(
        text("select report_id, report_name, report_type, generated_at from audit_reports where report_id = :report_id and institution_id = :inst_id"),
        {"report_id": report_id, "inst_id": user_ctx.institution_id},
    )
    report = report_res.mappings().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    html = f"""
    <html><body><h1>{report['report_name']}</h1><p>Type: {report['report_type']}</p><p>Generated: {report['generated_at']}</p></body></html>
    """
    return Response(content=html, media_type="text/html", headers={"Content-Disposition": f"attachment; filename={report['report_name']}.html"})
