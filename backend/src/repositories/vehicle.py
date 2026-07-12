"""Repository layer for vehicle registry models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.vehicle import Vehicle, VehicleActivityLog, VehicleStatus, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class VehicleRepository:
    """Data access for vehicle documents."""

    async def get_by_id(self, vehicle_id: str) -> Vehicle | None:
        return await Vehicle.get(_to_object_id(vehicle_id))

    async def get_by_registration_number(self, registration_number: str) -> Vehicle | None:
        return await Vehicle.find_one(Vehicle.registration_number == registration_number.upper())

    async def create(self, **vehicle_data: Any) -> Vehicle:
        vehicle = Vehicle(**vehicle_data)
        return await vehicle.insert()

    async def update(self, vehicle_id: str, **vehicle_data: Any) -> Vehicle:
        vehicle = await self.get_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        for field, value in vehicle_data.items():
            setattr(vehicle, field, value)

        vehicle.updated_at = utcnow()
        await vehicle.save()
        return vehicle

    async def delete(self, vehicle_id: str) -> Vehicle:
        vehicle = await self.get_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        vehicle.is_active = False
        vehicle.updated_at = utcnow()
        await vehicle.save()
        return vehicle

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[Vehicle], int]:
        query = Vehicle.find(Vehicle.is_active == True)

        if filters:
            region = filters.get("region")
            if region:
                query = query.find(Vehicle.region == region)

            status = filters.get("status")
            if status:
                query = query.find(Vehicle.status == status)

            vehicle_type = filters.get("vehicle_type")
            if vehicle_type:
                query = query.find(Vehicle.vehicle_type == vehicle_type)

        if search:
            query_text = search.lower().strip()
            query = query.find(
                {
                    "$or": [
                        {"registration_number": {"$regex": query_text, "$options": "i"}},
                        {"vehicle_name": {"$regex": query_text, "$options": "i"}},
                        {"vehicle_model": {"$regex": query_text, "$options": "i"}},
                        {"region": {"$regex": query_text, "$options": "i"}},
                    ]
                }
            )

        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = getattr(Vehicle, sort_by, Vehicle.created_at)
        total = await query.count()
        items = await query.sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        return items, total

    async def list_available(self) -> list[Vehicle]:
        return await Vehicle.find(
            (Vehicle.is_active == True) & (Vehicle.status == VehicleStatus.AVAILABLE)
        ).to_list()


class VehicleActivityLogRepository:
    """Data access for vehicle audit trail documents."""

    async def create(self, **log_data: Any) -> VehicleActivityLog:
        log_entry = VehicleActivityLog(**log_data)
        return await log_entry.insert()
