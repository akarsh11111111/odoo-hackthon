"""Authentication service layer."""

from dataclasses import dataclass

from src.core.config import get_settings
from src.core.exceptions import ConflictException, ForbiddenException, NotFoundException, UnauthorizedException
from src.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    validate_password_strength,
    verify_password,
)
from src.models.auth import Role, User
from src.repositories.auth import RefreshTokenRepository, RoleRepository, UserRepository
from src.schemas.auth import (
    AuthSessionResponse,
    AuthTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    RoleRead,
    UserRead,
)


@dataclass(slots=True)
class AuthService:
    """Coordinates auth business logic across repositories and token helpers."""

    user_repository: UserRepository
    role_repository: RoleRepository
    refresh_token_repository: RefreshTokenRepository

    async def register(self, payload: RegisterRequest) -> AuthSessionResponse:
        existing_user = await self.user_repository.get_by_email(payload.email)
        if existing_user is not None:
            raise ConflictException("Email already exists")

        role = await self.role_repository.get_by_name(payload.role_name)
        if role is None:
            raise NotFoundException("Role not found")

        validate_password_strength(payload.password)

        user = await self.user_repository.create(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role_id=role.id,
            is_active=True,
            is_verified=False,
        )
        return await self._issue_session(user=user, role=role)

    async def login(self, payload: LoginRequest) -> AuthSessionResponse:
        user = await self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("User account is inactive")

        role = await self.role_repository.get_by_id(str(user.role_id))
        if role is None:
            raise NotFoundException("Role not found")

        await self.user_repository.update_last_login(str(user.id))
        return await self._issue_session(user=user, role=role, device=payload.device, ip_address=payload.ip_address)

    async def logout(self, payload: LogoutRequest) -> dict[str, str]:
        await self.revoke_refresh_token(payload.refresh_token)
        return {"detail": "Logged out successfully"}

    async def refresh(self, payload: RefreshRequest) -> AuthSessionResponse:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
        user = await self.user_repository.get_by_id(str(token_payload["sub"]))
        if user is None:
            raise NotFoundException("User not found")

        stored_token = await self.refresh_token_repository.get_by_hashed_token(hash_refresh_token(payload.refresh_token))
        if stored_token is None or stored_token.is_revoked:
            raise UnauthorizedException("Refresh token has been revoked")

        role = await self.role_repository.get_by_id(str(user.role_id))
        if role is None:
            raise NotFoundException("Role not found")

        await self.refresh_token_repository.revoke(str(stored_token.refresh_token))
        return await self._issue_session(
            user=user,
            role=role,
            device=payload.device or stored_token.device,
            ip_address=payload.ip_address or stored_token.ip_address,
        )

    async def forgot_password(self, payload: ForgotPasswordRequest) -> dict[str, str]:
        user = await self.user_repository.get_by_email(payload.email)
        if user is None:
            return {"detail": "If the email exists, reset instructions have been generated"}

        reset_token, _ = create_password_reset_token(subject=str(user.id), email=str(user.email))
        return {"detail": "If the email exists, reset instructions have been generated", "reset_token": reset_token}

    async def reset_password(self, payload: ResetPasswordRequest) -> dict[str, str]:
        token_payload = decode_token(payload.reset_token, expected_type="password_reset")
        if token_payload.get("email") != str(payload.email):
            raise UnauthorizedException("Reset token does not match the requested email")

        user = await self.user_repository.get_by_email(payload.email)
        if user is None:
            raise NotFoundException("User not found")

        validate_password_strength(payload.new_password)
        await self.user_repository.update_password_hash(str(user.id), hash_password(payload.new_password))
        await self.refresh_token_repository.revoke_for_user(str(user.id))
        return {"detail": "Password reset successfully"}

    async def change_password(self, user: User, payload: ChangePasswordRequest) -> dict[str, str]:
        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        validate_password_strength(payload.new_password)
        await self.user_repository.update_password_hash(str(user.id), hash_password(payload.new_password))
        await self.refresh_token_repository.revoke_for_user(str(user.id))
        return {"detail": "Password changed successfully"}

    async def get_current_user(self, user: User) -> UserRead:
        role = await self.role_repository.get_by_id(str(user.role_id))
        if role is None:
            raise NotFoundException("Role not found")
        return self._to_user_read(user=user, role=role)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        hashed_token = hash_refresh_token(refresh_token)
        stored_token = await self.refresh_token_repository.get_by_hashed_token(hashed_token)
        if stored_token is None:
            raise NotFoundException("Refresh token not found")
        if stored_token.is_revoked:
            return
        await self.refresh_token_repository.revoke(hashed_token)

    async def _issue_session(
        self,
        *,
        user: User,
        role: Role,
        device: str | None = None,
        ip_address: str | None = None,
    ) -> AuthSessionResponse:
        access_token, _ = create_access_token(
            subject=str(user.id),
            role_name=role.role_name,
            email=str(user.email),
        )
        refresh_token, _ = create_refresh_token(
            subject=str(user.id),
            role_name=role.role_name,
            email=str(user.email),
        )

        hashed_refresh_token = hash_refresh_token(refresh_token)
        await self.refresh_token_repository.create(
            user_id=user.id,
            refresh_token=hashed_refresh_token,
            expires_at=_refresh_expires_at(),
            device=device,
            ip_address=ip_address,
        )

        return AuthSessionResponse(
            user=self._to_user_read(user=user, role=role),
            tokens=AuthTokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_in=get_settings().jwt_access_token_expire_minutes * 60,
                refresh_token_expires_in=get_settings().jwt_refresh_token_expire_days * 24 * 60 * 60,
            ),
        )

    def _to_user_read(self, *, user: User, role: Role) -> UserRead:
        return UserRead(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=RoleRead(
                id=str(role.id),
                role_name=role.role_name,
                permissions=role.permissions,
                description=role.description,
            ),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )


def _refresh_expires_at():
    """Return the absolute expiry timestamp for a refresh token record."""

    settings = get_settings()
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)


def get_auth_service() -> AuthService:
    """Build an auth service with concrete repositories."""

    return AuthService(
        user_repository=UserRepository(),
        role_repository=RoleRepository(),
        refresh_token_repository=RefreshTokenRepository(),
    )
