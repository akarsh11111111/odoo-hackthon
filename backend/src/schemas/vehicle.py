"""Vehicle registry request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.common import APIResponse


class VehicleCreateRequest(BaseModel):
    """Payload for creating a vehicle record."""

    registration_number: str = Field(min_length=1, examples=["ABC-123"])
    vehicle_name: str = Field(min_length=1, examples=["Box Truck"])
    vehicle_model: str = Field(min_length=1, examples=["Mercedes Actros"])
    vehicle_type: VehicleType = Field(examples=[VehicleType.TRUCK])
    maximum_load_capacity: int = Field(gt=0, examples=[12000])
    current_odometer: int = Field(ge=0, examples=[5000])
    acquisition_cost: float = Field(ge=0, examples=[180000.0])
    purchase_date: date = Field(examples=["2024-01-15"])
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, examples=[VehicleStatus.AVAILABLE])
    region: str = Field(min_length=1, examples=["North"])
    documents: list[str] = Field(default_factory=list, examples=[["insurance.pdf"]])
    insurance_expiry: date | None = Field(default=None, examples=["2025-01-01"])
    fitness_expiry: date | None = Field(default=None, examples=["2025-06-01"])
    pollution_expiry: date | None = Field(default=None, examples=["2025-07-01"])

    @field_validator("registration_number")
    @classmethod
    def normalize_registration_number(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("vehicle_name", "vehicle_model", "region")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()


class VehicleUpdateRequest(BaseModel):
    """Payload for updating an existing vehicle record."""

    registration_number: str | None = Field(default=None, min_length=1, examples=["ABC-124"])
    vehicle_name: str | None = Field(default=None, min_length=1, examples=["Box Truck"])
    vehicle_model: str | None = Field(default=None, min_length=1, examples=["Mercedes Actros"])
    vehicle_type: VehicleType | None = Field(default=None, examples=[VehicleType.TRUCK])
    maximum_load_capacity: int | None = Field(default=None, gt=0, examples=[14000])
    current_odometer: int | None = Field(default=None, ge=0, examples=[6000])
    acquisition_cost: float | None = Field(default=None, ge=0, examples=[200000.0])
    purchase_date: date | None = Field(default=None, examples=["2024-02-01"])
    status: VehicleStatus | None = Field(default=None, examples=[VehicleStatus.ON_TRIP])
    region: str | None = Field(default=None, min_length=1, examples=["Central"])
    documents: list[str] | None = Field(default=None, examples=[["insurance.pdf", "fitness.pdf"]])
    insurance_expiry: date | None = Field(default=None, examples=["2025-01-01"])
    fitness_expiry: date | None = Field(default=None, examples=["2025-06-01"])
    pollution_expiry: date | None = Field(default=None, examples=["2025-07-01"])
    previous_odometer: int | None = Field(default=None, ge=0, examples=[5000])

    @field_validator("registration_number")
    @classmethod
    def normalize_registration_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("vehicle_name", "vehicle_model", "region")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_odometer_against_previous(self) -> "VehicleUpdateRequest":
        if self.current_odometer is not None and self.previous_odometer is not None:
            if self.current_odometer < self.previous_odometer:
                raise ValueError("Current odometer cannot decrease")
        return self


class VehicleRead(BaseModel):
    """Public vehicle representation returned by the registry APIs."""

    id: str
    registration_number: str
    vehicle_name: str
    vehicle_model: str
    vehicle_type: VehicleType
    maximum_load_capacity: int
    current_odometer: int
    acquisition_cost: float
    purchase_date: date
    status: VehicleStatus
    region: str
    documents: list[str] = Field(default_factory=list)
    insurance_expiry: date | None = None
    fitness_expiry: date | None = None
    pollution_expiry: date | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class VehicleListResult(BaseModel):
    """Paginated vehicle listing payload."""

    items: list[VehicleRead]
    total: int
    page: int
    size: int


VehicleCreateResponse = APIResponse[VehicleRead]
VehicleUpdateResponse = APIResponse[VehicleRead]
VehicleListResponse = APIResponse[VehicleListResult]
VehicleDetailResponse = APIResponse[VehicleRead]
VehicleDeleteResponse = APIResponse[dict[str, str]]
VehicleSearchResponse = APIResponse[VehicleListResult]
VehicleAvailableResponse = APIResponse[VehicleListResult]
