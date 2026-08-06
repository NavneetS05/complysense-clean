# Use: Router managing academic and administrative departments CRUD.

from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext
from app.services.mail_service import MailService

router = APIRouter(prefix="/departments", tags=["departments"])

# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class DepartmentCreate(BaseModel):
    department_name: str
    department_code: str | None = None
    hod_name: str | None = None

class DepartmentUpdate(BaseModel):
    department_name: str | None = None
    department_code: str | None = None
    hod_name: str | None = None
    reviewer_user_id: str | None = None

class DepartmentStatusToggle(BaseModel):
    is_active: bool

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "",
    summary="List all departments in the institution",
)
async def list_departments(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_DEPARTMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status: str | None = Query(None),
    search: str | None = Query(None),
) -> list[dict[str, Any]]:
    query_str = """
        select d.department_id, d.institution_id, d.department_name, d.department_code,
               d.hod_name, d.reviewer_user_id, u.full_name as reviewer_name,
               u.email as reviewer_email, d.is_active, d.created_at
          from departments d
          left join users u on u.user_id = d.reviewer_user_id
         where d.institution_id = :inst_id
    """
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id}

    if status and status != "All":
        if status == "Active":
            query_str += " and d.is_active = true"
        elif status == "Inactive":
            query_str += " and d.is_active = false"

    if search:
        query_str += " and (lower(d.department_name) like lower(:search) or lower(d.department_code) like lower(:search))"
        params["search"] = f"%{search}%"

    query_str += " order by d.department_name asc"

    try:
        res = await session.execute(text(query_str), params)
        rows = res.mappings().all()

        out = []
        for r in rows:
            d = dict(r)
            d["department_id"] = str(d["department_id"])
            d["institution_id"] = str(d["institution_id"])
            d["reviewer_user_id"] = str(d["reviewer_user_id"]) if d["reviewer_user_id"] else None
            out.append(d)
        return out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "",
    summary="Create a new department in the active institution",
    status_code=201,
)
async def create_department(
    payload: DepartmentCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_DEPARTMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    # Check if department name already exists for this institution
    check = await session.execute(
        text(
            """
            select department_id from departments
             where institution_id = :inst_id
               and lower(department_name) = lower(:name)
            """
        ),
        {"inst_id": user_ctx.institution_id, "name": payload.department_name},
    )
    if check.mappings().first():
        raise HTTPException(status_code=400, detail="A department with this name already exists")

    insert_query = """
        insert into departments (
            institution_id, department_name, department_code, hod_name, is_active
        )
        values (
            :inst_id, :department_name, :department_code, :hod_name, true
        )
        returning department_id, department_name
    """
    
    try:
        res = await session.execute(
            text(insert_query),
            {
                "inst_id": user_ctx.institution_id,
                "department_name": payload.department_name,
                "department_code": payload.department_code,
                "hod_name": payload.hod_name,
            },
        )
        row = res.mappings().first()
        d = dict(row)
        dept_id = str(d["department_id"])
        d["department_id"] = dept_id

        from app.repositories.audit import AuditLogRepository
        await AuditLogRepository(session).write(
            institution_id=user_ctx.institution_id,
            user_id=user_ctx.user_id,
            active_role_id=user_ctx.active_role_id,
            action_type="department_created",
            entity_type="department",
            entity_id=dept_id,
            action_details={"department_name": payload.department_name},
        )
        await session.commit()
        return d
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch(
    "/{dept_id}",
    summary="Update department information or reviewer assignment",
)
async def update_department(
    dept_id: str,
    payload: DepartmentUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_DEPARTMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    update_fields = []
    params: dict[str, Any] = {"id": dept_id, "inst_id": user_ctx.institution_id}

    for field, val in payload.model_dump(exclude_unset=True).items():
        update_fields.append(f"{field} = :{field}")
        params[field] = val

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_str = ", ".join(update_fields)
    query = f"""
        update departments
           set {update_str}, updated_at = now()
         where department_id = :id
           and institution_id = :inst_id
        returning department_id
    """
    try:
        # If reviewer is being assigned, verify if the user exists and is a Department Reviewer
        if payload.reviewer_user_id:
            res_user = await session.execute(
                text(
                    """
                    select u.user_id from users u
                      join roles r on r.role_id = u.role_id
                     where u.user_id = :user_id
                       and u.institution_id = :inst_id
                       and r.role_name = 'Department Reviewer'
                    """
                ),
                {"user_id": payload.reviewer_user_id, "inst_id": user_ctx.institution_id},
            )
            if not res_user.mappings().first():
                raise HTTPException(
                    status_code=400,
                    detail="Reviewer must be an active user with 'Department Reviewer' role",
                )

        res = await session.execute(text(query), params)
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="Department not found")

        # Write audit log if reviewer assigned
        if payload.reviewer_user_id:
            reviewer_email_row = await session.execute(
                text(
                    """
                    select email, full_name
                      from users
                     where user_id = :user_id
                       and institution_id = :inst_id
                    """
                ),
                {"user_id": payload.reviewer_user_id, "inst_id": user_ctx.institution_id},
            )
            reviewer_row = reviewer_email_row.mappings().first()
            if reviewer_row:
                await MailService().send_message(
                    to_email=str(reviewer_row["email"]),
                    subject="ComplySense — You’ve been assigned as a department reviewer",
                    template_key="workflow",
                    context={
                        "title": "Department reviewer assignment",
                        "message": f"You have been assigned as the reviewer for department {dept_id}.",
                        "action_url": f"{get_settings().frontend_url}/departments",
                    },
                )
            await session.execute(
                text(
                    """
                    insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                    values (:inst_id, :admin_id, :role_id, 'reviewer_assigned', 'department', :entity_id, :details)
                    """
                ),
                {
                    "inst_id": user_ctx.institution_id,
                    "admin_id": user_ctx.user_id,
                    "role_id": user_ctx.active_role_id,
                    "entity_id": dept_id,
                    "details": f'{{"reviewer_user_id": "{payload.reviewer_user_id}"}}',
                },
            )

        await session.commit()
        return {"department_id": str(row["department_id"]), "message": "Updated successfully"}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.put(
    "/{dept_id}/status",
    summary="Toggle active status of a department",
)
async def toggle_department_status(
    dept_id: str,
    payload: DepartmentStatusToggle,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_DEPARTMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    try:
        res = await session.execute(
            text(
                """
                update departments
                   set is_active = :is_active, updated_at = now()
                 where department_id = :dept_id
                   and institution_id = :inst_id
                returning department_id, is_active
                """
            ),
            {
                "is_active": payload.is_active,
                "dept_id": dept_id,
                "inst_id": user_ctx.institution_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="Department not found")
        await session.commit()
        return {"department_id": str(row["department_id"]), "is_active": row["is_active"]}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
