"""Vehicle registry Beanie documents."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class VehicleStatus(str, Enum):
    """Lifecycle status for a vehicle record."""

    AVAILABLE = "Available"
    ON_TRIP = "On Trip"
    IN_SHOP = "In Shop"
    RETIRED = "Retired"


class VehicleType(str, Enum):
    """Vehicle classification used by the registry."""

    BUS = "Bus"
    TRUCK = "Truck"
    VAN = "Van"
    CAR = "Car"
    MOTORCYCLE = "Motorcycle"
    OTHER = "Other"


class Vehicle(Document):
    """Fleet vehicle stored in MongoDB."""

    registration_number: Indexed(str, unique=True)
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
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "vehicles"


class VehicleActivityLog(Document):
    """Audit trail entry for vehicle registry lifecycle events."""

    vehicle_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "vehicle_activity_logs"
