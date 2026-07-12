"""Timeline API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TimelineEntry(BaseModel):
    """Unified timeline event returned by the control-plane API."""

    timeline_type: str
    event_id: str
    timestamp: datetime
    entity_type: str | None = None
    entity_id: str | None = None
    action: str
    performed_by: str | None = None
    message: str
    read_status: bool | None = None


class TimelineListResponse(BaseModel):
    """Paginated timeline response."""

    items: list[TimelineEntry]
    total: int
    page: int
    size: int
