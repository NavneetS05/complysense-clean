# Use: Reusable transactional email delivery service using SMTP.
# Supports password resets, onboarding, workflow approvals, and assignment notifications.

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587


class MailService:
    """Sends transactional emails via SMTP (TLS on port 587).

    Returns True when the message is accepted by the relay. If False, callers may
    fall back to inline redirect behavior for reset flows.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._smtp_user = settings.smtp_user
        self._smtp_password = settings.smtp_password

    @property
    def _is_configured(self) -> bool:
        return bool(self._smtp_user and self._smtp_password)

    def send_message(self, *, to_email: str, subject: str, template_key: str, context: dict[str, Any]) -> bool:
        if not self._is_configured:
            logger.warning(
                "mail_service.smtp_not_configured: skipping email to %s for template %s",
                to_email,
                template_key,
            )
            return False

        message = self._build_message(
            to_email=to_email,
            subject=subject,
            template_key=template_key,
            context=context,
        )
        try:
            with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self._smtp_user, self._smtp_password)  # type: ignore[arg-type]
                server.sendmail(self._smtp_user, to_email, message.as_string())  # type: ignore[arg-type]
            logger.info("mail_service.sent: to=%s template=%s", to_email, template_key)
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "mail_service.auth_error: Gmail rejected credentials — "
                "check SMTP_USER and SMTP_PASSWORD in .env"
            )
        except smtplib.SMTPException as exc:
            logger.error("mail_service.smtp_error: %s", exc)
        except OSError as exc:
            logger.error("mail_service.network_error: %s", exc)
        return False

    def send_password_reset(self, *, to_email: str, reset_url: str) -> bool:
        return self.send_message(
            to_email=to_email,
            subject="ComplySense — Reset your password",
            template_key="password_reset",
            context={"reset_url": reset_url},
        )

    @staticmethod
    def _build_message(*, to_email: str, subject: str, template_key: str, context: dict[str, Any]) -> MIMEMultipart:
        settings = get_settings()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user or "no-reply@complysense.app"
        msg["To"] = to_email

        if template_key == "password_reset":
            reset_url = str(context.get("reset_url", ""))
            plain = (
                "You requested a password reset for your ComplySense account.\n\n"
                f"Use this link to continue: {reset_url}\n\n"
                "If you did not request this, you can safely ignore this email."
            )
            html = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#1a1a2e;background:#f5f6fa;padding:32px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <h2 style="color:#2563eb;margin-top:0;">Password Reset Request</h2>
    <p>You requested a password reset for your <strong>ComplySense</strong> account.</p>
    <p>Use the secure link below to continue. This link expires in <strong>5 minutes</strong>.</p>
    <p style="text-align:center;margin:32px 0;">
      <a href="{reset_url}" style="background:#2563eb;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:bold;display:inline-block;">Reset Password</a>
    </p>
    <p style="font-size:12px;color:#6b7280;">If the button does not work, copy and paste this URL into your browser.<br><a href="{reset_url}" style="color:#2563eb;">{reset_url}</a></p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
    <p style="font-size:12px;color:#9ca3af;">If you did not request a password reset, no action is needed.</p>
  </div>
</body>
</html>"""
        elif template_key == "welcome":
            full_name = str(context.get("full_name", "there"))
            login_url = str(context.get("login_url", ""))
            temporary_password = str(context.get("temporary_password", ""))
            plain = (
                f"Hello {full_name},\n\n"
                "Your ComplySense account has been created.\n"
                f"Use this temporary password to sign in: {temporary_password}\n"
                f"Sign in here: {login_url}\n"
            )
            html = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#1a1a2e;background:#f5f6fa;padding:32px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <h2 style="color:#2563eb;margin-top:0;">Welcome to ComplySense</h2>
    <p>Hello <strong>{full_name}</strong>,</p>
    <p>Your account has been created. Please sign in with the temporary password below.</p>
    <p><strong>Temporary password:</strong> {temporary_password}</p>
    <p style="text-align:center;margin:32px 0;"><a href="{login_url}" style="background:#2563eb;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:bold;display:inline-block;">Sign In</a></p>
  </div>
</body>
</html>"""
        elif template_key == "workflow":
            title = str(context.get("title", "Workflow update"))
            message_body = str(context.get("message", "A workflow update is available."))
            action_url = str(context.get("action_url", ""))
            plain = f"{title}\n\n{message_body}\n\n{action_url}".strip()
            html = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#1a1a2e;background:#f5f6fa;padding:32px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <h2 style="color:#2563eb;margin-top:0;">{title}</h2>
    <p>{message_body}</p>
    <p style="text-align:center;margin:32px 0;"><a href="{action_url}" style="background:#2563eb;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:bold;display:inline-block;">Open ComplySense</a></p>
  </div>
</body>
</html>"""
        else:
            plain = str(context.get("message", ""))
            html = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#1a1a2e;background:#f5f6fa;padding:32px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <h2 style="color:#2563eb;margin-top:0;">Notification</h2>
    <p>{plain}</p>
  </div>
</body>
</html>"""

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        return msg
