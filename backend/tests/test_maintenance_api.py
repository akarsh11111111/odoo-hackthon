from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from src.constants.auth import DISPATCHER, FLEET_MANAGER
from src.core.config import get_settings
from src.main import create_app
from src.models.maintenance import MaintenancePriority, MaintenanceStatus, MaintenanceType
from src.schemas.maintenance import MaintenanceCreateRequest, MaintenanceRead
from src.services.maintenance import get_maintenance_service


class FakeMaintenanceService:
    async def create(self, payload, created_by: str | None = None):
        return _fake_maintenance()

    async def list(self, *, page: int = 1, size: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None):
        return {"items": [_fake_maintenance()], "total": 1, "page": page, "size": size}

    async def get_by_id(self, maintenance_id: str):
        return _fake_maintenance()

    async def update(self, maintenance_id: str, payload, updated_by: str | None = None):
        return _fake_maintenance()

    async def delete(self, maintenance_id: str, deleted_by: str | None = None):
        return {"detail": "Maintenance deleted successfully"}

    async def approve(self, maintenance_id: str, payload, approved_by: str | None = None):
        return _fake_maintenance()

    async def reject(self, maintenance_id: str, payload, rejected_by: str | None = None):
        return _fake_maintenance()

    async def start(self, maintenance_id: str, payload, started_by: str | None = None):
        return _fake_maintenance()

    async def complete(self, maintenance_id: str, payload, completed_by: str | None = None):
        return _fake_maintenance()

    async def list_active(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_maintenance()], "total": 1, "page": page, "size": size}

    async def list_history(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_maintenance()], "total": 1, "page": page, "size": size}


def _fake_maintenance() -> MaintenanceRead:
    return MaintenanceRead(
        id="maint-1",
        maintenance_id="MAINT-20260712-0001",
        vehicle_id="vehicle-1",
        maintenance_type=MaintenanceType.REPAIR,
        title="Brake Inspection",
        description="Inspect front brakes and replace pads if needed.",
        priority=MaintenancePriority.HIGH,
        vendor_name="Metro Fleet Services",
        estimated_cost=320.0,
        actual_cost=None,
        scheduled_date=date(2026, 7, 15),
        started_at=None,
        completed_at=None,
        status=MaintenanceStatus.PENDING,
        notes=None,
        attachments=["inspection.pdf"],
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="user-1",
        updated_by="user-1",
    )


def test_maintenance_routes_are_mounted_and_return_envelope(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    app = create_app()
    app.dependency_overrides[get_maintenance_service] = lambda: FakeMaintenanceService()

    async def fake_current_active_user():
        return type("User", (), {"id": "user-1", "role_id": "role-1", "role_name": FLEET_MANAGER, "is_active": True})()

    from src.dependencies.auth import get_current_active_user

    app.dependency_overrides[get_current_active_user] = fake_current_active_user

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/maintenance",
            json={
                "vehicle_id": "vehicle-1",
                "maintenance_type": "Repair",
                "title": "Brake Inspection",
                "description": "Inspect front brakes and replace pads if needed.",
                "priority": "High",
                "vendor_name": "Metro Fleet Services",
                "estimated_cost": 320.0,
                "scheduled_date": "2026-07-15",
                "attachments": ["inspection.pdf"],
            },
        )

    payload = response.json()
    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["maintenance_id"] == "MAINT-20260712-0001"
