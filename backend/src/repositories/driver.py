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
        query = Driver.find(Driver.is_active == True)

        if filters:
            region = filters.get("region")
            if region:
                query = query.find(Driver.region == region)

            status = filters.get("status")
            if status:
                query = query.find(Driver.driver_status == status)

        if search:
            query_text = search.lower().strip()
            query = query.find(
                {
                    "$or": [
                        {"first_name": {"$regex": query_text, "$options": "i"}},
                        {"last_name": {"$regex": query_text, "$options": "i"}},
                        {"region": {"$regex": query_text, "$options": "i"}},
                        {"license_number": {"$regex": query_text, "$options": "i"}},
                    ]
                }
            )

        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = getattr(Driver, sort_by, Driver.created_at)
        total = await query.count()
        items = await query.sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        return items, total

    async def list_available(self) -> list[Driver]:
        return await Driver.find((Driver.is_active == True) & (Driver.driver_status == "Available")).to_list()


class DriverActivityLogRepository:
    """Data access for driver audit trail documents."""

    async def create(self, **log_data: Any) -> DriverActivityLog:
        log_entry = DriverActivityLog(**log_data)
        return await log_entry.insert()
