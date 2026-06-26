# Use: Router managing control assignments and their operational status.

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/controls", tags=["controls"])


class CreateControlAssignmentPayload(BaseModel):
    control_id: str
    framework_name: str
    assigned_to: str | None = None
    department_id: str | None = None
    due_date: str | None = None
    notes: str | None = None
    status: str = "not_started"


class UpdateControlStatusPayload(BaseModel):
    status: str


class UpdateControlNotesPayload(BaseModel):
    note: str


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
    return [
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
    return {
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
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Control assignment not found")
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
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Control assignment not found")
    return {"assignment_id": str(row["assignment_id"]), "notes": row["notes"]}
