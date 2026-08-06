# Use: Repository handling system notifications.

from __future__ import annotations

from typing import Any
from uuid import uuid4

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
        notification_id = str(uuid4())
        await self.session.execute(
            text(
                """
                insert into notifications (
                    notification_id, institution_id, user_id, title, message,
                    notification_type, related_entity_type, related_entity_id
                ) values (
                    :notification_id, :institution_id, :user_id, :title, :message,
                    :notification_type, :related_entity_type, :related_entity_id
                )
                """
            ),
            {
                "notification_id": notification_id,
                "institution_id": institution_id,
                "user_id": user_id,
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "related_entity_type": related_entity_type,
                "related_entity_id": related_entity_id,
            },
        )

    async def create_many(
        self,
        *,
        institution_id: str,
        user_ids: list[str],
        title: str,
        message: str | None = None,
        notification_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> None:
        if not user_ids:
            return
        params = [
            {
                "notification_id": str(uuid4()),
                "institution_id": institution_id,
                "user_id": uid,
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "related_entity_type": related_entity_type,
                "related_entity_id": related_entity_id,
            }
            for uid in user_ids
        ]
        await self.session.execute(
            text(
                """
                insert into notifications (
                    notification_id, institution_id, user_id, title, message,
                    notification_type, related_entity_type, related_entity_id
                ) values (
                    :notification_id, :institution_id, :user_id, :title, :message,
                    :notification_type, :related_entity_type, :related_entity_id
                )
                """
            ),
            params,
        )

    async def create_for_role(
        self,
        *,
        institution_id: str,
        role_name: str,
        title: str,
        message: str | None = None,
        notification_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> None:
        result = await self.session.execute(
            text(
                """
                select u.user_id
                from users u
                join roles r on u.role_id = r.role_id
                where u.institution_id = :institution_id
                  and r.role_name = :role_name
                """
            ),
            {"institution_id": institution_id, "role_name": role_name},
        )
        user_ids = [str(row["user_id"]) for row in result.mappings().all()]
        await self.create_many(
            institution_id=institution_id,
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=notification_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
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
