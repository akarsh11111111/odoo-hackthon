"""Driver management Beanie documents."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class DriverStatus(str, Enum):
    """Operational availability status for a driver."""

    AVAILABLE = "Available"
    ON_TRIP = "On Trip"
    OFF_DUTY = "Off Duty"
    SUSPENDED = "Suspended"


class Driver(Document):
    """Driver profile stored in MongoDB."""

    license_number: Indexed(str, unique=True)
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
    years_of_experience: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "drivers"
        indexes = [
            IndexModel([("is_active", ASCENDING), ("driver_status", ASCENDING)], name="driver_active_status_idx"),
            IndexModel([("region", ASCENDING), ("driver_status", ASCENDING)], name="driver_region_status_idx"),
        ]


class DriverActivityLog(Document):
    """Audit trail entry for driver lifecycle events."""

    driver_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "driver_activity_logs"
