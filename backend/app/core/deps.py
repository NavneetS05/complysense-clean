# Use: Defines common FastAPI dependencies such as database sessions and current authenticated user retrieval.

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.database import get_db_session
from app.repositories.rbac import RbacRepository
from app.repositories.sessions import SessionRepository
from app.schemas.auth import UserContext

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserContext:
    """FastAPI dependency that resolves and validates the current authenticated user.

    Flow:
        1. Extract Bearer token from Authorization header.
        2. Decode and verify JWT signature / expiry.
        3. Look up the session_id in user_sessions — confirms the session is active
           and has not been logged out or rotated away.
        4. Fetch full user + active role context from users + roles tables.
        5. Load permission list for the active role.

    Raises UnauthorizedError (HTTP 401) on any failure.
    """
    if credentials is None:
        raise UnauthorizedError()
    try:
        claims = decode_token(credentials.credentials)
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    # Must be an access token, not a refresh token
    if claims.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = str(claims.get("sub", ""))
    session_id = str(claims.get("session_id", ""))
    if not user_id or not session_id:
        raise UnauthorizedError()

    session_record = await SessionRepository(session).find_active(session_id)
    if not session_record or str(session_record["user_id"]) != user_id:
        raise UnauthorizedError("Session has expired or been revoked")

    result = await session.execute(
        text(
            """
            select u.user_id, u.institution_id, i.institution_name, u.role_id,
                   primary_role.role_name,
                   active_role.role_name   as active_role_name,
                   u.email, u.full_name, u.phone, u.designation, u.is_active
              from users u
              left join institutions i on i.institution_id = u.institution_id
              join roles primary_role on primary_role.role_id = u.role_id
              join roles active_role  on active_role.role_id  = :active_role_id
             where u.user_id = :user_id
               and u.is_active = true
            """
        ),
        {"user_id": user_id, "active_role_id": str(session_record["active_role_id"])},
    )
    row = result.mappings().first()
    if not row:
        raise UnauthorizedError("User account is inactive or does not exist")

    permissions = await RbacRepository(session).permissions_for_role(
        str(session_record["active_role_id"])
    )
    return UserContext(
        user_id=str(row["user_id"]),
        institution_id=str(row["institution_id"]),
        institution_name=str(row["institution_name"]) if row["institution_name"] else None,
        role_id=str(row["role_id"]),
        role_name=str(row["role_name"]),
        active_role_id=str(session_record["active_role_id"]),
        active_role_name=str(row["active_role_name"]),
        email=str(row["email"]),
        full_name=str(row["full_name"]) if row["full_name"] else None,
        phone=str(row["phone"]) if row["phone"] else None,
        designation=str(row["designation"]) if row["designation"] else None,
        permissions=permissions,
        session_id=session_id,
    )


def get_request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None
