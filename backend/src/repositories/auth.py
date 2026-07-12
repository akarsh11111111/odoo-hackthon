"""Repository layer for authentication models."""

from datetime import datetime, timezone

from beanie.odm.fields import PydanticObjectId

from src.constants.auth import DEFAULT_ROLE_PERMISSIONS, ROLE_NAMES
from src.core.exceptions import NotFoundException
from src.models.auth import RefreshToken, Role, User, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | None:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return None


class RoleRepository:
    """Data access for role documents."""

    async def get_by_name(self, role_name: str) -> Role | None:
        return await Role.find_one(Role.role_name == role_name)

    async def get_by_id(self, role_id: str) -> Role | None:
        object_id = _to_object_id(role_id)
        if object_id is None:
            return None
        return await Role.get(object_id)

    async def ensure_default_roles(self) -> None:
        for role_name in ROLE_NAMES:
            existing_role = await self.get_by_name(role_name)
            if existing_role is None:
                await Role(
                    role_name=role_name,
                    permissions=DEFAULT_ROLE_PERMISSIONS[role_name],
                    description=f"Default role for {role_name.lower()} operations",
                ).insert()


class UserRepository:
    """Data access for user documents."""

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email)

    async def get_by_id(self, user_id: str) -> User | None:
        object_id = _to_object_id(user_id)
        if object_id is None:
            return None
        return await User.get(object_id)

    async def create(self, **user_data: object) -> User:
        user = User(**user_data)
        return await user.insert()

    async def update_last_login(self, user_id: str) -> None:
        user = await self.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        user.last_login = datetime.now(timezone.utc)
        user.updated_at = utcnow()
        await user.save()

    async def update_password_hash(self, user_id: str, password_hash: str) -> None:
        user = await self.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        user.password_hash = password_hash
        user.updated_at = utcnow()
        await user.save()

    async def set_active_state(self, user_id: str, is_active: bool) -> None:
        user = await self.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        user.is_active = is_active
        user.updated_at = utcnow()
        await user.save()


class RefreshTokenRepository:
    """Data access for refresh token documents."""

    async def create(self, **token_data: object) -> RefreshToken:
        refresh_token = RefreshToken(**token_data)
        return await refresh_token.insert()

    async def get_by_hashed_token(self, hashed_token: str) -> RefreshToken | None:
        return await RefreshToken.find_one(RefreshToken.refresh_token == hashed_token)

    async def revoke(self, hashed_token: str) -> None:
        token = await self.get_by_hashed_token(hashed_token)
        if token is None:
            raise NotFoundException("Refresh token not found")
        token.is_revoked = True
        token.revoked_at = datetime.now(timezone.utc)
        await token.save()

    async def revoke_for_user(self, user_id: str) -> None:
        tokens = await RefreshToken.find(RefreshToken.user_id == _to_object_id(user_id)).to_list()
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            await token.save()
