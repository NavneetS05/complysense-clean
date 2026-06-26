# Use: Router for uploading and reviewing evidence files.

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", summary="List evidence documents for the current institution")
async def list_evidence(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select evidence_id, control_id, file_name, approval_status, file_size_kb, uploaded_at, description
        from evidence_documents
        where institution_id = :inst_id
        order by uploaded_at desc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "evidence_id": str(row["evidence_id"]),
            "control_id": row["control_id"],
            "file_name": row["file_name"],
            "approval_status": row["approval_status"],
            "file_size_kb": row["file_size_kb"],
            "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
            "description": row["description"],
        }
        for row in rows
    ]


@router.get("/{evidence_id}", summary="Get a single evidence document")
async def get_evidence(
    evidence_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select evidence_id, control_id, file_name, approval_status, file_size_kb, uploaded_at, description
        from evidence_documents
        where evidence_id = :evidence_id
          and institution_id = :inst_id
    """
    res = await session.execute(text(query), {"evidence_id": evidence_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {
        "evidence_id": str(row["evidence_id"]),
        "control_id": row["control_id"],
        "file_name": row["file_name"],
        "approval_status": row["approval_status"],
        "file_size_kb": row["file_size_kb"],
        "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
        "description": row["description"],
    }
