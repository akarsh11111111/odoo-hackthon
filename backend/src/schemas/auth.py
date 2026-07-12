"""Authentication and authorization schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.constants.auth import ROLE_NAMES
from src.schemas.common import APIResponse


RoleName = Literal["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"]


class RoleRead(BaseModel):
    """Public role representation."""

    id: str
    role_name: str
    permissions: list[str]
    description: str | None = None


class UserRead(BaseModel):
    """Public user profile returned by auth APIs."""

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    role: RoleRead
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None


class RegisterRequest(BaseModel):
    """Payload for creating a new user account."""

    first_name: str = Field(min_length=1, examples=["Alex"])
    last_name: str = Field(min_length=1, examples=["Morgan"])
    email: EmailStr = Field(examples=["alex@example.com"])
    phone: str | None = Field(default=None, examples=["+15551234567"])
    password: str = Field(min_length=8, examples=["Str0ng!Pass123"])
    role_name: RoleName = Field(default="Fleet Manager", examples=["Dispatcher"])

    @field_validator("role_name")
    @classmethod
    def validate_role_name(cls, value: str) -> str:
        if value not in ROLE_NAMES:
            raise ValueError("Invalid role name")
        return value


class LoginRequest(BaseModel):
    """Payload for logging in a user."""

    email: EmailStr = Field(examples=["alex@example.com"])
    password: str = Field(min_length=1, examples=["Str0ng!Pass123"])
    device: str | None = Field(default=None, examples=["Chrome on Windows"])
    ip_address: str | None = Field(default=None, examples=["203.0.113.10"])


class RefreshRequest(BaseModel):
    """Payload for rotating a refresh token."""

    refresh_token: str = Field(min_length=1, examples=["eyJhbGciOi..."])
    device: str | None = Field(default=None, examples=["Chrome on Windows"])
    ip_address: str | None = Field(default=None, examples=["203.0.113.10"])


class LogoutRequest(BaseModel):
    """Payload for logging out a session."""

    refresh_token: str = Field(min_length=1, examples=["eyJhbGciOi..."])


class ForgotPasswordRequest(BaseModel):
    """Payload for initiating a password reset flow."""

    email: EmailStr = Field(examples=["alex@example.com"])


class ResetPasswordRequest(BaseModel):
    """Payload for completing a password reset flow."""

    email: EmailStr = Field(examples=["alex@example.com"])
    reset_token: str = Field(min_length=1, examples=["eyJhbGciOi..."])
    new_password: str = Field(min_length=8, examples=["N3w!Pass123"])


class ChangePasswordRequest(BaseModel):
    """Payload for changing the current password."""

    current_password: str = Field(min_length=1, examples=["Str0ng!Pass123"])
    new_password: str = Field(min_length=8, examples=["N3w!Pass123"])


class AuthTokenResponse(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    refresh_token_expires_in: int


class AuthSessionResponse(BaseModel):
    """Complete auth payload returned from login and register."""

    user: UserRead
    tokens: AuthTokenResponse


class AuthMessageResponse(BaseModel):
    """Message-only response for security-sensitive endpoints."""

    detail: str


class ResetPasswordResponse(BaseModel):
    """Password reset response used for testing and API flow completeness."""

    reset_token: str
    detail: str


RegisterResponse = APIResponse[AuthSessionResponse]
LoginResponse = APIResponse[AuthSessionResponse]
SessionResponse = APIResponse[UserRead]
MessageResponse = APIResponse[AuthMessageResponse]
ResetResponse = APIResponse[ResetPasswordResponse]
