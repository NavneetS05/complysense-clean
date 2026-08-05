# Use: Router managing control assignments and their operational status.
# Phase 2: list_controls and get_control_detail now merge MongoDB control definitions
#           (control_title, description, evidence_requirements) from ControlLibraryStore
#           into the existing Postgres assignment payload.
#           All existing response fields are preserved — this is purely additive.

from __future__ import annotations

import asyncio
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.mongodb import get_mongo_database
from app.repositories.audit import AuditLogRepository
from app.repositories.notification import NotificationRepository
from app.schemas.auth import UserContext
from app.storage.control_library import ControlLibraryStore

router = APIRouter(prefix="/controls", tags=["controls"])


class ControlStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NA = "na"


class CreateControlAssignmentPayload(BaseModel):
    control_id: str
    framework_name: str
    assigned_to: str | None = None
    department_id: str | None = None
    due_date: str | None = None
    notes: str | None = None
    status: ControlStatus = ControlStatus.NOT_STARTED


class UpdateControlStatusPayload(BaseModel):
    status: ControlStatus


class UpdateControlNotesPayload(BaseModel):
    note: str


# ── Private helper ─────────────────────────────────────────────────────────────

async def _fetch_mongo_def(store: ControlLibraryStore, control_id: str) -> dict[str, Any]:
    """
    Best-effort lookup of a control definition in MongoDB.
    Returns an empty dict if Mongo is unavailable or the control_id is not found.
    Keyed by ``control_id`` field on the MongoDB document (not the Mongo _id).
    """
    try:
        doc = await store.find_by_control_id(control_id)
        return doc or {}
    except Exception as exc:
        logger.warning("mongodb.control_lookup_failed", control_id=control_id, error=str(exc))
        return {}


def _merge_mongo_fields(pg_row: dict[str, Any], mongo_doc: dict[str, Any]) -> dict[str, Any]:
    """
    Merges additive MongoDB fields into a Postgres-derived row dict.
    Existing PG keys are never overwritten.
    Fields added:
        control_title       – human-readable name from the control library
        description         – full regulatory description / requirement text
        evidence_requirements – list of evidence types required (if present)
    """
    pg_row["control_title"] = mongo_doc.get("control_title") or mongo_doc.get("title") or None
    pg_row["description"] = mongo_doc.get("description") or None
    pg_row["evidence_requirements"] = mongo_doc.get("evidence_requirements") or []
    return pg_row


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("", summary="List control assignments for the current institution")
async def list_controls(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select
            ca.assignment_id,
            ca.control_id,
            ca.framework_name,
            ca.status,
            ca.due_date,
            ca.assigned_to,
            d.department_name,
            u.full_name as assigned_name
        from control_assignments ca
        left join departments d on d.department_id = ca.department_id
        left join users u on u.user_id = ca.assigned_to
        where ca.institution_id = :inst_id
        order by ca.due_date asc nulls last, ca.created_at desc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()

    pg_items: list[dict[str, Any]] = [
        {
            "assignment_id": str(row["assignment_id"]),
            "control_id": row["control_id"],
            "framework_name": row["framework_name"],
            "status": row["status"],
            "due_date": row["due_date"].isoformat() if row["due_date"] else None,
            "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
            "department_name": row["department_name"],
            "assigned_name": row["assigned_name"],
        }
        for row in rows
    ]

    if not pg_items:
        return pg_items

    # Batch-fetch MongoDB control definitions concurrently (best-effort).
    store = ControlLibraryStore(get_mongo_database())
    distinct_control_ids = list({item["control_id"] for item in pg_items})
    mongo_docs_list = await asyncio.gather(
        *[_fetch_mongo_def(store, cid) for cid in distinct_control_ids],
        return_exceptions=False,
    )
    # Build lookup map: control_id -> mongo doc
    mongo_map: dict[str, dict[str, Any]] = {
        cid: doc
        for cid, doc in zip(distinct_control_ids, mongo_docs_list)
    }

    return [
        _merge_mongo_fields(item, mongo_map.get(item["control_id"], {}))
        for item in pg_items
    ]


@router.post("", status_code=201, summary="Create a new control assignment")
async def create_control_assignment(
    payload: CreateControlAssignmentPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        insert into control_assignments (
            institution_id, control_id, framework_name, assigned_to, department_id, status, due_date, notes, assigned_by
        ) values (
            :inst_id, :control_id, :framework_name, :assigned_to, :department_id, :status, :due_date, :notes, :assigned_by
        ) returning assignment_id, control_id, framework_name, status, due_date, assigned_to, department_id, notes
    """
    due_date = payload.due_date if payload.due_date else None
    res = await session.execute(
        text(query),
        {
            "inst_id": user_ctx.institution_id,
            "control_id": payload.control_id,
            "framework_name": payload.framework_name,
            "assigned_to": payload.assigned_to,
            "department_id": payload.department_id,
            "status": payload.status,
            "due_date": due_date,
            "notes": payload.notes,
            "assigned_by": user_ctx.user_id,
        },
    )
    row = res.mappings().first()
    if row:
        await AuditLogRepository(session).write(
            institution_id=user_ctx.institution_id,
            user_id=user_ctx.user_id,
            active_role_id=user_ctx.active_role_id,
            action_type="control_created",
            entity_type="control_assignment",
            entity_id=str(row["assignment_id"]),
            action_details={"control_id": payload.control_id},
        )
        if payload.assigned_to:
            await NotificationRepository(session).create(
                institution_id=str(user_ctx.institution_id),
                user_id=str(payload.assigned_to),
                title="New control assignment",
                message=f"You have been assigned a new control: {payload.control_id}",
                notification_type="control_assigned",
                related_entity_type="control_assignment",
                related_entity_id=str(row["assignment_id"]),
            )
    await session.commit()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create control assignment")
    return {
        "assignment_id": str(row["assignment_id"]),
        "control_id": row["control_id"],
        "framework_name": row["framework_name"],
        "status": row["status"],
        "due_date": row["due_date"].isoformat() if row["due_date"] else None,
        "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
        "department_id": str(row["department_id"]) if row["department_id"] else None,
        "notes": row["notes"],
    }


@router.get("/{assignment_id}", summary="Get a single control assignment")
async def get_control_detail(
    assignment_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select
            ca.assignment_id,
            ca.control_id,
            ca.framework_name,
            ca.status,
            ca.due_date,
            ca.notes,
            ca.assigned_to,
            ca.assigned_by,
            d.department_name,
            u.full_name as assigned_name,
            ab.full_name as assigned_by_name
        from control_assignments ca
        left join departments d on d.department_id = ca.department_id
        left join users u on u.user_id = ca.assigned_to
        left join users ab on ab.user_id = ca.assigned_by
        where ca.assignment_id = :assignment_id
          and ca.institution_id = :inst_id
    """
    res = await session.execute(text(query), {"assignment_id": assignment_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Control assignment not found")

    pg_response: dict[str, Any] = {
        "assignment_id": str(row["assignment_id"]),
        "control_id": row["control_id"],
        "framework_name": row["framework_name"],
        "status": row["status"],
        "due_date": row["due_date"].isoformat() if row["due_date"] else None,
        "notes": row["notes"],
        "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
        "assigned_by": str(row["assigned_by"]) if row["assigned_by"] else None,
        "department_name": row["department_name"],
        "assigned_name": row["assigned_name"],
        "assigned_by_name": row["assigned_by_name"],
    }

    # Merge MongoDB control definition (best-effort — degraded gracefully if Mongo is down).
    store = ControlLibraryStore(get_mongo_database())
    mongo_doc = await _fetch_mongo_def(store, row["control_id"])
    return _merge_mongo_fields(pg_response, mongo_doc)


@router.patch("/{assignment_id}/status", summary="Update control assignment status")
async def update_control_status(
    assignment_id: str,
    payload: UpdateControlStatusPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        update control_assignments
        set status = :status, updated_at = now()
        where assignment_id = :assignment_id and institution_id = :inst_id
        returning assignment_id, status
    """
    res = await session.execute(text(query), {"assignment_id": assignment_id, "inst_id": user_ctx.institution_id, "status": payload.status})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Control assignment not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="control_status_updated",
        entity_type="control_assignment",
        entity_id=assignment_id,
        action_details={"status": payload.status},
    )
    await session.commit()
    return {"assignment_id": str(row["assignment_id"]), "status": row["status"]}


@router.patch("/{assignment_id}/notes", summary="Append a note to a control assignment")
async def update_control_notes(
    assignment_id: str,
    payload: UpdateControlNotesPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_CONTROLS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    note_text = f"[{timestamp}] {payload.note}"
    query = """
        update control_assignments
        set notes = coalesce(notes, '') || '\n' || :note_text,
            updated_at = now()
        where assignment_id = :assignment_id and institution_id = :inst_id
        returning assignment_id, notes
    """
    res = await session.execute(text(query), {"assignment_id": assignment_id, "inst_id": user_ctx.institution_id, "note_text": note_text})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Control assignment not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="control_note_added",
        entity_type="control_assignment",
        entity_id=assignment_id,
    )
    await session.commit()
    return {"assignment_id": str(row["assignment_id"]), "notes": row["notes"]}
