"""Vehicle registry service layer."""

from __future__ import annotations

from dataclasses import dataclass

from src.constants.auth import FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, ForbiddenException, NotFoundException
from src.models.vehicle import Vehicle, VehicleActivityLog, VehicleStatus, VehicleType, utcnow
from src.repositories.vehicle import VehicleActivityLogRepository, VehicleRepository
from src.schemas.vehicle import VehicleCreateRequest, VehicleRead, VehicleUpdateRequest


@dataclass(slots=True)
class VehicleService:
    """Coordinates vehicle registry business logic and auditing."""

    vehicle_repository: VehicleRepository
    activity_log_repository: VehicleActivityLogRepository | None = None

    async def create(self, payload: VehicleCreateRequest, *, created_by: str | None = None) -> VehicleRead:
        normalized_registration_number = payload.registration_number.strip().upper()
        existing_vehicle = await self.vehicle_repository.get_by_registration_number(normalized_registration_number)
        if existing_vehicle is not None:
            raise ConflictException("Vehicle registration number already exists")

        vehicle = await self.vehicle_repository.create(
            registration_number=normalized_registration_number,
            vehicle_name=payload.vehicle_name.strip(),
            vehicle_model=payload.vehicle_model.strip(),
            vehicle_type=payload.vehicle_type,
            maximum_load_capacity=payload.maximum_load_capacity,
            current_odometer=payload.current_odometer,
            acquisition_cost=payload.acquisition_cost,
            purchase_date=payload.purchase_date,
            status=payload.status,
            region=payload.region.strip(),
            documents=list(payload.documents or []),
            insurance_expiry=payload.insurance_expiry,
            fitness_expiry=payload.fitness_expiry,
            pollution_expiry=payload.pollution_expiry,
            is_active=True,
            created_by=created_by,
            updated_by=created_by,
        )
        await self._log_activity(vehicle_id=vehicle.id, action="Vehicle Created", message=f"Vehicle {vehicle.registration_number} created", performed_by=created_by)
        return self._to_read(vehicle)

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
        items, total = await self.vehicle_repository.list(
            skip=skip,
            limit=size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        return {
            "items": [self._to_read(vehicle) for vehicle in items],
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_by_id(self, vehicle_id: str) -> VehicleRead:
        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")
        return self._to_read(vehicle)

    async def update(self, vehicle_id: str, payload: VehicleUpdateRequest, *, updated_by: str | None = None) -> VehicleRead:
        existing_vehicle = await self.vehicle_repository.get_by_id(vehicle_id)
        if existing_vehicle is None:
            raise NotFoundException("Vehicle not found")

        if payload.current_odometer is not None and payload.current_odometer < existing_vehicle.current_odometer:
            raise BusinessRuleException("Current odometer cannot decrease")

        if payload.status is not None and existing_vehicle.status == VehicleStatus.RETIRED and payload.status == VehicleStatus.AVAILABLE:
            raise BusinessRuleException("Retired vehicles cannot become available again")

        if payload.status is not None and existing_vehicle.status == VehicleStatus.IN_SHOP and payload.status == VehicleStatus.ON_TRIP:
            raise BusinessRuleException("In-shop vehicles cannot be assigned to trips")

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("previous_odometer", None)

        if update_data.get("registration_number") is not None:
            normalized_registration_number = str(update_data["registration_number"]).strip().upper()
            duplicate_vehicle = await self.vehicle_repository.get_by_registration_number(normalized_registration_number)
            if duplicate_vehicle is not None and str(duplicate_vehicle.id) != vehicle_id:
                raise ConflictException("Vehicle registration number already exists")
            update_data["registration_number"] = normalized_registration_number

        if update_data.get("vehicle_name") is not None:
            update_data["vehicle_name"] = str(update_data["vehicle_name"]).strip()

        if update_data.get("vehicle_model") is not None:
            update_data["vehicle_model"] = str(update_data["vehicle_model"]).strip()

        if update_data.get("region") is not None:
            update_data["region"] = str(update_data["region"]).strip()

        update_data["updated_by"] = updated_by
        vehicle = await self.vehicle_repository.update(vehicle_id, **update_data)
        await self._log_activity(vehicle_id=vehicle.id, action="Vehicle Updated", message=f"Vehicle {vehicle.registration_number} updated", performed_by=updated_by)
        return self._to_read(vehicle)

    async def delete(self, vehicle_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        await self.vehicle_repository.delete(vehicle_id)
        await self._log_activity(vehicle_id=vehicle.id, action="Vehicle Deleted", message=f"Vehicle {vehicle.registration_number} deleted", performed_by=deleted_by)
        return {"detail": "Vehicle deleted successfully"}

    async def search(self, *, query: str, page: int = 1, size: int = 20) -> dict[str, object]:
        return await self.list(page=page, size=size, search=query)

    async def list_available(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.vehicle_repository.list_available()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(vehicle) for vehicle in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _log_activity(self, *, vehicle_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            vehicle_id=vehicle_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _to_read(vehicle: Vehicle) -> VehicleRead:
        return VehicleRead(
            id=str(vehicle.id),
            registration_number=vehicle.registration_number,
            vehicle_name=vehicle.vehicle_name,
            vehicle_model=vehicle.vehicle_model,
            vehicle_type=vehicle.vehicle_type,
            maximum_load_capacity=vehicle.maximum_load_capacity,
            current_odometer=vehicle.current_odometer,
            acquisition_cost=vehicle.acquisition_cost,
            purchase_date=vehicle.purchase_date,
            status=vehicle.status,
            region=vehicle.region,
            documents=vehicle.documents,
            insurance_expiry=vehicle.insurance_expiry,
            fitness_expiry=vehicle.fitness_expiry,
            pollution_expiry=vehicle.pollution_expiry,
            is_active=vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            created_by=vehicle.created_by,
            updated_by=vehicle.updated_by,
        )


def get_vehicle_service() -> VehicleService:
    """Build a vehicle service with concrete repositories."""

    return VehicleService(
        vehicle_repository=VehicleRepository(),
        activity_log_repository=VehicleActivityLogRepository(),
    )
