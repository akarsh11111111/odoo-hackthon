"""Repository layer for maintenance management models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.maintenance import Maintenance, MaintenanceLog, MaintenanceStatus, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class MaintenanceRepository:
    """Data access for maintenance documents."""

    async def get_by_id(self, maintenance_id: str) -> Maintenance | None:
        return await Maintenance.get(_to_object_id(maintenance_id))

    async def get_by_maintenance_id(self, maintenance_id: str) -> Maintenance | None:
        return await Maintenance.find_one(Maintenance.maintenance_id == maintenance_id)

    async def create(self, **maintenance_data: Any) -> Maintenance:
        maintenance = Maintenance(**maintenance_data)
        return await maintenance.insert()

    async def update(self, maintenance_id: str, **maintenance_data: Any) -> Maintenance:
        maintenance = await self.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        for field, value in maintenance_data.items():
            setattr(maintenance, field, value)

        maintenance.updated_at = utcnow()
        await maintenance.save()
        return maintenance

    async def delete(self, maintenance_id: str) -> Maintenance:
        maintenance = await self.get_by_id(maintenance_id)
        if maintenance is None:
            raise NotFoundException("Maintenance request not found")

        maintenance.is_active = False
        maintenance.updated_at = utcnow()
        await maintenance.save()
        return maintenance

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[Maintenance], int]:
        items = await Maintenance.find((Maintenance.is_active == True) & (Maintenance.status != MaintenanceStatus.REJECTED)).to_list()

        if filters:
            vehicle_id = filters.get("vehicle_id")
            if vehicle_id:
                items = [item for item in items if str(item.vehicle_id) == str(vehicle_id)]

            status = filters.get("status")
            if status:
                items = [item for item in items if item.status == status]

            priority = filters.get("priority")
            if priority:
                items = [item for item in items if item.priority == priority]

            vendor_name = filters.get("vendor_name")
            if vendor_name:
                items = [item for item in items if item.vendor_name == vendor_name]

            scheduled_date = filters.get("scheduled_date")
            if scheduled_date:
                items = [item for item in items if item.scheduled_date == scheduled_date]

        if search:
            query = search.lower().strip()
            items = [
                item
                for item in items
                if query in item.maintenance_id.lower()
                or query in item.title.lower()
                or query in item.description.lower()
                or query in item.vendor_name.lower()
            ]

        items.sort(key=lambda item: getattr(item, sort_by, item.created_at), reverse=sort_order == "desc")
        total = len(items)
        return items[skip : skip + limit], total

    async def list_active(self) -> list[Maintenance]:
        return await Maintenance.find(
            (Maintenance.is_active == True)
            & (
                (Maintenance.status == MaintenanceStatus.PENDING)
                | (Maintenance.status == MaintenanceStatus.APPROVED)
                | (Maintenance.status == MaintenanceStatus.IN_PROGRESS)
            )
        ).to_list()

    async def list_history(self) -> list[Maintenance]:
        return await Maintenance.find(
            (Maintenance.is_active == True)
            & (
                (Maintenance.status == MaintenanceStatus.COMPLETED)
                | (Maintenance.status == MaintenanceStatus.REJECTED)
            )
        ).to_list()

    async def get_active_by_vehicle(self, vehicle_id: str) -> Maintenance | None:
        return await Maintenance.find_one(
            (Maintenance.is_active == True)
            & (Maintenance.vehicle_id == _to_object_id(vehicle_id))
            & (
                (Maintenance.status == MaintenanceStatus.PENDING)
                | (Maintenance.status == MaintenanceStatus.APPROVED)
                | (Maintenance.status == MaintenanceStatus.IN_PROGRESS)
            )
        )


class MaintenanceLogRepository:
    """Data access for maintenance audit trail documents."""

    async def create(self, **log_data: Any) -> MaintenanceLog:
        log_entry = MaintenanceLog(**log_data)
        return await log_entry.insert()
