# Use: Repository for querying active user details, creating users, login throttling, password resets.

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # LOOKUP
    # ------------------------------------------------------------------

    async def find_active_by_email(self, email: str) -> dict[str, Any] | None:
        """Return a user row joined with role name.
        Includes throttling columns (failed_login_attempts, blocked_until).
        """
        result = await self.session.execute(
            text(
                """
                select u.user_id, u.institution_id, i.institution_name, u.role_id, r.role_name,
                       u.full_name, u.email, u.password_hash, u.is_active,
                       u.failed_login_attempts, u.blocked_until
                  from users u
                  join roles r on r.role_id = u.role_id
                  left join institutions i on i.institution_id = u.institution_id
                 where lower(u.email) = lower(:email)
                   and u.is_active = true
                 limit 1
                """
            ),
            {"email": email},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Return full user profile row by primary key."""
        result = await self.session.execute(
            text(
                """
                select u.user_id, u.institution_id, i.institution_name, u.role_id, r.role_name,
                       u.full_name, u.email, u.phone, u.designation,
                       u.is_active, u.created_at, u.updated_at
                  from users u
                  join roles r on r.role_id = u.role_id
                  left join institutions i on i.institution_id = u.institution_id
                 where u.user_id = :user_id
                 limit 1
                """
            ),
            {"user_id": user_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def find_by_email_any_status(self, email: str) -> dict[str, Any] | None:
        """Return user by email regardless of is_active — used for password reset."""
        result = await self.session.execute(
            text(
                """
                select u.user_id, u.institution_id, u.role_id,
                       u.full_name, u.email, u.is_active
                  from users u
                 where lower(u.email) = lower(:email)
                 limit 1
                """
            ),
            {"email": email},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def find_by_institution(
        self, institution_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List all users belonging to a specific institution."""
        result = await self.session.execute(
            text(
                """
                select u.user_id, u.institution_id, u.role_id, r.role_name,
                       u.full_name, u.email, u.phone, u.designation,
                       u.is_active, u.last_login, u.created_at
                  from users u
                  join roles r on r.role_id = u.role_id
                 where u.institution_id = :institution_id
                 order by u.created_at desc
                 limit :limit offset :offset
                """
            ),
            {"institution_id": institution_id, "limit": limit, "offset": offset},
        )
        return [dict(row) for row in result.mappings().all()]

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        institution_id: str,
        role_id: str,
        full_name: str,
        email: str,
        password_hash: str,
        phone: str | None = None,
        designation: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new user and return the full row."""
        result = await self.session.execute(
            text(
                """
                insert into users (
                    institution_id, role_id, full_name, email, password_hash,
                    phone, designation
                )
                values (
                    :institution_id, :role_id, :full_name, :email, :password_hash,
                    :phone, :designation
                )
                returning user_id, institution_id, role_id, full_name, email,
                          phone, designation, is_active, created_at
                """
            ),
            {
                "institution_id": institution_id,
                "role_id": role_id,
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "phone": phone,
                "designation": designation,
            },
        )
        row = result.mappings().first()
        return dict(row)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # UPDATE — PROFILE
    # ------------------------------------------------------------------

    async def update_profile(
        self,
        user_id: str,
        *,
        full_name: str | None = None,
        phone: str | None = None,
        designation: str | None = None,
    ) -> None:
        """Partial update of user profile fields that are provided (non-None)."""
        await self.session.execute(
            text(
                """
                update users
                   set full_name    = coalesce(:full_name, full_name),
                       phone        = coalesce(:phone, phone),
                       designation  = coalesce(:designation, designation),
                       updated_at   = current_timestamp
                 where user_id = :user_id
                """
            ),
            {
                "user_id": user_id,
                "full_name": full_name,
                "phone": phone,
                "designation": designation,
            },
        )

    async def update_last_login(self, user_id: str) -> None:
        await self.session.execute(
            text(
                "update users set last_login = current_timestamp where user_id = :user_id"
            ),
            {"user_id": user_id},
        )

    async def update_password(self, user_id: str, password_hash: str) -> None:
        """Update password hash and reset throttling state."""
        await self.session.execute(
            text(
                """
                update users
                   set password_hash         = :password_hash,
                       failed_login_attempts  = 0,
                       blocked_until          = null,
                       updated_at             = current_timestamp
                 where user_id = :user_id
                """
            ),
            {"user_id": user_id, "password_hash": password_hash},
        )

    async def update_status(self, user_id: str, *, is_active: bool) -> None:
        """Activate or deactivate a user account."""
        await self.session.execute(
            text(
                """
                update users
                   set is_active  = :is_active,
                       updated_at = current_timestamp
                 where user_id = :user_id
                """
            ),
            {"user_id": user_id, "is_active": is_active},
        )

    # ------------------------------------------------------------------
    # LOGIN THROTTLING
    # ------------------------------------------------------------------

    async def increment_failed_attempts(self, user_id: str) -> int:
        """Increment failed_login_attempts and return the new count."""
        result = await self.session.execute(
            text(
                """
                update users
                   set failed_login_attempts = failed_login_attempts + 1,
                       updated_at            = current_timestamp
                 where user_id = :user_id
                returning failed_login_attempts
                """
            ),
            {"user_id": user_id},
        )
        return int(result.scalar_one())

    async def block_user(self, user_id: str, *, blocked_until: datetime) -> None:
        """Set blocked_until to block the user until the specified datetime."""
        await self.session.execute(
            text(
                """
                update users
                   set blocked_until         = :blocked_until,
                       updated_at            = current_timestamp
                 where user_id = :user_id
                """
            ),
            {"user_id": user_id, "blocked_until": blocked_until},
        )

    async def reset_failed_attempts(self, user_id: str) -> None:
        """Reset throttling counters after a successful login."""
        await self.session.execute(
            text(
                """
                update users
                   set failed_login_attempts = 0,
                       blocked_until         = null,
                       updated_at            = current_timestamp
                 where user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )

    # ------------------------------------------------------------------
    # PASSWORD RESET TOKENS
    # ------------------------------------------------------------------

    async def create_reset_token(
        self, user_id: str, token: str, expires_at: datetime
    ) -> str:
        """Insert a password-reset token and return the token_id."""
        result = await self.session.execute(
            text(
                """
                insert into password_reset_tokens (user_id, token, expires_at)
                values (:user_id, :token, :expires_at)
                returning token_id
                """
            ),
            {"user_id": user_id, "token": token, "expires_at": expires_at},
        )
        return str(result.scalar_one())

    async def consume_reset_token(self, token: str) -> dict[str, Any] | None:
        """Find a valid (unused, non-expired) reset token and mark it used atomically.

        Returns the token row (including user_id) on success, None if invalid / expired.
        """
        result = await self.session.execute(
            text(
                """
                update password_reset_tokens
                   set used = true
                 where token      = :token
                   and used       = false
                   and expires_at > current_timestamp
                returning token_id, user_id, expires_at
                """
            ),
            {"token": token},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def invalidate_all_user_tokens(self, user_id: str) -> None:
        """Mark all pending reset tokens for a user as used (one-use-per-reset policy)."""
        await self.session.execute(
            text(
                """
                update password_reset_tokens
                   set used = true
                 where user_id = :user_id
                   and used   = false
                """
            ),
            {"user_id": user_id},
        )

    async def validate_reset_token(self, token: str) -> dict[str, Any] | None:
        """Find a valid (unused, non-expired) reset token without marking it used."""
        result = await self.session.execute(
            text(
                """
                select token_id, pr.user_id, expires_at, u.email
                  from password_reset_tokens pr
                  join users u on u.user_id = pr.user_id
                 where token      = :token
                   and used       = false
                   and expires_at > current_timestamp
                 limit 1
                """
            ),
            {"token": token},
        )
        row = result.mappings().first()
        return dict(row) if row else None
