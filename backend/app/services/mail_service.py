# Use: Email delivery service using Gmail SMTP.
# Sends password reset emails. Returns False on any failure so callers can fall back to inline redirect.

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587


class MailService:
    """Sends transactional emails via Gmail SMTP (TLS on port 587).

    Call ``send_password_reset`` and check the bool return value.
    If ``False``, the caller should expose the reset URL directly to the client
    so the frontend can open the reset page automatically (inline-redirect fallback).
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._smtp_user = settings.smtp_user
        self._smtp_password = settings.smtp_password

    @property
    def _is_configured(self) -> bool:
        return bool(self._smtp_user and self._smtp_password)

    def send_password_reset(self, *, to_email: str, reset_url: str) -> bool:
        """Send a password-reset email.

        Returns:
            ``True``  — email was accepted by the SMTP relay.
            ``False`` — SMTP not configured or delivery failed; caller must use fallback.
        """
        if not self._is_configured:
            logger.warning(
                "mail_service.smtp_not_configured: skipping email to %s; "
                "forgot-password endpoint will return reset_url for inline redirect",
                to_email,
            )
            return False

        message = self._build_message(to_email=to_email, reset_url=reset_url)
        try:
            with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self._smtp_user, self._smtp_password)  # type: ignore[arg-type]
                server.sendmail(self._smtp_user, to_email, message.as_string())  # type: ignore[arg-type]
            logger.info("mail_service.sent: to=%s", to_email)
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

    @staticmethod
    def _build_message(*, to_email: str, reset_url: str) -> MIMEMultipart:
        settings = get_settings()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "ComplySense — Reset your password"
        msg["From"] = settings.smtp_user or "no-reply@complysense.app"
        msg["To"] = to_email

        plain = (
            f"You requested a password reset for your ComplySense account.\n\n"
            f"Click the link below to set a new password (expires in 5 minutes):\n\n"
            f"{reset_url}\n\n"
            f"If you did not request this, you can safely ignore this email.\n"
        )
        html = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#1a1a2e;background:#f5f6fa;padding:32px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;
              box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <h2 style="color:#2563eb;margin-top:0;">Password Reset Request</h2>
    <p>You requested a password reset for your <strong>ComplySense</strong> account.</p>
    <p>Click the button below to set a new password.
       This link expires in <strong>5&nbsp;minutes</strong>.</p>
    <p style="text-align:center;margin:32px 0;">
      <a href="{reset_url}"
         style="background:#2563eb;color:#fff;text-decoration:none;padding:12px 28px;
                border-radius:6px;font-weight:bold;display:inline-block;">
        Reset Password
      </a>
    </p>
    <p style="font-size:12px;color:#6b7280;">
      If the button does not work, copy and paste this URL into your browser:<br>
      <a href="{reset_url}" style="color:#2563eb;">{reset_url}</a>
    </p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
    <p style="font-size:12px;color:#9ca3af;">
      If you did not request a password reset, no action is needed.
    </p>
  </div>
</body>
</html>"""
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        return msg
