# Use: Router for uploading and reviewing evidence files.

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.schemas.auth import UserContext

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", summary="List evidence documents for the current institution")
async def list_evidence(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select evidence_id, control_id, file_name, approval_status, file_size_kb, uploaded_at, description, assignment_id, department_id
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
            "assignment_id": str(row["assignment_id"]) if row["assignment_id"] else None,
            "department_id": str(row["department_id"]) if row["department_id"] else None,
            "file_name": row["file_name"],
            "approval_status": row["approval_status"],
            "file_size_kb": row["file_size_kb"],
            "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
            "description": row["description"],
        }
        for row in rows
    ]


@router.post("", status_code=201, summary="Upload evidence for a control assignment")
async def upload_evidence(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.UPLOAD_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    file: UploadFile = File(...),
    control_id: str = Form(...),
    assignment_id: str | None = Form(None),
    description: str | None = Form(None),
) -> dict[str, Any]:
    if assignment_id is not None:
        assignment_id = assignment_id.strip() or None
    if description is not None:
        description = description.strip() or None

    if user_ctx.active_role_name not in {RoleName.DEPARTMENT_REVIEWER, RoleName.IT_SECURITY_OFFICER, RoleName.COMPLIANCE_OFFICER}:
        raise HTTPException(status_code=403, detail="Only department reviewers and security/compliance staff can upload evidence")

    if assignment_id:
        assignment_check = await session.execute(
            text("select assignment_id from control_assignments where assignment_id = :assignment_id and institution_id = :inst_id"),
            {"assignment_id": assignment_id, "inst_id": user_ctx.institution_id},
        )
        if not assignment_check.mappings().first():
            raise HTTPException(status_code=404, detail="Control assignment not found")

    safe_name = Path(file.filename or "evidence.bin").name
    safe_name = safe_name.replace(" ", "_")
    evidence_id = uuid4()
    upload_dir = Path(__file__).resolve().parents[2] / "uploads" / "evidence"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"{evidence_id}_{safe_name}"
    content = await file.read()
    stored_path.write_bytes(content)

    department_id = None
    if assignment_id:
        assignment_row = await session.execute(
            text("select department_id from control_assignments where assignment_id = :assignment_id and institution_id = :inst_id"),
            {"assignment_id": assignment_id, "inst_id": user_ctx.institution_id},
        )
        assignment_data = assignment_row.mappings().first()
        department_id = assignment_data["department_id"] if assignment_data else None

    res = await session.execute(
        text(
            """
            insert into evidence_documents (
                evidence_id, institution_id, control_id, assignment_id, department_id, file_name, file_path, mime_type, file_size_kb, description, uploaded_by, approval_status
            ) values (
                :evidence_id, :inst_id, :control_id, :assignment_id, :department_id, :file_name, :file_path, :mime_type, :file_size_kb, :description, :uploaded_by, 'pending'
            ) returning evidence_id, file_name, approval_status, file_size_kb, uploaded_at
            """
        ),
        {
            "evidence_id": evidence_id,
            "inst_id": user_ctx.institution_id,
            "control_id": control_id,
            "assignment_id": assignment_id,
            "department_id": department_id,
            "file_name": safe_name,
            "file_path": str(stored_path),
            "mime_type": file.content_type,
            "file_size_kb": max(1, len(content) // 1024),
            "description": description,
            "uploaded_by": user_ctx.user_id,
        },
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to save evidence")
    return {
        "evidence_id": str(row["evidence_id"]),
        "file_name": row["file_name"],
        "approval_status": row["approval_status"],
        "file_size_kb": row["file_size_kb"],
        "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
    }


@router.get("/{evidence_id}", summary="Get a single evidence document")
async def get_evidence(
    evidence_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select evidence_id, control_id, file_name, approval_status, file_size_kb, uploaded_at, description, assignment_id, department_id
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
        "assignment_id": str(row["assignment_id"]) if row["assignment_id"] else None,
        "department_id": str(row["department_id"]) if row["department_id"] else None,
        "file_name": row["file_name"],
        "approval_status": row["approval_status"],
        "file_size_kb": row["file_size_kb"],
        "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
        "description": row["description"],
    }
