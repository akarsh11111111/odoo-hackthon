"""Unified activity timeline service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.services.audit import AuditLogService
from src.services.notification import NotificationService


@dataclass(slots=True)
class TimelineService:
    """Aggregate audit and notification events into a unified timeline."""

    audit_service: AuditLogService
    notification_service: NotificationService

    async def list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_filters = filters or {}
        audit_filters = {
            "entity_type": normalized_filters.get("entity_type"),
            "entity_id": normalized_filters.get("entity_id"),
            "action": normalized_filters.get("action"),
            "performed_by": normalized_filters.get("user"),
            "date_from": normalized_filters.get("date_from"),
            "date_to": normalized_filters.get("date_to"),
        }
        notification_filters = {
            "recipient_user_id": normalized_filters.get("user"),
            "type": normalized_filters.get("entity_type"),
            "priority": normalized_filters.get("priority"),
            "is_read": normalized_filters.get("is_read"),
        }

        audit_items, audit_total = await self.audit_service.list(page=1, size=1000, filters=audit_filters)
        notification_items, notification_total = await self.notification_service.list(page=1, size=1000, filters=notification_filters)

        combined = [
            {
                "timeline_type": "audit",
                "event_id": item["audit_id"],
                "timestamp": item["timestamp"],
                "entity_type": item["entity_type"],
                "entity_id": item["entity_id"],
                "action": item["action"],
                "performed_by": item["performed_by"],
                "message": item["action"],
                "read_status": None,
            }
            for item in audit_items
        ] + [
            {
                "timeline_type": "notification",
                "event_id": item["notification_id"],
                "timestamp": item["created_at"],
                "entity_type": item["entity_type"],
                "entity_id": item["entity_id"],
                "action": item["type"],
                "performed_by": item["recipient_user_id"],
                "message": item["message"],
                "read_status": item["is_read"],
            }
            for item in notification_items
        ]

        combined.sort(key=lambda item: item["timestamp"], reverse=True)
        total = audit_total + notification_total
        skip = (page - 1) * size
        paginated = combined[skip : skip + size]
        return {
            "items": paginated,
            "total": total,
            "page": page,
            "size": size,
        }


def get_timeline_service() -> TimelineService:
    """Build a timeline service with the active audit and notification service dependencies."""

    from src.services.audit import get_audit_service
    from src.services.notification import get_notification_service

    return TimelineService(
        audit_service=get_audit_service(),
        notification_service=get_notification_service(),
    )
