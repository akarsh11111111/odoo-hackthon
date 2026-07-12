"""Fuel log request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from src.models.fuel import FuelType
from src.schemas.common import APIResponse


class FuelLogCreateRequest(BaseModel):
    """Payload for creating a fuel log."""

    vehicle_id: str = Field(min_length=1, examples=["vehicle-1"])
    trip_id: str | None = Field(default=None, examples=["trip-1"])
    driver_id: str = Field(min_length=1, examples=["driver-1"])
    fuel_station: str = Field(min_length=1, examples=["Metro Fuel Hub"])
    fuel_type: FuelType = Field(default=FuelType.DIESEL, examples=[FuelType.DIESEL])
    liters: float = Field(gt=0, examples=[40.0])
    price_per_liter: float = Field(gt=0, examples=[1.35])
    current_odometer: int = Field(ge=0, examples=[5300])
    fuel_date: date = Field(examples=["2026-07-12"])
    receipt_image: str | None = Field(default=None, examples=["receipt.png"])
    notes: str | None = Field(default=None, examples=["Top up before dispatch"])

    @field_validator("fuel_station", "notes")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @property
    def total_cost(self) -> float:
        return self.liters * self.price_per_liter


class FuelLogUpdateRequest(BaseModel):
    """Payload for updating an existing fuel log."""

    trip_id: str | None = Field(default=None, examples=["trip-1"])
    driver_id: str | None = Field(default=None, min_length=1, examples=["driver-1"])
    fuel_station: str | None = Field(default=None, min_length=1, examples=["Metro Fuel Hub"])
    fuel_type: FuelType | None = Field(default=None, examples=[FuelType.DIESEL])
    liters: float | None = Field(default=None, gt=0, examples=[45.0])
    price_per_liter: float | None = Field(default=None, gt=0, examples=[1.45])
    current_odometer: int | None = Field(default=None, ge=0, examples=[5350])
    fuel_date: date | None = Field(default=None, examples=["2026-07-12"])
    receipt_image: str | None = Field(default=None, examples=["receipt.png"])
    notes: str | None = Field(default=None, examples=["Updated refuel record"])

    @field_validator("fuel_station", "notes")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class FuelLogRead(BaseModel):
    """Public fuel log representation returned by the API."""

    id: str
    fuel_log_id: str
    vehicle_id: str
    trip_id: str | None = None
    driver_id: str
    fuel_station: str
    fuel_type: FuelType
    liters: float
    price_per_liter: float
    total_cost: float
    current_odometer: int
    fuel_date: date
    receipt_image: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class FuelLogListResult(BaseModel):
    """Paginated fuel log listing payload."""

    items: list[FuelLogRead]
    total: int
    page: int
    size: int


FuelLogCreateResponse = APIResponse[FuelLogRead]
FuelLogUpdateResponse = APIResponse[FuelLogRead]
FuelLogListResponse = APIResponse[FuelLogListResult]
FuelLogDetailResponse = APIResponse[FuelLogRead]
FuelLogDeleteResponse = APIResponse[dict[str, str]]
FuelLogHistoryResponse = APIResponse[FuelLogListResult]
FuelLogVehicleResponse = APIResponse[FuelLogListResult]
