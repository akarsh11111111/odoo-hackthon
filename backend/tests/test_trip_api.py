from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.constants.auth import FLEET_MANAGER
from src.core.config import get_settings
from src.main import create_app
from src.models.trip import TripPriority, TripStatus
from src.schemas.trip import TripCreateRequest, TripRead
from src.services.trip import get_trip_service


class FakeTripService:
    async def create(self, payload, created_by: str | None = None):
        return _fake_trip()

    async def list(self, *, page: int = 1, size: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None):
        return {"items": [_fake_trip()], "total": 1, "page": page, "size": size}

    async def get_by_id(self, trip_id: str):
        return _fake_trip()

    async def update(self, trip_id: str, payload, updated_by: str | None = None):
        return _fake_trip()

    async def delete(self, trip_id: str, deleted_by: str | None = None):
        return {"detail": "Trip deleted successfully"}

    async def dispatch(self, trip_id: str, payload, dispatched_by: str | None = None):
        return _fake_trip(status=TripStatus.DISPATCHED)

    async def complete(self, trip_id: str, payload, completed_by: str | None = None):
        return _fake_trip(status=TripStatus.COMPLETED)

    async def cancel(self, trip_id: str, cancellation_reason: str | None = None, cancelled_by: str | None = None):
        return _fake_trip(status=TripStatus.CANCELLED)

    async def list_active(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_trip(status=TripStatus.DISPATCHED)], "total": 1, "page": page, "size": size}

    async def list_history(self, *, page: int = 1, size: int = 20):
        return {"items": [_fake_trip(status=TripStatus.COMPLETED)], "total": 1, "page": page, "size": size}


def _fake_trip(*, status: TripStatus = TripStatus.DRAFT) -> TripRead:
    return TripRead(
        id="trip-1",
        trip_number="TRIP-20260712-0001",
        vehicle_id="vehicle-1",
        driver_id="driver-1",
        source="Hub A",
        destination="Hub B",
        cargo_description="Medical supplies",
        cargo_weight=5000.0,
        estimated_distance=140.0,
        estimated_duration=180,
        dispatch_time=datetime(2026, 7, 12, 8, 0, tzinfo=timezone.utc),
        expected_arrival=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc),
        priority=TripPriority.HIGH,
        status=status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="user-1",
        updated_by="user-1",
    )


def test_trip_routes_are_mounted_and_return_envelope(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    app = create_app()
    app.dependency_overrides[get_trip_service] = lambda: FakeTripService()

    async def fake_current_active_user():
        return type("User", (), {"id": "user-1", "role_id": "role-1", "role_name": FLEET_MANAGER, "is_active": True})()

    from src.dependencies.auth import get_current_active_user

    app.dependency_overrides[get_current_active_user] = fake_current_active_user

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/trips",
            json={
                "vehicle_id": "vehicle-1",
                "driver_id": "driver-1",
                "source": "Hub A",
                "destination": "Hub B",
                "cargo_description": "Medical supplies",
                "cargo_weight": 5000,
                "estimated_distance": 140,
                "estimated_duration": 180,
                "dispatch_time": "2026-07-12T08:00:00+00:00",
                "expected_arrival": "2026-07-12T11:00:00+00:00",
                "priority": "High",
                "status": "Draft",
            },
        )

    payload = response.json()
    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["trip_number"] == "TRIP-20260712-0001"
