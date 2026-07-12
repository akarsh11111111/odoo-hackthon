"""Security helpers for password hashing and JWT handling."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from src.core.config import get_settings
from src.core.exceptions import BusinessRuleException, UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""

    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""

    return pwd_context.verify(password, password_hash)


def validate_password_strength(password: str) -> None:
    """Enforce minimum password complexity."""

    settings = get_settings()
    if len(password) < settings.password_min_length:
        raise BusinessRuleException(f"Password must be at least {settings.password_min_length} characters long")

    checks = [
        any(char.islower() for char in password),
        any(char.isupper() for char in password),
        any(char.isdigit() for char in password),
        any(not char.isalnum() for char in password),
    ]
    if not all(checks):
        raise BusinessRuleException(
            "Password must include uppercase, lowercase, numeric, and special characters"
        )


def _token_expiry(*, minutes: int | None = None, days: int | None = None) -> datetime:
    now = datetime.now(timezone.utc)
    if minutes is not None:
        return now + timedelta(minutes=minutes)
    if days is not None:
        return now + timedelta(days=days)
    return now


def create_access_token(*, subject: str, role_name: str, email: str) -> tuple[str, datetime]:
    """Create a signed JWT access token."""

    settings = get_settings()
    expires_at = _token_expiry(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": subject,
        "role": role_name,
        "email": email,
        "token_type": "access",
        "jti": uuid4().hex,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def create_refresh_token(*, subject: str, role_name: str, email: str) -> tuple[str, datetime]:
    """Create a signed JWT refresh token."""

    settings = get_settings()
    expires_at = _token_expiry(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": subject,
        "role": role_name,
        "email": email,
        "token_type": "refresh",
        "jti": uuid4().hex,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def create_password_reset_token(*, subject: str, email: str) -> tuple[str, datetime]:
    """Create a short-lived password reset token."""

    settings = get_settings()
    expires_at = _token_expiry(minutes=settings.reset_password_token_expire_minutes)
    payload = {
        "sub": subject,
        "email": email,
        "token_type": "password_reset",
        "jti": uuid4().hex,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Decode and validate a JWT token."""

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as exc:
        raise UnauthorizedException("Token has expired") from exc
    except InvalidTokenError as exc:
        raise UnauthorizedException("Invalid token") from exc

    if expected_type is not None and payload.get("token_type") != expected_type:
        raise UnauthorizedException("Invalid token type")

    return payload


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token before storing it."""

    settings = get_settings()
    payload = f"{settings.jwt_secret_key}:{token}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_refresh_token(token: str, hashed_token: str) -> bool:
    """Verify a refresh token against its stored hash."""

    return hash_refresh_token(token) == hashed_token
