"""Authentication context middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.exceptions import UnauthorizedException
from src.core.security import decode_token
from src.models.auth import User
from src.repositories.auth import UserRepository


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Attach the current user to request state when a valid bearer token is present."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.current_user = None
        request.state.current_token_payload = None

        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
            try:
                payload = decode_token(token, expected_type="access")
                user = await UserRepository().get_by_id(str(payload["sub"]))
                if isinstance(user, User) and user.is_active:
                    request.state.current_user = user
                    request.state.current_token_payload = payload
            except UnauthorizedException:
                pass

        response = await call_next(request)
        return response
