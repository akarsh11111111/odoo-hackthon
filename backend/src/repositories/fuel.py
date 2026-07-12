"""Repository layer for fuel log models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.fuel import FuelLog, FuelLogActivityLog, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class FuelLogRepository:
    """Data access for fuel log documents."""

    async def get_by_id(self, fuel_log_id: str) -> FuelLog | None:
        return await FuelLog.get(_to_object_id(fuel_log_id))

    async def get_by_fuel_log_id(self, fuel_log_id: str) -> FuelLog | None:
        return await FuelLog.find_one(FuelLog.fuel_log_id == fuel_log_id)

    async def create(self, **fuel_data: Any) -> FuelLog:
        fuel_log = FuelLog(**fuel_data)
        return await fuel_log.insert()

    async def update(self, fuel_log_id: str, **fuel_data: Any) -> FuelLog:
        fuel_log = await self.get_by_id(fuel_log_id)
        if fuel_log is None:
            raise NotFoundException("Fuel log not found")

        for field, value in fuel_data.items():
            setattr(fuel_log, field, value)

        fuel_log.updated_at = utcnow()
        await fuel_log.save()
        return fuel_log

    async def delete(self, fuel_log_id: str) -> FuelLog:
        fuel_log = await self.get_by_id(fuel_log_id)
        if fuel_log is None:
            raise NotFoundException("Fuel log not found")

        fuel_log.is_active = False
        fuel_log.updated_at = utcnow()
        await fuel_log.save()
        return fuel_log

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[FuelLog], int]:
        query = FuelLog.find(FuelLog.is_active == True)

        if filters:
            vehicle_id = filters.get("vehicle_id")
            if vehicle_id:
                query = query.find(FuelLog.vehicle_id == _to_object_id(str(vehicle_id)))

            trip_id = filters.get("trip_id")
            if trip_id:
                query = query.find(FuelLog.trip_id == _to_object_id(str(trip_id)))

            driver_id = filters.get("driver_id")
            if driver_id:
                query = query.find(FuelLog.driver_id == _to_object_id(str(driver_id)))

            fuel_type = filters.get("fuel_type")
            if fuel_type:
                query = query.find(FuelLog.fuel_type == fuel_type)

        if search:
            query_text = search.lower().strip()
            query = query.find(
                {
                    "$or": [
                        {"fuel_log_id": {"$regex": query_text, "$options": "i"}},
                        {"fuel_station": {"$regex": query_text, "$options": "i"}},
                        {"notes": {"$regex": query_text, "$options": "i"}},
                    ]
                }
            )

        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = getattr(FuelLog, sort_by, FuelLog.created_at)
        total = await query.count()
        items = await query.sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        return items, total

    async def list_history(self) -> list[FuelLog]:
        return await FuelLog.find(FuelLog.is_active == True).to_list()

    async def list_by_vehicle(self, vehicle_id: str) -> list[FuelLog]:
        return await FuelLog.find((FuelLog.is_active == True) & (FuelLog.vehicle_id == _to_object_id(vehicle_id))).to_list()


class FuelLogActivityLogRepository:
    """Data access for fuel audit trail documents."""

    async def create(self, **log_data: Any) -> FuelLogActivityLog:
        log_entry = FuelLogActivityLog(**log_data)
        return await log_entry.insert()
