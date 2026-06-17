# Use: Router for user authentication endpoints (login, register, logout, refresh, password reset).

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db_session
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
    UserContext,
    UpdateProfileRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=LoginResponse,
    summary="Register a new user account",
    status_code=201,
)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Create a user account within an existing institution.

    Requires a valid ``institution_id`` and ``role_id`` — both must already
    exist in the database (seeded by Super Admin or pre-provisioned).
    Returns a full token pair: the user is immediately logged in after registration.
    """
    return await AuthService(session).register(payload, request)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and receive JWT token pair",
)
async def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Authenticate with email and password.

    - Returns access + refresh tokens on success.
    - After 3 consecutive failures the account is blocked for 5 minutes.
      Each failure and the block event are recorded in ``audit_logs``.
    """
    return await AuthService(session).login(payload, request)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Invalidate the current session",
)
async def logout(
    request: Request,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """Delete the active session from ``user_sessions``.

    The access token remains technically valid until it expires, but the session
    row is gone so ``get_current_user`` will reject it on the next request.
    """
    return await AuthService(session).logout(user, request)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Rotate refresh token and obtain a new token pair",
)
async def refresh(
    payload: TokenRefreshRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Exchange a valid refresh token for a brand-new access + refresh token pair.

    Refresh token rotation is applied: the existing session is deleted and a new
    session row is inserted, invalidating the previous refresh token.
    """
    return await AuthService(session).refresh(payload, request)


@router.get(
    "/me",
    response_model=UserContext,
    summary="Return the currently authenticated user context",
)
async def me(
    user: Annotated[UserContext, Depends(get_current_user)],
) -> UserContext:
    """Return the full user context including institution, active role, and permissions.

    Useful for the frontend to hydrate its auth store after page refresh.
    """
    return user


@router.patch(
    "/me",
    response_model=MessageResponse,
    summary="Update own profile (full_name, phone, designation)",
)
async def update_me(
    payload: UpdateProfileRequest,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """Allow the authenticated user to update their own profile fields."""
    from app.repositories.users import UserRepository

    repo = UserRepository(session)
    await repo.update_profile(
        user.user_id,
        full_name=payload.full_name,
        phone=payload.phone,
        designation=payload.designation,
    )
    from app.repositories.audit import AuditLogRepository

    await AuditLogRepository(session).write(
        institution_id=user.institution_id,
        user_id=user.user_id,
        active_role_id=user.active_role_id,
        action_type="profile_update",
        entity_type="users",
        entity_id=user.user_id,
    )
    await session.commit()
    return MessageResponse(message="Profile updated successfully")


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request a password reset link",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ForgotPasswordResponse:
    """Generate a single-use, 5-minute password reset token.

    If SMTP is configured the token is emailed and ``email_sent=True`` is returned.
    If SMTP is unavailable ``email_sent=False`` and ``reset_url`` are returned —
    the frontend must automatically redirect the user to the reset page using that URL.

    The response is identical whether or not the email address is registered
    (prevents user enumeration). When the email is not found, ``reset_url`` is
    always ``null`` regardless of SMTP state.
    """
    return await AuthService(session).forgot_password(payload, request)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Set a new password using a reset token",
)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """Consume a password-reset token and set a new password.

    - Token is single-use and expires 5 minutes after creation.
    - On success all existing sessions are revoked (user must log in again).
    - The token is consumed atomically — replaying the same token returns 401.
    """
    return await AuthService(session).reset_password(payload, request)
