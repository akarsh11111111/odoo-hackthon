from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest

from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.driver import DriverStatus
from src.models.trip import TripPriority, TripStatus
from src.models.vehicle import VehicleStatus, VehicleType
from src.repositories.trip import TripRepository
from src.schemas.trip import TripCompleteRequest, TripCreateRequest, TripDispatchRequest, TripUpdateRequest
from src.services.trip import TripService


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


@dataclass
class FakeDriver:
    id: str
    license_number: str
    first_name: str
    last_name: str
    license_expiry: date
    safety_score: int = 100
    driver_status: str = DriverStatus.AVAILABLE.value
    region: str = "North"
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    date_of_birth: date | None = None
    documents: list[str] = field(default_factory=list)
    years_of_experience: int = 0
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
    dispatch_time: datetime | None = None
    expected_arrival: datetime | None = None
    priority: str = TripPriority.NORMAL.value
    status: str = TripStatus.DRAFT.value
    actual_distance: float | None = None
    fuel_consumed: float | None = None
    final_odometer: float | None = None
    completion_notes: str | None = None
    cancellation_reason: str | None = None
    fuel_efficiency: float | None = None
    actual_duration: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_by: str | None = None


class FakeVehicleRepository:
    def __init__(self) -> None:
        self.vehicles: dict[str, FakeVehicle] = {
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


class FakeDriverRepository:
    def __init__(self) -> None:
        self.drivers: dict[str, FakeDriver] = {
            "driver-1": FakeDriver(
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
                driver_status=DriverStatus.AVAILABLE.value,
                region="North",
                years_of_experience=6,
            )
        }

    async def get_by_id(self, driver_id: str) -> FakeDriver | None:
        return self.drivers.get(driver_id)

    async def update(self, driver_id: str, **driver_data: object) -> FakeDriver:
        driver = self.drivers[driver_id]
        if driver is None:
            raise NotFoundException("Driver not found")
        for key, value in driver_data.items():
            setattr(driver, key, value)
        driver.updated_at = datetime.now(timezone.utc)
        return driver


class FakeTripRepository(TripRepository):
    def __init__(self) -> None:
        self.trips: dict[str, FakeTrip] = {}

    async def get_by_id(self, trip_id: str) -> FakeTrip | None:
        return self.trips.get(trip_id)

    async def get_by_trip_number(self, trip_number: str) -> FakeTrip | None:
        return next((trip for trip in self.trips.values() if trip.trip_number == trip_number), None)

    async def create(self, **trip_data: object) -> FakeTrip:
        trip_id = f"trip-{len(self.trips) + 1}"
        trip = FakeTrip(id=trip_id, **trip_data)
        self.trips[trip_id] = trip
        return trip

    async def update(self, trip_id: str, **trip_data: object) -> FakeTrip:
        trip = self.trips[trip_id]
        if trip is None:
            raise NotFoundException("Trip not found")
        for key, value in trip_data.items():
            setattr(trip, key, value)
        trip.updated_at = datetime.now(timezone.utc)
        return trip

    async def delete(self, trip_id: str) -> FakeTrip:
        trip = self.trips[trip_id]
        if trip is None:
            raise NotFoundException("Trip not found")
        trip.status = TripStatus.CANCELLED.value
        trip.updated_at = datetime.now(timezone.utc)
        return trip

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeTrip], int]:
        items = list(self.trips.values())
        if filters:
            if filters.get("status"):
                items = [item for item in items if item.status == filters["status"]]
            if filters.get("priority"):
                items = [item for item in items if item.priority == filters["priority"]]
            if filters.get("vehicle_id"):
                items = [item for item in items if item.vehicle_id == filters["vehicle_id"]]
            if filters.get("driver_id"):
                items = [item for item in items if item.driver_id == filters["driver_id"]]
        if search:
            query = search.lower().strip()
            items = [item for item in items if query in item.trip_number.lower() or query in item.source.lower() or query in item.destination.lower()]
        items = sorted(items, key=lambda item: getattr(item, sort_by), reverse=sort_order == "desc")
        return items[skip : skip + limit], len(items)

    async def list_active(self) -> list[FakeTrip]:
        return [trip for trip in self.trips.values() if trip.status == TripStatus.DISPATCHED.value]

    async def list_history(self) -> list[FakeTrip]:
        return [trip for trip in self.trips.values() if trip.status in {TripStatus.COMPLETED.value, TripStatus.CANCELLED.value}]


class FakeTripActivityLogRepository:
    def __init__(self) -> None:
        self.logs: list[dict[str, object]] = []

    async def create(self, **log_data: object) -> dict[str, object]:
        self.logs.append(log_data)
        return log_data


@pytest.fixture()
def trip_service() -> TripService:
    return TripService(
        trip_repository=FakeTripRepository(),
        vehicle_repository=FakeVehicleRepository(),
        driver_repository=FakeDriverRepository(),
        activity_log_repository=FakeTripActivityLogRepository(),
    )


@pytest.mark.asyncio
async def test_create_trip_generates_trip_number_and_persists_fields(trip_service: TripService) -> None:
    payload = TripCreateRequest(
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
        status=TripStatus.DRAFT,
    )

    trip = await trip_service.create(payload, created_by="user-1")

    assert trip.trip_number.startswith("TRIP-")
    assert trip.created_by == "user-1"
    assert trip.status == TripStatus.DRAFT


@pytest.mark.asyncio
async def test_trip_service_rejects_unavailable_vehicle_and_disabled_driver(trip_service: TripService) -> None:
    vehicle_repo = trip_service.vehicle_repository
    driver_repo = trip_service.driver_repository
    vehicle_repo.vehicles["vehicle-1"].status = VehicleStatus.IN_SHOP.value

    payload = TripCreateRequest(
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
        status=TripStatus.DRAFT,
    )

    with pytest.raises(BusinessRuleException):
        await trip_service.create(payload, created_by="user-1")

    vehicle_repo.vehicles["vehicle-1"].status = VehicleStatus.AVAILABLE.value
    driver_repo.drivers["driver-1"].driver_status = DriverStatus.SUSPENDED.value

    with pytest.raises(BusinessRuleException):
        await trip_service.create(payload, created_by="user-1")


@pytest.mark.asyncio
async def test_trip_service_dispatch_updates_vehicle_and_driver_status(trip_service: TripService) -> None:
    trip = await trip_service.create(
        TripCreateRequest(
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
            status=TripStatus.DRAFT,
        ),
        created_by="user-1",
    )

    dispatched = await trip_service.dispatch(trip.id, TripDispatchRequest(), dispatched_by="user-2")

    assert dispatched.status == TripStatus.DISPATCHED

    vehicle = await trip_service.vehicle_repository.get_by_id("vehicle-1")
    driver = await trip_service.driver_repository.get_by_id("driver-1")

    assert vehicle is not None
    assert vehicle.status == VehicleStatus.ON_TRIP.value
    assert driver is not None
    assert driver.driver_status == DriverStatus.ON_TRIP.value
    assert len(trip_service.activity_log_repository.logs) >= 1


@pytest.mark.asyncio
async def test_trip_service_complete_calculates_efficiency_and_restores_availability(trip_service: TripService) -> None:
    trip = await trip_service.create(
        TripCreateRequest(
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
            status=TripStatus.DRAFT,
        ),
        created_by="user-1",
    )

    await trip_service.dispatch(trip.id, TripDispatchRequest(), dispatched_by="user-2")

    completed = await trip_service.complete(
        trip.id,
        TripCompleteRequest(
            final_distance=150.0,
            fuel_consumed=38.0,
            final_odometer=5150.0,
            completion_notes="Delivered on time",
        ),
        completed_by="user-3",
    )

    assert completed.status == TripStatus.COMPLETED
    assert completed.fuel_efficiency == pytest.approx(3.9473684210526314)

    vehicle = await trip_service.vehicle_repository.get_by_id("vehicle-1")
    driver = await trip_service.driver_repository.get_by_id("driver-1")

    assert vehicle is not None
    assert vehicle.status == VehicleStatus.AVAILABLE.value
    assert driver is not None
    assert driver.driver_status == DriverStatus.AVAILABLE.value


@pytest.mark.asyncio
async def test_trip_service_cancel_restores_state_and_records_reason(trip_service: TripService) -> None:
    trip = await trip_service.create(
        TripCreateRequest(
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
            status=TripStatus.DRAFT,
        ),
        created_by="user-1",
    )

    await trip_service.dispatch(trip.id, TripDispatchRequest(), dispatched_by="user-2")
    cancelled = await trip_service.cancel(trip.id, cancellation_reason="Weather alert", cancelled_by="user-4")

    assert cancelled.status == TripStatus.CANCELLED
    assert cancelled.cancellation_reason == "Weather alert"

    vehicle = await trip_service.vehicle_repository.get_by_id("vehicle-1")
    driver = await trip_service.driver_repository.get_by_id("driver-1")

    assert vehicle is not None
    assert vehicle.status == VehicleStatus.AVAILABLE.value
    assert driver is not None
    assert driver.driver_status == DriverStatus.AVAILABLE.value


@pytest.mark.asyncio
async def test_trip_service_rejects_duplicate_dispatch_and_invalid_status_transitions(trip_service: TripService) -> None:
    trip = await trip_service.create(
        TripCreateRequest(
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
            status=TripStatus.DRAFT,
        ),
        created_by="user-1",
    )

    with pytest.raises(BusinessRuleException):
        await trip_service.complete(
            trip.id,
            TripCompleteRequest(
                final_distance=150.0,
                fuel_consumed=38.0,
                final_odometer=5150.0,
                completion_notes="Delivered",
            ),
            completed_by="user-3",
        )

    await trip_service.dispatch(trip.id, TripDispatchRequest(), dispatched_by="user-2")

    with pytest.raises(BusinessRuleException):
        await trip_service.dispatch(trip.id, TripDispatchRequest(), dispatched_by="user-3")

    await trip_service.cancel(trip.id, cancellation_reason="Weather alert", cancelled_by="user-4")

    with pytest.raises(BusinessRuleException):
        await trip_service.complete(
            trip.id,
            TripCompleteRequest(
                final_distance=150.0,
                fuel_consumed=38.0,
                final_odometer=5150.0,
                completion_notes="Delivered",
            ),
            completed_by="user-3",
        )


@pytest.mark.asyncio
async def test_trip_service_soft_delete_only(trip_service: TripService) -> None:
    trip = await trip_service.create(
        TripCreateRequest(
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
            status=TripStatus.DRAFT,
        ),
        created_by="user-1",
    )

    await trip_service.delete(trip.id, deleted_by="user-1")

    stored = await trip_service.trip_repository.get_by_id(trip.id)
    assert stored is not None
    assert stored.status == TripStatus.CANCELLED.value
