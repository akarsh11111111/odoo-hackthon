"""Fuel management Beanie documents."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class FuelType(str, Enum):
    """Fuel classification used by fleet operations."""

    DIESEL = "Diesel"
    PETROL = "Petrol"
    CNG = "CNG"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"
    OTHER = "Other"


class FuelLog(Document):
    """Fuel consumption record persisted in MongoDB."""

    fuel_log_id: Indexed(str, unique=True)
    vehicle_id: PydanticObjectId
    trip_id: PydanticObjectId | None = None
    driver_id: PydanticObjectId
    fuel_station: str
    fuel_type: FuelType
    liters: float = Field(ge=0)
    price_per_liter: float = Field(ge=0)
    total_cost: float = Field(ge=0)
    current_odometer: int = Field(ge=0)
    fuel_date: date
    receipt_image: str | None = None
    notes: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "fuel_logs"


class FuelLogActivityLog(Document):
    """Audit trail entry for fuel lifecycle events."""

    fuel_log_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "fuel_log_activity_logs"
