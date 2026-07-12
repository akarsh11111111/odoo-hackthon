"""Trip management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.constants.auth import FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.driver import Driver, DriverStatus
from src.models.trip import Trip, TripActivityLog, TripPriority, TripStatus
from src.models.vehicle import Vehicle, VehicleStatus, VehicleType
from src.repositories.driver import DriverRepository
from src.repositories.trip import TripActivityLogRepository, TripRepository
from src.repositories.vehicle import VehicleRepository
from src.schemas.trip import TripCompleteRequest, TripCreateRequest, TripDispatchRequest, TripRead, TripUpdateRequest


@dataclass(slots=True)
class TripService:
    """Coordinates trip logistics business logic and auditing."""

    trip_repository: TripRepository
    vehicle_repository: VehicleRepository
    driver_repository: DriverRepository
    activity_log_repository: TripActivityLogRepository | None = None

    async def create(self, payload: TripCreateRequest, *, created_by: str | None = None) -> TripRead:
        vehicle = await self.vehicle_repository.get_by_id(payload.vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        driver = await self.driver_repository.get_by_id(payload.driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")

        self._validate_vehicle_for_assignment(vehicle)
        self._validate_driver_for_assignment(driver)

        if payload.cargo_weight > vehicle.maximum_load_capacity:
            raise BusinessRuleException("Cargo weight exceeds vehicle capacity")

        trip_number = await self._generate_trip_number()
        trip = await self.trip_repository.create(
            trip_number=trip_number,
            vehicle_id=vehicle.id,
            driver_id=driver.id,
            source=payload.source.strip(),
            destination=payload.destination.strip(),
            cargo_description=payload.cargo_description.strip(),
            cargo_weight=payload.cargo_weight,
            estimated_distance=payload.estimated_distance,
            estimated_duration=payload.estimated_duration,
            dispatch_time=payload.dispatch_time,
            expected_arrival=payload.expected_arrival,
            priority=payload.priority,
            status=payload.status,
            created_by=created_by,
            updated_by=created_by,
        )

        await self._log_activity(trip_id=trip.id, action="Trip Created", message=f"Trip {trip.trip_number} created", performed_by=created_by)
        return self._to_read(trip)

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
        items, total = await self.trip_repository.list(
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

    async def get_by_id(self, trip_id: str) -> TripRead:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")
        return self._to_read(trip)

    async def update(self, trip_id: str, payload: TripUpdateRequest, *, updated_by: str | None = None) -> TripRead:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        if trip.status == TripStatus.COMPLETED or trip.status == TripStatus.CANCELLED:
            raise BusinessRuleException("Completed or cancelled trips cannot be updated")

        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("vehicle_id") is not None:
            vehicle = await self.vehicle_repository.get_by_id(str(update_data["vehicle_id"]))
            if vehicle is None:
                raise NotFoundException("Vehicle not found")
            self._validate_vehicle_for_assignment(vehicle)
            update_data["vehicle_id"] = vehicle.id

        if update_data.get("driver_id") is not None:
            driver = await self.driver_repository.get_by_id(str(update_data["driver_id"]))
            if driver is None:
                raise NotFoundException("Driver not found")
            self._validate_driver_for_assignment(driver)
            update_data["driver_id"] = driver.id

        if update_data.get("source") is not None:
            update_data["source"] = str(update_data["source"]).strip()

        if update_data.get("destination") is not None:
            update_data["destination"] = str(update_data["destination"]).strip()

        if update_data.get("cargo_description") is not None:
            update_data["cargo_description"] = str(update_data["cargo_description"]).strip()

        if update_data.get("completion_notes") is not None:
            update_data["completion_notes"] = str(update_data["completion_notes"]).strip()

        if update_data.get("cancellation_reason") is not None:
            update_data["cancellation_reason"] = str(update_data["cancellation_reason"]).strip()

        update_data["updated_by"] = updated_by
        trip = await self.trip_repository.update(trip_id, **update_data)
        await self._log_activity(trip_id=trip.id, action="Trip Updated", message=f"Trip {trip.trip_number} updated", performed_by=updated_by)
        return self._to_read(trip)

    async def delete(self, trip_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        await self.trip_repository.delete(trip_id)
        await self._log_activity(trip_id=trip.id, action="Trip Cancelled", message=f"Trip {trip.trip_number} deleted", performed_by=deleted_by)
        return {"detail": "Trip deleted successfully"}

    async def dispatch(self, trip_id: str, payload: TripDispatchRequest, *, dispatched_by: str | None = None) -> TripRead:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        if trip.status != TripStatus.DRAFT:
            raise BusinessRuleException("Only draft trips can be dispatched")

        vehicle = await self.vehicle_repository.get_by_id(str(trip.vehicle_id))
        driver = await self.driver_repository.get_by_id(str(trip.driver_id))
        if vehicle is None or driver is None:
            raise NotFoundException("Vehicle or driver not found")

        self._validate_vehicle_for_assignment(vehicle)
        self._validate_driver_for_assignment(driver)

        vehicle.status = VehicleStatus.ON_TRIP
        driver.driver_status = DriverStatus.ON_TRIP
        vehicle.updated_by = dispatched_by
        driver.updated_by = dispatched_by
        await self.vehicle_repository.update(str(vehicle.id), status=vehicle.status, updated_by=dispatched_by)
        await self.driver_repository.update(str(driver.id), driver_status=driver.driver_status, updated_by=dispatched_by)

        update_data = {
            "status": TripStatus.DISPATCHED,
            "dispatch_time": payload.dispatch_time or trip.dispatch_time or datetime.now(timezone.utc),
            "expected_arrival": payload.expected_arrival or trip.expected_arrival,
            "updated_by": dispatched_by,
        }
        trip = await self.trip_repository.update(trip_id, **update_data)
        await self._log_activity(trip_id=trip.id, action="Trip Dispatched", message=f"Trip {trip.trip_number} dispatched", performed_by=dispatched_by)
        return self._to_read(trip)

    async def complete(self, trip_id: str, payload: TripCompleteRequest, *, completed_by: str | None = None) -> TripRead:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        if trip.status != TripStatus.DISPATCHED:
            raise BusinessRuleException("Only dispatched trips can be completed")

        if payload.fuel_consumed <= 0:
            raise BusinessRuleException("Fuel consumed must be greater than zero")

        vehicle = await self.vehicle_repository.get_by_id(str(trip.vehicle_id))
        driver = await self.driver_repository.get_by_id(str(trip.driver_id))
        if vehicle is None or driver is None:
            raise NotFoundException("Vehicle or driver not found")

        completion_time = datetime.now(timezone.utc)
        actual_duration = None
        if trip.dispatch_time is not None:
            actual_duration = int((completion_time - trip.dispatch_time).total_seconds() // 60)

        fuel_efficiency = payload.final_distance / payload.fuel_consumed if payload.fuel_consumed else None

        await self.vehicle_repository.update(
            str(vehicle.id),
            status=VehicleStatus.AVAILABLE,
            current_odometer=payload.final_odometer,
            updated_by=completed_by,
        )
        await self.driver_repository.update(
            str(driver.id),
            driver_status=DriverStatus.AVAILABLE,
            updated_by=completed_by,
        )

        trip = await self.trip_repository.update(
            trip_id,
            status=TripStatus.COMPLETED,
            actual_distance=payload.final_distance,
            fuel_consumed=payload.fuel_consumed,
            final_odometer=payload.final_odometer,
            completion_notes=payload.completion_notes.strip(),
            fuel_efficiency=fuel_efficiency,
            actual_duration=actual_duration,
            updated_by=completed_by,
        )
        await self._log_activity(trip_id=trip.id, action="Trip Completed", message=f"Trip {trip.trip_number} completed", performed_by=completed_by)
        return self._to_read(trip)

    async def cancel(self, trip_id: str, *, cancellation_reason: str | None = None, cancelled_by: str | None = None) -> TripRead:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise NotFoundException("Trip not found")

        if trip.status == TripStatus.COMPLETED:
            raise BusinessRuleException("Completed trips cannot be cancelled")

        vehicle = await self.vehicle_repository.get_by_id(str(trip.vehicle_id))
        driver = await self.driver_repository.get_by_id(str(trip.driver_id))
        if vehicle is None or driver is None:
            raise NotFoundException("Vehicle or driver not found")

        await self.vehicle_repository.update(str(vehicle.id), status=VehicleStatus.AVAILABLE, updated_by=cancelled_by)
        await self.driver_repository.update(str(driver.id), driver_status=DriverStatus.AVAILABLE, updated_by=cancelled_by)

        trip = await self.trip_repository.update(
            trip_id,
            status=TripStatus.CANCELLED,
            cancellation_reason=cancellation_reason.strip() if cancellation_reason else None,
            updated_by=cancelled_by,
        )
        await self._log_activity(trip_id=trip.id, action="Trip Cancelled", message=f"Trip {trip.trip_number} cancelled", performed_by=cancelled_by)
        return self._to_read(trip)

    async def list_active(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.trip_repository.list_active()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def list_history(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.trip_repository.list_history()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _generate_trip_number(self) -> str:
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        items, total = await self.trip_repository.list(limit=1000)
        trip_count = total + 1

        while True:
            candidate = f"TRIP-{date_stamp}-{trip_count:04d}"
            existing_trip = await self.trip_repository.get_by_trip_number(candidate)
            if existing_trip is None:
                return candidate
            trip_count += 1

    async def _log_activity(self, *, trip_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            trip_id=trip_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _validate_vehicle_for_assignment(vehicle: Vehicle) -> None:
        if not vehicle.is_active:
            raise BusinessRuleException("Vehicle is inactive")
        if vehicle.status in {VehicleStatus.RETIRED, VehicleStatus.IN_SHOP, VehicleStatus.ON_TRIP}:
            raise BusinessRuleException("Vehicle is unavailable for dispatch")

    @staticmethod
    def _validate_driver_for_assignment(driver: Driver) -> None:
        if not driver.is_active:
            raise BusinessRuleException("Driver is inactive")
        if driver.driver_status in {DriverStatus.SUSPENDED, DriverStatus.ON_TRIP}:
            raise BusinessRuleException("Driver is unavailable for dispatch")
        if driver.license_expiry < datetime.now(timezone.utc).date():
            raise BusinessRuleException("Driver license is expired")

    @staticmethod
    def _to_read(trip: Trip) -> TripRead:
        return TripRead(
            id=str(trip.id),
            trip_number=trip.trip_number,
            vehicle_id=str(trip.vehicle_id),
            driver_id=str(trip.driver_id),
            source=trip.source,
            destination=trip.destination,
            cargo_description=trip.cargo_description,
            cargo_weight=trip.cargo_weight,
            estimated_distance=trip.estimated_distance,
            estimated_duration=trip.estimated_duration,
            dispatch_time=trip.dispatch_time,
            expected_arrival=trip.expected_arrival,
            priority=trip.priority,
            status=trip.status,
            actual_distance=trip.actual_distance,
            fuel_consumed=trip.fuel_consumed,
            final_odometer=trip.final_odometer,
            completion_notes=trip.completion_notes,
            cancellation_reason=trip.cancellation_reason,
            fuel_efficiency=trip.fuel_efficiency,
            actual_duration=trip.actual_duration,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
            created_by=trip.created_by,
            updated_by=trip.updated_by,
        )


def get_trip_service() -> TripService:
    """Build a trip service with concrete repositories."""

    return TripService(
        trip_repository=TripRepository(),
        vehicle_repository=VehicleRepository(),
        driver_repository=DriverRepository(),
        activity_log_repository=TripActivityLogRepository(),
    )
