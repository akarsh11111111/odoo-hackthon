from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.main import create_app
from src.schemas.auth import AuthSessionResponse, AuthTokenResponse, RoleRead, UserRead
from src.services.auth import get_auth_service


@dataclass
class FakeAuthService:
    async def register(self, payload):
        return _fake_session(payload.email)

    async def login(self, payload):
        return _fake_session(payload.email)

    async def logout(self, payload):
        return {"detail": "Logged out successfully"}

    async def refresh(self, payload):
        return _fake_session("alex@example.com")

    async def forgot_password(self, payload):
        return {"detail": "If the email exists, reset instructions have been generated", "reset_token": "reset-token"}

    async def reset_password(self, payload):
        return {"detail": "Password reset successfully"}

    async def change_password(self, user, payload):
        return {"detail": "Password changed successfully"}

    async def get_current_user(self, user):
        return user


def _fake_session(email: str) -> AuthSessionResponse:
    user = UserRead(
        id="user-1",
        first_name="Alex",
        last_name="Morgan",
        email=email,
        phone=None,
        role=RoleRead(id="role-1", role_name="Fleet Manager", permissions=["vehicles:write"], description=None),
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login=None,
    )
    tokens = AuthTokenResponse(
        access_token="access-token",
        refresh_token="refresh-token",
        access_token_expires_in=1800,
        refresh_token_expires_in=604800,
    )
    return AuthSessionResponse(user=user, tokens=tokens)


def test_auth_routes_with_dependency_override(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    app = create_app()
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Alex",
                "last_name": "Morgan",
                "email": "alex@example.com",
                "password": "Str0ng!Pass123",
                "role_name": "Fleet Manager",
            },
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["user"]["email"] == "alex@example.com"
