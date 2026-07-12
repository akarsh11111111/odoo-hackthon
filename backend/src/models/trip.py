"""Trip logistics Beanie documents."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class TripStatus(str, Enum):
    """Lifecycle status for a trip record."""

    DRAFT = "Draft"
    DISPATCHED = "Dispatched"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TripPriority(str, Enum):
    """Priority classification for operational routing."""

    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class Trip(Document):
    """Operational trip document stored in MongoDB."""

    trip_number: Indexed(str, unique=True)
    vehicle_id: PydanticObjectId
    driver_id: PydanticObjectId
    source: str
    destination: str
    cargo_description: str
    cargo_weight: float = Field(ge=0)
    estimated_distance: float = Field(ge=0)
    estimated_duration: int = Field(ge=0)
    dispatch_time: datetime | None = None
    expected_arrival: datetime | None = None
    priority: TripPriority
    status: TripStatus = Field(default=TripStatus.DRAFT)
    actual_distance: float | None = Field(default=None, ge=0)
    fuel_consumed: float | None = Field(default=None, ge=0)
    final_odometer: float | None = Field(default=None, ge=0)
    completion_notes: str | None = None
    cancellation_reason: str | None = None
    fuel_efficiency: float | None = Field(default=None, ge=0)
    actual_duration: int | None = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "trips"


class TripActivityLog(Document):
    """Audit trail entry for trip lifecycle operations."""

    trip_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "trip_activity_logs"
