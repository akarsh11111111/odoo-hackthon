"""Notification center document model."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class NotificationType(str, Enum):
    """Notification categories used by the control-plane module."""

    SYSTEM = "System"
    MAINTENANCE = "Maintenance"
    TRIP = "Trip"
    VEHICLE = "Vehicle"
    DRIVER = "Driver"
    FINANCE = "Finance"


class NotificationPriority(str, Enum):
    """Notification severity level."""

    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class Notification(Document):
    """User-facing notification stored in MongoDB."""

    notification_id: Indexed(str, unique=True) = Field(default_factory=lambda: uuid4().hex)
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    title: str
    message: str
    recipient_user_id: Indexed(str)
    entity_type: str | None = None
    entity_id: str | None = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    read_at: datetime | None = None

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("recipient_user_id", ASCENDING), ("is_read", ASCENDING)], name="notification_recipient_read_idx"),
            IndexModel([("recipient_user_id", ASCENDING), ("created_at", DESCENDING)], name="notification_recipient_created_idx"),
        ]
