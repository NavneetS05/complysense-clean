# Use: Router managing IT security incident command center, timelines, and reporting.
# Covers: CERT-In 6-hour deadline tracking, DPDP notification flags, timeline logging,
# checklist step completion, and incident lifecycle (open → investigating → contained → resolved → closed).


# // ================= Incident Management APIs =================

# // GET /incidents/dashboard-stats
# // - Get dashboard statistics
# // - 5 KPIs
# // - Active incidents
# // - CERT-In chart

# // GET /incidents
# // - Get paginated incident list
# // - Filter by status, severity, type, CERT-In, search, and date

# // POST /incidents
# // - Create a new incident
# // - Auto-calculate CERT-In deadline (detected_at + 6 hours)

# // GET /incidents/{id}
# // - Get incident details
# // - Get incident timeline

# // PATCH /incidents/{id}
# // - Update incident information
# // - Status, CERT-In flag, resolution notes, etc.

# // PUT /incidents/{id}/close
# // - Close an incident
# // - resolution_notes is required

# // DELETE /incidents/{id}
# // - Delete an incident
# // - Allowed only if incident is open and has no extra timeline entries

# // POST /incidents/{id}/timeline
# // - Add a timeline entry

# // GET /incidents/{id}/timeline
# // - Get all timeline entries

# // PATCH /incidents/{id}/checklist
# // - Update CERT-In checklist

# // GET /incidents/{id}/checklist
# // - Get CERT-In checklist status


from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/incidents", tags=["incidents"])


# ─── Pydantic Schemas ────────────────────────────────────────────────────────


class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str
    # data_breach / unauthorized_access / ransomware / phishing / system_failure / ddos / other
    severity: str
    # critical / high / medium / low
    occurred_at: str           # ISO datetime string
    detected_at: str           # ISO datetime string — CERT-In clock starts here
    affected_systems: str | None = None
    affected_data_categories: str | None = None
    dpdp_notification_required: bool = False
    assigned_to: str | None = None   # user_id UUID string


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    incident_type: str | None = None
    severity: str | None = None
    status: str | None = None
    # open / investigating / contained / resolved / closed
    affected_systems: str | None = None
    affected_data_categories: str | None = None
    dpdp_notification_required: bool | None = None
    dpdp_notified_at: str | None = None          # ISO datetime or "now"
    cert_in_reported: bool | None = None
    cert_in_reported_at: str | None = None        # ISO datetime or "now"
    resolved_at: str | None = None
    resolution_notes: str | None = None
    assigned_to: str | None = None


class TimelineEntryCreate(BaseModel):
    action_taken: str


class ChecklistStepUpdate(BaseModel):
    step: int          # 1–8
    checked: bool


# ─── Helper ──────────────────────────────────────────────────────────────────


def _parse_dt(value: str) -> datetime:
    """Parse ISO datetime string; raises ValueError on bad input."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert UUID fields to str and datetime fields to ISO strings."""
    uuid_keys = {
        "incident_id", "institution_id", "reported_by",
        "assigned_to", "assigned_to_id",
    }
    dt_keys = {
        "occurred_at", "detected_at", "cert_in_deadline",
        "cert_in_reported_at", "dpdp_notified_at",
        "resolved_at", "created_at", "updated_at",
    }
    d = dict(row)
    for k in uuid_keys:
        if k in d and d[k] is not None:
            d[k] = str(d[k])
    for k in dt_keys:
        if k in d and d[k] is not None:
            d[k] = d[k].isoformat() if hasattr(d[k], "isoformat") else str(d[k])
    return d


async def _write_audit(
    session: AsyncSession,
    institution_id: str,
    user_id: str,
    role_id: str,
    action_type: str,
    entity_id: str,
    details: dict[str, Any],
) -> None:
    """Insert an audit_logs row. Silently ignored on failure (non-critical side effect)."""
    try:
        await session.execute(
            text(
                """
                insert into audit_logs
                    (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values
                    (:inst_id, :user_id, :role_id, :action_type, 'incident', :entity_id, :details)
                """
            ),
            {
                "inst_id": institution_id,
                "user_id": user_id,
                "role_id": role_id,
                "action_type": action_type,
                "entity_id": entity_id,
                "details": json.dumps(details),
            },
        )
    except Exception:
        pass  # audit logging should never break the main operation


async def _add_timeline(
    session: AsyncSession,
    incident_id: str,
    action_taken: str,
    action_by: str | None,
) -> None:
    """Insert an incident_timeline row."""
    await session.execute(
        text(
            """
            insert into incident_timeline (incident_id, action_taken, action_by)
            values (:incident_id, :action_taken, :action_by)
            """
        ),
        {
            "incident_id": incident_id,
            "action_taken": action_taken,
            "action_by": action_by,
        },
    )


# ─── Security Dashboard Stats ────────────────────────────────────────────────


@router.get(
    "/dashboard-stats",
    summary="KPI stats for IT Security Officer dashboard",
)
async def get_security_dashboard_stats(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """
    Returns:
    - 5 KPI cards: open_incidents, cert_in_pending, critical_open, controls_summary, last_closed
    - Active incidents list (for the card)
    - Critical alert (for the red banner)
    - 90-day CERT-In history for the timeline chart
    """
    inst_id = user_ctx.institution_id

    try:
        # ── KPI: incident counts ──────────────────────────────────────────────
        counts_res = await session.execute(
            text(
                """
                select
                    count(*) filter (where status not in ('resolved', 'closed'))               as open_incidents,
                    count(*) filter (where cert_in_reported = false
                                       and status not in ('resolved', 'closed'))                as cert_in_pending,
                    count(*) filter (where severity = 'critical'
                                       and status not in ('resolved', 'closed'))                as critical_open,
                    max(resolved_at) filter (where status in ('resolved', 'closed'))            as last_resolved_at
                from incidents
                where institution_id = :inst_id
                """
            ),
            {"inst_id": inst_id},
        )
        counts = dict(counts_res.mappings().first() or {})

        # ── KPI: controls summary (assigned to IT Security) ───────────────────
        controls_res = await session.execute(
            text(
                """
                select
                    count(*)                                            as total,
                    count(*) filter (where status = 'compliant')       as compliant,
                    count(*) filter (where status = 'non_compliant')   as failing
                from control_assignments
                where institution_id = :inst_id
                """
            ),
            {"inst_id": inst_id},
        )
        ctrl = dict(controls_res.mappings().first() or {})

        # ── Active incidents list (for sidebar card) ──────────────────────────
        active_res = await session.execute(
            text(
                """
                select i.incident_id, i.title, i.incident_type, i.severity, i.status,
                       i.detected_at, i.cert_in_deadline, i.cert_in_reported, i.cert_in_reported_at,
                       u.full_name as assigned_to_name
                from incidents i
                left join users u on u.user_id = i.assigned_to
                where i.institution_id = :inst_id
                  and i.status not in ('resolved', 'closed')
                order by case i.severity
                    when 'critical' then 0
                    when 'high'     then 1
                    when 'medium'   then 2
                    else 3
                end, i.created_at desc
                limit 10
                """
            ),
            {"inst_id": inst_id},
        )
        active_incidents = [_serialize_row(r) for r in active_res.mappings().all()]

        # ── Critical alert (for the red top banner) ───────────────────────────
        alert_res = await session.execute(
            text(
                """
                select incident_id, title, severity, cert_in_deadline, cert_in_reported
                from incidents
                where institution_id = :inst_id
                  and status not in ('resolved', 'closed')
                  and (
                      severity = 'critical'
                      or (cert_in_reported = false and cert_in_deadline is not null)
                  )
                order by case severity when 'critical' then 0 else 1 end,
                         cert_in_deadline asc nulls last
                limit 1
                """
            ),
            {"inst_id": inst_id},
        )
        alert_row = alert_res.mappings().first()
        critical_alert = None
        if alert_row:
            critical_alert = _serialize_row(dict(alert_row))

        # ── 90-day CERT-In history (for the bar chart) ────────────────────────
        history_res = await session.execute(
            text(
                """
                select
                    date_trunc('week', detected_at)                                           as week_start,
                    count(*)                                                                   as total,
                    count(*) filter (where cert_in_reported = true
                                       and cert_in_reported_at <= cert_in_deadline)           as on_time,
                    count(*) filter (where cert_in_reported = true
                                       and cert_in_reported_at > cert_in_deadline)            as late,
                    count(*) filter (where cert_in_reported = false
                                       and cert_in_deadline < now())                          as not_reported
                from incidents
                where institution_id = :inst_id
                  and detected_at >= now() - interval '90 days'
                group by date_trunc('week', detected_at)
                order by week_start asc
                """
            ),
            {"inst_id": inst_id},
        )
        history = []
        for r in history_res.mappings().all():
            d = dict(r)
            d["week_start"] = d["week_start"].isoformat() if d["week_start"] else None
            history.append(d)

        # ── CERT-In compliance rate ───────────────────────────────────────────
        rate_res = await session.execute(
            text(
                """
                select
                    count(*) filter (where cert_in_reported = true
                                       and cert_in_reported_at <= cert_in_deadline) as on_time,
                    count(*) filter (where cert_in_deadline is not null)             as total_with_deadline
                from incidents
                where institution_id = :inst_id
                  and detected_at >= now() - interval '90 days'
                """
            ),
            {"inst_id": inst_id},
        )
        rate_row = dict(rate_res.mappings().first() or {})
        total_with_deadline = int(rate_row.get("total_with_deadline") or 0)
        on_time = int(rate_row.get("on_time") or 0)
        cert_in_rate = round((on_time / total_with_deadline) * 100, 1) if total_with_deadline else 100.0

        last_resolved = counts.get("last_resolved_at")

        return {
            "kpis": {
                "open_incidents":  int(counts.get("open_incidents") or 0),
                "cert_in_pending": int(counts.get("cert_in_pending") or 0),
                "critical_open":   int(counts.get("critical_open") or 0),
                "controls_total":  int(ctrl.get("total") or 0),
                "controls_compliant": int(ctrl.get("compliant") or 0),
                "controls_failing":   int(ctrl.get("failing") or 0),
                "last_resolved_at": last_resolved.isoformat() if last_resolved else None,
            },
            "active_incidents": active_incidents,
            "critical_alert":   critical_alert,
            "cert_in_history":  history,
            "cert_in_rate":     cert_in_rate,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ─── List Incidents ───────────────────────────────────────────────────────────


@router.get(
    "",
    summary="List all incidents for the institution with filters and status tabs",
)
async def list_incidents(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status: str | None = Query(None),          # open / investigating / contained / resolved / closed
    severity: str | None = Query(None),        # critical / high / medium / low
    incident_type: str | None = Query(None),
    cert_in_filter: str | None = Query(None),  # reported / not_reported / overdue
    search: str | None = Query(None),
    from_date: str | None = Query(None),       # YYYY-MM-DD
    to_date: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:

    base = """
        select
            i.incident_id, i.title, i.incident_type, i.severity, i.status,
            i.occurred_at, i.detected_at, i.cert_in_deadline,
            i.cert_in_reported, i.cert_in_reported_at,
            i.dpdp_notification_required, i.dpdp_notified_at,
            i.resolved_at, i.created_at,
            rep.full_name  as reported_by_name,
            asn.full_name  as assigned_to_name,
            asn.user_id    as assigned_to_id
        from incidents i
        left join users rep on rep.user_id = i.reported_by
        left join users asn on asn.user_id = i.assigned_to
        where i.institution_id = :inst_id
    """
    count_base = """
        select count(*)
        from incidents i
        left join users rep on rep.user_id = i.reported_by
        left join users asn on asn.user_id = i.assigned_to
        where i.institution_id = :inst_id
    """
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id}
    where = ""

    if status and status != "All":
        where += " and i.status = :status"
        params["status"] = status

    if severity and severity != "All":
        where += " and i.severity = :severity"
        params["severity"] = severity

    if incident_type and incident_type != "All":
        where += " and i.incident_type = :incident_type"
        params["incident_type"] = incident_type

    if cert_in_filter == "reported":
        where += " and i.cert_in_reported = true"
    elif cert_in_filter == "not_reported":
        where += " and i.cert_in_reported = false and i.cert_in_deadline is not null"
    elif cert_in_filter == "overdue":
        where += " and i.cert_in_reported = false and i.cert_in_deadline < now()"

    if search:
        where += " and (lower(i.title) like lower(:search) or lower(i.description) like lower(:search))"
        params["search"] = f"%{search}%"

    if from_date:
        where += " and i.detected_at >= :from_date"
        params["from_date"] = f"{from_date} 00:00:00"

    if to_date:
        where += " and i.detected_at <= :to_date"
        params["to_date"] = f"{to_date} 23:59:59"

    # Status tab counts
    try:
        tab_res = await session.execute(
            text(
                f"""
                select status, count(*) as cnt
                from incidents i
                where i.institution_id = :inst_id
                group by status
                """
            ),
            {"inst_id": user_ctx.institution_id},
        )
        tab_counts: dict[str, int] = {r["status"]: int(r["cnt"]) for r in tab_res.mappings().all()}
        tab_counts["all"] = sum(tab_counts.values())
    except Exception:
        tab_counts = {}

    # Total count for pagination
    count_res = await session.execute(text(f"{count_base}{where}"), params)
    total = count_res.scalar() or 0

    # Paginated results
    offset = (page - 1) * limit
    params["limit"] = limit
    params["offset"] = offset
    order = """
        order by
            case i.severity when 'critical' then 0 when 'high' then 1 when 'medium' then 2 else 3 end,
            i.created_at desc
        limit :limit offset :offset
    """

    try:
        res = await session.execute(text(f"{base}{where}{order}"), params)
        incidents = [_serialize_row(r) for r in res.mappings().all()]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "incidents": incidents,
        "total": total,
        "page": page,
        "limit": limit,
        "tab_counts": tab_counts,
    }


# ─── Create Incident ──────────────────────────────────────────────────────────


@router.post(
    "",
    summary="Log a new IT security incident (starts CERT-In 6-hour clock)",
    status_code=201,
)
async def create_incident(
    payload: IncidentCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    try:
        occurred_dt = _parse_dt(payload.occurred_at)
        detected_dt = _parse_dt(payload.detected_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {exc}")

    # CERT-In deadline = detected_at + 6 hours (mandatory by CERT-In 2022 Directions)
    cert_in_deadline = detected_dt + timedelta(hours=6)

    query = """
        insert into incidents (
            institution_id, title, description, incident_type, severity,
            status, occurred_at, detected_at, cert_in_deadline,
            cert_in_reported, dpdp_notification_required,
            affected_systems, affected_data_categories,
            reported_by, assigned_to
        ) values (
            :inst_id, :title, :description, :incident_type, :severity,
            'open', :occurred_at, :detected_at, :cert_in_deadline,
            false, :dpdp_required,
            :affected_systems, :affected_data_categories,
            :reported_by, :assigned_to
        )
        returning incident_id, title, severity, status, cert_in_deadline, created_at
    """

    try:
        res = await session.execute(
            text(query),
            {
                "inst_id":                 user_ctx.institution_id,
                "title":                   payload.title,
                "description":             payload.description,
                "incident_type":           payload.incident_type,
                "severity":                payload.severity,
                "occurred_at":             occurred_dt,
                "detected_at":             detected_dt,
                "cert_in_deadline":        cert_in_deadline,
                "dpdp_required":           payload.dpdp_notification_required,
                "affected_systems":        payload.affected_systems,
                "affected_data_categories": payload.affected_data_categories,
                "reported_by":             user_ctx.user_id,
                "assigned_to":             payload.assigned_to or user_ctx.user_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create incident")

        incident_id = str(row["incident_id"])

        # First timeline entry
        await _add_timeline(
            session,
            incident_id,
            f"Incident logged by {user_ctx.user_id}. CERT-In deadline set: {cert_in_deadline.isoformat()}",
            user_ctx.user_id,
        )

        # Audit log
        await _write_audit(
            session, user_ctx.institution_id, user_ctx.user_id,
            user_ctx.active_role_id, "incident_created", incident_id,
            {"severity": payload.severity, "incident_type": payload.incident_type},
        )

        await session.commit()

        d = _serialize_row(dict(row))
        d["cert_in_deadline"] = cert_in_deadline.isoformat()
        return d

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Get Single Incident ──────────────────────────────────────────────────────


@router.get(
    "/{incident_id}",
    summary="Get full incident detail — command center data",
)
async def get_incident(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    res = await session.execute(
        text(
            """
            select
                i.*,
                rep.full_name  as reported_by_name,
                rep.email      as reported_by_email,
                asn.full_name  as assigned_to_name,
                asn.email      as assigned_to_email,
                asn.user_id    as assigned_to_id
            from incidents i
            left join users rep on rep.user_id = i.reported_by
            left join users asn on asn.user_id = i.assigned_to
            where i.incident_id = :id
              and i.institution_id = :inst_id
            """
        ),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = _serialize_row(dict(row))

    # Timeline (newest first)
    tl_res = await session.execute(
        text(
            """
            select t.timeline_id, t.action_taken, t.action_at, u.full_name as action_by_name
            from incident_timeline t
            left join users u on u.user_id = t.action_by
            where t.incident_id = :id
            order by t.action_at desc
            """
        ),
        {"id": incident_id},
    )
    timeline = []
    for r in tl_res.mappings().all():
        d = dict(r)
        d["timeline_id"] = str(d["timeline_id"])
        d["action_at"] = d["action_at"].isoformat() if d["action_at"] else None
        timeline.append(d)

    incident["timeline"] = timeline
    return incident


# ─── Update Incident ──────────────────────────────────────────────────────────


@router.patch(
    "/{incident_id}",
    summary="Update incident fields (status, severity, CERT-In flag, resolution notes, etc.)",
)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    # Fetch current state for comparison (needed for timeline entries on status change)
    cur_res = await session.execute(
        text("select status, cert_in_reported from incidents where incident_id = :id and institution_id = :inst_id"),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    current = cur_res.mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_fields: list[str] = []
    params: dict[str, Any] = {"id": incident_id, "inst_id": user_ctx.institution_id}
    data = payload.model_dump(exclude_unset=True)

    # Parse datetime strings where needed
    dt_fields = {"occurred_at", "detected_at", "resolved_at", "dpdp_notified_at", "cert_in_reported_at"}
    for field, val in data.items():
        if field in dt_fields and val is not None:
            if val == "now":
                val = datetime.now(timezone.utc).isoformat()
            try:
                val = _parse_dt(val)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid datetime for {field}: {exc}")
        update_fields.append(f"{field} = :{field}")
        params[field] = val

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_str = ", ".join(update_fields)
    query = f"""
        update incidents
           set {update_str}, updated_at = now()
         where incident_id = :id
           and institution_id = :inst_id
        returning incident_id, title, status, severity, cert_in_reported
    """

    try:
        res = await session.execute(text(query), params)
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="Incident not found")

        # Auto-timeline on status change
        new_status = data.get("status")
        if new_status and new_status != current["status"]:
            await _add_timeline(
                session,
                incident_id,
                f"Status changed from '{current['status']}' to '{new_status}'",
                user_ctx.user_id,
            )

        # Auto-timeline on CERT-In reported
        if data.get("cert_in_reported") is True and not current["cert_in_reported"]:
            await _add_timeline(
                session,
                incident_id,
                "CERT-In report marked as submitted to the CERT-In portal",
                user_ctx.user_id,
            )

        # Audit
        await _write_audit(
            session, user_ctx.institution_id, user_ctx.user_id,
            user_ctx.active_role_id, "incident_updated", incident_id,
            {k: str(v) for k, v in data.items()},
        )

        await session.commit()
        return _serialize_row(dict(row))

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Close Incident ───────────────────────────────────────────────────────────


@router.put(
    "/{incident_id}/close",
    summary="Close a resolved incident (requires resolution_notes to be filled)",
)
async def close_incident(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    # Verify incident exists and has resolution notes
    check = await session.execute(
        text(
            """
            select incident_id, status, resolution_notes
            from incidents
            where incident_id = :id and institution_id = :inst_id
            """
        ),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    row = check.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not row["resolution_notes"]:
        raise HTTPException(
            status_code=400,
            detail="Resolution notes are required before closing an incident",
        )

    try:
        res = await session.execute(
            text(
                """
                update incidents
                   set status = 'closed', updated_at = now()
                 where incident_id = :id and institution_id = :inst_id
                returning incident_id, status
                """
            ),
            {"id": incident_id, "inst_id": user_ctx.institution_id},
        )
        updated = res.mappings().first()
        if not updated:
            await session.rollback()
            raise HTTPException(status_code=404, detail="Incident not found")

        await _add_timeline(
            session, incident_id,
            "Incident closed and archived",
            user_ctx.user_id,
        )
        await _write_audit(
            session, user_ctx.institution_id, user_ctx.user_id,
            user_ctx.active_role_id, "incident_closed", incident_id, {},
        )
        await session.commit()
        return {"incident_id": str(updated["incident_id"]), "status": updated["status"]}

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Delete Incident ──────────────────────────────────────────────────────────


@router.delete(
    "/{incident_id}",
    summary="Delete an incident (only allowed if status=open and no timeline entries)",
)
async def delete_incident(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    # Guard: only open incidents with no manual timeline entries can be deleted
    check = await session.execute(
        text(
            """
            select i.incident_id, i.status,
                   (select count(*) from incident_timeline t where t.incident_id = i.incident_id) as timeline_count
            from incidents i
            where i.incident_id = :id and i.institution_id = :inst_id
            """
        ),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    row = check.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    if row["status"] != "open":
        raise HTTPException(status_code=400, detail="Only open incidents can be deleted")
    if int(row["timeline_count"] or 0) > 1:
        # Allow 1 entry (the auto-created one on logging); block if user added more
        raise HTTPException(
            status_code=400,
            detail="Incidents with timeline entries cannot be deleted",
        )

    try:
        await session.execute(
            text("delete from incident_timeline where incident_id = :id"),
            {"id": incident_id},
        )
        await session.execute(
            text("delete from incidents where incident_id = :id and institution_id = :inst_id"),
            {"id": incident_id, "inst_id": user_ctx.institution_id},
        )
        await _write_audit(
            session, user_ctx.institution_id, user_ctx.user_id,
            user_ctx.active_role_id, "incident_deleted", incident_id, {},
        )
        await session.commit()
        return {"incident_id": incident_id, "deleted": True}

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Timeline Endpoints ───────────────────────────────────────────────────────


@router.post(
    "/{incident_id}/timeline",
    summary="Add a manual timeline entry to an incident",
    status_code=201,
)
async def add_timeline_entry(
    incident_id: str,
    payload: TimelineEntryCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    # Verify incident belongs to institution
    check = await session.execute(
        text("select incident_id from incidents where incident_id = :id and institution_id = :inst_id"),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="Incident not found")

    try:
        res = await session.execute(
            text(
                """
                insert into incident_timeline (incident_id, action_taken, action_by)
                values (:incident_id, :action_taken, :action_by)
                returning timeline_id, action_taken, action_at
                """
            ),
            {
                "incident_id": incident_id,
                "action_taken": payload.action_taken,
                "action_by": user_ctx.user_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to add timeline entry")

        await session.commit()
        d = dict(row)
        d["timeline_id"] = str(d["timeline_id"])
        d["action_at"] = d["action_at"].isoformat() if d["action_at"] else None
        return d

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/{incident_id}/timeline",
    summary="Get full timeline for an incident (newest first)",
)
async def get_timeline(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:

    # Verify incident belongs to institution
    check = await session.execute(
        text("select incident_id from incidents where incident_id = :id and institution_id = :inst_id"),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="Incident not found")

    res = await session.execute(
        text(
            """
            select t.timeline_id, t.action_taken, t.action_at,
                   u.full_name as action_by_name, u.user_id as action_by_id
            from incident_timeline t
            left join users u on u.user_id = t.action_by
            where t.incident_id = :id
            order by t.action_at desc
            """
        ),
        {"id": incident_id},
    )
    result = []
    for r in res.mappings().all():
        d = dict(r)
        d["timeline_id"] = str(d["timeline_id"])
        d["action_by_id"] = str(d["action_by_id"]) if d["action_by_id"] else None
        d["action_at"] = d["action_at"].isoformat() if d["action_at"] else None
        result.append(d)
    return result


# ─── CERT-In Checklist ────────────────────────────────────────────────────────


# The 8 official CERT-In 2022 mandatory response steps
CERT_IN_STEPS = {
    1: "Contain the incident (isolate affected systems)",
    2: "Document initial findings",
    3: "Notify internal stakeholders",
    4: "Preserve evidence (logs, screenshots)",
    5: "Identify affected data categories",
    6: "Draft CERT-In report",
    7: "Submit report to CERT-In portal",
    8: "Update incident status",
}


@router.patch(
    "/{incident_id}/checklist",
    summary="Mark a CERT-In checklist step as completed or uncompleted",
)
async def update_checklist_step(
    incident_id: str,
    payload: ChecklistStepUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:

    if payload.step not in CERT_IN_STEPS:
        raise HTTPException(status_code=400, detail=f"Step must be between 1 and {len(CERT_IN_STEPS)}")

    # Verify incident exists
    check = await session.execute(
        text("select incident_id from incidents where incident_id = :id and institution_id = :inst_id"),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="Incident not found")

    step_desc = CERT_IN_STEPS[payload.step]
    action = "completed" if payload.checked else "unchecked"
    timeline_entry = f"Checklist step {payload.step} {action}: {step_desc}"

    try:
        await _add_timeline(session, incident_id, timeline_entry, user_ctx.user_id)
        await session.commit()
        return {
            "incident_id": incident_id,
            "step": payload.step,
            "checked": payload.checked,
            "description": step_desc,
        }
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/{incident_id}/checklist",
    summary="Get CERT-In checklist state derived from timeline entries",
)
async def get_checklist(
    incident_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_INCIDENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """
    Derives checklist state from timeline entries.
    A step is 'checked' if the most recent timeline entry for that step says 'completed',
    and 'unchecked' if the most recent says 'unchecked'.
    """
    check = await session.execute(
        text("select incident_id from incidents where incident_id = :id and institution_id = :inst_id"),
        {"id": incident_id, "inst_id": user_ctx.institution_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="Incident not found")

    tl_res = await session.execute(
        text(
            """
            select action_taken, action_at
            from incident_timeline
            where incident_id = :id
              and action_taken like 'Checklist step %'
            order by action_at asc
            """
        ),
        {"id": incident_id},
    )

    # Replay timeline to get current state of each step
    step_states: dict[int, bool] = {i: False for i in range(1, len(CERT_IN_STEPS) + 1)}
    for r in tl_res.mappings().all():
        text_val: str = r["action_taken"]
        # Format: "Checklist step N completed: ..." or "Checklist step N unchecked: ..."
        try:
            parts = text_val.split()
            step_num = int(parts[2])
            action_word = parts[3]
            if step_num in step_states:
                step_states[step_num] = (action_word == "completed")
        except (IndexError, ValueError):
            continue

    steps = [
        {
            "step": step,
            "description": desc,
            "checked": step_states.get(step, False),
        }
        for step, desc in CERT_IN_STEPS.items()
    ]
    completed = sum(1 for s in steps if s["checked"])

    return {
        "incident_id": incident_id,
        "steps": steps,
        "completed": completed,
        "total": len(CERT_IN_STEPS),
    }