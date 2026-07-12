"""Driver management request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.driver import DriverStatus
from src.schemas.common import APIResponse


class DriverCreateRequest(BaseModel):
    """Payload for creating a driver record."""

    license_number: str = Field(min_length=1, examples=["DL-1001"])
    first_name: str = Field(min_length=1, examples=["Asha"])
    last_name: str = Field(min_length=1, examples=["Patel"])
    phone: str | None = Field(default=None, examples=["+15550000001"])
    email: str | None = Field(default=None, examples=["asha@example.com"])
    address: str | None = Field(default=None, examples=["12 Main Road"])
    date_of_birth: date | None = Field(default=None, examples=["1990-05-20"])
    license_expiry: date = Field(examples=["2027-01-01"])
    safety_score: int = Field(ge=0, le=100, examples=[92])
    driver_status: DriverStatus = Field(default=DriverStatus.AVAILABLE, examples=[DriverStatus.AVAILABLE])
    region: str = Field(min_length=1, examples=["North"])
    documents: list[str] = Field(default_factory=list, examples=[["license.pdf"]])
    years_of_experience: int = Field(ge=0, examples=[6])

    @field_validator("license_number")
    @classmethod
    def normalize_license_number(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("first_name", "last_name", "region", "address")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class DriverUpdateRequest(BaseModel):
    """Payload for updating an existing driver record."""

    license_number: str | None = Field(default=None, min_length=1, examples=["DL-1002"])
    first_name: str | None = Field(default=None, min_length=1, examples=["Asha"])
    last_name: str | None = Field(default=None, min_length=1, examples=["Patel"])
    phone: str | None = Field(default=None, examples=["+15550000001"])
    email: str | None = Field(default=None, examples=["asha@example.com"])
    address: str | None = Field(default=None, examples=["12 Main Road"])
    date_of_birth: date | None = Field(default=None, examples=["1990-05-20"])
    license_expiry: date | None = Field(default=None, examples=["2027-01-01"])
    safety_score: int | None = Field(default=None, ge=0, le=100, examples=[92])
    driver_status: DriverStatus | None = Field(default=None, examples=[DriverStatus.AVAILABLE])
    region: str | None = Field(default=None, min_length=1, examples=["North"])
    documents: list[str] | None = Field(default=None, examples=[["license.pdf"]])
    years_of_experience: int | None = Field(default=None, ge=0, examples=[7])

    @field_validator("license_number")
    @classmethod
    def normalize_license_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("first_name", "last_name", "region", "address")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_driver_update(self) -> "DriverUpdateRequest":
        if self.license_expiry is not None and self.license_expiry < date.today():
            raise ValueError("License expiry must be in the future")
        return self


class DriverRead(BaseModel):
    """Public driver representation returned by the driver APIs."""

    id: str
    license_number: str
    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    date_of_birth: date | None = None
    license_expiry: date
    safety_score: int
    driver_status: DriverStatus
    region: str
    documents: list[str] = Field(default_factory=list)
    years_of_experience: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class DriverListResult(BaseModel):
    """Paginated driver listing payload."""

    items: list[DriverRead]
    total: int
    page: int
    size: int


DriverCreateResponse = APIResponse[DriverRead]
DriverUpdateResponse = APIResponse[DriverRead]
DriverListResponse = APIResponse[DriverListResult]
DriverDetailResponse = APIResponse[DriverRead]
DriverDeleteResponse = APIResponse[dict[str, str]]
DriverSearchResponse = APIResponse[DriverListResult]
DriverAvailableResponse = APIResponse[DriverListResult]
