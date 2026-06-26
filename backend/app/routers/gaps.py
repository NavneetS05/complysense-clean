# Use: Router for compliance gap inspection and remediation actions.

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/gaps", tags=["gaps"])


@router.get("", summary="List compliance gaps for the current institution")
async def list_gaps(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_GAPS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select gap_id, control_id, framework_name, severity, title, remediation_status, created_at
        from compliance_gaps
        where institution_id = :inst_id
        order by case severity when 'critical' then 0 when 'high' then 1 when 'medium' then 2 else 3 end, created_at desc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "gap_id": str(row["gap_id"]),
            "control_id": row["control_id"],
            "framework_name": row["framework_name"],
            "severity": row["severity"],
            "title": row["title"],
            "remediation_status": row["remediation_status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
        for row in rows
    ]


@router.get("/{gap_id}", summary="Get a single compliance gap")
async def get_gap(
    gap_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_GAPS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select gap_id, control_id, framework_name, severity, title, description, remediation_status, created_at
        from compliance_gaps
        where gap_id = :gap_id
          and institution_id = :inst_id
    """
    res = await session.execute(text(query), {"gap_id": gap_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Gap not found")
    return {
        "gap_id": str(row["gap_id"]),
        "control_id": row["control_id"],
        "framework_name": row["framework_name"],
        "severity": row["severity"],
        "title": row["title"],
        "description": row["description"],
        "remediation_status": row["remediation_status"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }
