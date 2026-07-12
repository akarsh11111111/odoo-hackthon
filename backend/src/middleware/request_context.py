"""Request context middleware for tracing and timing."""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.logging import request_id_context, role_context, token_context, user_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id and processing time to every response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        request_token = request_id_context.set(request_id)
        current_user = getattr(request.state, "current_user", None)
        current_role = getattr(current_user, "role_name", None) or getattr(request.state, "current_token_payload", {}).get("role", "-")
        current_user_id = str(getattr(current_user, "id", "-")) if current_user is not None else "-"
        current_token_type = getattr(request.state, "current_token_payload", {}).get("token_type", "-")
        user_token = user_context.set(current_user_id)
        role_token = role_context.set(str(current_role))
        token_type_token = token_context.set(str(current_token_type))
        start_time = perf_counter()

        try:
            response = await call_next(request)
        finally:
            token_context.reset(token_type_token)
            role_context.reset(role_token)
            user_context.reset(user_token)
            request_id_context.reset(request_token)

        duration_ms = (perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
        return response
