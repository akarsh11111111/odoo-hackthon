"""Repository access for the notification center collection."""

from __future__ import annotations

from typing import Any

from src.core.database import get_database
from src.models.notification import Notification, NotificationPriority, NotificationType, utcnow


class NotificationRepository:
    """Repository for notification center records."""

    def __init__(self, database: Any | None = None) -> None:
        self.database = database if database is not None else get_database()

    async def create(self, **notification_data: Any) -> Notification:
        notification = Notification(**notification_data)
        notification.created_at = notification.created_at or utcnow()
        return await notification.insert()

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[Notification], int]:
        query = Notification.find()
        normalized = filters or {}

        if normalized.get("recipient_user_id"):
            query = query.find(Notification.recipient_user_id == str(normalized["recipient_user_id"]))
        if normalized.get("is_read") is not None:
            query = query.find(Notification.is_read == bool(normalized["is_read"]))
        if normalized.get("type"):
            query = query.find(Notification.type == NotificationType(str(normalized["type"])))
        if normalized.get("priority"):
            query = query.find(Notification.priority == NotificationPriority(str(normalized["priority"])))

        items = await query.sort(-Notification.created_at).skip(skip).limit(limit).to_list()
        total = await query.count()
        return items, total

    async def mark_read(self, notification_id: str) -> Notification | None:
        notification = await Notification.find_one(Notification.notification_id == notification_id)
        if notification is None:
            return None
        notification.is_read = True
        notification.read_at = utcnow()
        await notification.save()
        return notification

    async def mark_all_read(self, *, recipient_user_id: str) -> int:
        notifications = await Notification.find(
            (Notification.recipient_user_id == recipient_user_id) & (Notification.is_read == False)
        ).to_list()
        updated = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = utcnow()
            await notification.save()
            updated += 1
        return updated
