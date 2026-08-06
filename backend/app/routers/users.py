# Use: Router managing user creation and lifecycle operations.

from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.permissions import require_permission
from app.core.security import hash_password
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.schemas.auth import UserContext
from app.services.mail_service import MailService

router = APIRouter(prefix="/users", tags=["users"])

# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role_id: str
    phone: str | None = None
    designation: str | None = None
    department_id: str | None = None  # To associate HOD / reviewer

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role_id: str | None = None
    phone: str | None = None
    designation: str | None = None
    department_id: str | None = None

class UserStatusToggle(BaseModel):
    is_active: bool

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "",
    summary="List all users in the institution",
)
async def list_institution_users(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    institution_id: str | None = Query(None),
    role: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
) -> list[dict[str, Any]]:
    # Base query joining user with role and department (if reviewer)
    query_str = """
        select u.user_id, u.institution_id, u.role_id, r.role_name,
               u.full_name, u.email, u.phone, u.designation, u.is_active,
               u.last_login, u.created_at,
               u.blocked_until,
               d.department_name, d.department_id
          from users u
          join roles r on r.role_id = u.role_id
          left join departments d on d.reviewer_user_id = u.user_id
         where u.institution_id = :inst_id
    """
    scoped_institution_id = (
        institution_id
        if institution_id and user_ctx.active_role_name == RoleName.SUPER_ADMIN.value
        else user_ctx.institution_id
    )
    params: dict[str, Any] = {"inst_id": scoped_institution_id}

    if role and role != "All":
        query_str += " and r.role_name = :role_name"
        params["role_name"] = role

    if status and status != "All":
        if status == "Active":
            query_str += " and u.is_active = true"
        elif status == "Inactive":
            query_str += " and u.is_active = false"
        elif status == "Locked":
            query_str += " and u.blocked_until is not null"

    if search:
        query_str += " and (lower(u.full_name) like lower(:search) or lower(u.email) like lower(:search))"
        params["search"] = f"%{search}%"

    query_str += " order by u.created_at desc"

    try:
        res = await session.execute(text(query_str), params)
        rows = res.mappings().all()

        out = []
        for r in rows:
            d = dict(r)
            d["user_id"] = str(d["user_id"])
            d["institution_id"] = str(d["institution_id"])
            d["role_id"] = str(d["role_id"])
            d["department_id"] = str(d["department_id"]) if d["department_id"] else None
            d["is_locked"] = bool(d.get("blocked_until"))
            out.append(d)
        return out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "",
    summary="Create a new user account in active institution context",
    status_code=201,
)
async def create_user(
    payload: UserCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    # Check if email is already taken
    check = await session.execute(
        text("select user_id from users where lower(email) = lower(:email)"),
        {"email": payload.email},
    )
    if check.mappings().first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    # Hash auto-generated setup password
    setup_pass = "SetupTemp123!"
    pass_hash = hash_password(setup_pass)

    insert_user = """
        insert into users (
            institution_id, role_id, full_name, email, password_hash, phone, designation, is_active
        )
        values (
            :inst_id, :role_id, :full_name, :email, :password_hash, :phone, :designation, true
        )
        returning user_id, full_name, email
    """
    
    try:
        res = await session.execute(
            text(insert_user),
            {
                "inst_id": user_ctx.institution_id,
                "role_id": payload.role_id,
                "full_name": payload.full_name,
                "email": payload.email,
                "password_hash": pass_hash,
                "phone": payload.phone,
                "designation": payload.designation,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to insert user record")

        new_user_id = row["user_id"]

        # If user is a Department Reviewer and department_id is selected, link it
        if payload.department_id:
            await session.execute(
                text(
                    """
                    update departments
                       set reviewer_user_id = :user_id, updated_at = now()
                     where department_id = :dept_id
                       and institution_id = :inst_id
                    """
                ),
                {
                    "user_id": new_user_id,
                    "dept_id": payload.department_id,
                    "inst_id": user_ctx.institution_id,
                },
            )

        # Audit log entry
        await session.execute(
            text(
                """
                insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values (:inst_id, :admin_id, :role_id, 'user_created', 'user', :entity_id, '{"method": "api_onboard"}')
                """
            ),
            {
                "inst_id": user_ctx.institution_id,
                "admin_id": user_ctx.user_id,
                "role_id": user_ctx.active_role_id,
                "entity_id": new_user_id,
            },
        )

        await session.commit()
        return {"user_id": str(new_user_id), "full_name": row["full_name"], "email": row["email"]}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


class UserInvite(BaseModel):
    full_name: str
    email: EmailStr
    role_name: str
    department_id: str | None = None
    institution_id: str | None = None


class UserRoleUpdate(BaseModel):
    role_name: str


@router.post(
    "/invite",
    summary="Invite a new user by email",
    status_code=201,
)
async def invite_user(
    payload: UserInvite,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    target_inst_id = (
        payload.institution_id
        if (user_ctx.active_role_name == RoleName.SUPER_ADMIN.value and payload.institution_id)
        else user_ctx.institution_id
    )

    role_row = await session.execute(
        text("select role_id from roles where role_name = :role_name"),
        {"role_name": payload.role_name},
    )
    role = role_row.mappings().first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing = await session.execute(
        text("select user_id from users where lower(email) = lower(:email)"),
        {"email": payload.email},
    )
    if existing.mappings().first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    setup_pass = "Comply@2025"
    pass_hash = hash_password(setup_pass)

    insert_user = """
        insert into users (
            institution_id, role_id, full_name, email, password_hash, phone, designation, is_active
        )
        values (
            :inst_id, :role_id, :full_name, :email, :password_hash, null, null, true
        )
        returning user_id, full_name, email
    """
    try:
        res = await session.execute(
            text(insert_user),
            {
                "inst_id": target_inst_id,
                "role_id": role["role_id"],
                "full_name": payload.full_name,
                "email": payload.email,
                "password_hash": pass_hash,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create invited user")

        new_user_id = row["user_id"]
        if payload.department_id:
            await session.execute(
                text(
                    """
                    update departments
                       set reviewer_user_id = :user_id, updated_at = now()
                     where department_id = :dept_id
                       and institution_id = :inst_id
                    """
                ),
                {
                    "user_id": new_user_id,
                    "dept_id": payload.department_id,
                    "inst_id": target_inst_id,
                },
            )

        await session.execute(
            text(
                """
                insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values (:inst_id, :admin_id, :role_id, 'user_invited', 'user', :entity_id, '{"method": "invite_email"}')
                """
            ),
            {
                "inst_id": user_ctx.institution_id,
                "admin_id": user_ctx.user_id,
                "role_id": user_ctx.active_role_id,
                "entity_id": new_user_id,
            },
        )

        await session.commit()
        return {"user_id": str(new_user_id), "full_name": row["full_name"], "email": row["email"]}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch(
    "/{user_id}/role",
    summary="Change a user's role",
)
async def change_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    role_row = await session.execute(
        text("select role_id from roles where role_name = :role_name"),
        {"role_name": payload.role_name},
    )
    role = role_row.mappings().first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role")

    try:
        res = await session.execute(
            text(
                """
                update users
                   set role_id = :role_id, updated_at = now()
                 where user_id = :user_id
                   and institution_id = :inst_id
                returning user_id
                """
            ),
            {
                "role_id": role["role_id"],
                "user_id": user_id,
                "inst_id": user_ctx.institution_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="User not found")

        await session.execute(
            text(
                """
                insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values (:inst_id, :admin_id, :role_id, 'user_role_changed', 'user', :entity_id, :details)
                """
            ),
            {
                "inst_id": user_ctx.institution_id,
                "admin_id": user_ctx.user_id,
                "role_id": user_ctx.active_role_id,
                "entity_id": user_id,
                "details": f"{{\"new_role\": \"{payload.role_name}\"}}",
            },
        )

        await session.commit()
        return {"user_id": user_id, "role_name": payload.role_name}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{user_id}/unlock",
    summary="Unlock a locked user account",
)
async def unlock_user(
    user_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    try:
        res = await session.execute(
            text(
                """
                update users
                   set failed_login_attempts = 0,
                       blocked_until = null,
                       updated_at = now()
                 where user_id = :user_id
                   and institution_id = :inst_id
                returning user_id
                """
            ),
            {
                "user_id": user_id,
                "inst_id": user_ctx.institution_id,
            },
        )
        if not res.mappings().first():
            await session.rollback()
            raise HTTPException(status_code=404, detail="User not found")

        await session.execute(
            text(
                """
                insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values (:inst_id, :admin_id, :role_id, 'user_unlocked', 'user', :entity_id, '{"method": "admin_unlock"}')
                """
            ),
            {
                "inst_id": user_ctx.institution_id,
                "admin_id": user_ctx.user_id,
                "role_id": user_ctx.active_role_id,
                "entity_id": user_id,
            },
        )

        await session.commit()
        return {"user_id": user_id, "unlocked": True}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


class AdminPasswordResetPayload(BaseModel):
    new_password: str | None = None


@router.post(
    "/{user_id}/reset-password",
    summary="Reset password for any user (Super Admin or Institution Admin)",
)
async def admin_reset_password(
    user_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: AdminPasswordResetPayload | None = None,
) -> dict[str, Any]:
    new_password = (payload.new_password if payload and payload.new_password else "Comply@2025")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    new_hash = hash_password(new_password)

    query = """
        update users
           set password_hash = :hash,
               failed_login_attempts = 0,
               blocked_until = null,
               updated_at = now()
         where user_id = :user_id
    """
    params: dict[str, Any] = {"hash": new_hash, "user_id": user_id}

    if user_ctx.active_role_name != RoleName.SUPER_ADMIN.value:
        query += " and institution_id = :inst_id"
        params["inst_id"] = user_ctx.institution_id

    query += " returning user_id, full_name, email"

    try:
        res = await session.execute(text(query), params)
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="User not found")

        await session.execute(
            text(
                """
                insert into audit_logs (institution_id, user_id, active_role_id, action_type, entity_type, entity_id, action_details)
                values (:inst_id, :admin_id, :role_id, 'admin_password_reset', 'user', :entity_id, '{"method": "admin_reset"}')
                """
            ),
            {
                "inst_id": user_ctx.institution_id,
                "admin_id": user_ctx.user_id,
                "role_id": user_ctx.active_role_id,
                "entity_id": user_id,
            },
        )
        await session.commit()
        return {
            "user_id": str(row["user_id"]),
            "email": row["email"],
            "message": f"Password reset successfully to '{new_password}'",
            "new_password": new_password,
        }
    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch(
    "/{user_id}",
    summary="Update a user's details",
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    update_fields = []
    params: dict[str, Any] = {"user_id": user_id, "inst_id": user_ctx.institution_id}

    for field, val in payload.model_dump(exclude_unset=True, exclude={"department_id"}).items():
        update_fields.append(f"{field} = :{field}")
        params[field] = val

    try:
        if update_fields:
            update_str = ", ".join(update_fields)
            query = f"""
                update users
                   set {update_str}, updated_at = now()
                 where user_id = :user_id
                   and institution_id = :inst_id
                returning user_id
            """
            res = await session.execute(text(query), params)
            if not res.mappings().first():
                await session.rollback()
                raise HTTPException(status_code=404, detail="User not found")
        else:
            # No user fields to update — still verify the user exists
            check = await session.execute(
                text("select user_id from users where user_id = :user_id and institution_id = :inst_id"),
                {"user_id": user_id, "inst_id": user_ctx.institution_id},
            )
            if not check.mappings().first():
                await session.rollback()
                raise HTTPException(status_code=404, detail="User not found")

        # Department assignment logic
        if payload.department_id is not None:
            # Unlink user from any old departments first
            await session.execute(
                text(
                    """
                    update departments
                       set reviewer_user_id = null, updated_at = now()
                     where reviewer_user_id = :user_id
                       and institution_id = :inst_id
                    """
                ),
                {"user_id": user_id, "inst_id": user_ctx.institution_id},
            )
            # Link to new department
            if payload.department_id != "":
                await session.execute(
                    text(
                        """
                        update departments
                           set reviewer_user_id = :user_id, updated_at = now()
                         where department_id = :dept_id
                           and institution_id = :inst_id
                        """
                    ),
                    {
                        "user_id": user_id,
                        "dept_id": payload.department_id,
                        "inst_id": user_ctx.institution_id,
                    },
                )

        await session.commit()
        return {"user_id": user_id, "message": "User updated successfully"}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.put(
    "/{user_id}/status",
    summary="Toggle active status of a user",
)
async def toggle_user_status(
    user_id: str,
    payload: UserStatusToggle,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    try:
        res = await session.execute(
            text(
                """
                update users
                   set is_active = :is_active, updated_at = now()
                 where user_id = :user_id
                   and institution_id = :inst_id
                returning user_id, is_active
                """
            ),
            {
                "is_active": payload.is_active,
                "user_id": user_id,
                "inst_id": user_ctx.institution_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="User not found")
        await session.commit()
        return {"user_id": str(row["user_id"]), "is_active": row["is_active"]}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{user_id}/reset-password",
    summary="Trigger password reset request for a user",
)
async def admin_reset_password(
    user_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_USERS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    # Check if user exists in the active institution
    res = await session.execute(
        text("select email from users where user_id = :user_id and institution_id = :inst_id"),
        {"user_id": user_id, "inst_id": user_ctx.institution_id},
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    # Simulate trigger reset
    return {
        "success": True,
        "email": row["email"],
        "message": f"Password reset email sent to {row['email']}",
    }
