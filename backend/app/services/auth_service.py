# Use: Service encapsulating business logic for user login, registration, logout,
# token refresh, password reset, and audit logging.

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import UnauthorizedError, LockedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_reset_token,
    hash_password,
    verify_password,
)
from app.repositories.audit import AuditLogRepository
from app.repositories.rbac import RbacRepository
from app.repositories.sessions import SessionRepository
from app.repositories.users import UserRepository
from app.schemas.auth import (
    AssumeRoleRequest,
    ExitRoleAssumptionResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserContext,
    ValidateResetTokenResponse,
)
from app.services.mail_service import MailService

_MAX_ATTEMPTS = 3
_BLOCK_SECONDS = 5 * 60


@dataclass(frozen=True)
class AuthTokenResult:
    response: LoginResponse
    refresh_token: str


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.users = UserRepository(session)
        self.sessions = SessionRepository(session)
        self.rbac = RbacRepository(session)
        self.audit = AuditLogRepository(session)
        self.mail = MailService()

    # ------------------------------------------------------------------
    # REGISTER
    # ------------------------------------------------------------------

    async def register(self, payload: RegisterRequest, request: Request) -> AuthTokenResult:
        """Create a new user account within an existing institution.

        Raises UnauthorizedError if the email is already in use.
        Issues a full token pair on success (user is immediately logged in).
        """
        existing = await self.users.find_by_email_any_status(payload.email)
        if existing:
            raise UnauthorizedError("Email address is already registered")

        new_user = await self.users.create(
            institution_id=payload.institution_id,
            role_id=payload.role_id,
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            phone=payload.phone,
            designation=payload.designation,
        )

        permissions = await self.rbac.permissions_for_role(str(new_user["role_id"]))
        session_id = await self._create_session(
            user_id=str(new_user["user_id"]),
            role_id=str(new_user["role_id"]),
            request=request,
        )

        await self.audit.write(
            institution_id=str(new_user["institution_id"]),
            user_id=str(new_user["user_id"]),
            active_role_id=str(new_user["role_id"]),
            action_type="register",
            entity_type="users",
            entity_id=str(new_user["user_id"]),
            ip_address=_get_ip(request),
        )
        await self.session.commit()

        context = UserContext(
            user_id=str(new_user["user_id"]),
            institution_id=str(new_user["institution_id"]),
            role_id=str(new_user["role_id"]),
            role_name="",  # no join on creation — refreshed on next login
            active_role_id=str(new_user["role_id"]),
            active_role_name="",
            email=str(new_user["email"]),
            permissions=permissions,
            session_id=session_id,
        )
        return self._build_token_pair(context)

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------

    async def login(self, payload: LoginRequest, request: Request) -> AuthTokenResult:
        ip = _get_ip(request)
        user = await self.users.find_active_by_email(payload.email)

        # ---- account not found — generic error to prevent user enumeration ----
        if not user:
            raise UnauthorizedError("Invalid email or password")

        user_id = str(user["user_id"])
        institution_id = str(user["institution_id"])
        role_id = str(user["role_id"])

        # ---- check throttle block ----
        blocked_until: datetime | None = user.get("blocked_until")
        if blocked_until:
            # Make timezone-aware for comparison
            if blocked_until.tzinfo is None:
                blocked_until = blocked_until.replace(tzinfo=UTC)
            if datetime.now(UTC) < blocked_until:
                remaining = int((blocked_until - datetime.now(UTC)).total_seconds() / 60) + 1
                await self.audit.write(
                    institution_id=institution_id,
                    user_id=user_id,
                    active_role_id=role_id,
                    action_type="failed_login",
                    action_details={"reason": "account_blocked", "ip": ip},
                    ip_address=ip,
                )
                await self.session.commit()
                raise LockedError(
                    f"Account is temporarily locked. Try again in {remaining} minute(s).",
                    blocked_until=blocked_until.isoformat(),
                )

        # ---- verify password ----
        if not verify_password(payload.password, str(user["password_hash"])):
            new_count = await self.users.increment_failed_attempts(user_id)

            if new_count >= _MAX_ATTEMPTS:
                blocked_until_dt = datetime.now(UTC) + timedelta(seconds=_BLOCK_SECONDS)
                await self.users.block_user(user_id, blocked_until=blocked_until_dt)
                await self.audit.write(
                    institution_id=institution_id,
                    user_id=user_id,
                    active_role_id=role_id,
                    action_type="user_blocked",
                    action_details={
                        "reason": "max_failed_attempts",
                        "attempts": new_count,
                        "blocked_until": blocked_until_dt.isoformat(),
                        "ip": ip,
                    },
                    ip_address=ip,
                )
            else:
                await self.audit.write(
                    institution_id=institution_id,
                    user_id=user_id,
                    active_role_id=role_id,
                    action_type="failed_login",
                    action_details={"attempts": new_count, "max": _MAX_ATTEMPTS, "ip": ip},
                    ip_address=ip,
                )
            await self.session.commit()
            raise UnauthorizedError("Invalid email or password")

        # ---- successful login ----
        await self.users.reset_failed_attempts(user_id)
        await self.users.update_last_login(user_id)

        permissions = await self.rbac.permissions_for_role(role_id)
        session_id = await self._create_session(
            user_id=user_id, role_id=role_id, request=request
        )

        await self.audit.write(
            institution_id=institution_id,
            user_id=user_id,
            active_role_id=role_id,
            action_type="login",
            entity_type="user_sessions",
            entity_id=session_id,
            ip_address=ip,
        )
        await self.session.commit()

        context = UserContext(
            user_id=user_id,
            institution_id=institution_id,
            role_id=role_id,
            role_name=str(user["role_name"]),
            active_role_id=role_id,
            active_role_name=str(user["role_name"]),
            email=str(user["email"]),
            permissions=permissions,
            session_id=session_id,
        )
        return self._build_token_pair(context)

    # ------------------------------------------------------------------
    # LOGOUT
    # ------------------------------------------------------------------

    async def logout(self, user: UserContext, request: Request) -> MessageResponse:
        await self.sessions.delete(user.session_id)
        await self.audit.write(
            institution_id=user.institution_id,
            user_id=user.user_id,
            active_role_id=user.active_role_id,
            action_type="logout",
            entity_type="user_sessions",
            entity_id=user.session_id,
            ip_address=_get_ip(request),
        )
        await self.session.commit()
        return MessageResponse(message="Logged out successfully")

    # ------------------------------------------------------------------
    # REFRESH TOKEN
    # ------------------------------------------------------------------

    async def refresh(self, refresh_token: str, request: Request) -> AuthTokenResult:
        """Validate the refresh token, rotate session, and return a new token pair.

        Refresh token rotation: old session is deleted, new session is created.
        """
        ip = _get_ip(request)
        try:
            claims = _decode_verified(refresh_token, expected_type="refresh")
        except (JWTError, ValueError) as exc:
            raise UnauthorizedError("Invalid or expired refresh token") from exc

        user_id = str(claims.get("sub", ""))
        session_id = str(claims.get("session_id", ""))
        if not user_id or not session_id:
            raise UnauthorizedError("Malformed refresh token")

        existing_session = await self.sessions.find_active(session_id)
        if not existing_session or str(existing_session["user_id"]) != user_id:
            raise UnauthorizedError("Session not found or expired")

        user = await self.users.find_by_id(user_id)
        if not user or not user.get("is_active"):
            raise UnauthorizedError("User account is inactive")

        role_id = str(existing_session["active_role_id"])
        institution_id = str(user["institution_id"])

        # Rotate: delete old session, create new one
        await self.sessions.delete(session_id)
        new_session_id = await self._create_session(
            user_id=user_id, role_id=role_id, request=request
        )
        permissions = await self.rbac.permissions_for_role(role_id)

        await self.audit.write(
            institution_id=institution_id,
            user_id=user_id,
            active_role_id=role_id,
            action_type="refresh_token",
            entity_type="user_sessions",
            entity_id=new_session_id,
            ip_address=ip,
        )
        await self.session.commit()

        context = UserContext(
            user_id=user_id,
            institution_id=institution_id,
            role_id=str(user["role_id"]),
            role_name=str(user["role_name"]),
            active_role_id=role_id,
            active_role_name=str(existing_session["role_name"]),
            email=str(user["email"]),
            permissions=permissions,
            session_id=new_session_id,
        )
        return self._build_token_pair(context)

    # ------------------------------------------------------------------
    # FORGOT PASSWORD
    # ------------------------------------------------------------------

    async def forgot_password(
        self, payload: ForgotPasswordRequest, request: Request
    ) -> ForgotPasswordResponse:
        """Issue a password-reset token.

        - Looks up user by email (any status, prevents enumeration via same response).
        - Creates a password_reset_tokens row with 5-minute expiry.
        - Attempts SMTP delivery. If it fails, returns reset_url in the response
          so the frontend can open the reset page automatically (inline-redirect fallback).
        """
        ip = _get_ip(request)
        user = await self.users.find_by_email_any_status(payload.email)

        # Always write a log and commit — prevents user enumeration via timing differences
        if not user:
            await self.audit.write(
                institution_id=None,
                user_id=None,
                active_role_id=None,
                action_type="password_reset_requested",
                action_details={"email": payload.email, "found": False, "ip": ip},
                ip_address=ip,
            )
            await self.session.commit()
            # Return generic success to prevent enumeration
            return ForgotPasswordResponse(
                email_sent=False,
                reset_url=None,
                message="If that email address is registered you will receive a reset link shortly.",
            )

        raw_token = generate_reset_token()
        expires_at = datetime.now(UTC) + timedelta(minutes=5)

        # Invalidate any previous pending tokens before creating a new one
        await self.users.invalidate_all_user_tokens(str(user["user_id"]))
        await self.users.create_reset_token(str(user["user_id"]), raw_token, expires_at)

        reset_url = f"{self.settings.frontend_url}/reset-password/{raw_token}"

        await self.audit.write(
            institution_id=str(user["institution_id"]),
            user_id=str(user["user_id"]),
            active_role_id=None,
            action_type="password_reset_requested",
            entity_type="users",
            entity_id=str(user["user_id"]),
            action_details={"email": payload.email, "found": True, "ip": ip},
            ip_address=ip,
        )
        await self.session.commit()

        email_sent = self.mail.send_password_reset(
            to_email=str(user["email"]), reset_url=reset_url
        )

        if email_sent:
            return ForgotPasswordResponse(
                email_sent=True,
                reset_url=None,
                message="Password reset instructions have been sent to your email address.",
            )

        # SMTP unavailable — return the reset URL so the client can redirect automatically
        return ForgotPasswordResponse(
            email_sent=False,
            reset_url=reset_url,
            message=(
                "Email delivery is unavailable. "
                "You will be redirected to the password reset page automatically."
            ),
        )

    # ------------------------------------------------------------------
    # RESET PASSWORD
    # ------------------------------------------------------------------

    async def reset_password(
        self, payload: ResetPasswordRequest, request: Request
    ) -> MessageResponse:
        """Validate the reset token, update password, revoke all sessions.

        Token is consumed (marked used) atomically in the DB — single-use only.
        """
        ip = _get_ip(request)
        token_row = await self.users.consume_reset_token(payload.token)

        if not token_row:
            raise UnauthorizedError("Reset link is invalid or has expired")

        user_id = str(token_row["user_id"])
        user = await self.users.find_by_id(user_id)
        if not user:
            raise UnauthorizedError("Reset link is invalid or has expired")

        await self.users.update_password(user_id, hash_password(payload.new_password))
        # Revoke all active sessions — force re-login everywhere
        await self.sessions.delete_all_for_user(user_id)

        await self.audit.write(
            institution_id=str(user["institution_id"]),
            user_id=user_id,
            active_role_id=None,
            action_type="password_change",
            entity_type="users",
            entity_id=user_id,
            action_details={"method": "reset_token", "ip": ip},
            ip_address=ip,
        )
        await self.session.commit()
        return MessageResponse(message="Password has been reset successfully. Please log in.")

    # ------------------------------------------------------------------
    # VALIDATE RESET TOKEN  (read-only peek — does NOT consume the token)
    # ------------------------------------------------------------------

    async def validate_reset_token(
        self, token: str
    ) -> ValidateResetTokenResponse:
        """Return whether a password-reset token is valid and its associated email.

        Does NOT mark the token as used — that happens only on /reset-password.
        Returns valid=False with email=None for any invalid / expired / used token.
        """
        row = await self.users.validate_reset_token(token)
        if not row:
            return ValidateResetTokenResponse(valid=False, email=None)
        return ValidateResetTokenResponse(valid=True, email=str(row["email"]))

    # ------------------------------------------------------------------
    # EXIT ROLE ASSUMPTION
    # ------------------------------------------------------------------

    async def exit_role_assumption(
        self, user: UserContext, request: Request
    ) -> ExitRoleAssumptionResponse:
        """Reset the session's active_role_id back to the user's primary role.

        If the user is not currently assuming a different role this is a no-op
        (returns success anyway so the frontend can safely call it on any exit).
        After the role is reset a fresh token pair is issued so the frontend's
        JWT immediately reflects the restored primary role without a separate
        refresh call.
        """
        primary_role_id = user.role_id
        active_role_id = user.active_role_id

        # Update session only when an assumption is actually in place
        if primary_role_id != active_role_id:
            await self.sessions.update_role(
                session_id=user.session_id, active_role_id=primary_role_id
            )

        # Reload permissions for the restored primary role
        permissions = await self.rbac.permissions_for_role(primary_role_id)
        primary_user = await self.users.find_by_id(user.user_id)
        role_name = str(primary_user["role_name"]) if primary_user else user.role_name

        await self.audit.write(
            institution_id=user.institution_id,
            user_id=user.user_id,
            active_role_id=primary_role_id,
            action_type="exit_role_assumption",
            action_details={
                "previous_assumed_role_id": active_role_id,
                "restored_role_id": primary_role_id,
                "ip": _get_ip(request),
            },
            ip_address=_get_ip(request),
        )
        await self.session.commit()

        restored_context = UserContext(
            user_id=user.user_id,
            institution_id=user.institution_id,
            role_id=primary_role_id,
            role_name=role_name,
            active_role_id=primary_role_id,
            active_role_name=role_name,
            email=user.email,
            permissions=permissions,
            session_id=user.session_id,
        )
        return ExitRoleAssumptionResponse(
            message="Role assumption exited. Primary role restored.",
            user=restored_context,
        )

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    async def _create_session(
        self, *, user_id: str, role_id: str, request: Request
    ) -> str:
        from datetime import UTC, datetime, timedelta

        expires_at = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days)
        return await self.sessions.create(
            user_id=user_id,
            active_role_id=role_id,
            user_agent=request.headers.get("user-agent"),
            ip_address=_get_ip(request),
            expires_at=expires_at,
        )

    def _build_token_pair(self, context: UserContext) -> AuthTokenResult:
        claims = {
            "institution_id": context.institution_id,
            "role_id": context.role_id,
            "active_role_id": context.active_role_id,
            "session_id": context.session_id,
        }
        access = create_access_token(context.user_id, claims)
        refresh = create_refresh_token(context.user_id, context.session_id)
        return AuthTokenResult(
            response=LoginResponse(
                access_token=access,
                user=context,
            ),
            refresh_token=refresh,
        )


# ---------------------------------------------------------------------------
# MODULE-LEVEL HELPERS
# ---------------------------------------------------------------------------


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _decode_verified(token: str, expected_type: str) -> dict:
    from app.core.security import decode_token

    claims = decode_token(token)
    if claims.get("type") != expected_type:
        raise ValueError(f"Expected token type '{expected_type}', got '{claims.get('type')}'")
    return claims
