"""Trip logistics request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.trip import TripPriority, TripStatus
from src.schemas.common import APIResponse


class TripCreateRequest(BaseModel):
    """Payload for creating a trip record."""

    vehicle_id: str = Field(min_length=1, examples=["vehicle-1"])
    driver_id: str = Field(min_length=1, examples=["driver-1"])
    source: str = Field(min_length=1, examples=["Hub A"])
    destination: str = Field(min_length=1, examples=["Hub B"])
    cargo_description: str = Field(min_length=1, examples=["Medical supplies"])
    cargo_weight: float = Field(ge=0, examples=[5000.0])
    estimated_distance: float = Field(ge=0, examples=[140.0])
    estimated_duration: int = Field(ge=0, examples=[180])
    dispatch_time: datetime | None = Field(default=None, examples=["2026-07-12T08:00:00+00:00"])
    expected_arrival: datetime | None = Field(default=None, examples=["2026-07-12T11:00:00+00:00"])
    priority: TripPriority = Field(default=TripPriority.NORMAL, examples=[TripPriority.HIGH])
    status: TripStatus = Field(default=TripStatus.DRAFT, examples=[TripStatus.DRAFT])

    @field_validator("source", "destination", "cargo_description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_time_window(self) -> "TripCreateRequest":
        if self.dispatch_time is not None and self.expected_arrival is not None:
            if self.expected_arrival < self.dispatch_time:
                raise ValueError("Expected arrival must be after dispatch time")
        return self


class TripUpdateRequest(BaseModel):
    """Payload for updating an existing trip record."""

    vehicle_id: str | None = Field(default=None, min_length=1, examples=["vehicle-2"])
    driver_id: str | None = Field(default=None, min_length=1, examples=["driver-2"])
    source: str | None = Field(default=None, min_length=1, examples=["Hub C"])
    destination: str | None = Field(default=None, min_length=1, examples=["Hub D"])
    cargo_description: str | None = Field(default=None, min_length=1, examples=["Spare parts"])
    cargo_weight: float | None = Field(default=None, ge=0, examples=[4500.0])
    estimated_distance: float | None = Field(default=None, ge=0, examples=[150.0])
    estimated_duration: int | None = Field(default=None, ge=0, examples=[200])
    dispatch_time: datetime | None = Field(default=None, examples=["2026-07-12T08:00:00+00:00"])
    expected_arrival: datetime | None = Field(default=None, examples=["2026-07-12T11:00:00+00:00"])
    priority: TripPriority | None = Field(default=None, examples=[TripPriority.HIGH])
    status: TripStatus | None = Field(default=None, examples=[TripStatus.DRAFT])
    actual_distance: float | None = Field(default=None, ge=0, examples=[150.0])
    fuel_consumed: float | None = Field(default=None, ge=0, examples=[38.0])
    final_odometer: float | None = Field(default=None, ge=0, examples=[5150.0])
    completion_notes: str | None = Field(default=None, examples=["Delivered on time"])
    cancellation_reason: str | None = Field(default=None, examples=["Weather alert"])

    @field_validator("source", "destination", "cargo_description", "completion_notes", "cancellation_reason")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_time_window(self) -> "TripUpdateRequest":
        if self.dispatch_time is not None and self.expected_arrival is not None:
            if self.expected_arrival < self.dispatch_time:
                raise ValueError("Expected arrival must be after dispatch time")
        return self


class TripDispatchRequest(BaseModel):
    """Payload used when dispatching a trip."""

    dispatch_time: datetime | None = Field(default=None, examples=["2026-07-12T08:00:00+00:00"])
    expected_arrival: datetime | None = Field(default=None, examples=["2026-07-12T11:00:00+00:00"])


class TripCompleteRequest(BaseModel):
    """Payload used when completing a dispatched trip."""

    final_distance: float = Field(ge=0, examples=[150.0])
    fuel_consumed: float = Field(ge=0, examples=[38.0])
    final_odometer: float = Field(ge=0, examples=[5150.0])
    completion_notes: str = Field(min_length=1, examples=["Delivered on time"])


class TripRead(BaseModel):
    """Public trip representation returned by the API."""

    id: str
    trip_number: str
    vehicle_id: str
    driver_id: str
    source: str
    destination: str
    cargo_description: str
    cargo_weight: float
    estimated_distance: float
    estimated_duration: int
    dispatch_time: datetime | None = None
    expected_arrival: datetime | None = None
    priority: TripPriority
    status: TripStatus
    actual_distance: float | None = None
    fuel_consumed: float | None = None
    final_odometer: float | None = None
    completion_notes: str | None = None
    cancellation_reason: str | None = None
    fuel_efficiency: float | None = None
    actual_duration: int | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class TripListResult(BaseModel):
    """Paginated trip listing payload."""

    items: list[TripRead]
    total: int
    page: int
    size: int


TripCreateResponse = APIResponse[TripRead]
TripUpdateResponse = APIResponse[TripRead]
TripListResponse = APIResponse[TripListResult]
TripDetailResponse = APIResponse[TripRead]
TripDeleteResponse = APIResponse[dict[str, str]]
TripDispatchResponse = APIResponse[TripRead]
TripCompleteResponse = APIResponse[TripRead]
TripCancelResponse = APIResponse[TripRead]
TripActiveResponse = APIResponse[TripListResult]
TripHistoryResponse = APIResponse[TripListResult]
