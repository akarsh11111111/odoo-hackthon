"""Expense request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from src.models.expense import ExpenseType
from src.schemas.common import APIResponse


class ExpenseCreateRequest(BaseModel):
    """Payload for creating an expense."""

    vehicle_id: str = Field(min_length=1, examples=["vehicle-1"])
    trip_id: str | None = Field(default=None, examples=["trip-1"])
    expense_type: ExpenseType = Field(default=ExpenseType.MISCELLANEOUS, examples=[ExpenseType.FUEL])
    amount: float = Field(ge=0, examples=[54.0])
    vendor: str = Field(min_length=1, examples=["Metro Fuel Hub"])
    invoice_number: str = Field(min_length=1, examples=["INV-9001"])
    expense_date: date = Field(examples=["2026-07-12"])
    description: str = Field(min_length=1, examples=["Fuel purchase for dispatch"])
    attachment: str | None = Field(default=None, examples=["invoice.pdf"])

    @field_validator("vendor", "description", "invoice_number", "attachment")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class ExpenseUpdateRequest(BaseModel):
    """Payload for updating an existing expense."""

    trip_id: str | None = Field(default=None, examples=["trip-1"])
    expense_type: ExpenseType | None = Field(default=None, examples=[ExpenseType.FUEL])
    amount: float | None = Field(default=None, ge=0, examples=[60.0])
    vendor: str | None = Field(default=None, min_length=1, examples=["Metro Fuel Hub"])
    invoice_number: str | None = Field(default=None, min_length=1, examples=["INV-9001"])
    expense_date: date | None = Field(default=None, examples=["2026-07-12"])
    description: str | None = Field(default=None, min_length=1, examples=["Fuel purchase for dispatch"])
    attachment: str | None = Field(default=None, examples=["invoice.pdf"])

    @field_validator("vendor", "description", "invoice_number", "attachment")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class ExpenseRead(BaseModel):
    """Public expense representation returned by the API."""

    id: str
    expense_id: str
    vehicle_id: str
    trip_id: str | None = None
    expense_type: ExpenseType
    amount: float
    vendor: str
    invoice_number: str
    expense_date: date
    description: str
    attachment: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class ExpenseListResult(BaseModel):
    """Paginated expense listing payload."""

    items: list[ExpenseRead]
    total: int
    page: int
    size: int


ExpenseCreateResponse = APIResponse[ExpenseRead]
ExpenseUpdateResponse = APIResponse[ExpenseRead]
ExpenseListResponse = APIResponse[ExpenseListResult]
ExpenseDetailResponse = APIResponse[ExpenseRead]
ExpenseDeleteResponse = APIResponse[dict[str, str]]
ExpenseHistoryResponse = APIResponse[ExpenseListResult]
ExpenseVehicleResponse = APIResponse[ExpenseListResult]
