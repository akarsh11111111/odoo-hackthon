"""Dashboard analytics service tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.services.dashboard import DashboardAnalyticsService


class FakeCollection:
    def __init__(self, data: list[dict[str, object]]) -> None:
        self.data = data

    def aggregate(self, pipeline: list[dict[str, object]]):
        return self

    async def to_list(self, length: int | None = None) -> list[dict[str, object]]:
        return self.data


class FakeDatabase:
    def __init__(self, collections: dict[str, list[dict[str, object]]]) -> None:
        self.collections = collections

    def get_collection(self, name: str) -> FakeCollection:
        return FakeCollection(self.collections[name])


@pytest.mark.asyncio
async def test_dashboard_overview_returns_expected_key_metrics() -> None:
    fake_database = FakeDatabase(
        collections={
            "vehicles": [
                {
                    "total_vehicles": 10,
                    "available_vehicles": 6,
                    "on_trip_vehicles": 2,
                    "vehicles_in_shop": 1,
                    "retired_vehicles": 1,
                }
            ],
            "drivers": [
                {
                    "total_drivers": 9,
                    "available_drivers": 5,
                    "drivers_on_trip": 2,
                    "drivers_suspended": 1,
                }
            ],
            "trips": [
                {
                    "total_active_trips": 3,
                    "completed_trips": 5,
                    "cancelled_trips": 1,
                    "pending_trips": 1,
                }
            ],
            "fuel_logs": [{"value": 20.0}],
            "maintenance_requests": [{"value": 15.0}],
            "expenses": [{"value": 5.0}],
            "vehicles_acquisition": [{"total_acquisition_cost": 1000.0}],
            "trips_distance": [{"distance_covered": 2500.0}],
        }
    )

    service = DashboardAnalyticsService(database=fake_database)
    service._aggregate = AsyncMock(side_effect=[fake_database.collections["vehicles"], fake_database.collections["drivers"], fake_database.collections["trips"], [{"value": 20.0}], [{"value": 15.0}], [{"value": 5.0}]])
    service._sum_numeric_value = AsyncMock(side_effect=[20.0, 5.0])
    service._sum_maintenance_cost = AsyncMock(return_value=15.0)
    service._average_numeric_value = AsyncMock(return_value=7.4)
    service._calculate_vehicle_roi = AsyncMock(return_value=2.5)

    result = await service.get_overview()

    assert result["total_vehicles"] == 10
    assert result["available_vehicles"] == 6
    assert result["fuel_cost"] == 20.0
    assert result["maintenance_cost"] == 15.0
    assert result["operational_cost"] == 40.0
    assert result["fleet_utilization_percent"] == 80.0
    assert result["average_fuel_efficiency"] == 7.4
    assert result["vehicle_roi"] == 2.5
