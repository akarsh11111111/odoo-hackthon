"""Shared response and error schemas."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Structured error payload for standard API responses."""

    field: str = ""
    message: str
    code: str = "error"


class APIResponse(BaseModel, Generic[DataT]):
    """Standard API envelope returned by every endpoint."""

    success: bool
    message: str
    data: DataT | None = None
    errors: list[ErrorDetail] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def build_response(
    *,
    success: bool,
    message: str,
    data: Any | None = None,
    errors: list[ErrorDetail] | None = None,
) -> APIResponse[Any]:
    """Create a standard response envelope."""

    return APIResponse[Any](success=success, message=message, data=data, errors=errors)
