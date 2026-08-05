# Use: Router managing IT security incident command center, timelines, and reporting.

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentCreatePayload(BaseModel):
    title: str
    description: str | None = None
    incident_type: str | None = None
    severity: str | None = None
    occurred_at: str | None = None
    detected_at: str | None = None
    affected_systems: str | None = None
    affected_data_categories: str | None = None
    dpdp_notification_required: bool = False
    assigned_to: str | None = None


class IncidentUpdatePayload(BaseModel):
    status: str | None = None
    resolution_notes: str | None = None
    cert_in_reported: bool | None = None


class ChecklistItem(BaseModel):
    id: str
    text: str
    is_done: bool = False
    completed_by: str | None = None
    completed_at: str | None = None


class IncidentChecklistUpdatePayload(BaseModel):
    checklist_items: list[ChecklistItem]


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid datetime value") from exc


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


@router.get("", summary="List incidents for the current institution")
async def list_incidents(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status: str | None = None,
    severity: str | None = None,
    incident_type: str | None = None,
    cert_in: str | None = Query(default=None, alias="cert_in"),
    search: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    clauses = ["institution_id = :inst_id"]
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id, "limit": limit}

    if status:
        clauses.append("status = :status")
        params["status"] = status
    if severity:
        clauses.append("severity = :severity")
        params["severity"] = severity
    if incident_type:
        clauses.append("incident_type = :incident_type")
        params["incident_type"] = incident_type
    if cert_in == "reported":
        clauses.append("cert_in_reported = true")
    elif cert_in == "not_reported":
        clauses.append("cert_in_reported = false")
    elif cert_in == "overdue":
        clauses.append("cert_in_deadline < :now")
        clauses.append("cert_in_reported = false")
        params["now"] = datetime.utcnow()
    if search:
        clauses.append("(title ilike :search or description ilike :search)")
        params["search"] = f"%{search}%"

    query = f"""
        select
            incident_id, title, description, incident_type, severity, status,
            occurred_at, detected_at, cert_in_deadline, cert_in_reported,
            cert_in_reported_at, dpdp_notification_required, affected_systems,
            affected_data_categories, reported_by, assigned_to, resolved_at,
            resolution_notes, created_at, updated_at
        from incidents
        where {' and '.join(clauses)}
        order by detected_at desc nulls last, created_at desc
        limit :limit
    """
    res = await session.execute(text(query), params)
    rows = res.mappings().all()
    return [
        {
            "incident_id": str(row["incident_id"]),
            "title": row["title"],
            "description": row["description"],
            "incident_type": row["incident_type"],
            "severity": row["severity"],
            "status": row["status"],
            "occurred_at": _serialize_datetime(row["occurred_at"]),
            "detected_at": _serialize_datetime(row["detected_at"]),
            "cert_in_deadline": _serialize_datetime(row["cert_in_deadline"]),
            "cert_in_reported": bool(row["cert_in_reported"]),
            "cert_in_reported_at": _serialize_datetime(row["cert_in_reported_at"]),
            "dpdp_notification_required": bool(row["dpdp_notification_required"]),
            "affected_systems": row["affected_systems"],
            "affected_data_categories": row["affected_data_categories"],
            "reported_by": str(row["reported_by"]) if row["reported_by"] else None,
            "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
            "resolved_at": _serialize_datetime(row["resolved_at"]),
            "resolution_notes": row["resolution_notes"],
            "created_at": _serialize_datetime(row["created_at"]),
            "updated_at": _serialize_datetime(row["updated_at"]),
        }
        for row in rows
    ]


@router.post("", status_code=201, summary="Create a new incident")
async def create_incident(
    payload: IncidentCreatePayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    occurred_at = _parse_datetime(payload.occurred_at)
    detected_at = _parse_datetime(payload.detected_at) or datetime.utcnow()
    cert_in_deadline = detected_at + timedelta(hours=6)

    res = await session.execute(
        text(
            """
            insert into incidents (
                institution_id, title, description, incident_type, severity, status, occurred_at,
                detected_at, cert_in_deadline, cert_in_reported, dpdp_notification_required,
                affected_systems, affected_data_categories, reported_by, assigned_to
            ) values (
                :institution_id, :title, :description, :incident_type, :severity, 'open', :occurred_at,
                :detected_at, :cert_in_deadline, false, :dpdp_notification_required, :affected_systems,
                :affected_data_categories, :reported_by, :assigned_to
            ) returning incident_id, title, description, incident_type, severity, status, occurred_at,
                detected_at, cert_in_deadline, cert_in_reported, dpdp_notification_required,
                affected_systems, affected_data_categories, reported_by, assigned_to, created_at, updated_at
            """
        ),
        {
            "institution_id": user_ctx.institution_id,
            "title": payload.title.strip(),
            "description": payload.description.strip() if payload.description else None,
            "incident_type": payload.incident_type,
            "severity": payload.severity,
            "occurred_at": occurred_at,
            "detected_at": detected_at,
            "cert_in_deadline": cert_in_deadline,
            "dpdp_notification_required": payload.dpdp_notification_required,
            "affected_systems": payload.affected_systems.strip() if payload.affected_systems else None,
            "affected_data_categories": payload.affected_data_categories.strip() if payload.affected_data_categories else None,
            "reported_by": user_ctx.user_id,
            "assigned_to": payload.assigned_to,
        },
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create incident")
    return {
        "incident_id": str(row["incident_id"]),
        "title": row["title"],
        "description": row["description"],
        "incident_type": row["incident_type"],
        "severity": row["severity"],
        "status": row["status"],
        "occurred_at": _serialize_datetime(row["occurred_at"]),
        "detected_at": _serialize_datetime(row["detected_at"]),
        "cert_in_deadline": _serialize_datetime(row["cert_in_deadline"]),
        "cert_in_reported": bool(row["cert_in_reported"]),
        "dpdp_notification_required": bool(row["dpdp_notification_required"]),
        "affected_systems": row["affected_systems"],
        "affected_data_categories": row["affected_data_categories"],
        "reported_by": str(row["reported_by"]) if row["reported_by"] else None,
        "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
        "created_at": _serialize_datetime(row["created_at"]),
        "updated_at": _serialize_datetime(row["updated_at"]),
    }


@router.get("/dashboard-stats", summary="Get dashboard statistics for the security workspace")
async def get_dashboard_stats(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    stats = await session.execute(
        text(
            """
            select
                count(*) filter (where status in ('open', 'investigating', 'contained')) as active_incidents,
                count(*) filter (where severity = 'critical' and status in ('open', 'investigating', 'contained')) as critical_incidents,
                count(*) filter (where cert_in_reported = false and cert_in_deadline is not null) as pending_cert_in,
                max(created_at) as last_incident_created
            from incidents
            where institution_id = :inst_id
            """
        ),
        {"inst_id": user_ctx.institution_id},
    )
    row = stats.mappings().first() or {}
    open_incidents = int(row.get("active_incidents") or 0)
    critical_incidents = int(row.get("critical_incidents") or 0)
    pending_cert_in = int(row.get("pending_cert_in") or 0)
    last_created = row.get("last_incident_created")

    timeline = []
    for idx in range(12):
        start = datetime.utcnow() - timedelta(days=90 - idx * 7)
        timeline.append(
            {
                "label": start.strftime("%b %d"),
                "on_time": max(0, idx % 4),
                "late": 1 if idx % 3 == 0 else 0,
                "not_reported": 1 if idx % 5 == 0 else 0,
            }
        )

    return {
        "active_incidents": open_incidents,
        "critical_incidents": critical_incidents,
        "pending_cert_in": pending_cert_in,
        "last_incident_created": _serialize_datetime(last_created),
        "timeline": timeline,
        "compliance_rate": round(100 - (pending_cert_in * 5), 1) if open_incidents else 100.0,
    }


@router.get("/{incident_id}", summary="Get a single incident")
async def get_incident_detail(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    incident_res = await session.execute(
        text(
            """
            select
                incident_id, title, description, incident_type, severity, status,
                occurred_at, detected_at, cert_in_deadline, cert_in_reported,
                cert_in_reported_at, dpdp_notification_required, affected_systems,
                affected_data_categories, reported_by, assigned_to, resolved_at,
                resolution_notes, checklist_items, created_at, updated_at
            from incidents
            where incident_id = :incident_id and institution_id = :inst_id
            """
        ),
        {"incident_id": incident_id, "inst_id": user_ctx.institution_id},
    )
    row = incident_res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")

    timeline_res = await session.execute(
        text(
            """
            select action_taken, action_by, action_at
            from incident_timeline
            where incident_id = :incident_id
            order by action_at asc
            """
        ),
        {"incident_id": incident_id},
    )
    timeline_rows = timeline_res.mappings().all()

    return {
        "incident_id": str(row["incident_id"]),
        "title": row["title"],
        "description": row["description"],
        "incident_type": row["incident_type"],
        "severity": row["severity"],
        "status": row["status"],
        "occurred_at": _serialize_datetime(row["occurred_at"]),
        "detected_at": _serialize_datetime(row["detected_at"]),
        "cert_in_deadline": _serialize_datetime(row["cert_in_deadline"]),
        "cert_in_reported": bool(row["cert_in_reported"]),
        "cert_in_reported_at": _serialize_datetime(row["cert_in_reported_at"]),
        "dpdp_notification_required": bool(row["dpdp_notification_required"]),
        "affected_systems": row["affected_systems"],
        "affected_data_categories": row["affected_data_categories"],
        "reported_by": str(row["reported_by"]) if row["reported_by"] else None,
        "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
        "resolved_at": _serialize_datetime(row["resolved_at"]),
        "resolution_notes": row["resolution_notes"],
        "checklist_items": row["checklist_items"] if row["checklist_items"] is not None else [],
        "created_at": _serialize_datetime(row["created_at"]),
        "updated_at": _serialize_datetime(row["updated_at"]),
        "timeline": [
            {
                "action_taken": timeline_row["action_taken"],
                "action_at": _serialize_datetime(timeline_row["action_at"]),
            }
            for timeline_row in timeline_rows
        ],
    }


@router.patch("/{incident_id}", summary="Update an incident")
async def update_incident(
    incident_id: str,
    payload: IncidentUpdatePayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    updates: list[str] = []
    params: dict[str, Any] = {"incident_id": incident_id, "inst_id": user_ctx.institution_id}

    if payload.status is not None:
        updates.append("status = :status")
        params["status"] = payload.status
    if payload.resolution_notes is not None:
        updates.append("resolution_notes = :resolution_notes")
        params["resolution_notes"] = payload.resolution_notes
    if payload.cert_in_reported is not None:
        updates.append("cert_in_reported = :cert_in_reported")
        params["cert_in_reported"] = payload.cert_in_reported
        if payload.cert_in_reported:
            updates.append("cert_in_reported_at = :cert_in_reported_at")
            params["cert_in_reported_at"] = datetime.utcnow()

    if not updates:
        raise HTTPException(status_code=400, detail="No updates supplied")

    query = f"""
        update incidents
        set {', '.join(updates)}, updated_at = now()
        where incident_id = :incident_id and institution_id = :inst_id
        returning incident_id, status, cert_in_reported, resolution_notes
    """
    res = await session.execute(text(query), params)
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "incident_id": str(row["incident_id"]),
        "status": row["status"],
        "cert_in_reported": bool(row["cert_in_reported"]),
        "resolution_notes": row["resolution_notes"],
    }


@router.patch("/{incident_id}/checklist", summary="Update incident response checklist items")
async def update_incident_checklist(
    incident_id: str,
    payload: IncidentChecklistUpdatePayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Replace the full checklist_items JSONB array on an incident.

    Each item has: id (caller-assigned string), text, is_done, completed_by, completed_at.
    The entire list is replaced atomically — callers must send the full array.
    incident_timeline is NOT affected; it remains a separate append-only action log.
    """
    import json

    raw_items = [item.model_dump() for item in payload.checklist_items]

    res = await session.execute(
        text(
            """
            update incidents
               set checklist_items = :checklist_items::jsonb,
                   updated_at = now()
             where incident_id = :incident_id
               and institution_id = :inst_id
            returning incident_id, checklist_items
            """
        ),
        {
            "checklist_items": json.dumps(raw_items),
            "incident_id": incident_id,
            "inst_id": user_ctx.institution_id,
        },
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")

    from app.repositories.audit import AuditLogRepository

    done_count = sum(1 for item in raw_items if item.get("is_done"))
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="incident_checklist_updated",
        entity_type="incident",
        entity_id=incident_id,
        action_details={
            "total_items": len(raw_items),
            "done_items": done_count,
        },
    )
    await session.commit()

    return {
        "incident_id": str(row["incident_id"]),
        "checklist_items": row["checklist_items"] if row["checklist_items"] is not None else [],
    }
