# Use: Router handling operations related to compliance assessments.

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.repositories.audit import AuditLogRepository
from app.schemas.auth import UserContext

router = APIRouter(prefix="/assessments", tags=["assessments"])


class AssessmentResponseValue(StrEnum):
    YES = "yes"
    NO = "no"
    PARTIAL = "partial"
    FULLY_IMPLEMENTED = "fully implemented"
    NOT_IMPLEMENTED = "not implemented"


class CreateAssessmentPayload(BaseModel):
    assessment_name: str
    framework_name: str


class SaveAssessmentResponsePayload(BaseModel):
    question_id: str
    control_id: str
    response_value: AssessmentResponseValue
    score_value: float | None = None


@router.get("", summary="List assessments for the current institution")
async def list_assessments(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select assessment_id, assessment_name, framework_name, assessment_status, started_at, completed_at
        from assessments
        where institution_id = :inst_id
        order by started_at desc, assessment_name asc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "assessment_id": str(row["assessment_id"]),
            "assessment_name": row["assessment_name"],
            "framework_name": row["framework_name"],
            "assessment_status": row["assessment_status"],
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
        }
        for row in rows
    ]


@router.post("", status_code=201, summary="Create a new assessment")
async def create_assessment(
    payload: CreateAssessmentPayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        insert into assessments (institution_id, assessment_name, framework_name, assessment_status, started_by)
        values (:inst_id, :assessment_name, :framework_name, 'in_progress', :started_by)
        returning assessment_id, assessment_name, framework_name, assessment_status, started_at
    """
    res = await session.execute(
        text(query),
        {
            "inst_id": user_ctx.institution_id,
            "assessment_name": payload.assessment_name,
            "framework_name": payload.framework_name,
            "started_by": user_ctx.user_id,
        },
    )
    row = res.mappings().first()
    if row:
        await AuditLogRepository(session).write(
            institution_id=user_ctx.institution_id,
            user_id=user_ctx.user_id,
            active_role_id=user_ctx.active_role_id,
            action_type="assessment_created",
            entity_type="assessment",
            entity_id=str(row["assessment_id"]),
        )
    await session.commit()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create assessment")
    return {
        "assessment_id": str(row["assessment_id"]),
        "assessment_name": row["assessment_name"],
        "framework_name": row["framework_name"],
        "assessment_status": row["assessment_status"],
        "started_at": row["started_at"].isoformat() if row["started_at"] else None,
    }


@router.get("/{assessment_id}", summary="Get a single assessment")
async def get_assessment(
    assessment_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        select assessment_id, assessment_name, framework_name, assessment_status, started_at, completed_at
        from assessments
        where assessment_id = :assessment_id
          and institution_id = :inst_id
    """
    res = await session.execute(text(query), {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {
        "assessment_id": str(row["assessment_id"]),
        "assessment_name": row["assessment_name"],
        "framework_name": row["framework_name"],
        "assessment_status": row["assessment_status"],
        "started_at": row["started_at"].isoformat() if row["started_at"] else None,
        "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
    }


@router.get("/{assessment_id}/responses", summary="List saved responses for an assessment")
async def list_assessment_responses(
    assessment_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = "select response_id, question_id, control_id, response_value, score_value, answered_by, created_at from assessment_responses where assessment_id = :assessment_id and institution_id = :inst_id"
    res = await session.execute(text(query), {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "response_id": str(r["response_id"]),
            "question_id": r["question_id"],
            "control_id": r["control_id"],
            "response_value": r["response_value"],
            "score_value": float(r["score_value"]) if r["score_value"] is not None else None,
            "answered_by": str(r["answered_by"]) if r["answered_by"] else None,
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


@router.patch("/{assessment_id}/responses", summary="Save one assessment response")
async def save_assessment_response(
    assessment_id: str,
    payload: SaveAssessmentResponsePayload,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    existing_query = """
        select response_id
        from assessment_responses
        where assessment_id = :assessment_id and question_id = :question_id
    """
    existing = await session.execute(text(existing_query), {"assessment_id": assessment_id, "question_id": payload.question_id})
    existing_row = existing.mappings().first()

    if existing_row:
        update_query = """
            update assessment_responses
            set response_value = :response_value,
                score_value = :score_value,
                answered_by = :answered_by,
                updated_at = now()
            where response_id = :response_id
            returning response_id
        """
        res = await session.execute(text(update_query), {"response_id": existing_row["response_id"], "response_value": payload.response_value, "score_value": payload.score_value, "answered_by": user_ctx.user_id})
    else:
        insert_query = """
            insert into assessment_responses (assessment_id, question_id, control_id, response_value, score_value, answered_by)
            values (:assessment_id, :question_id, :control_id, :response_value, :score_value, :answered_by)
            returning response_id
        """
        res = await session.execute(text(insert_query), {"assessment_id": assessment_id, "question_id": payload.question_id, "control_id": payload.control_id, "response_value": payload.response_value, "score_value": payload.score_value, "answered_by": user_ctx.user_id})
    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="assessment_response_saved",
        entity_type="assessment",
        entity_id=assessment_id,
        action_details={"question_id": payload.question_id, "control_id": payload.control_id},
    )
    await session.commit()
    return {"status": "saved", "question_id": payload.question_id, "response_value": payload.response_value}


@router.post("/{assessment_id}/submit", summary="Submit an assessment and generate compliance gaps")
async def submit_assessment(
    assessment_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_ASSESSMENTS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    assessment_query = """
        update assessments
        set assessment_status = 'completed', completed_at = now()
        where assessment_id = :assessment_id and institution_id = :inst_id
        returning assessment_id, assessment_name, framework_name
    """
    assessment_res = await session.execute(text(assessment_query), {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id})
    assessment_row = assessment_res.mappings().first()
    if not assessment_row:
        raise HTTPException(status_code=404, detail="Assessment not found")

    responses_query = """
        select response_value, control_id
        from assessment_responses
        where assessment_id = :assessment_id
    """
    responses_res = await session.execute(text(responses_query), {"assessment_id": assessment_id})
    responses = responses_res.mappings().all()

    yes_count = sum(1 for row in responses if str(row["response_value"]).lower() in {"yes", "fully implemented"})
    percentage = round((yes_count / max(len(responses), 1)) * 100, 2) if responses else 0.0

    await session.execute(
        text(
            """
            delete from compliance_results
            where assessment_id = :assessment_id and institution_id = :inst_id
            """
        ),
        {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id},
    )
    await session.execute(
        text(
            """
            delete from compliance_gaps
            where assessment_id = :assessment_id and institution_id = :inst_id
            """
        ),
        {"assessment_id": assessment_id, "inst_id": user_ctx.institution_id},
    )

    result_query = """
        insert into compliance_results (assessment_id, institution_id, framework_name, compliance_percentage, compliant_controls, partial_controls, non_compliant_controls, critical_gap_count)
        values (:assessment_id, :inst_id, :framework_name, :percentage, :compliant, :partial, :non_compliant, :critical)
        returning result_id
    """
    await session.execute(
        text(result_query),
        {
            "assessment_id": assessment_id,
            "inst_id": user_ctx.institution_id,
            "framework_name": assessment_row["framework_name"],
            "percentage": percentage,
            "compliant": yes_count,
            "partial": 0,
            "non_compliant": max(len(responses) - yes_count, 0),
            "critical": 0,
        },
    )

    gaps = []
    for row in responses:
        value = str(row["response_value"]).lower()
        if value in {"no", "partial", "not implemented"}:
            severity = "high" if value in {"no", "not implemented"} else "medium"
            gaps.append((row["control_id"], severity))
    for control_id, severity in gaps:
        await session.execute(
            text(
                """
                insert into compliance_gaps (assessment_id, institution_id, control_id, framework_name, severity, title, description, remediation_status)
                values (:assessment_id, :inst_id, :control_id, :framework_name, :severity, :title, :description, 'open')
                """
            ),
            {
                "assessment_id": assessment_id,
                "inst_id": user_ctx.institution_id,
                "control_id": control_id,
                "framework_name": assessment_row["framework_name"],
                "severity": severity,
                "title": f"Follow-up required for {control_id}",
                "description": "Assessment response indicates a gap that requires remediation.",
            },
        )

    await AuditLogRepository(session).write(
        institution_id=user_ctx.institution_id,
        user_id=user_ctx.user_id,
        active_role_id=user_ctx.active_role_id,
        action_type="assessment_submitted",
        entity_type="assessment",
        entity_id=assessment_id,
        action_details={"gap_count": len(gaps), "compliance_percentage": percentage},
    )
    await session.commit()
    return {
        "assessment_id": str(assessment_row["assessment_id"]),
        "assessment_status": "completed",
        "compliance_percentage": percentage,
        "gap_count": len(gaps),
    }
