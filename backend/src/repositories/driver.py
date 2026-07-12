"""Repository layer for driver management models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.driver import Driver, DriverActivityLog, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class DriverRepository:
    """Data access for driver documents."""

    async def get_by_id(self, driver_id: str) -> Driver | None:
        return await Driver.get(_to_object_id(driver_id))

    async def get_by_license_number(self, license_number: str) -> Driver | None:
        return await Driver.find_one(Driver.license_number == license_number.upper())

    async def create(self, **driver_data: Any) -> Driver:
        driver = Driver(**driver_data)
        return await driver.insert()

    async def update(self, driver_id: str, **driver_data: Any) -> Driver:
        driver = await self.get_by_id(driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")

        for field, value in driver_data.items():
            setattr(driver, field, value)

        driver.updated_at = utcnow()
        await driver.save()
        return driver

    async def delete(self, driver_id: str) -> Driver:
        driver = await self.get_by_id(driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")

        driver.is_active = False
        driver.updated_at = utcnow()
        await driver.save()
        return driver

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[Driver], int]:
        items = await Driver.find(Driver.is_active == True).to_list()

        if filters:
            region = filters.get("region")
            if region:
                items = [item for item in items if item.region == region]

            status = filters.get("status")
            if status:
                items = [item for item in items if item.driver_status == status]

        if search:
            query = search.lower().strip()
            items = [
                item
                for item in items
                if query in item.first_name.lower()
                or query in item.last_name.lower()
                or query in item.region.lower()
                or query in item.license_number.lower()
            ]

        items.sort(key=lambda item: getattr(item, sort_by, item.created_at), reverse=sort_order == "desc")
        total = len(items)
        return items[skip : skip + limit], total

    async def list_available(self) -> list[Driver]:
        return await Driver.find((Driver.is_active == True) & (Driver.driver_status == "Available")).to_list()


class DriverActivityLogRepository:
    """Data access for driver audit trail documents."""

    async def create(self, **log_data: Any) -> DriverActivityLog:
        log_entry = DriverActivityLog(**log_data)
        return await log_entry.insert()
