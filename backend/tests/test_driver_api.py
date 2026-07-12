from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from src.constants.auth import FLEET_MANAGER
from src.core.config import get_settings
from src.main import create_app
from src.models.driver import DriverStatus
from src.schemas.driver import DriverCreateRequest, DriverRead
from src.services.driver import get_driver_service


class FakeDriverService:
    async def create(self, payload, created_by: str | None = None):
        return _fake_driver()

    async def list(self, *, page: int = 1, size: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None):
        return {"items": [_fake_driver()], "total": 1, "page": page, "size": size}

    async def get_by_id(self, driver_id: str):
        return _fake_driver()

    async def update(self, driver_id: str, payload, updated_by: str | None = None):
        return _fake_driver()

    async def delete(self, driver_id: str, deleted_by: str | None = None):
        return {"detail": "Driver deleted successfully"}

    async def list_available(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_driver()], "total": 1, "page": page, "size": size}


def _fake_driver() -> DriverRead:
    return DriverRead(
        id="driver-1",
        license_number="DL-1001",
        first_name="Asha",
        last_name="Patel",
        phone="+15550000001",
        email="asha@example.com",
        address="12 Main Road",
        date_of_birth=date(1990, 5, 20),
        license_expiry=date(2027, 1, 1),
        safety_score=92,
        driver_status=DriverStatus.AVAILABLE,
        region="North",
        documents=["license.pdf"],
        years_of_experience=6,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="user-1",
        updated_by="user-1",
    )


def test_driver_routes_are_mounted_and_return_envelope(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    app = create_app()
    app.dependency_overrides[get_driver_service] = lambda: FakeDriverService()

    async def fake_current_active_user():
        return type("User", (), {"id": "user-1", "role_id": "role-1", "role_name": FLEET_MANAGER, "is_active": True})()

    from src.dependencies.auth import get_current_active_user

    app.dependency_overrides[get_current_active_user] = fake_current_active_user

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/drivers",
            json={
                "license_number": "DL-1001",
                "first_name": "Asha",
                "last_name": "Patel",
                "phone": "+15550000001",
                "email": "asha@example.com",
                "address": "12 Main Road",
                "date_of_birth": "1990-05-20",
                "license_expiry": "2027-01-01",
                "safety_score": 92,
                "driver_status": "Available",
                "region": "North",
                "documents": ["license.pdf"],
                "years_of_experience": 6,
            },
        )

    payload = response.json()
    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["license_number"] == "DL-1001"
