from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest

from src.constants.auth import FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.vehicle import Vehicle, VehicleStatus, VehicleType
from src.repositories.vehicle import VehicleRepository
from src.schemas.vehicle import VehicleCreateRequest, VehicleUpdateRequest
from src.services.vehicle import VehicleService


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
    insurance_expiry: date | None = None
    fitness_expiry: date | None = None
    pollution_expiry: date | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_by: str | None = None


class FakeVehicleRepository(VehicleRepository):
    def __init__(self) -> None:
        self.vehicles: dict[str, FakeVehicle] = {}

    async def get_by_registration_number(self, registration_number: str) -> FakeVehicle | None:
        return next((vehicle for vehicle in self.vehicles.values() if vehicle.registration_number == registration_number), None)

    async def get_by_id(self, vehicle_id: str) -> FakeVehicle | None:
        return self.vehicles.get(vehicle_id)

    async def create(self, **vehicle_data: object) -> FakeVehicle:
        vehicle_id = f"vehicle-{len(self.vehicles) + 1}"
        vehicle = FakeVehicle(id=vehicle_id, **vehicle_data)
        self.vehicles[vehicle_id] = vehicle
        return vehicle

    async def update(self, vehicle_id: str, **vehicle_data: object) -> FakeVehicle:
        vehicle = self.vehicles[vehicle_id]
        if vehicle is None:
            raise NotFoundException("Vehicle not found")
        for key, value in vehicle_data.items():
            setattr(vehicle, key, value)
        vehicle.updated_at = datetime.now(timezone.utc)
        return vehicle

    async def delete(self, vehicle_id: str) -> None:
        vehicle = self.vehicles[vehicle_id]
        if vehicle is None:
            raise NotFoundException("Vehicle not found")
        vehicle.is_active = False
        vehicle.updated_at = datetime.now(timezone.utc)

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeVehicle], int]:
        items = list(self.vehicles.values())
        if filters:
            if filters.get("region"):
                items = [item for item in items if item.region == filters["region"]]
            if filters.get("status"):
                items = [item for item in items if item.status == filters["status"]]
            if filters.get("vehicle_type"):
                items = [item for item in items if item.vehicle_type == filters["vehicle_type"]]
        if search:
            items = [item for item in items if search.lower() in item.vehicle_name.lower()]
        items = sorted(items, key=lambda item: getattr(item, sort_by), reverse=sort_order == "desc")
        return items[skip : skip + limit], len(items)

    async def list_available(self) -> list[FakeVehicle]:
        return [vehicle for vehicle in self.vehicles.values() if vehicle.status == VehicleStatus.AVAILABLE.value and vehicle.is_active]


@pytest.fixture()
def vehicle_service() -> VehicleService:
    return VehicleService(vehicle_repository=FakeVehicleRepository())


@pytest.mark.asyncio
async def test_create_vehicle_uses_auditing_and_persists_fields(vehicle_service: VehicleService) -> None:
    payload = VehicleCreateRequest(
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
    )

    vehicle = await vehicle_service.create(payload, created_by="user-1")

    assert vehicle.registration_number == "ABC-123"
    assert vehicle.created_by == "user-1"
    assert vehicle.status == VehicleStatus.AVAILABLE


@pytest.mark.asyncio
async def test_vehicle_service_rejects_duplicate_registration_and_odometer_regression(vehicle_service: VehicleService) -> None:
    payload = VehicleCreateRequest(
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
    )

    await vehicle_service.create(payload, created_by="user-1")

    with pytest.raises(ConflictException):
        await vehicle_service.create(payload, created_by="user-2")

    with pytest.raises(BusinessRuleException):
        await vehicle_service.update(
            vehicle_id="vehicle-1",
            payload=VehicleUpdateRequest(current_odometer=4990),
            updated_by="user-2",
        )


@pytest.mark.asyncio
async def test_vehicle_service_soft_delete_only(vehicle_service: VehicleService) -> None:
    payload = VehicleCreateRequest(
        registration_number="ABC-456",
        vehicle_name="Mini Bus",
        vehicle_model="Volvo 9700",
        vehicle_type=VehicleType.BUS,
        maximum_load_capacity=5000,
        current_odometer=1000,
        acquisition_cost=90000.0,
        purchase_date=date(2023, 1, 1),
        status=VehicleStatus.AVAILABLE,
        region="Central",
    )

    await vehicle_service.create(payload, created_by="user-1")
    await vehicle_service.delete(vehicle_id="vehicle-1", deleted_by="user-1")

    stored = await vehicle_service.vehicle_repository.get_by_id("vehicle-1")
    assert stored is not None
    assert stored.is_active is False
