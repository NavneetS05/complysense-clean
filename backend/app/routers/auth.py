# Use: Router for user authentication endpoints (login, register, logout, refresh, password reset).

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.deps import get_current_user
from app.core.exceptions import UnauthorizedError
from app.database import get_db_session
from app.schemas.auth import (
    AssumeRoleRequest,
    ChangePasswordRequest,
    ExitRoleAssumptionResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserContext,
    UpdateProfileRequest,
    ValidateResetTokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _refresh_cookie_path() -> str:
    return f"/api/{get_settings().api_version}/auth"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path=_refresh_cookie_path(),
    )


def _clear_refresh_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=_refresh_cookie_path(),
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )


@router.post(
    "/register",
    response_model=LoginResponse,
    summary="Register a new user account",
    status_code=201,
)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Create a user account within an existing institution.

    Requires a valid ``institution_id`` and ``role_id`` — both must already
    exist in the database (seeded by Super Admin or pre-provisioned).
    Returns a full token pair: the user is immediately logged in after registration.
    """
    result = await AuthService(session).register(payload, request)
    _set_refresh_cookie(response, result.refresh_token)
    return result.response


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and receive JWT token pair",
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Authenticate with email and password.

    - Returns access + refresh tokens on success.
    - After 3 consecutive failures the account is blocked for 5 minutes.
      Each failure and the block event are recorded in ``audit_logs``.
    """
    result = await AuthService(session).login(payload, request)
    _set_refresh_cookie(response, result.refresh_token)
    return result.response


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Invalidate the current session",
)
async def logout(
    request: Request,
    response: Response,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """Delete the active session from ``user_sessions``.

    The access token remains technically valid until it expires, but the session
    row is gone so ``get_current_user`` will reject it on the next request.
    """
    result = await AuthService(session).logout(user, request)
    _clear_refresh_cookie(response)
    return result


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Rotate refresh token and obtain a new token pair",
)
async def refresh(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    refresh_cookie: Annotated[str | None, Cookie(alias=get_settings().refresh_cookie_name)] = None,
) -> LoginResponse:
    """Exchange a valid refresh token for a brand-new access + refresh token pair.

    Refresh token rotation is applied: the existing session is deleted and a new
    session row is inserted, invalidating the previous refresh token.
    """
    if not refresh_cookie:
        raise UnauthorizedError("Missing refresh token")
    result = await AuthService(session).refresh(refresh_cookie, request)
    _set_refresh_cookie(response, result.refresh_token)
    return result.response


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
    "/change-password",
    response_model=MessageResponse,
    summary="Change password for current logged in user",
)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """Allow any authenticated user to change their password."""
    return await AuthService(session).change_password(
        user=user,
        current_pass=payload.current_password,
        new_pass=payload.new_password,
        request=request,
    )


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


@router.get(
    "/validate-reset-token",
    response_model=ValidateResetTokenResponse,
    summary="Check whether a password-reset token is valid (non-destructive)",
)
async def validate_reset_token(
    token: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ValidateResetTokenResponse:
    """Peek at a password-reset token without consuming it.

    Returns ``{ "valid": true, "email": "user@example.com" }`` when the token
    exists, is unused, and has not expired.  Returns ``{ "valid": false }``
    otherwise.  The Reset Password screen calls this on mount to decide
    whether to show the reset form or an "invalid link" error state.
    """
    return await AuthService(session).validate_reset_token(token)


@router.post(
    "/assume-role",
    response_model=ExitRoleAssumptionResponse,
    summary="Temporarily assume another role for review purposes",
)
async def assume_role(
    payload: AssumeRoleRequest,
    request: Request,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExitRoleAssumptionResponse:
    """Allow a Super Admin or Institution Admin to temporarily assume another role.

    The session's ``active_role_id`` is updated to the target role so subsequent
    requests use the assumed role's permissions.  A fresh ``UserContext`` is
    returned so the frontend can re-hydrate its auth store immediately.

    Use ``POST /exit-role-assumption`` to revert back to the primary role.
    """
    return await AuthService(session).assume_role(user, payload, request)


@router.post(
    "/exit-role-assumption",
    response_model=ExitRoleAssumptionResponse,
    summary="Exit an active role assumption and restore the primary role",
)
async def exit_role_assumption(
    request: Request,
    user: Annotated[UserContext, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExitRoleAssumptionResponse:
    """Restore the authenticated user's session to their primary (native) role.

    When a Super Admin or Institution Admin temporarily assumes another role
    for review purposes, this endpoint exits that assumption. The session's
    ``active_role_id`` is reset to the user's own ``role_id``, an audit event
    is written, and a fresh ``UserContext`` (with restored permissions) is
    returned so the frontend can re-hydrate its auth store without a
    separate refresh call.

    Calling this when no role assumption is active is a safe no-op.
    """
    return await AuthService(session).exit_role_assumption(user, request)
