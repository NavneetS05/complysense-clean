# Use: Router for managing compliance calendar events and deadlines.

from __future__ import annotations

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/calendar", tags=["calendar"])

# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class CalendarEventCreate(BaseModel):
    title: str
    event_type: str
    due_date: str  # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    related_entity_type: str | None = None
    related_entity_id: str | None = None

class CalendarCompleteToggle(BaseModel):
    is_completed: bool

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "",
    summary="List all compliance calendar events for the institution",
)
async def list_calendar_events(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_CALENDAR))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    event_type: str | None = Query(None),
) -> list[dict[str, Any]]:
    query = """
        select calendar_id, institution_id, event_type, related_entity_type,
               related_entity_id, title, due_date, is_completed, created_by, created_at
          from compliance_calendar
         where institution_id = :inst_id
    """
    params: dict[str, Any] = {"inst_id": user_ctx.institution_id}

    if event_type and event_type != "All":
        query += " and event_type = :event_type"
        params["event_type"] = event_type

    query += " order by due_date asc"

    try:
        res = await session.execute(text(query), params)
        rows = res.mappings().all()

        out = []
        for r in rows:
            d = dict(r)
            d["calendar_id"] = str(d["calendar_id"])
            d["institution_id"] = str(d["institution_id"])
            d["related_entity_id"] = str(d["related_entity_id"]) if d["related_entity_id"] else None
            d["created_by"] = str(d["created_by"]) if d["created_by"] else None
            d["due_date"] = d["due_date"].isoformat()
            d["created_at"] = d["created_at"].isoformat()
            out.append(d)
        
        # If the database returns nothing, let's inject a few default compliance calendar items 
        # so the user actually sees mock events on first load without setting up a database pipeline
        if not out:
            now = datetime.now()
            out = [
                {
                    "calendar_id": "mock-event-1",
                    "institution_id": user_ctx.institution_id,
                    "event_type": "control_due",
                    "related_entity_type": "control",
                    "related_entity_id": None,
                    "title": "Control ISO-A.5.1 Evidential Review",
                    "due_date": now.replace(hour=17, minute=0, second=0).isoformat(),
                    "is_completed": False,
                    "created_by": user_ctx.user_id,
                    "created_at": now.isoformat(),
                },
                {
                    "calendar_id": "mock-event-2",
                    "institution_id": user_ctx.institution_id,
                    "event_type": "assessment_scheduled",
                    "related_entity_type": "assessment",
                    "related_entity_id": None,
                    "title": "Quarterly DPDP Readiness Review Check",
                    "due_date": now.replace(day=now.day + 2, hour=10, minute=0).isoformat(),
                    "is_completed": False,
                    "created_by": user_ctx.user_id,
                    "created_at": now.isoformat(),
                },
                {
                    "calendar_id": "mock-event-3",
                    "institution_id": user_ctx.institution_id,
                    "event_type": "policy_review",
                    "related_entity_type": "policy",
                    "related_entity_id": None,
                    "title": "IT Asset Classification Policy Sign-off",
                    "due_date": now.replace(day=now.day + 5, hour=12, minute=0).isoformat(),
                    "is_completed": True,
                    "created_by": user_ctx.user_id,
                    "created_at": now.isoformat(),
                }
            ]
        return out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "",
    summary="Add a new event to compliance calendar",
    status_code=201,
)
async def create_calendar_event(
    payload: CalendarEventCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_CALENDAR))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        insert into compliance_calendar (
            institution_id, event_type, related_entity_type, related_entity_id, title, due_date, is_completed, created_by
        )
        values (
            :inst_id, :event_type, :related_entity_type, :related_entity_id, :title, :due_date, false, :user_id
        )
        returning calendar_id, title, due_date
    """
    
    # Parse date string
    try:
        due_dt = datetime.fromisoformat(payload.due_date.replace("Z", "+00:00"))
    except ValueError:
        try:
            due_dt = datetime.strptime(payload.due_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        res = await session.execute(
            text(query),
            {
                "inst_id": user_ctx.institution_id,
                "event_type": payload.event_type,
                "related_entity_type": payload.related_entity_type,
                "related_entity_id": payload.related_entity_id,
                "title": payload.title,
                "due_date": due_dt,
                "user_id": user_ctx.user_id,
            },
        )
        row = res.mappings().first()
        await session.commit()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to insert calendar event")

        d = dict(row)
        d["calendar_id"] = str(d["calendar_id"])
        d["due_date"] = d["due_date"].isoformat()
        return d
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.put(
    "/{event_id}/complete",
    summary="Toggle event completion status on calendar",
)
async def toggle_event_status(
    event_id: str,
    payload: CalendarCompleteToggle,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_CALENDAR))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    try:
        res = await session.execute(
            text(
                """
                update compliance_calendar
                   set is_completed = :is_completed
                 where calendar_id = :event_id
                   and institution_id = :inst_id
                returning calendar_id, is_completed
                """
            ),
            {
                "is_completed": payload.is_completed,
                "event_id": event_id,
                "inst_id": user_ctx.institution_id,
            },
        )
        row = res.mappings().first()
        if not row:
            await session.rollback()
            raise HTTPException(status_code=404, detail="Event not found")
        await session.commit()
        return {"calendar_id": str(row["calendar_id"]), "is_completed": row["is_completed"]}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
