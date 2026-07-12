from __future__ import annotations

from src.services.audit import AuditLogService
from src.services.notification import NotificationService
from src.services.timeline import TimelineService
from src.services.search import GlobalSearchService


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.entries = []

    async def create(self, **log_data: object) -> dict[str, object]:
        self.entries.append(log_data)
        return log_data

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None) -> tuple[list[dict[str, object]], int]:
        items = self.entries[skip : skip + limit]
        return items, len(self.entries)


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.entries = [
            {
                "notification_id": "n-1",
                "type": "System",
                "priority": "High",
                "title": "Sync complete",
                "message": "Fleet sync finished",
                "recipient_user_id": "u-1",
                "is_read": False,
            }
        ]

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None) -> tuple[list[dict[str, object]], int]:
        items = self.entries[skip : skip + limit]
        return items, len(self.entries)

    async def mark_read(self, notification_id: str) -> dict[str, object] | None:
        for item in self.entries:
            if item["notification_id"] == notification_id:
                item["is_read"] = True
                return item
        return None

    async def mark_all_read(self, *, recipient_user_id: str) -> int:
        updated = 0
        for item in self.entries:
            if item.get("recipient_user_id") == recipient_user_id and not item.get("is_read"):
                item["is_read"] = True
                updated += 1
        return updated


class FakeSearchRepository:
    async def search(self, *, query: str, page: int = 1, size: int = 20) -> dict[str, object]:
        return {
            "items": [
                {"entity_type": "vehicles", "entity_id": "v-1", "name": "Vehicle 1"},
                {"entity_type": "drivers", "entity_id": "d-1", "name": "Driver 1"},
            ],
            "total": 2,
            "page": page,
            "size": size,
        }


async def test_audit_log_service_records_and_lists_entries() -> None:
    repo = FakeAuditLogRepository()
    service = AuditLogService(repository=repo)

    created = await service.record(
        entity_type="vehicles",
        entity_id="v-1",
        action="Vehicle Created",
        performed_by="u-1",
        performed_role="Fleet Manager",
        old_value=None,
        new_value={"registration_number": "ABC-123"},
        ip_address="127.0.0.1",
        user_agent="pytest",
    )

    assert created["entity_type"] == "vehicles"
    assert created["action"] == "Vehicle Created"
    assert len(repo.entries) == 1

    items, total = await service.list(page=1, size=10)
    assert total == 1
    assert len(items) == 1


async def test_notification_service_marks_notifications_read() -> None:
    repo = FakeNotificationRepository()
    service = NotificationService(repository=repo)

    result = await service.mark_read("n-1")
    assert result is not None
    assert result["is_read"] is True

    updated_count = await service.mark_all_read(recipient_user_id="u-1")
    assert updated_count == 0


async def test_timeline_and_global_search_services_return_unified_results() -> None:
    audit_service = AuditLogService(repository=FakeAuditLogRepository())
    notification_service = NotificationService(repository=FakeNotificationRepository())
    timeline_service = TimelineService(audit_service=audit_service, notification_service=notification_service)
    search_service = GlobalSearchService(repository=FakeSearchRepository())

    timeline = await timeline_service.list(page=1, size=10)
    assert timeline["total"] >= 0

    search_result = await search_service.search(query="vehicle", page=1, size=10)
    assert search_result["total"] == 2
    assert len(search_result["items"]) == 2
