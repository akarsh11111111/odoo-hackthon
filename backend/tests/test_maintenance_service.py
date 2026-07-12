from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest

from src.core.exceptions import BusinessRuleException, NotFoundException
from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.maintenance import (
    MaintenanceApproveRequest,
    MaintenanceCompleteRequest,
    MaintenanceCreateRequest,
    MaintenanceRejectRequest,
    MaintenanceStartRequest,
    MaintenanceUpdateRequest,
)
from src.services.maintenance import MaintenanceService


@dataclass
class FakeVehicle:
    id: str
    registration_number: str
    vehicle_name: str
    vehicle_model: str
    vehicle_type: str
    maximum_load_capacity: int
    current_odometer: int
    acquisition_cost: float
    purchase_date: date
    status: str
    region: str
    documents: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_by: str | None = None


@dataclass
class FakeTrip:
    id: str
    trip_number: str
    vehicle_id: str
    driver_id: str
    source: str
    destination: str
    cargo_description: str
    cargo_weight: float
    estimated_distance: float
    estimated_duration: int
    status: str
    priority: str
    dispatch_time: datetime | None = None
    expected_arrival: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FakeMaintenance:
    id: str
    maintenance_id: str
    vehicle_id: str
    maintenance_type: str
    title: str
    description: str
    priority: str
    vendor_name: str
    estimated_cost: float
    actual_cost: float | None = None
    scheduled_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str = "Pending"
    notes: str | None = None
    attachments: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_by: str | None = None


class FakeVehicleRepository:
    def __init__(self) -> None:
        self.vehicles = {
            "vehicle-1": FakeVehicle(
                id="vehicle-1",
                registration_number="ABC-123",
                vehicle_name="Box Truck",
                vehicle_model="Mercedes Actros",
                vehicle_type=VehicleType.TRUCK.value,
                maximum_load_capacity=12000,
                current_odometer=5000,
                acquisition_cost=180000.0,
                purchase_date=date(2024, 1, 15),
                status=VehicleStatus.AVAILABLE.value,
                region="North",
            ),
            "vehicle-2": FakeVehicle(
                id="vehicle-2",
                registration_number="RET-999",
                vehicle_name="Retired Van",
                vehicle_model="Old Van",
                vehicle_type=VehicleType.VAN.value,
                maximum_load_capacity=5000,
                current_odometer=3500,
                acquisition_cost=25000.0,
                purchase_date=date(2023, 1, 1),
                status=VehicleStatus.RETIRED.value,
                region="South",
            ),
        }

    async def get_by_id(self, vehicle_id: str) -> FakeVehicle | None:
        return self.vehicles.get(vehicle_id)

    async def update(self, vehicle_id: str, **vehicle_data: object) -> FakeVehicle:
        vehicle = self.vehicles[vehicle_id]
        if vehicle is None:
            raise NotFoundException("Vehicle not found")
        for key, value in vehicle_data.items():
            setattr(vehicle, key, value)
        vehicle.updated_at = datetime.now(timezone.utc)
        return vehicle


class FakeTripRepository:
    async def list_active(self) -> list[FakeTrip]:
        return []


class FakeMaintenanceRepository:
    def __init__(self) -> None:
        self.maintenances: dict[str, FakeMaintenance] = {}

    async def get_by_id(self, maintenance_id: str) -> FakeMaintenance | None:
        return self.maintenances.get(maintenance_id)

    async def get_by_maintenance_id(self, maintenance_id: str) -> FakeMaintenance | None:
        return next((item for item in self.maintenances.values() if item.maintenance_id == maintenance_id), None)

    async def create(self, **maintenance_data: object) -> FakeMaintenance:
        maintenance_id = f"maint-{len(self.maintenances) + 1}"
        maintenance = FakeMaintenance(id=maintenance_id, **maintenance_data)
        self.maintenances[maintenance_id] = maintenance
        return maintenance

    async def update(self, maintenance_id: str, **maintenance_data: object) -> FakeMaintenance:
        maintenance = self.maintenances[maintenance_id]
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")
        for key, value in maintenance_data.items():
            setattr(maintenance, key, value)
        maintenance.updated_at = datetime.now(timezone.utc)
        return maintenance

    async def delete(self, maintenance_id: str) -> FakeMaintenance:
        maintenance = self.maintenances[maintenance_id]
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")
        maintenance.is_active = False
        maintenance.updated_at = datetime.now(timezone.utc)
        return maintenance

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeMaintenance], int]:
        items = list(self.maintenances.values())
        if filters:
            if filters.get("vehicle_id"):
                items = [item for item in items if item.vehicle_id == filters["vehicle_id"]]
            if filters.get("status"):
                items = [item for item in items if item.status == filters["status"]]
            if filters.get("priority"):
                items = [item for item in items if item.priority == filters["priority"]]
            if filters.get("vendor_name"):
                items = [item for item in items if item.vendor_name == filters["vendor_name"]]
        if search:
            query = search.lower().strip()
            items = [item for item in items if query in item.maintenance_id.lower() or query in item.vendor_name.lower() or query in item.title.lower()]
        items = sorted(items, key=lambda item: getattr(item, sort_by), reverse=sort_order == "desc")
        return items[skip : skip + limit], len(items)

    async def list_active(self) -> list[FakeMaintenance]:
        return [item for item in self.maintenances.values() if item.status in {"Pending", "Approved", "In Progress"}]

    async def list_history(self) -> list[FakeMaintenance]:
        return [item for item in self.maintenances.values() if item.status in {"Completed", "Rejected"}]

    async def get_active_by_vehicle(self, vehicle_id: str) -> FakeMaintenance | None:
        return next((item for item in self.maintenances.values() if item.vehicle_id == vehicle_id and item.status in {"Pending", "Approved", "In Progress"}), None)


class FakeMaintenanceLogRepository:
    def __init__(self) -> None:
        self.logs: list[dict[str, object]] = []

    async def create(self, **log_data: object) -> dict[str, object]:
        self.logs.append(log_data)
        return log_data


@pytest.fixture()
def maintenance_service() -> MaintenanceService:
    return MaintenanceService(
        maintenance_repository=FakeMaintenanceRepository(),
        vehicle_repository=FakeVehicleRepository(),
        trip_repository=FakeTripRepository(),
        activity_log_repository=FakeMaintenanceLogRepository(),
    )


@pytest.mark.asyncio
async def test_create_maintenance_places_vehicle_in_shop_and_persists_request(maintenance_service: MaintenanceService) -> None:
    payload = MaintenanceCreateRequest(
        vehicle_id="vehicle-1",
        maintenance_type="Repair",
        title="Brake Inspection",
        description="Inspect front brakes and replace pads if needed.",
        priority="High",
        vendor_name="Metro Fleet Services",
        estimated_cost=320.0,
        scheduled_date=date(2026, 7, 15),
    )

    maintenance = await maintenance_service.create(payload, created_by="user-1")

    assert maintenance.status == "Pending"
    assert maintenance.maintenance_id.startswith("MAINT-")
    assert maintenance.vehicle_id == "vehicle-1"

    vehicle = await maintenance_service.vehicle_repository.get_by_id("vehicle-1")
    assert vehicle is not None
    assert vehicle.status == VehicleStatus.IN_SHOP.value


@pytest.mark.asyncio
async def test_get_by_id_returns_maintenance_read_model(maintenance_service: MaintenanceService) -> None:
    created = await maintenance_service.create(
        MaintenanceCreateRequest(
            vehicle_id="vehicle-1",
            maintenance_type="Repair",
            title="Brake Inspection",
            description="Inspect front brakes and replace pads if needed.",
            priority="High",
            vendor_name="Metro Fleet Services",
            estimated_cost=320.0,
            scheduled_date=date(2026, 7, 15),
        ),
        created_by="user-1",
    )

    fetched = await maintenance_service.get_by_id(created.id)

    assert fetched.id == created.id
    assert fetched.maintenance_id == created.maintenance_id
    assert fetched.vehicle_id == created.vehicle_id
    assert fetched.status == created.status


@pytest.mark.asyncio
async def test_complete_maintenance_restores_vehicle_to_available(maintenance_service: MaintenanceService) -> None:
    created = await maintenance_service.create(
        MaintenanceCreateRequest(
            vehicle_id="vehicle-1",
            maintenance_type="Repair",
            title="Brake Inspection",
            description="Inspect front brakes and replace pads if needed.",
            priority="High",
            vendor_name="Metro Fleet Services",
            estimated_cost=320.0,
            scheduled_date=date(2026, 7, 15),
        ),
        created_by="user-1",
    )

    await maintenance_service.approve(created.id, MaintenanceApproveRequest(), approved_by="user-2")
    await maintenance_service.start(created.id, MaintenanceStartRequest(), started_by="user-3")
    completed = await maintenance_service.complete(
        created.id,
        MaintenanceCompleteRequest(
            actual_cost=310.0,
            completion_notes="Brake pads replaced and alignment verified.",
        ),
        completed_by="user-4",
    )

    assert completed.status == "Completed"
    vehicle = await maintenance_service.vehicle_repository.get_by_id("vehicle-1")
    assert vehicle is not None
    assert vehicle.status == VehicleStatus.AVAILABLE.value
