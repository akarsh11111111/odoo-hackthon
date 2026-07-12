"""Reports and export service regression coverage."""

from __future__ import annotations

from fastapi.responses import StreamingResponse

from src.services.reports import ExportService, ReportsService


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


async def test_reports_service_summary_uses_aggregation_shape() -> None:
    fake_database = FakeDatabase(
        collections={
            "vehicles": [{"total_vehicles": 12, "available_vehicles": 8, "on_trip_vehicles": 3, "vehicles_in_shop": 1}],
            "drivers": [{"total_drivers": 10, "available_drivers": 6, "drivers_on_trip": 2, "drivers_suspended": 1}],
            "trips": [{"total_active_trips": 4, "completed_trips": 56, "cancelled_trips": 2, "pending_trips": 1}],
            "fuel_logs": [{"value": 150.0}],
            "maintenance_requests": [{"value": 90.0}],
            "expenses": [{"value": 35.0}],
        }
    )

    service = ReportsService(database=fake_database)
    result = await service.get_summary(filters={})

    assert result["total_vehicles"] == 12
    assert result["total_drivers"] == 10
    assert result["total_active_trips"] == 4
    assert result["fuel_cost"] == 150.0
    assert result["maintenance_cost"] == 90.0
    assert result["operational_cost"] == 275.0


async def test_export_service_csv_streams_report_rows() -> None:
    fake_database = FakeDatabase(
        collections={
            "vehicles": [
                {"vehicle_id": "v-1", "registration_number": "ABC-123", "status": "Available"},
                {"vehicle_id": "v-2", "registration_number": "DEF-456", "status": "On Trip"},
            ]
        }
    )

    export_service = ExportService(database=fake_database)
    response = await export_service.export_csv(report_name="fleet", filters={})

    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/csv"
    assert response.headers["content-disposition"].startswith("attachment; filename=")
