# Use: Pydantic validation schemas for authentication request and response serialization.

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# REQUESTS
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    mac_address: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class RegisterRequest(BaseModel):
    institution_id: str
    role_id: str
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=15)
    designation: str | None = Field(default=None, max_length=100)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=15)
    designation: str | None = Field(default=None, max_length=100)


# ---------------------------------------------------------------------------
# RESPONSES
# ---------------------------------------------------------------------------


class UserContext(BaseModel):
    user_id: str
    institution_id: str
    institution_name: str | None = None
    role_id: str
    role_name: str
    active_role_id: str
    active_role_name: str
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    designation: str | None = None
    permissions: list[str]
    session_id: str


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserContext


class ForgotPasswordResponse(BaseModel):
    email_sent: bool
    # Populated only when email delivery fails — client must redirect user to reset_url
    reset_url: str | None = None
    # Informational message shown in the UI
    message: str


class MessageResponse(BaseModel):
    message: str


class ValidateResetTokenResponse(BaseModel):
    valid: bool
    email: str | None = None


class AssumeRoleRequest(BaseModel):
    target_role_id: str


class ExitRoleAssumptionResponse(BaseModel):
    message: str
    user: UserContext
