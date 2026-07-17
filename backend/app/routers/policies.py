# Use: Router managing organization policies and executive compliance reports.

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.repositories.audit import AuditLogRepository
from app.routers.audit import create_audit_report_entry
from app.schemas.auth import UserContext
from app.services.mail_service import MailService

router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ReportType(StrEnum):
    NAAC = "naac"
    ISO_READINESS = "iso_readiness"
    DPDP_ASSESSMENT = "dpdp_assessment"
    CUSTOM = "custom"


class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    period_from: str | None = None
    period_to: str | None = None


class CreatePolicyPayload(BaseModel):
    policy_name: str
    related_control_id: str | None = None
    policy_content: str | None = None
    policy_status: PolicyStatus = PolicyStatus.DRAFT
    parent_policy_id: str | None = None


class UpdatePolicyPayload(BaseModel):
    policy_name: str | None = None
    policy_content: str | None = None
    policy_status: PolicyStatus | None = None
    related_control_id: str | None = None
    submitted_to: str | None = None
    rejection_reason: str | None = None


class PolicyApprovalPayload(BaseModel):
    rejection_reason: str | None = None


@router.get("", summary="List policies for the current institution")
async def list_policies(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select policy_id, policy_name, version_number, policy_status, related_control_id, created_at, policy_content
        from generated_policies
        where institution_id = :inst_id
        order by created_at desc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "policy_id": str(row["policy_id"]),
            "policy_name": row["policy_name"],
            "version_number": row["version_number"],
            "policy_status": row["policy_status"],
            "related_control_id": row["related_control_id"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "policy_content": row["policy_content"],
        }
        for row in rows
    ]


@router.post("", status_code=201, summary="Create a policy draft")
async def create_policy(
    payload: CreatePolicyPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    parent_policy_id = None
    version_number = 1
    if payload.parent_policy_id:
        parent_res = await session.execute(
            text(
                """
                select policy_id, version_number
                from generated_policies
                where policy_id = :policy_id and institution_id = :inst_id
                """
            ),
            {"policy_id": payload.parent_policy_id, "inst_id": user_ctx.institution_id},
        )
        parent = parent_res.mappings().first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent policy not found")
        parent_policy_id = str(parent["policy_id"])
        version_number = int(parent["version_number"] or 1) + 1

    query = """
        insert into generated_policies (
            institution_id, related_control_id, policy_name, policy_content,
            version_number, policy_status, generated_by, parent_policy_id
        )
        values (
            :inst_id, :related_control_id, :policy_name, :policy_content,
            :version_number, :policy_status, :generated_by, :parent_policy_id
        )
        returning policy_id, policy_name, version_number, policy_status, related_control_id, created_at, policy_content, parent_policy_id
    """
    res = await session.execute(
        text(query),
        {
            "inst_id": user_ctx.institution_id,
            "related_control_id": payload.related_control_id,
            "policy_name": payload.policy_name,
            "policy_content": payload.policy_content,
            "version_number": version_number,
            "policy_status": payload.policy_status,
            "generated_by": user_ctx.user_id,
            "parent_policy_id": parent_policy_id,
        },
    )
    row = res.mappings().first()
    if row:
        await AuditLogRepository(session).write(
            institution_id=user_ctx.institution_id,
            user_id=user_ctx.user_id,
            active_role_id=user_ctx.active_role_id,
            action_type="policy_created",
            entity_type="policy",
            entity_id=str(row["policy_id"]),
            action_details={"policy_name": payload.policy_name, "parent_policy_id": parent_policy_id},
        )
    await session.commit()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create policy")
    return {
        "policy_id": str(row["policy_id"]),
        "policy_name": row["policy_name"],
        "version_number": row["version_number"],
        "policy_status": row["policy_status"],
        "related_control_id": row["related_control_id"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "policy_content": row["policy_content"],
        "parent_policy_id": str(row["parent_policy_id"]) if row["parent_policy_id"] else None,
    }


@router.get("/{policy_id}", summary="Get a single policy")
async def get_policy(
    policy_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select policy_id, policy_name, version_number, policy_status, related_control_id, created_at, policy_content, submitted_to
        from generated_policies
        where policy_id = :policy_id and institution_id = :inst_id
    """
    res = await session.execute(text(query), {"policy_id": policy_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {
        "policy_id": str(row["policy_id"]),
        "policy_name": row["policy_name"],
        "version_number": row["version_number"],
        "policy_status": row["policy_status"],
        "related_control_id": row["related_control_id"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "policy_content": row["policy_content"],
        "submitted_to": str(row["submitted_to"]) if row["submitted_to"] else None,
    }


@router.patch("/{policy_id}", summary="Update policy metadata")
async def update_policy(
    policy_id: str,
    payload: UpdatePolicyPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    if payload.policy_status in {PolicyStatus.APPROVED, PolicyStatus.REJECTED}:
        raise HTTPException(
            status_code=403,
            detail="Use the approve/reject endpoints for approval decisions",
        )
    updates = []
    values: dict[str, Any] = {"policy_id": policy_id, "inst_id": user_ctx.institution_id}
    for field in ["policy_name", "policy_content", "policy_status", "related_control_id", "submitted_to", "rejection_reason"]:
        value = getattr(payload, field, None)
        if value is not None:
            updates.append(f"{field} = :{field}")
            values[field] = value
    if not updates:
        raise HTTPException(status_code=400, detail="No update values provided")
    query = f"update generated_policies set {', '.join(updates)}, updated_at = now() where policy_id = :policy_id and institution_id = :inst_id returning policy_id"
    res = await session.execute(text(query), values)
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="policy_updated",
        entity_type="policy",
        entity_id=policy_id,
        action_details={"fields": [field for field in updates]},
    )
    await session.commit()
    return {"policy_id": str(row["policy_id"]), "updated": True}


@router.post("/{policy_id}/approve", summary="Approve a submitted policy")
async def approve_policy(
    policy_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.APPROVE_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    res = await session.execute(
        text(
            """
            update generated_policies
               set policy_status = 'approved',
                   approved_by = :approved_by,
                   approved_at = now(),
                   rejection_reason = null,
                   updated_at = now()
             where policy_id = :policy_id
               and institution_id = :inst_id
            returning policy_id, policy_status
            """
        ),
        {"policy_id": policy_id, "inst_id": user_ctx.institution_id, "approved_by": user_ctx.user_id},
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="policy_approved",
        entity_type="policy",
        entity_id=policy_id,
    )
    await session.commit()
    return {"policy_id": str(row["policy_id"]), "policy_status": row["policy_status"]}


@router.post("/{policy_id}/reject", summary="Reject a submitted policy")
async def reject_policy(
    policy_id: str,
    payload: PolicyApprovalPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.APPROVE_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    res = await session.execute(
        text(
            """
            update generated_policies
               set policy_status = 'rejected',
                   rejection_reason = :rejection_reason,
                   updated_at = now()
             where policy_id = :policy_id
               and institution_id = :inst_id
            returning policy_id, policy_status
            """
        ),
        {
            "policy_id": policy_id,
            "inst_id": user_ctx.institution_id,
            "rejection_reason": payload.rejection_reason,
        },
    )
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="policy_rejected",
        entity_type="policy",
        entity_id=policy_id,
        action_details={"has_rejection_reason": bool(payload.rejection_reason)},
    )
    await session.commit()
    return {"policy_id": str(row["policy_id"]), "policy_status": row["policy_status"]}


@router.put("/{policy_id}/content", summary="Save policy content")
async def save_policy_content(
    policy_id: str,
    payload: UpdatePolicyPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        update generated_policies
        set policy_content = :policy_content, updated_at = now()
        where policy_id = :policy_id and institution_id = :inst_id
        returning policy_id
    """
    res = await session.execute(text(query), {"policy_id": policy_id, "inst_id": user_ctx.institution_id, "policy_content": payload.policy_content})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="policy_content_saved",
        entity_type="policy",
        entity_id=policy_id,
    )
    await session.commit()
    return {"policy_id": str(row["policy_id"]), "updated": True}


@router.get(
    "/reports",
    summary="List all generated compliance reports for the institution",
)
async def list_reports(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select report_id, institution_id, assessment_id, report_name, report_type, file_path, generated_by, generated_at
          from audit_reports
         where institution_id = :inst_id
         order by generated_at desc
    """
    try:
        res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
        rows = res.mappings().all()
        out = []
        for r in rows:
            d = dict(r)
            d["report_id"] = str(d["report_id"])
            d["institution_id"] = str(d["institution_id"])
            d["assessment_id"] = str(d["assessment_id"]) if d["assessment_id"] else None
            d["generated_by"] = str(d["generated_by"]) if d["generated_by"] else None
            d["generated_at"] = d["generated_at"].isoformat()
            out.append(d)
        return out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/reports/generate",
    summary="Generate a new compliance executive briefing",
    status_code=201,
)
async def generate_executive_report(
    payload: ReportGenerateRequest,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.DRAFT_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    types_map = {
        "naac": "NAAC Criteria 4 & 6 Verification Briefing",
        "iso_readiness": "ISO 27001 Gap Analysis Executive Report",
        "dpdp_assessment": "DPDP Section 8 Compliance Assessment",
        "custom": "Compliance Status Custom Executive Briefing",
    }

    report_name = types_map.get(payload.report_type, "Compliance Status Summary Report")
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_name = f"{report_name} ({timestamp_str})"

    file_path = f"/reports/{payload.report_type}_generated.pdf"

    try:
        row = await create_audit_report_entry(
            session,
            institution_id=user_ctx.institution_id,
            generated_by=user_ctx.user_id,
            report_name=report_name,
            report_type=payload.report_type,
            file_path=file_path,
        )
        await session.commit()

        d = dict(row)
        d["report_id"] = str(d["report_id"])
        d["generated_at"] = d["generated_at"].isoformat()
        return d
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/reports/{report_id}/download", summary="Download a generated compliance report")
async def download_policy_report(
    report_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_POLICIES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    res = await session.execute(
        text(
            "select report_id, report_name, report_type, file_path, generated_at "
            "from audit_reports where report_id = :report_id and institution_id = :inst_id"
        ),
        {"report_id": report_id, "inst_id": user_ctx.institution_id},
    )
    report = res.mappings().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report_name = report["report_name"] or "report"
    generated_at = report["generated_at"]
    header_name = f"{report_name}.pdf" if report_name.endswith(".pdf") else f"{report_name}.pdf"
    content = (
        f"Report Name: {report_name}\n"
        f"Report Type: {report['report_type']}\n"
        f"Generated At: {generated_at.isoformat() if generated_at else 'unknown'}\n"
        "\nThis endpoint provides a download placeholder for compliance reports."
    )
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{header_name}\""},
    )
