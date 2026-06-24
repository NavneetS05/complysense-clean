# Use: Router for querying and retrieving the central audit trail logs.

from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.schemas.auth import UserContext

router = APIRouter(prefix="/audit", tags=["audit"])

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
        return [dict(r) for r in rows]
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
    from_date: str | None = Query(None),  # e.g., "YYYY-MM-DD"
    to_date: str | None = Query(None),    # e.g., "YYYY-MM-DD"
    format: str | None = Query(None),      # "csv" or None
    page: int = Query(1),
    limit: int = Query(50),
) -> Any:
    # 1. Enforce permission
    if PermissionKey.VIEW_AUDIT_TRAIL.value not in user.permissions:
        raise HTTPException(status_code=403, detail="Missing permission: view_audit_trail")

    # 2. Scope check
    # Non-superadmins cannot see logs of other institutions
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

    # CSV bypasses pagination
    if format == "csv":
        query_csv = f"{query_select} {where_clause} order by al.created_at desc"
        res = await session.execute(text(query_csv), params)
        rows = res.mappings().all()

        output = io.StringIO()
        writer = csv.writer(output)
        # CSV headers
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

    # Count total for pagination
    res_count = await session.execute(text(f"{query_count} {where_clause}"), params)
    total_count = res_count.scalar() or 0

    # Retrieve paginated logs
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

    return {
        "logs": logs,
        "total": total_count,
        "page": page,
        "limit": limit,
    }
