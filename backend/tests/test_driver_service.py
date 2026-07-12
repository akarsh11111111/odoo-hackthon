from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest

from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.driver import Driver, DriverStatus
from src.repositories.driver import DriverRepository
from src.schemas.driver import DriverCreateRequest, DriverUpdateRequest
from src.services.driver import DriverService


@dataclass
class FakeDriver:
    id: str
    license_number: str
    first_name: str
    last_name: str
    license_expiry: date
    safety_score: int
    driver_status: str
    region: str
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


class FakeDriverRepository(DriverRepository):
    def __init__(self) -> None:
        self.drivers: dict[str, FakeDriver] = {}

    async def get_by_license_number(self, license_number: str) -> FakeDriver | None:
        return next((driver for driver in self.drivers.values() if driver.license_number == license_number), None)

    async def get_by_id(self, driver_id: str) -> FakeDriver | None:
        return self.drivers.get(driver_id)

    async def create(self, **driver_data: object) -> FakeDriver:
        driver_id = f"driver-{len(self.drivers) + 1}"
        driver = FakeDriver(id=driver_id, **driver_data)
        self.drivers[driver_id] = driver
        return driver

    async def update(self, driver_id: str, **driver_data: object) -> FakeDriver:
        driver = self.drivers[driver_id]
        if driver is None:
            raise NotFoundException("Driver not found")
        for key, value in driver_data.items():
            setattr(driver, key, value)
        driver.updated_at = datetime.now(timezone.utc)
        return driver

    async def delete(self, driver_id: str) -> FakeDriver:
        driver = self.drivers[driver_id]
        if driver is None:
            raise NotFoundException("Driver not found")
        driver.is_active = False
        driver.updated_at = datetime.now(timezone.utc)
        return driver

    async def list(self, *, skip: int = 0, limit: int = 20, filters: dict[str, object] | None = None, sort_by: str = "created_at", sort_order: str = "desc", search: str | None = None) -> tuple[list[FakeDriver], int]:
        items = list(self.drivers.values())
        if filters:
            if filters.get("region"):
                items = [item for item in items if item.region == filters["region"]]
            if filters.get("status"):
                items = [item for item in items if item.driver_status == filters["status"]]
        if search:
            query = search.lower().strip()
            items = [item for item in items if query in item.first_name.lower() or query in item.last_name.lower() or query in item.region.lower()]
        items = sorted(items, key=lambda item: getattr(item, sort_by), reverse=sort_order == "desc")
        return items[skip : skip + limit], len(items)

    async def list_available(self) -> list[FakeDriver]:
        return [driver for driver in self.drivers.values() if driver.driver_status == DriverStatus.AVAILABLE.value and driver.is_active]


@pytest.fixture()
def driver_service() -> DriverService:
    return DriverService(driver_repository=FakeDriverRepository())


@pytest.mark.asyncio
async def test_create_driver_uses_auditing_and_persists_fields(driver_service: DriverService) -> None:
    payload = DriverCreateRequest(
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
    )

    driver = await driver_service.create(payload, created_by="user-1")

    assert driver.license_number == "DL-1001"
    assert driver.created_by == "user-1"
    assert driver.driver_status == DriverStatus.AVAILABLE


@pytest.mark.asyncio
async def test_driver_service_rejects_duplicate_license_and_suspended_dispatch(driver_service: DriverService) -> None:
    payload = DriverCreateRequest(
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
        years_of_experience=6,
    )

    await driver_service.create(payload, created_by="user-1")

    with pytest.raises(ConflictException):
        await driver_service.create(payload, created_by="user-2")

    with pytest.raises(BusinessRuleException):
        await driver_service.update(
            driver_id="driver-1",
            payload=DriverUpdateRequest(driver_status=DriverStatus.SUSPENDED),
            updated_by="user-2",
        )


@pytest.mark.asyncio
async def test_driver_service_soft_delete_only(driver_service: DriverService) -> None:
    payload = DriverCreateRequest(
        license_number="DL-1002",
        first_name="Rahul",
        last_name="Sharma",
        phone="+15550000002",
        email="rahul@example.com",
        address="55 Market Street",
        date_of_birth=date(1988, 8, 10),
        license_expiry=date(2026, 12, 31),
        safety_score=89,
        driver_status=DriverStatus.OFF_DUTY,
        region="Central",
        years_of_experience=9,
    )

    await driver_service.create(payload, created_by="user-1")
    await driver_service.delete(driver_id="driver-1", deleted_by="user-1")

    stored = await driver_service.driver_repository.get_by_id("driver-1")
    assert stored is not None
    assert stored.is_active is False
