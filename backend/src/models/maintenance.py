"""Maintenance management Beanie documents."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class MaintenanceStatus(str, Enum):
    """Lifecycle status for a maintenance request."""

    PENDING = "Pending"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REJECTED = "Rejected"


class MaintenancePriority(str, Enum):
    """Priority classification for maintenance requests."""

    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class MaintenanceType(str, Enum):
    """Maintenance classification used by the fleet operations team."""

    INSPECTION = "Inspection"
    REPAIR = "Repair"
    SERVICE = "Service"
    EMERGENCY = "Emergency"
    OTHER = "Other"


class Maintenance(Document):
    """Operational maintenance request stored in MongoDB."""

    maintenance_id: Indexed(str, unique=True)
    vehicle_id: PydanticObjectId
    maintenance_type: MaintenanceType
    title: str
    description: str
    priority: MaintenancePriority
    vendor_name: str
    estimated_cost: float = Field(ge=0)
    actual_cost: float | None = Field(default=None, ge=0)
    scheduled_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: MaintenanceStatus = Field(default=MaintenanceStatus.PENDING)
    notes: str | None = None
    attachments: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "maintenance_requests"
        indexes = [
            IndexModel([("vehicle_id", ASCENDING), ("status", ASCENDING)], name="maintenance_vehicle_status_idx"),
            IndexModel([("status", ASCENDING), ("priority", ASCENDING)], name="maintenance_status_priority_idx"),
            IndexModel([("created_at", DESCENDING)], name="maintenance_created_at_idx"),
        ]


class MaintenanceLog(Document):
    """Audit trail entry for maintenance lifecycle events."""

    maintenance_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "maintenance_logs"
