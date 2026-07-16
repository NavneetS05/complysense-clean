# Use: Router for mitigation tasks and remediation work tracking.

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.repositories.audit import AuditLogRepository
from app.schemas.auth import UserContext

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskPayload(BaseModel):
    task_title: str
    task_description: str | None = None
    assigned_to: str | None = None
    department_id: str | None = None
    priority: str = "medium"
    task_status: str = "open"
    due_date: str | None = None
    gap_id: str | None = None
    assignment_id: str | None = None


class UpdateTaskPayload(BaseModel):
    task_title: str | None = None
    task_description: str | None = None
    assigned_to: str | None = None
    department_id: str | None = None
    priority: str | None = None
    task_status: str | None = None
    due_date: str | None = None


@router.get("", summary="List mitigation tasks for the current institution")
async def list_tasks(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_TASKS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id, "user_id": user_ctx.user_id}
    query = """
        select task_id, task_title, priority, task_status, due_date, assigned_to, department_id, task_description, assignment_id
        from mitigation_tasks
        where institution_id = :inst_id
    """
    if user_ctx.active_role_name == RoleName.DEPARTMENT_REVIEWER:
        reviewer_department = await session.execute(
            text("select department_id from departments where institution_id = :inst_id and reviewer_user_id = :user_id"),
            params,
        )
        dept_row = reviewer_department.mappings().first()
        if dept_row and dept_row["department_id"]:
            query += " and (department_id = :dept_id or assigned_to = :user_id)"
            params["dept_id"] = dept_row["department_id"]
        else:
            query += " and assigned_to = :user_id"
    query += " order by due_date asc nulls last, created_at desc"
    res = await session.execute(text(query), params)
    rows = res.mappings().all()
    return [
        {
            "task_id": str(row["task_id"]),
            "task_title": row["task_title"],
            "priority": row["priority"],
            "task_status": row["task_status"],
            "due_date": row["due_date"].isoformat() if row["due_date"] else None,
            "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
            "department_id": str(row["department_id"]) if row["department_id"] else None,
            "assignment_id": str(row["assignment_id"]) if row["assignment_id"] else None,
            "task_description": row["task_description"],
        }
        for row in rows
    ]


@router.get("/{task_id}", summary="Get a single mitigation task")
async def get_task(
    task_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_TASKS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select task_id, task_title, priority, task_status, due_date, assigned_to, department_id, task_description, assignment_id
        from mitigation_tasks
        where task_id = :task_id and institution_id = :inst_id
    """
    res = await session.execute(text(query), {"task_id": task_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": str(row["task_id"]),
        "task_title": row["task_title"],
        "priority": row["priority"],
        "task_status": row["task_status"],
        "due_date": row["due_date"].isoformat() if row["due_date"] else None,
        "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
        "department_id": str(row["department_id"]) if row["department_id"] else None,
        "assignment_id": str(row["assignment_id"]) if row["assignment_id"] else None,
        "task_description": row["task_description"],
    }


@router.post("", status_code=201, summary="Create a mitigation task")
async def create_task(
    payload: CreateTaskPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_TASKS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        insert into mitigation_tasks (
            institution_id, gap_id, assignment_id, assigned_to, department_id, task_title, task_description, priority, task_status, due_date, created_by
        ) values (
            :inst_id, :gap_id, :assignment_id, :assigned_to, :department_id, :task_title, :task_description, :priority, :task_status, :due_date, :created_by
        ) returning task_id, task_title, priority, task_status, due_date
    """
    res = await session.execute(
        text(query),
        {
            "inst_id": user_ctx.institution_id,
            "gap_id": payload.gap_id,
            "assignment_id": payload.assignment_id,
            "assigned_to": payload.assigned_to,
            "department_id": payload.department_id,
            "task_title": payload.task_title,
            "task_description": payload.task_description,
            "priority": payload.priority,
            "task_status": payload.task_status,
            "due_date": payload.due_date,
            "created_by": user_ctx.user_id,
        },
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create task")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="task_created",
        entity_type="mitigation_task",
        entity_id=str(row["task_id"]),
        action_details={"priority": payload.priority},
    )
    await session.commit()
    return {
        "task_id": str(row["task_id"]),
        "task_title": row["task_title"],
        "priority": row["priority"],
        "task_status": row["task_status"],
        "due_date": row["due_date"].isoformat() if row["due_date"] else None,
    }


@router.patch("/{task_id}", summary="Update an existing mitigation task")
async def update_task(
    task_id: str,
    payload: UpdateTaskPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_TASKS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    fields = ["task_title", "task_description", "assigned_to", "department_id", "priority", "task_status", "due_date"]
    updates = []
    values: dict[str, Any] = {"task_id": task_id, "inst_id": user_ctx.institution_id}
    for field in fields:
        value = getattr(payload, field, None)
        if value is not None:
            updates.append(f"{field} = :{field}")
            values[field] = value
    if not updates:
        raise HTTPException(status_code=400, detail="No update values provided")
    query = f"update mitigation_tasks set {', '.join(updates)} where task_id = :task_id and institution_id = :inst_id returning task_id"
    res = await session.execute(text(query), values)
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="task_updated",
        entity_type="mitigation_task",
        entity_id=task_id,
        action_details={"fields": [field for field in fields if getattr(payload, field, None) is not None]},
    )
    await session.commit()
    return {"task_id": str(row["task_id"]), "updated": True}


@router.post("/{task_id}/submit", summary="Submit a department task and mark the linked control assignment")
async def submit_task(
    task_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_TASKS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    task_check = await session.execute(
        text("select assignment_id from mitigation_tasks where task_id = :task_id and institution_id = :inst_id"),
        {"task_id": task_id, "inst_id": user_ctx.institution_id},
    )
    task_row = task_check.mappings().first()
    if not task_row:
        raise HTTPException(status_code=404, detail="Task not found")

    res = await session.execute(
        text(
            """
            update mitigation_tasks
               set task_status = 'completed', completed_at = now(), updated_at = now()
             where task_id = :task_id and institution_id = :inst_id
            returning task_id, task_status
            """
        ),
        {"task_id": task_id, "inst_id": user_ctx.institution_id},
    )
    if task_row["assignment_id"]:
        await session.execute(
            text(
                """
                update control_assignments
                   set status = 'submitted', updated_at = now()
                 where assignment_id = :assignment_id and institution_id = :inst_id
                """
            ),
            {"assignment_id": task_row["assignment_id"], "inst_id": user_ctx.institution_id},
        )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to submit task")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="task_submitted",
        entity_type="mitigation_task",
        entity_id=task_id,
    )
    await session.commit()
    return {"task_id": str(row["task_id"]), "task_status": row["task_status"]}
