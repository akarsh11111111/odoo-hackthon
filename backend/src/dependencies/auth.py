"""Authentication and authorization dependencies."""

from collections.abc import Callable

from fastapi import Depends, Request

from src.core.exceptions import ForbiddenException, UnauthorizedException
from src.core.security import decode_token
from src.models.auth import User
from src.repositories.auth import RoleRepository, UserRepository


async def get_current_user(
    request: Request,
) -> User:
    """Return the currently authenticated user from request state or bearer token."""

    current_user = getattr(request.state, "current_user", None)
    if isinstance(current_user, User):
        return current_user

    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Authentication credentials were not provided")

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token, expected_type="access")
    user = await UserRepository().get_by_id(str(payload["sub"]))
    if user is None:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ForbiddenException("User account is inactive")

    request.state.current_user = user
    request.state.current_token_payload = payload
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user is active."""

    if not current_user.is_active:
        raise ForbiddenException("User account is inactive")
    return current_user


def require_role(*allowed_roles: str) -> Callable:
    """Create a reusable RBAC dependency for one or more role names."""

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        role = await RoleRepository().get_by_id(str(current_user.role_id))
        if role is None:
            return current_user

        if allowed_roles and role.role_name not in allowed_roles:
            raise ForbiddenException("You do not have permission to access this resource")

        return current_user

    return dependency
