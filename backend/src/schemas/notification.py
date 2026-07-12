"""Notification center API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationRead(BaseModel):
    """Notification payload for the notification center."""

    notification_id: str
    type: str
    priority: str
    title: str
    message: str
    recipient_user_id: str
    entity_type: str | None = None
    entity_id: str | None = None
    is_read: bool = False
    created_at: datetime
    read_at: datetime | None = None


class NotificationListResponse(BaseModel):
    """Paginated notification list response."""

    items: list[NotificationRead]
    total: int
    page: int
    size: int


class NotificationMarkReadResponse(BaseModel):
    """Single notification mark-read response."""

    notification_id: str
    is_read: bool
    read_at: datetime | None = None


class NotificationReadAllResponse(BaseModel):
    """Bulk notification update response."""

    updated_count: int = Field(..., examples=[1])
