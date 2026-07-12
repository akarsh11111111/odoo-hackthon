from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from src.constants.auth import FLEET_MANAGER
from src.core.config import get_settings
from src.core.exceptions import ConflictException
from src.core.security import hash_password
from src.repositories.auth import RefreshTokenRepository, RoleRepository, UserRepository
from src.schemas.auth import ChangePasswordRequest, ForgotPasswordRequest, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, ResetPasswordRequest
from src.services.auth import AuthService


@dataclass
class FakeRole:
    id: str
    role_name: str
    permissions: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class FakeUser:
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    password_hash: str
    role_id: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime | None = None


@dataclass
class FakeRefreshToken:
    user_id: str
    refresh_token: str
    expires_at: datetime
    device: str | None = None
    ip_address: str | None = None
    is_revoked: bool = False


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[str, FakeUser] = {}

    async def get_by_email(self, email: str):
        return next((user for user in self.users.values() if user.email == email), None)

    async def get_by_id(self, user_id: str):
        return self.users.get(user_id)

    async def create(self, **user_data: object):
        user_id = f"user-{len(self.users) + 1}"
        user = FakeUser(id=user_id, **user_data)
        self.users[user_id] = user
        return user

    async def update_last_login(self, user_id: str) -> None:
        self.users[user_id].last_login = datetime.now(timezone.utc)

    async def update_password_hash(self, user_id: str, password_hash: str) -> None:
        self.users[user_id].password_hash = password_hash


class FakeRoleRepository(RoleRepository):
    def __init__(self) -> None:
        self.roles = {
            FLEET_MANAGER: FakeRole(id="role-1", role_name=FLEET_MANAGER, permissions=["vehicles:write"]),
        }

    async def get_by_name(self, role_name: str):
        return self.roles.get(role_name)

    async def get_by_id(self, role_id: str):
        return next((role for role in self.roles.values() if role.id == role_id), None)


class FakeRefreshRepository(RefreshTokenRepository):
    def __init__(self) -> None:
        self.tokens: dict[str, FakeRefreshToken] = {}

    async def create(self, **token_data: object):
        token = FakeRefreshToken(**token_data)
        self.tokens[token.refresh_token] = token
        return token

    async def get_by_hashed_token(self, hashed_token: str):
        return self.tokens.get(hashed_token)

    async def revoke(self, hashed_token: str) -> None:
        self.tokens[hashed_token].is_revoked = True

    async def revoke_for_user(self, user_id: str) -> None:
        for token in self.tokens.values():
            if token.user_id == user_id:
                token.is_revoked = True


@pytest.fixture()
def auth_service() -> AuthService:
    get_settings.cache_clear()
    return AuthService(
        user_repository=FakeUserRepository(),
        role_repository=FakeRoleRepository(),
        refresh_token_repository=FakeRefreshRepository(),
    )


@pytest.mark.asyncio
async def test_register_login_refresh_logout_flow(auth_service: AuthService) -> None:
    register_payload = RegisterRequest(
        first_name="Alex",
        last_name="Morgan",
        email="alex@example.com",
        password="Str0ng!Pass123",
        role_name=FLEET_MANAGER,
    )

    session = await auth_service.register(register_payload)
    assert session.user.email == "alex@example.com"

    login_session = await auth_service.login(LoginRequest(email="alex@example.com", password="Str0ng!Pass123"))
    assert login_session.tokens.access_token

    refreshed_session = await auth_service.refresh(RefreshRequest(refresh_token=login_session.tokens.refresh_token))
    assert refreshed_session.tokens.refresh_token

    logout_result = await auth_service.logout(LogoutRequest(refresh_token=refreshed_session.tokens.refresh_token))
    assert logout_result["detail"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_register_duplicate_email_raises(auth_service: AuthService) -> None:
    payload = RegisterRequest(
        first_name="Alex",
        last_name="Morgan",
        email="alex@example.com",
        password="Str0ng!Pass123",
        role_name=FLEET_MANAGER,
    )
    await auth_service.register(payload)

    with pytest.raises(ConflictException):
        await auth_service.register(payload)


@pytest.mark.asyncio
async def test_change_and_reset_password(auth_service: AuthService) -> None:
    register_payload = RegisterRequest(
        first_name="Alex",
        last_name="Morgan",
        email="alex@example.com",
        password="Str0ng!Pass123",
        role_name=FLEET_MANAGER,
    )
    await auth_service.register(register_payload)
    user = await auth_service.user_repository.get_by_email("alex@example.com")

    await auth_service.change_password(user, ChangePasswordRequest(current_password="Str0ng!Pass123", new_password="N3w!Pass123"))
    await auth_service.login(LoginRequest(email="alex@example.com", password="N3w!Pass123"))

    forgot = await auth_service.forgot_password(ForgotPasswordRequest(email="alex@example.com"))
    reset_token = forgot["reset_token"]

    result = await auth_service.reset_password(
        ResetPasswordRequest(email="alex@example.com", reset_token=reset_token, new_password="An0ther!Pass123")
    )
    assert result["detail"] == "Password reset successfully"
