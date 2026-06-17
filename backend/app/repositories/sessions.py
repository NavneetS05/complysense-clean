# Use: Repository managing user sessions and active role assumptions in PostgreSQL.

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: str,
        active_role_id: str,
        user_agent: str | None,
        ip_address: str | None,
        expires_at: datetime,
    ) -> str:
        """Insert a new user session and return the session_id UUID."""
        result = await self.session.execute(
            text(
                """
                insert into user_sessions (user_id, active_role_id, user_agent, ip_address, expires_at)
                values (:user_id, :active_role_id, :user_agent, :ip_address, :expires_at)
                returning session_id
                """
            ),
            {
                "user_id": user_id,
                "active_role_id": active_role_id,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "expires_at": expires_at,
            },
        )
        return str(result.scalar_one())

    async def find_active(self, session_id: str) -> dict[str, Any] | None:
        """Return a session row joined with role name if still valid (not expired)."""
        result = await self.session.execute(
            text(
                """
                select s.session_id, s.user_id, s.active_role_id, r.role_name,
                       s.expires_at
                  from user_sessions s
                  join roles r on r.role_id = s.active_role_id
                 where s.session_id = :session_id
                   and (s.expires_at is null or s.expires_at > current_timestamp)
                 limit 1
                """
            ),
            {"session_id": session_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def delete(self, session_id: str) -> None:
        """Remove a session row, effectively logging the user out / revoking the token."""
        await self.session.execute(
            text(
                """
                delete from user_sessions
                 where session_id = :session_id
                """
            ),
            {"session_id": session_id},
        )

    async def delete_all_for_user(self, user_id: str) -> None:
        """Remove every session for a user — used on password change or account block."""
        await self.session.execute(
            text(
                """
                delete from user_sessions
                 where user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )

    async def update_role(self, session_id: str, active_role_id: str) -> None:
        """Update the active role on an existing session (role assumption flow)."""
        await self.session.execute(
            text(
                """
                update user_sessions
                   set active_role_id = :active_role_id
                 where session_id = :session_id
                """
            ),
            {"session_id": session_id, "active_role_id": active_role_id},
        )
