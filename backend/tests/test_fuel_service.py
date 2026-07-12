from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest

from src.core.exceptions import BusinessRuleException, NotFoundException
from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.fuel import FuelLogCreateRequest, FuelLogRead
from src.schemas.expense import ExpenseCreateRequest, ExpenseRead
from src.services.fuel import FuelService
from src.services.expense import ExpenseService


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


@dataclass
class FakeDriver:
    id: str
    license_number: str
    first_name: str
    last_name: str
    license_expiry: date
    safety_score: int = 100
    driver_status: str = "Available"
    region: str = "North"
    is_active: bool = True


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


@dataclass
class FakeFuelLog:
    id: str
    fuel_log_id: str
    vehicle_id: str
    driver_id: str
    fuel_station: str
    fuel_type: str
    liters: float
    price_per_liter: float
    total_cost: float
    current_odometer: int
    fuel_date: date
    trip_id: str | None = None
    receipt_image: str | None = None
    notes: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FakeExpense:
    id: str
    expense_id: str
    vehicle_id: str
    expense_type: str
    amount: float
    vendor: str
    invoice_number: str
    expense_date: date
    description: str
    trip_id: str | None = None
    attachment: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


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
            )
        }

    async def get_by_id(self, vehicle_id: str) -> FakeVehicle | None:
        return self.vehicles.get(vehicle_id)

    async def update(self, vehicle_id: str, **vehicle_data: object) -> FakeVehicle:
        vehicle = self.vehicles[vehicle_id]
        for key, value in vehicle_data.items():
            setattr(vehicle, key, value)
        vehicle.updated_at = datetime.now(timezone.utc)
        return vehicle


class FakeDriverRepository:
    def __init__(self) -> None:
        self.drivers = {
            "driver-1": FakeDriver(
                id="driver-1",
                license_number="DL-1001",
                first_name="Asha",
                last_name="Patel",
                license_expiry=date(2027, 1, 1),
                safety_score=92,
                driver_status="Available",
                region="North",
                is_active=True,
            )
        }

    async def get_by_id(self, driver_id: str) -> FakeDriver | None:
        return self.drivers.get(driver_id)


class FakeTripRepository:
    async def get_by_id(self, trip_id: str) -> FakeTrip | None:
        return None


class FakeFuelLogRepository:
    def __init__(self) -> None:
        self.logs: dict[str, FakeFuelLog] = {}

    async def get_by_id(self, fuel_log_id: str) -> FakeFuelLog | None:
        return self.logs.get(fuel_log_id)

    async def get_by_fuel_log_id(self, fuel_log_id: str) -> FakeFuelLog | None:
        return next((item for item in self.logs.values() if item.fuel_log_id == fuel_log_id), None)

    async def create(self, **fuel_log_data: object) -> FakeFuelLog:
        fuel_log_id = str(fuel_log_data.get("fuel_log_id", f"fuel-{len(self.logs) + 1}"))
        fake_data = dict(fuel_log_data)
        fake_data.pop("fuel_log_id", None)
        fuel_log = FakeFuelLog(id=fuel_log_id, fuel_log_id=fuel_log_id, **fake_data)
        self.logs[fuel_log_id] = fuel_log
        return fuel_log

    async def update(self, fuel_log_id: str, **fuel_log_data: object) -> FakeFuelLog:
        fuel_log = self.logs[fuel_log_id]
        for key, value in fuel_log_data.items():
            setattr(fuel_log, key, value)
        fuel_log.updated_at = datetime.now(timezone.utc)
        return fuel_log

    async def delete(self, fuel_log_id: str) -> FakeFuelLog:
        fuel_log = self.logs[fuel_log_id]
        fuel_log.is_active = False
        return fuel_log

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeFuelLog], int]:
        items = list(self.logs.values())
        return items[skip : skip + limit], len(items)

    async def list_history(self) -> list[FakeFuelLog]:
        return list(self.logs.values())

    async def list_by_vehicle(self, vehicle_id: str) -> list[FakeFuelLog]:
        return [item for item in self.logs.values() if item.vehicle_id == vehicle_id]


class FakeExpenseRepository:
    def __init__(self) -> None:
        self.expenses: dict[str, FakeExpense] = {}

    async def get_by_id(self, expense_id: str) -> FakeExpense | None:
        return self.expenses.get(expense_id)

    async def get_by_expense_id(self, expense_id: str) -> FakeExpense | None:
        return next((item for item in self.expenses.values() if item.expense_id == expense_id), None)

    async def create(self, **expense_data: object) -> FakeExpense:
        expense_id = str(expense_data.get("expense_id", f"expense-{len(self.expenses) + 1}"))
        fake_data = dict(expense_data)
        fake_data.pop("expense_id", None)
        expense = FakeExpense(id=expense_id, expense_id=expense_id, **fake_data)
        self.expenses[expense_id] = expense
        return expense

    async def update(self, expense_id: str, **expense_data: object) -> FakeExpense:
        expense = self.expenses[expense_id]
        for key, value in expense_data.items():
            setattr(expense, key, value)
        expense.updated_at = datetime.now(timezone.utc)
        return expense

    async def delete(self, expense_id: str) -> FakeExpense:
        expense = self.expenses[expense_id]
        expense.is_active = False
        return expense

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeExpense], int]:
        items = list(self.expenses.values())
        return items[skip : skip + limit], len(items)

    async def list_history(self) -> list[FakeExpense]:
        return list(self.expenses.values())

    async def list_by_vehicle(self, vehicle_id: str) -> list[FakeExpense]:
        return [item for item in self.expenses.values() if item.vehicle_id == vehicle_id]


@pytest.fixture()
def fuel_service() -> FuelService:
    return FuelService(
        fuel_log_repository=FakeFuelLogRepository(),
        vehicle_repository=FakeVehicleRepository(),
        trip_repository=FakeTripRepository(),
        driver_repository=FakeDriverRepository(),
    )


@pytest.fixture()
def expense_service() -> ExpenseService:
    return ExpenseService(
        expense_repository=FakeExpenseRepository(),
        vehicle_repository=FakeVehicleRepository(),
        trip_repository=FakeTripRepository(),
    )


@pytest.mark.asyncio
async def test_create_fuel_log_calculates_total_cost_and_updates_odometer(fuel_service: FuelService) -> None:
    payload = FuelLogCreateRequest(
        vehicle_id="vehicle-1",
        trip_id=None,
        driver_id="driver-1",
        fuel_station="Metro Fuel Hub",
        fuel_type="Diesel",
        liters=40.0,
        price_per_liter=1.35,
        current_odometer=5300,
        fuel_date=date(2026, 7, 12),
        notes="Top up before dispatch",
    )

    fuel_log = await fuel_service.create(payload, created_by="user-1")

    assert fuel_log.total_cost == pytest.approx(54.0)
    vehicle = await fuel_service.vehicle_repository.get_by_id("vehicle-1")
    assert vehicle is not None
    assert vehicle.current_odometer == 5300


@pytest.mark.asyncio
async def test_get_by_id_returns_fuel_read_model(fuel_service: FuelService) -> None:
    created = await fuel_service.create(
        FuelLogCreateRequest(
            vehicle_id="vehicle-1",
            trip_id=None,
            driver_id="driver-1",
            fuel_station="Metro Fuel Hub",
            fuel_type="Diesel",
            liters=40.0,
            price_per_liter=1.35,
            current_odometer=5300,
            fuel_date=date(2026, 7, 12),
            notes="Top up before dispatch",
        ),
        created_by="user-1",
    )

    fetched = await fuel_service.get_by_id(created.id)

    assert fetched.id == created.id
    assert fetched.fuel_log_id == created.fuel_log_id
    assert fetched.total_cost == pytest.approx(54.0)


@pytest.mark.asyncio
async def test_create_expense_records_operational_cost(expense_service: ExpenseService) -> None:
    payload = ExpenseCreateRequest(
        vehicle_id="vehicle-1",
        trip_id=None,
        expense_type="Fuel",
        amount=54.0,
        vendor="Metro Fuel Hub",
        invoice_number="INV-9001",
        expense_date=date(2026, 7, 12),
        description="Fuel purchase for dispatch",
    )

    expense = await expense_service.create(payload, created_by="user-1")

    assert expense.expense_type == "Fuel"
    assert expense.amount == pytest.approx(54.0)
