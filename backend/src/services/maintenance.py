"""Maintenance management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.constants.auth import FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, ForbiddenException, NotFoundException
from src.models.maintenance import Maintenance, MaintenanceLog, MaintenancePriority, MaintenanceStatus, MaintenanceType, utcnow
from src.models.vehicle import VehicleStatus
from src.repositories.maintenance import MaintenanceLogRepository, MaintenanceRepository
from src.repositories.trip import TripRepository
from src.repositories.vehicle import VehicleRepository
from src.schemas.maintenance import MaintenanceApproveRequest, MaintenanceCompleteRequest, MaintenanceCreateRequest, MaintenanceRejectRequest, MaintenanceStartRequest, MaintenanceUpdateRequest, MaintenanceRead


@dataclass(slots=True)
class MaintenanceService:
    """Coordinates maintenance business rules and audit logging."""

    maintenance_repository: MaintenanceRepository
    vehicle_repository: VehicleRepository
    trip_repository: TripRepository
    activity_log_repository: MaintenanceLogRepository | None = None

    async def create(self, payload: MaintenanceCreateRequest, *, created_by: str | None = None) -> MaintenanceRead:
        vehicle = await self.vehicle_repository.get_by_id(payload.vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        if not vehicle.is_active:
            raise BusinessRuleException("Vehicle is inactive")

        if vehicle.status == VehicleStatus.RETIRED:
            raise BusinessRuleException("Retired vehicles cannot enter maintenance")

        active_trip = await self.trip_repository.list_active()
        if any(str(trip.vehicle_id) == str(vehicle.id) for trip in active_trip):
            raise BusinessRuleException("Vehicle is currently on an active trip")

        existing_active = await self.maintenance_repository.get_active_by_vehicle(str(vehicle.id))
        if existing_active is not None:
            raise ConflictException("Vehicle already has an active maintenance request")

        maintenance_id = await self._generate_maintenance_id()
        maintenance = await self.maintenance_repository.create(
            maintenance_id=maintenance_id,
            vehicle_id=vehicle.id,
            maintenance_type=payload.maintenance_type,
            title=payload.title.strip(),
            description=payload.description.strip(),
            priority=payload.priority,
            vendor_name=payload.vendor_name.strip(),
            estimated_cost=payload.estimated_cost,
            actual_cost=None,
            scheduled_date=payload.scheduled_date,
            started_at=None,
            completed_at=None,
            status=MaintenanceStatus.PENDING,
            notes=payload.notes.strip() if payload.notes else None,
            attachments=list(payload.attachments or []),
            created_by=created_by,
            updated_by=created_by,
        )

        await self.vehicle_repository.update(
            str(vehicle.id),
            status=VehicleStatus.IN_SHOP,
            updated_by=created_by,
        )
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Created",
            message=f"Maintenance request {maintenance.maintenance_id} created",
            performed_by=created_by,
        )
        return self._to_read(maintenance)

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
        items, total = await self.maintenance_repository.list(
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

    async def get_by_id(self, maintenance_id: str) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")
        return self._to_read(maintenance)

    async def update(self, maintenance_id: str, payload: MaintenanceUpdateRequest, *, updated_by: str | None = None) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        if maintenance.status in {MaintenanceStatus.COMPLETED, MaintenanceStatus.REJECTED}:
            raise BusinessRuleException("Completed or rejected maintenance requests cannot be updated")

        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("title") is not None:
            update_data["title"] = str(update_data["title"]).strip()
        if update_data.get("description") is not None:
            update_data["description"] = str(update_data["description"]).strip()
        if update_data.get("vendor_name") is not None:
            update_data["vendor_name"] = str(update_data["vendor_name"]).strip()
        if update_data.get("notes") is not None:
            update_data["notes"] = str(update_data["notes"]).strip()

        update_data["updated_by"] = updated_by
        maintenance = await self.maintenance_repository.update(maintenance_id, **update_data)
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Updated",
            message=f"Maintenance request {maintenance.maintenance_id} updated",
            performed_by=updated_by,
        )
        return self._to_read(maintenance)

    async def delete(self, maintenance_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        await self.maintenance_repository.delete(maintenance_id)
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Deleted",
            message=f"Maintenance request {maintenance.maintenance_id} deleted",
            performed_by=deleted_by,
        )
        return {"detail": "Maintenance deleted successfully"}

    async def approve(self, maintenance_id: str, payload: MaintenanceApproveRequest, *, approved_by: str | None = None) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        if maintenance.status != MaintenanceStatus.PENDING:
            raise BusinessRuleException("Only pending maintenance requests can be approved")

        vehicle = await self.vehicle_repository.get_by_id(str(maintenance.vehicle_id))
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        if vehicle.status == VehicleStatus.RETIRED:
            raise BusinessRuleException("Retired vehicles cannot be approved for maintenance")

        maintenance = await self.maintenance_repository.update(
            maintenance_id,
            status=MaintenanceStatus.APPROVED,
            notes=(payload.approval_notes or maintenance.notes).strip() if payload.approval_notes else maintenance.notes,
            updated_by=approved_by,
        )
        await self.vehicle_repository.update(str(vehicle.id), status=VehicleStatus.IN_SHOP, updated_by=approved_by)
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Approved",
            message=f"Maintenance request {maintenance.maintenance_id} approved",
            performed_by=approved_by,
        )
        return self._to_read(maintenance)

    async def reject(self, maintenance_id: str, payload: MaintenanceRejectRequest, *, rejected_by: str | None = None) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        if maintenance.status not in {MaintenanceStatus.PENDING, MaintenanceStatus.APPROVED}:
            raise BusinessRuleException("Only pending or approved maintenance requests can be rejected")

        vehicle = await self.vehicle_repository.get_by_id(str(maintenance.vehicle_id))
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        maintenance = await self.maintenance_repository.update(
            maintenance_id,
            status=MaintenanceStatus.REJECTED,
            notes=payload.rejection_reason.strip(),
            updated_by=rejected_by,
        )

        if vehicle.status != VehicleStatus.RETIRED:
            await self.vehicle_repository.update(str(vehicle.id), status=VehicleStatus.AVAILABLE, updated_by=rejected_by)

        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Rejected",
            message=f"Maintenance request {maintenance.maintenance_id} rejected",
            performed_by=rejected_by,
        )
        return self._to_read(maintenance)

    async def start(self, maintenance_id: str, payload: MaintenanceStartRequest, *, started_by: str | None = None) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        if maintenance.status != MaintenanceStatus.APPROVED:
            raise BusinessRuleException("Only approved maintenance requests can be started")

        vehicle = await self.vehicle_repository.get_by_id(str(maintenance.vehicle_id))
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        maintenance = await self.maintenance_repository.update(
            maintenance_id,
            status=MaintenanceStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            notes=(payload.technician_notes or maintenance.notes).strip() if payload.technician_notes else maintenance.notes,
            updated_by=started_by,
        )
        await self.vehicle_repository.update(str(vehicle.id), status=VehicleStatus.IN_SHOP, updated_by=started_by)
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Started",
            message=f"Maintenance request {maintenance.maintenance_id} started",
            performed_by=started_by,
        )
        return self._to_read(maintenance)

    async def complete(self, maintenance_id: str, payload: MaintenanceCompleteRequest, *, completed_by: str | None = None) -> MaintenanceRead:
        maintenance = await self.maintenance_repository.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        if maintenance.status != MaintenanceStatus.IN_PROGRESS:
            raise BusinessRuleException("Only in-progress maintenance requests can be completed")

        vehicle = await self.vehicle_repository.get_by_id(str(maintenance.vehicle_id))
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        completion_time = datetime.now(timezone.utc)
        actual_duration = None
        if maintenance.started_at is not None:
            actual_duration = int((completion_time - maintenance.started_at).total_seconds() // 60)

        maintenance = await self.maintenance_repository.update(
            maintenance_id,
            status=MaintenanceStatus.COMPLETED,
            actual_cost=payload.actual_cost,
            completed_at=completion_time,
            notes=payload.completion_notes.strip(),
            updated_by=completed_by,
        )

        new_vehicle_status = VehicleStatus.RETIRED if vehicle.status == VehicleStatus.RETIRED else VehicleStatus.AVAILABLE
        await self.vehicle_repository.update(
            str(vehicle.id),
            status=new_vehicle_status,
            current_odometer=payload.final_odometer or vehicle.current_odometer,
            updated_by=completed_by,
        )
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Maintenance Completed",
            message=f"Maintenance request {maintenance.maintenance_id} completed",
            performed_by=completed_by,
        )
        await self._log_activity(
            maintenance_id=maintenance.id,
            action="Vehicle Returned To Service",
            message=f"Vehicle {vehicle.registration_number} returned to service",
            performed_by=completed_by,
        )
        return self._to_read(maintenance)

    async def list_active(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.maintenance_repository.list_active()
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
        items = await self.maintenance_repository.list_history()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _generate_maintenance_id(self) -> str:
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        items, total = await self.maintenance_repository.list(limit=1000)
        maintenance_count = total + 1

        while True:
            candidate = f"MAINT-{date_stamp}-{maintenance_count:04d}"
            existing = await self.maintenance_repository.get_by_maintenance_id(candidate)
            if existing is None:
                return candidate
            maintenance_count += 1

    async def _log_activity(self, *, maintenance_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            maintenance_id=maintenance_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _to_read(maintenance: Maintenance) -> MaintenanceRead:
        return MaintenanceRead(
            id=str(maintenance.id),
            maintenance_id=maintenance.maintenance_id,
            vehicle_id=str(maintenance.vehicle_id),
            maintenance_type=maintenance.maintenance_type,
            title=maintenance.title,
            description=maintenance.description,
            priority=maintenance.priority,
            vendor_name=maintenance.vendor_name,
            estimated_cost=maintenance.estimated_cost,
            actual_cost=maintenance.actual_cost,
            scheduled_date=maintenance.scheduled_date,
            started_at=maintenance.started_at,
            completed_at=maintenance.completed_at,
            status=maintenance.status,
            notes=maintenance.notes,
            attachments=maintenance.attachments,
            is_active=maintenance.is_active,
            created_at=maintenance.created_at,
            updated_at=maintenance.updated_at,
            created_by=maintenance.created_by,
            updated_by=maintenance.updated_by,
        )


def get_maintenance_service() -> MaintenanceService:
    """Build a maintenance service with concrete repositories."""

    return MaintenanceService(
        maintenance_repository=MaintenanceRepository(),
        vehicle_repository=VehicleRepository(),
        trip_repository=TripRepository(),
        activity_log_repository=MaintenanceLogRepository(),
    )
