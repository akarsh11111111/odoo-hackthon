from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from src.constants.auth import DISPATCHER, FLEET_MANAGER
from src.core.config import get_settings
from src.main import create_app
from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.vehicle import VehicleCreateRequest, VehicleRead
from src.services.vehicle import get_vehicle_service


class FakeVehicleService:
    async def create(self, payload, created_by: str | None = None):
        return _fake_vehicle()

    async def list(self, *, page: int = 1, size: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None):
        return {"items": [_fake_vehicle()], "total": 1, "page": page, "size": size}

    async def get_by_id(self, vehicle_id: str):
        return _fake_vehicle()

    async def update(self, vehicle_id: str, payload, updated_by: str | None = None):
        return _fake_vehicle()

    async def delete(self, vehicle_id: str, deleted_by: str | None = None):
        return {"detail": "Vehicle deleted successfully"}

    async def search(self, *, query: str, page: int = 1, size: int = 20):
        return {"items": [_fake_vehicle()], "total": 1, "page": page, "size": size}

    async def list_available(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_vehicle()], "total": 1, "page": page, "size": size}


def _fake_vehicle() -> VehicleRead:
    return VehicleRead(
        id="vehicle-1",
        registration_number="ABC-123",
        vehicle_name="Box Truck",
        vehicle_model="Mercedes Actros",
        vehicle_type=VehicleType.TRUCK,
        maximum_load_capacity=12000,
        current_odometer=5000,
        acquisition_cost=180000.0,
        purchase_date=date(2024, 1, 15),
        status=VehicleStatus.AVAILABLE,
        region="North",
        documents=["insurance.pdf"],
        insurance_expiry=date(2025, 1, 1),
        fitness_expiry=date(2025, 6, 1),
        pollution_expiry=date(2025, 7, 1),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="user-1",
        updated_by="user-1",
    )


def test_vehicle_routes_are_mounted_and_return_envelope(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    app = create_app()
    app.dependency_overrides[get_vehicle_service] = lambda: FakeVehicleService()

    async def fake_current_active_user():
        return type("User", (), {"id": "user-1", "role_id": "role-1", "role_name": FLEET_MANAGER, "is_active": True})()

    from src.dependencies.auth import get_current_active_user

    app.dependency_overrides[get_current_active_user] = fake_current_active_user

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/vehicles",
            json={
                "registration_number": "ABC-123",
                "vehicle_name": "Box Truck",
                "vehicle_model": "Mercedes Actros",
                "vehicle_type": "Truck",
                "maximum_load_capacity": 12000,
                "current_odometer": 5000,
                "acquisition_cost": 180000,
                "purchase_date": "2024-01-15",
                "status": "Available",
                "region": "North",
                "documents": ["insurance.pdf"],
                "insurance_expiry": "2025-01-01",
                "fitness_expiry": "2025-06-01",
                "pollution_expiry": "2025-07-01",
            },
        )

    payload = response.json()
    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["registration_number"] == "ABC-123"
