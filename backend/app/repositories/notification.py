# Use: Repository handling system notifications.

from __future__ import annotations

from typing import Any

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
