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

        await self.mail.send_message(
            to_email=str(new_user["email"]),
            subject="ComplySense — Welcome to your account",
            template_key="welcome",
            context={
                "full_name": str(new_user["full_name"]),
                "login_url": f"{self.settings.frontend_url}/login",
                "temporary_password": "Use the password you chose during registration",
            },
        )

        context = UserContext(
            user_id=str(new_user["user_id"]),
            institution_id=str(new_user["institution_id"]),
            institution_name=str(new_user["institution_name"]) if new_user.get("institution_name") else None,
            role_id=str(new_user["role_id"]),
            role_name=str(new_user["role_name"]),
            active_role_id=str(new_user["role_id"]),
            active_role_name=str(new_user["role_name"]),
            email=str(new_user["email"]),
            full_name=str(new_user["full_name"]) if new_user.get("full_name") else None,
            phone=str(new_user["phone"]) if new_user.get("phone") else None,
            designation=str(new_user["designation"]) if new_user.get("designation") else None,
            permissions=permissions,
            session_id=session_id,
        )
        return self._build_token_pair(context)

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------

    async def login(self, payload: LoginRequest, request: Request) -> AuthTokenResult:
        ip = _get_ip(request)
        mac = _get_mac(request, payload)
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
                    action_details={"reason": "account_blocked", "ip": ip, "mac_address": mac},
                    ip_address=ip,
                    mac_address=mac,
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
                        "mac_address": mac,
                    },
                    ip_address=ip,
                    mac_address=mac,
                )
            else:
                await self.audit.write(
                    institution_id=institution_id,
                    user_id=user_id,
                    active_role_id=role_id,
                    action_type="failed_login",
                    action_details={"attempts": new_count, "max": _MAX_ATTEMPTS, "ip": ip, "mac_address": mac},
                    ip_address=ip,
                    mac_address=mac,
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
            mac_address=mac,
        )
        await self.session.commit()

        context = UserContext(
            user_id=user_id,
            institution_id=institution_id,
            institution_name=str(user["institution_name"]) if user.get("institution_name") else None,
            role_id=role_id,
            role_name=str(user["role_name"]),
            active_role_id=role_id,
            active_role_name=str(user["role_name"]),
            email=str(user["email"]),
            full_name=str(user["full_name"]) if user.get("full_name") else None,
            phone=str(user["phone"]) if user.get("phone") else None,
            designation=str(user["designation"]) if user.get("designation") else None,
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
    # CHANGE PASSWORD
    # ------------------------------------------------------------------

    async def change_password(
        self, user: UserContext, current_pass: str, new_pass: str, request: Request
    ) -> MessageResponse:
        from sqlalchemy import text

        user_row = await self.users.find_active_by_email(user.email)
        if not user_row:
            raise UnauthorizedError("User not found")

        if not verify_password(current_pass, str(user_row["password_hash"])):
            raise UnauthorizedError("Current password is incorrect")

        if len(new_pass) < 6:
            raise UnauthorizedError("New password must be at least 6 characters long")

        new_hash = hash_password(new_pass)
        await self.session.execute(
            text("update users set password_hash = :hash, updated_at = now() where user_id = :uid"),
            {"hash": new_hash, "uid": user.user_id},
        )
        await self.audit.write(
            institution_id=user.institution_id,
            user_id=user.user_id,
            active_role_id=user.active_role_id,
            action_type="password_changed",
            entity_type="users",
            entity_id=user.user_id,
            ip_address=_get_ip(request),
        )
        await self.session.commit()
        return MessageResponse(message="Password changed successfully")

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
            institution_name=str(user["institution_name"]) if user.get("institution_name") else None,
            role_id=str(user["role_id"]),
            role_name=str(user["role_name"]),
            active_role_id=role_id,
            active_role_name=str(existing_session["role_name"]),
            email=str(user["email"]),
            full_name=str(user["full_name"]) if user.get("full_name") else None,
            phone=str(user["phone"]) if user.get("phone") else None,
            designation=str(user["designation"]) if user.get("designation") else None,
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

        email_sent = await self.mail.send_password_reset(
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
    # ASSUME ROLE
    # ------------------------------------------------------------------

    async def assume_role(
        self, user: UserContext, payload: AssumeRoleRequest, request: Request
    ) -> ExitRoleAssumptionResponse:
        """Switch the session's active_role_id to the requested target role.

        Only Super Admin and Institution Admin users are allowed to assume roles.
        The target role must exist in the database.
        """
        allowed_roles = {"Super Admin", "Institution Admin"}
        if user.role_name not in allowed_roles:
            raise UnauthorizedError("Only administrators can assume other roles")

        target_role = await self.rbac.find_role_by_id(payload.target_role_id)
        if not target_role:
            raise UnauthorizedError("Target role does not exist")

        await self.sessions.update_role(
            session_id=user.session_id, active_role_id=payload.target_role_id
        )

        permissions = await self.rbac.permissions_for_role(payload.target_role_id)

        await self.audit.write(
            institution_id=user.institution_id,
            user_id=user.user_id,
            active_role_id=payload.target_role_id,
            action_type="assume_role",
            action_details={
                "previous_role_id": user.active_role_id,
                "assumed_role_id": payload.target_role_id,
                "assumed_role_name": str(target_role["role_name"]),
                "ip": _get_ip(request),
            },
            ip_address=_get_ip(request),
        )
        await self.session.commit()

        assumed_context = UserContext(
            user_id=user.user_id,
            institution_id=user.institution_id,
            institution_name=user.institution_name,
            role_id=user.role_id,
            role_name=user.role_name,
            active_role_id=payload.target_role_id,
            active_role_name=str(target_role["role_name"]),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            designation=user.designation,
            permissions=permissions,
            session_id=user.session_id,
        )
        return ExitRoleAssumptionResponse(
            message=f"Now assuming role: {target_role['role_name']}",
            user=assumed_context,
        )

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
            institution_name=user.institution_name,
            role_id=primary_role_id,
            role_name=role_name,
            active_role_id=primary_role_id,
            active_role_name=role_name,
            email=user.email,
            full_name=primary_user.get("full_name") if primary_user else user.full_name,
            phone=primary_user.get("phone") if primary_user else user.phone,
            designation=primary_user.get("designation") if primary_user else user.designation,
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


_CACHED_HOST_MAC: str | None = None


def _get_host_mac() -> str:
    global _CACHED_HOST_MAC
    if _CACHED_HOST_MAC:
        return _CACHED_HOST_MAC

    try:
        import subprocess

        cmd = subprocess.run(["getmac", "/fo", "csv", "/v"], capture_output=True, text=True, timeout=2)
        for line in cmd.stdout.splitlines():
            parts = [p.strip('"') for p in line.split(",")]
            if len(parts) >= 3:
                conn_name = parts[0].lower()
                adapter_name = parts[1].lower()
                mac = parts[2].replace("-", ":").upper()
                if mac and mac != "N/A" and len(mac) == 17 and (
                    "wi-fi" in conn_name
                    or "ethernet" in conn_name
                    or "intel" in adapter_name
                    or "realtek" in adapter_name
                ):
                    _CACHED_HOST_MAC = mac
                    return mac
    except Exception:
        pass

    try:
        import uuid

        node = uuid.getnode()
        mac = ":".join(f"{(node >> i) & 0xff:02x}" for i in range(0, 48, 8)[::-1]).upper()
        if mac and mac != "00:00:00:00:00:00":
            _CACHED_HOST_MAC = mac
            return mac
    except Exception:
        pass

    _CACHED_HOST_MAC = "DC:97:BA:5E:CA:EA"
    return _CACHED_HOST_MAC


def _get_mac(request: Request | None = None, payload: Any = None) -> str:
    # 1. Check payload passed from client web application
    if payload and getattr(payload, "mac_address", None):
        return str(payload.mac_address)

    # 2. Check HTTP headers injected by client / proxy / gateway / VPN
    if request:
        for header_name in ("X-Client-MAC", "X-Forwarded-MAC", "X-MAC-Address", "X-Device-MAC", "x-mac-address"):
            val = request.headers.get(header_name)
            if val:
                return val

        # 3. Check ARP table for remote client IP if on local network
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip not in ("127.0.0.1", "::1", "localhost"):
            try:
                import re
                import subprocess

                cmd = subprocess.run(["arp", "-a", client_ip], capture_output=True, text=True, timeout=1)
                match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", cmd.stdout)
                if match:
                    return match.group(0).replace("-", ":").upper()
            except Exception:
                pass

    return _get_host_mac()


def _decode_verified(token: str, expected_type: str) -> dict:
    from app.core.security import decode_token

    claims = decode_token(token)
    if claims.get("type") != expected_type:
        raise ValueError(f"Expected token type '{expected_type}', got '{claims.get('type')}'")
    return claims
