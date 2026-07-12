"""Fuel management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.constants.auth import DISPATCHER, FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.driver import DriverStatus
from src.models.fuel import FuelLog, FuelLogActivityLog, FuelType, utcnow
from src.models.vehicle import VehicleStatus
from src.repositories.driver import DriverRepository
from src.repositories.fuel import FuelLogActivityLogRepository, FuelLogRepository
from src.repositories.trip import TripRepository
from src.repositories.vehicle import VehicleRepository
from src.schemas.fuel import FuelLogCreateRequest, FuelLogRead, FuelLogUpdateRequest
from src.services.analytics import FuelExpenseAnalyticsService


@dataclass(slots=True)
class FuelService:
    """Coordinates fuel consumption business logic and analytics."""

    fuel_log_repository: FuelLogRepository
    vehicle_repository: VehicleRepository
    trip_repository: TripRepository
    driver_repository: DriverRepository
    activity_log_repository: FuelLogActivityLogRepository | None = None

    async def create(self, payload: FuelLogCreateRequest, *, created_by: str | None = None) -> FuelLogRead:
        vehicle = await self.vehicle_repository.get_by_id(payload.vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        if vehicle.status == VehicleStatus.RETIRED:
            raise BusinessRuleException("Retired vehicles cannot receive fuel logs")

        if payload.current_odometer < vehicle.current_odometer:
            raise BusinessRuleException("Current odometer cannot decrease")

        driver = await self.driver_repository.get_by_id(payload.driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")

        if driver.is_active is False:
            raise BusinessRuleException("Driver is inactive")

        trip = None
        if payload.trip_id:
            trip = await self.trip_repository.get_by_id(str(payload.trip_id))
            if trip is None:
                raise NotFoundException("Trip not found")

        total_cost = payload.liters * payload.price_per_liter
        fuel_log_id = await self._generate_fuel_log_id()
        fuel_log = await self.fuel_log_repository.create(
            fuel_log_id=fuel_log_id,
            vehicle_id=vehicle.id,
            trip_id=trip.id if trip is not None else None,
            driver_id=driver.id,
            fuel_station=payload.fuel_station.strip(),
            fuel_type=payload.fuel_type,
            liters=payload.liters,
            price_per_liter=payload.price_per_liter,
            total_cost=total_cost,
            current_odometer=payload.current_odometer,
            fuel_date=payload.fuel_date,
            receipt_image=payload.receipt_image,
            notes=payload.notes.strip() if payload.notes else None,
            created_by=created_by,
            updated_by=created_by,
        )

        await self.vehicle_repository.update(
            str(vehicle.id),
            current_odometer=payload.current_odometer,
            updated_by=created_by,
        )
        await self._log_activity(
            fuel_log_id=fuel_log.id,
            action="Fuel Added",
            message=f"Fuel log {fuel_log.fuel_log_id} created",
            performed_by=created_by,
        )
        return self._to_read(fuel_log)

    async def list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: dict[str, object] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * size
        items, total = await self.fuel_log_repository.list(
            skip=skip,
            limit=size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        return {
            "items": [self._to_read(item) for item in items],
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_by_id(self, fuel_log_id: str) -> FuelLogRead:
        fuel_log = await self.fuel_log_repository.get_by_id(fuel_log_id)
        if fuel_log is None:
            raise NotFoundException("Fuel log not found")
        return self._to_read(fuel_log)

    async def update(self, fuel_log_id: str, payload: FuelLogUpdateRequest, *, updated_by: str | None = None) -> FuelLogRead:
        fuel_log = await self.fuel_log_repository.get_by_id(fuel_log_id)
        if fuel_log is None:
            raise NotFoundException("Fuel log not found")

        vehicle = await self.vehicle_repository.get_by_id(str(fuel_log.vehicle_id))
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        if payload.current_odometer is not None and payload.current_odometer < vehicle.current_odometer:
            raise BusinessRuleException("Current odometer cannot decrease")

        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("fuel_station") is not None:
            update_data["fuel_station"] = str(update_data["fuel_station"]).strip()
        if update_data.get("notes") is not None:
            update_data["notes"] = str(update_data["notes"]).strip()

        if update_data.get("fuel_type") is not None:
            update_data["fuel_type"] = update_data["fuel_type"]

        if update_data.get("liters") is not None and update_data.get("price_per_liter") is not None:
            update_data["total_cost"] = update_data["liters"] * update_data["price_per_liter"]
        elif update_data.get("liters") is not None:
            update_data["total_cost"] = update_data["liters"] * fuel_log.price_per_liter
        elif update_data.get("price_per_liter") is not None:
            update_data["total_cost"] = fuel_log.liters * update_data["price_per_liter"]

        update_data["updated_by"] = updated_by
        fuel_log = await self.fuel_log_repository.update(fuel_log_id, **update_data)
        await self._log_activity(
            fuel_log_id=fuel_log.id,
            action="Fuel Updated",
            message=f"Fuel log {fuel_log.fuel_log_id} updated",
            performed_by=updated_by,
        )
        return self._to_read(fuel_log)

    async def delete(self, fuel_log_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        fuel_log = await self.fuel_log_repository.get_by_id(fuel_log_id)
        if fuel_log is None:
            raise NotFoundException("Fuel log not found")

        await self.fuel_log_repository.delete(fuel_log_id)
        await self._log_activity(
            fuel_log_id=fuel_log.id,
            action="Fuel Deleted",
            message=f"Fuel log {fuel_log.fuel_log_id} deleted",
            performed_by=deleted_by,
        )
        return {"detail": "Fuel log deleted successfully"}

    async def list_history(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.fuel_log_repository.list_history()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def list_by_vehicle(self, vehicle_id: str, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.fuel_log_repository.list_by_vehicle(vehicle_id)
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _generate_fuel_log_id(self) -> str:
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        items, total = await self.fuel_log_repository.list(limit=1000)
        fuel_count = total + 1

        while True:
            candidate = f"FUEL-{date_stamp}-{fuel_count:04d}"
            existing = await self.fuel_log_repository.get_by_fuel_log_id(candidate)
            if existing is None:
                return candidate
            fuel_count += 1

    async def _log_activity(self, *, fuel_log_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            fuel_log_id=fuel_log_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _to_read(fuel_log: FuelLog) -> FuelLogRead:
        return FuelLogRead(
            id=str(fuel_log.id),
            fuel_log_id=fuel_log.fuel_log_id,
            vehicle_id=str(fuel_log.vehicle_id),
            trip_id=str(fuel_log.trip_id) if fuel_log.trip_id is not None else None,
            driver_id=str(fuel_log.driver_id),
            fuel_station=fuel_log.fuel_station,
            fuel_type=fuel_log.fuel_type,
            liters=fuel_log.liters,
            price_per_liter=fuel_log.price_per_liter,
            total_cost=fuel_log.total_cost,
            current_odometer=fuel_log.current_odometer,
            fuel_date=fuel_log.fuel_date,
            receipt_image=fuel_log.receipt_image,
            notes=fuel_log.notes,
            created_at=fuel_log.created_at,
            updated_at=fuel_log.updated_at,
            created_by=fuel_log.created_by,
            updated_by=fuel_log.updated_by,
        )


def get_fuel_service() -> FuelService:
    """Build a fuel service with concrete repositories."""

    return FuelService(
        fuel_log_repository=FuelLogRepository(),
        vehicle_repository=VehicleRepository(),
        trip_repository=TripRepository(),
        driver_repository=DriverRepository(),
        activity_log_repository=FuelLogActivityLogRepository(),
    )
