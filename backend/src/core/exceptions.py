"""Custom exceptions and application-level handlers."""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.schemas.common import APIResponse, ErrorDetail

logger = logging.getLogger(__name__)
UNPROCESSABLE_STATUS = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)


class TransitOpsException(Exception):
    """Base application exception for TransitOps."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, code: str = "error") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class NotFoundException(TransitOpsException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, code="not_found")


class ConflictException(TransitOpsException):
    def __init__(self, message: str = "Conflict detected") -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, code="conflict")


class UnauthorizedException(TransitOpsException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, code="unauthorized")


class ForbiddenException(TransitOpsException):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN, code="forbidden")


class BusinessRuleException(TransitOpsException):
    def __init__(self, message: str = "Business rule violated") -> None:
        super().__init__(message=message, status_code=UNPROCESSABLE_STATUS, code="business_rule")


def _base_response(
    *,
    success: bool,
    message: str,
    data: object | None = None,
    errors: list[ErrorDetail] | None = None,
) -> dict[str, object]:
    response = APIResponse(success=success, message=message, data=data, errors=errors)
    return response.model_dump(mode="json")


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""

    @app.exception_handler(TransitOpsException)
    async def transitops_exception_handler(_: Request, exc: TransitOpsException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_base_response(success=False, message=exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            ErrorDetail(
                field=".".join(str(part) for part in error.get("loc", []) if part != "body"),
                message=error.get("msg", "Invalid input"),
                code=error.get("type", "validation_error"),
            )
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=UNPROCESSABLE_STATUS,
            content=_base_response(success=False, message="Validation failed", errors=errors),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_base_response(success=False, message=str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_base_response(success=False, message="Internal server error"),
        )
