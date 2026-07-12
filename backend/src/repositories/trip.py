"""Repository layer for trip logistics models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.trip import Trip, TripActivityLog, TripStatus, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class TripRepository:
    """Data access for trip documents."""

    async def get_by_id(self, trip_id: str) -> Trip | None:
        return await Trip.get(_to_object_id(trip_id))

    async def get_by_trip_number(self, trip_number: str) -> Trip | None:
        return await Trip.find_one(Trip.trip_number == trip_number)

    async def create(self, **trip_data: Any) -> Trip:
        trip = Trip(**trip_data)
        return await trip.insert()

    async def update(self, trip_id: str, **trip_data: Any) -> Trip:
        trip = await self.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        for field, value in trip_data.items():
            setattr(trip, field, value)

        trip.updated_at = utcnow()
        await trip.save()
        return trip

    async def delete(self, trip_id: str) -> Trip:
        trip = await self.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        trip.status = TripStatus.CANCELLED
        trip.updated_at = utcnow()
        await trip.save()
        return trip

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[Trip], int]:
        query = Trip.find(Trip.status != TripStatus.CANCELLED)

        if filters:
            status = filters.get("status")
            if status:
                query = query.find(Trip.status == status)

            priority = filters.get("priority")
            if priority:
                query = query.find(Trip.priority == priority)

            vehicle_id = filters.get("vehicle_id")
            if vehicle_id:
                query = query.find(Trip.vehicle_id == _to_object_id(str(vehicle_id)))

            driver_id = filters.get("driver_id")
            if driver_id:
                query = query.find(Trip.driver_id == _to_object_id(str(driver_id)))

        if search:
            query_text = search.lower().strip()
            query = query.find(
                {
                    "$or": [
                        {"trip_number": {"$regex": query_text, "$options": "i"}},
                        {"source": {"$regex": query_text, "$options": "i"}},
                        {"destination": {"$regex": query_text, "$options": "i"}},
                    ]
                }
            )

        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = getattr(Trip, sort_by, Trip.created_at)
        total = await query.count()
        items = await query.sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        return items, total

    async def list_active(self) -> list[Trip]:
        return await Trip.find(Trip.status == TripStatus.DISPATCHED).to_list()

    async def list_history(self) -> list[Trip]:
        return await Trip.find((Trip.status == TripStatus.COMPLETED) | (Trip.status == TripStatus.CANCELLED)).to_list()


class TripActivityLogRepository:
    """Data access for trip audit trail documents."""

    async def create(self, **log_data: Any) -> TripActivityLog:
        log_entry = TripActivityLog(**log_data)
        return await log_entry.insert()
