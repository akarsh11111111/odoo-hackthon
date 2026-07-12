"""Notification center service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.repositories.notification import NotificationRepository


@dataclass(slots=True)
class NotificationService:
    """Read-only notification management service for the enterprise control-plane."""

    repository: NotificationRepository

    async def list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        skip = (page - 1) * size
        items, total = await self.repository.list(skip=skip, limit=size, filters=filters)
        return [self._to_read(item) for item in items], total

    async def mark_read(self, notification_id: str) -> dict[str, Any] | None:
        notification = await self.repository.mark_read(notification_id)
        if notification is None:
            return None
        return self._to_read(notification)

    async def mark_all_read(self, *, recipient_user_id: str) -> int:
        return await self.repository.mark_all_read(recipient_user_id=recipient_user_id)

    @staticmethod
    def _to_read(entry: Any) -> dict[str, Any]:
        if isinstance(entry, dict):
            return {
                "notification_id": entry.get("notification_id"),
                "type": entry.get("type"),
                "priority": entry.get("priority"),
                "title": entry.get("title"),
                "message": entry.get("message"),
                "recipient_user_id": entry.get("recipient_user_id"),
                "entity_type": entry.get("entity_type"),
                "entity_id": entry.get("entity_id"),
                "is_read": entry.get("is_read"),
                "created_at": entry.get("created_at"),
                "read_at": entry.get("read_at"),
            }

        return {
            "notification_id": getattr(entry, "notification_id", None),
            "type": entry.type,
            "priority": entry.priority,
            "title": entry.title,
            "message": entry.message,
            "recipient_user_id": entry.recipient_user_id,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "is_read": entry.is_read,
            "created_at": entry.created_at,
            "read_at": entry.read_at,
        }


def get_notification_service() -> NotificationService:
    """Build a notification service with the active repository dependency."""

    return NotificationService(repository=NotificationRepository())
