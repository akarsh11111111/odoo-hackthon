"""Enterprise audit log document model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class AuditLog(Document):
    """Central audit trail entry for system-wide actions."""

    audit_id: Indexed(str, unique=True) = Field(default_factory=lambda: uuid4().hex)
    entity_type: Indexed(str)
    entity_id: str
    action: Indexed(str)
    performed_by: Indexed(str) | None = None
    performed_role: str | None = None
    timestamp: datetime = Field(default_factory=utcnow)
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None

    class Settings:
        name = "audit_logs"
        indexes = [
            IndexModel([("entity_type", ASCENDING), ("entity_id", ASCENDING), ("timestamp", DESCENDING)], name="audit_entity_timestamp_idx"),
            IndexModel([("performed_by", ASCENDING), ("timestamp", DESCENDING)], name="audit_actor_timestamp_idx"),
        ]
