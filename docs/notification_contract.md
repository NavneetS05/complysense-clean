# ComplySense Backend Contract
## Notifications — API & Repository Specification

Status: Ready to implement. Schema and pattern already exist — this is not a design task, it's a build task.

---

### 1. Why this exists

`frontend/src/components/shared/Topbar.tsx` polls `GET /api/v1/notifications` every 30 seconds and calls `PATCH /api/v1/notifications/read-all` on demand. `frontend/src/components/shared/Sidebar.tsx` reads `unreadCount` from `useNotificationStore` to render badge counts. Both currently fail silently (`catch { /* ignore */ }`), meaning the frontend is already built defensively for this endpoint to not exist yet.

`backend/app/routers/notifications.py` is currently a router with no handlers:

```python
router = APIRouter(prefix="/notifications", tags=["notifications"])
```

No handler exists for either call. This doc specifies exactly what needs to be added.

---

### 2. Database schema (verified, already exists in `schema.sql` — no migration needed)

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID REFERENCES institutions(institution_id),
    user_id         UUID REFERENCES users(user_id),
    title           VARCHAR(255) NOT NULL,
    message         TEXT,
    notification_type VARCHAR(100),
    related_entity_type VARCHAR(100),
    related_entity_id   UUID,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
```

Note: there is no `meta` / JSONB column on this table. Any notification content beyond `title` and `message` must fit into `related_entity_type` + `related_entity_id`, or the schema needs a follow-up migration — do not invent a `meta` field in the API response without adding the column first.

---

### 3. `NotificationRepository`

Model this directly on the existing `AuditLogRepository` pattern (`backend/app/repositories/audit.py`) — same constructor shape, same session-scoped, same institution-filtered query style.

```python
# backend/app/repositories/notification.py

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        institution_id: str,
        user_id: str,
        title: str,
        message: str | None = None,
        notification_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> None:
        """Insert a notification row for a single user."""
        await self.session.execute(
            text(
                """
                insert into notifications (
                    institution_id, user_id, title, message,
                    notification_type, related_entity_type, related_entity_id
                ) values (
                    :institution_id, :user_id, :title, :message,
                    :notification_type, :related_entity_type, :related_entity_id
                )
                """
            ),
            {
                "institution_id": institution_id,
                "user_id": user_id,
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "related_entity_type": related_entity_type,
                "related_entity_id": related_entity_id,
            },
        )

    async def list_for_user(
        self,
        *,
        institution_id: str,
        user_id: str,
        limit: int = 10,
        unread_only: bool = False,
    ) -> list[dict[str, Any]]:
        where_unread = "and is_read = false" if unread_only else ""
        result = await self.session.execute(
            text(
                f"""
                select notification_id, title, message, notification_type,
                       related_entity_type, related_entity_id, is_read, created_at
                from notifications
                where institution_id = :institution_id
                  and user_id = :user_id
                  {where_unread}
                order by created_at desc
                limit :limit
                """
            ),
            {"institution_id": institution_id, "user_id": user_id, "limit": limit},
        )
        return [dict(row) for row in result.mappings().all()]

    async def unread_count(self, *, institution_id: str, user_id: str) -> int:
        result = await self.session.execute(
            text(
                """
                select count(*) as cnt
                from notifications
                where institution_id = :institution_id
                  and user_id = :user_id
                  and is_read = false
                """
            ),
            {"institution_id": institution_id, "user_id": user_id},
        )
        row = result.mappings().first()
        return int(row["cnt"]) if row else 0

    async def mark_all_read(self, *, institution_id: str, user_id: str) -> int:
        """Marks all unread notifications as read. Returns count of rows updated."""
        result = await self.session.execute(
            text(
                """
                update notifications
                set is_read = true
                where institution_id = :institution_id
                  and user_id = :user_id
                  and is_read = false
                """
            ),
            {"institution_id": institution_id, "user_id": user_id},
        )
        return result.rowcount
```

Caller is responsible for `session.commit()`, matching the existing pattern used by `AuditLogRepository` call sites (see `vendor.py`).

---

### 4. `GET /api/v1/notifications`

**Query params** (both required by current frontend usage — confirmed from `Topbar.tsx`):

| param | type | default | notes |
|---|---|---|---|
| `limit` | int | 10 | matches frontend call `{ limit: 10, unread: true }` |
| `unread` | bool | false | when true, only unread rows returned |

**Response shape:**

```json
{
  "notifications": [
    {
      "notification_id": "uuid-string",
      "title": "string",
      "message": "string | null",
      "notification_type": "string | null",
      "related_entity_type": "string | null",
      "related_entity_id": "uuid-string | null",
      "is_read": false,
      "created_at": "2026-07-17T10:32:00Z"
    }
  ],
  "unread_count": 3
}
```

This exactly matches what `Topbar.tsx` already destructures:
```ts
setNotifications(res.data.notifications ?? []);
setUnreadCount(res.data.unread_count ?? 0);
```

**Handler implementation:**

```python
@router.get("", summary="List notifications for the current user")
async def list_notifications(
    limit: int = 10,
    unread: bool = False,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_OWN_NOTIFICATIONS))] = ...,
    session: Annotated[AsyncSession, Depends(get_db_session)] = ...,
) -> dict[str, Any]:
    repo = NotificationRepository(session)
    notifications = await repo.list_for_user(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        limit=limit,
        unread_only=unread,
    )
    unread_count = await repo.unread_count(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )
    return {"notifications": notifications, "unread_count": unread_count}
```

Note: `PermissionKey.VIEW_OWN_NOTIFICATIONS` is assumed to not yet exist in `app.domain.rbac`. Verify this permission key exists or needs adding — every other route in this codebase gates on a specific `PermissionKey`, so this should follow the same convention rather than being left ungated.

---

### 5. `PATCH /api/v1/notifications/read-all`

**Request body:** none.

**Response shape:**

```json
{ "message": "ok" }
```

**Handler implementation:**

```python
@router.patch("/read-all", summary="Mark all notifications as read for current user")
async def mark_all_read(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_OWN_NOTIFICATIONS))] = ...,
    session: Annotated[AsyncSession, Depends(get_db_session)] = ...,
) -> dict[str, str]:
    repo = NotificationRepository(session)
    await repo.mark_all_read(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )
    await session.commit()
    return {"message": "ok"}
```

Matches current frontend usage exactly:
```ts
await api.patch("/api/v1/notifications/read-all");
markAllRead();  // local store update, doesn't depend on response body content
```

---

### 6. Event-emission mapping — where `NotificationRepository.create()` needs to be called

This is the part that requires wiring into existing write paths, not just adding the two endpoints above. Without this, the table exists and the API works, but nothing ever populates it.

| Event | Trigger location | `notification_type` | `related_entity_type` | Recipient |
|---|---|---|---|---|
| Control assigned | control assignment creation | `control_assigned` | `control_assignment` | assigned user |
| Evidence submitted | evidence upload | `evidence_submitted` | `evidence` | control's reviewing officer |
| Evidence approved | evidence status update | `evidence_approved` | `evidence` | evidence uploader |
| Evidence rejected | evidence status update | `evidence_rejected` | `evidence` | evidence uploader |
| Incident logged | incident creation | `incident_logged` | `incident` | assigned IT security officer |
| Incident CERT-In deadline approaching | scheduled job (see note below) | `cert_in_deadline_warning` | `incident` | assigned officer |
| Policy pending approval | policy submission | `policy_pending` | `generated_policies` | policy approver |
| Vendor risk flagged | vendor risk assessment creation (`vendor.py`, already calls `AuditLogRepository.write` — add a `NotificationRepository.create` call alongside it) | `vendor_risk_flagged` | `vendor_risk_assessment` | vendor reviewer |
| Task assigned | task creation | `task_assigned` | `task` | assigned user |
| Task overdue | scheduled job (see note below) | `task_overdue` | `task` | assigned user |

**Open question, not yet resolved:** Two rows above depend on a scheduled/cron job (CERT-In deadline warning, task overdue) rather than a discrete write-time event, since nothing "happens" at the moment a deadline approaches — time just passes. No scheduler (Celery beat, APScheduler, or similar) has been confirmed to exist in this codebase yet. This needs a decision before those two rows can be implemented — flag this to your guide/lead as an infra dependency, not something this doc can resolve on its own.

**Implementation pattern** — mirror how `AuditLogRepository.write()` is called inline at existing write points (confirmed working example in `backend/app/routers/ai/vendor.py`):

```python
await NotificationRepository(session).create(
    institution_id=str(user_ctx.institution_id),
    user_id=str(assigned_user_id),
    title="Vendor risk assessment flagged",
    message=f"New risk assessment created for vendor {vendor_name}",
    notification_type="vendor_risk_flagged",
    related_entity_type="vendor_risk_assessment",
    related_entity_id=str(assessment_row["vendor_risk_id"]),
)
```

Should be called in the same transaction as the `AuditLogRepository.write()` call, before `session.commit()`.