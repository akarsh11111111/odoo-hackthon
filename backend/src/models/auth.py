"""Authentication-related Beanie documents."""

from datetime import datetime, timezone

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import EmailStr, Field


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class Role(Document):
    """Authorization role stored in MongoDB."""

    role_name: Indexed(str, unique=True)
    permissions: list[str] = Field(default_factory=list)
    description: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "roles"


class User(Document):
    """Application user stored in MongoDB."""

    first_name: str
    last_name: str
    email: Indexed(EmailStr, unique=True)
    phone: str | None = None
    password_hash: str
    role_id: PydanticObjectId
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    last_login: datetime | None = None

    class Settings:
        name = "users"


class RefreshToken(Document):
    """Stored refresh token record used for rotation and revocation."""

    user_id: PydanticObjectId
    refresh_token: Indexed(str, unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=utcnow)
    device: str | None = None
    ip_address: str | None = None
    is_revoked: bool = False
    revoked_at: datetime | None = None

    class Settings:
        name = "refresh_tokens"
