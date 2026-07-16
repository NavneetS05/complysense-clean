# Use: Router for uploading and reviewing evidence files.

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey, RoleName
from app.mongodb import get_mongo_database
from app.repositories.audit import AuditLogRepository
from app.schemas.auth import UserContext
from app.storage.documents import DocumentStore

router = APIRouter(prefix="/evidence", tags=["evidence"])

MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
STREAM_CHUNK_BYTES = 1024 * 1024
ALLOWED_EVIDENCE_TYPES = {
    ".pdf": {"application/pdf"},
    ".png": {"image/png"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".doc": {"application/msword"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".xls": {"application/vnd.ms-excel"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    ".csv": {"text/csv", "application/csv", "application/vnd.ms-excel"},
    ".txt": {"text/plain"},
    ".pptx": {"application/vnd.openxmlformats-officedocument.presentationml.presentation"},
}


class EvidenceReviewStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class EvidenceReviewPayload(BaseModel):
    approval_status: EvidenceReviewStatus
    rejection_reason: str | None = None


async def malware_scan_file(_: Path) -> None:
    """Pluggable malware scanning hook. Replace body with scanner integration."""
    return None


def _validate_file_type(filename: str, content_type: str | None) -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EVIDENCE_TYPES:
        raise HTTPException(status_code=400, detail="File extension is not allowed")
    mime = (content_type or "application/octet-stream").lower()
    if mime not in ALLOWED_EVIDENCE_TYPES[ext]:
        raise HTTPException(status_code=400, detail="File MIME type does not match the allowed evidence types")
    return ext, mime


async def _write_upload_stream(file: UploadFile, stored_path: Path) -> int:
    total = 0
    with stored_path.open("wb") as out:
        while True:
            chunk = await file.read(STREAM_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_EVIDENCE_BYTES:
                out.close()
                stored_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Evidence file exceeds 10MB limit")
            out.write(chunk)
    return total


def _extract_text_preview(stored_path: Path, mime_type: str) -> str | None:
    if mime_type == "text/plain":
        return stored_path.read_text(encoding="utf-8", errors="ignore")[:20000]
    if mime_type in {"text/csv", "application/csv"}:
        return stored_path.read_text(encoding="utf-8", errors="ignore")[:20000]
    return None


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

    _ext, mime_type = _validate_file_type(file.filename or "evidence.bin", file.content_type)

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
    try:
        file_size_bytes = await _write_upload_stream(file, stored_path)
        await malware_scan_file(stored_path)

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
                "mime_type": mime_type,
                "file_size_kb": max(1, file_size_bytes // 1024),
                "description": description,
                "uploaded_by": user_ctx.user_id,
            },
        )
        row = res.mappings().first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to save evidence")
        extracted_text = _extract_text_preview(stored_path, mime_type)
        mongo_document_id = await DocumentStore(get_mongo_database()).save_metadata(
            institution_id=user_ctx.institution_id,
            source_type="evidence",
            source_id=str(row["evidence_id"]),
            metadata={
                "file_name": safe_name,
                "file_path": str(stored_path),
                "mime_type": mime_type,
                "file_size_kb": max(1, file_size_bytes // 1024),
                "control_id": control_id,
                "assignment_id": assignment_id,
                "department_id": str(department_id) if department_id else None,
            },
            extracted_text=extracted_text,
        )
        await AuditLogRepository(session).write(
            institution_id=user_ctx.institution_id,
            user_id=user_ctx.user_id,
            active_role_id=user_ctx.active_role_id,
            action_type="evidence_uploaded",
            entity_type="evidence_document",
            entity_id=str(row["evidence_id"]),
            action_details={"file_name": safe_name, "mongo_document_id": mongo_document_id},
        )
        await session.commit()
    except HTTPException:
        await session.rollback()
        stored_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        await session.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to upload evidence") from exc
    return {
        "evidence_id": str(row["evidence_id"]),
        "file_name": row["file_name"],
        "approval_status": row["approval_status"],
        "file_size_kb": row["file_size_kb"],
        "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
    }


@router.patch("/{evidence_id}/review", summary="Approve or reject a pending evidence document")
async def review_evidence(
    evidence_id: str,
    payload: EvidenceReviewPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.REVIEW_EVIDENCE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if payload.approval_status == EvidenceReviewStatus.REJECTED and not payload.rejection_reason:
        raise HTTPException(status_code=400, detail="rejection_reason is required when rejecting evidence")
    res = await session.execute(
        text(
            """
            update evidence_documents
               set approval_status = :approval_status,
                   approved_by = :reviewed_by,
                   approved_at = now(),
                   rejection_reason = :rejection_reason
             where evidence_id = :evidence_id
               and institution_id = :inst_id
               and approval_status = 'pending'
            returning evidence_id, approval_status, rejection_reason
            """
        ),
        {
            "evidence_id": evidence_id,
            "inst_id": user_ctx.institution_id,
            "approval_status": payload.approval_status,
            "reviewed_by": user_ctx.user_id,
            "rejection_reason": payload.rejection_reason if payload.approval_status == EvidenceReviewStatus.REJECTED else None,
        },
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Pending evidence not found")
    action_type = f"evidence_{payload.approval_status}"
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type=action_type,
        entity_type="evidence_document",
        entity_id=str(row["evidence_id"]),
        action_details={
            "approval_status": payload.approval_status,
            "rejection_reason": payload.rejection_reason,
        },
    )
    await session.commit()
    return {
        "evidence_id": str(row["evidence_id"]),
        "approval_status": row["approval_status"],
        "rejection_reason": row["rejection_reason"],
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
