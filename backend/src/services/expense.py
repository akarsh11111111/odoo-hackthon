"""Expense management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.constants.auth import FLEET_MANAGER
from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.expense import Expense, ExpenseActivityLog, ExpenseType, utcnow
from src.models.vehicle import VehicleStatus
from src.repositories.expense import ExpenseActivityLogRepository, ExpenseRepository
from src.repositories.trip import TripRepository
from src.repositories.vehicle import VehicleRepository
from src.schemas.expense import ExpenseCreateRequest, ExpenseRead, ExpenseUpdateRequest


@dataclass(slots=True)
class ExpenseService:
    """Coordinates expense capture business rules and audit logging."""

    expense_repository: ExpenseRepository
    vehicle_repository: VehicleRepository
    trip_repository: TripRepository
    activity_log_repository: ExpenseActivityLogRepository | None = None

    async def create(self, payload: ExpenseCreateRequest, *, created_by: str | None = None) -> ExpenseRead:
        vehicle = await self.vehicle_repository.get_by_id(payload.vehicle_id)
        if vehicle is None:
            raise NotFoundException("Vehicle not found")

        if vehicle.status == VehicleStatus.RETIRED:
            raise BusinessRuleException("Retired vehicles cannot receive expense records")

        trip = None
        if payload.trip_id:
            trip = await self.trip_repository.get_by_id(str(payload.trip_id))
            if trip is None:
                raise NotFoundException("Trip not found")

        expense_id = await self._generate_expense_id()
        expense = await self.expense_repository.create(
            expense_id=expense_id,
            vehicle_id=vehicle.id,
            trip_id=trip.id if trip is not None else None,
            expense_type=payload.expense_type,
            amount=payload.amount,
            vendor=payload.vendor.strip(),
            invoice_number=payload.invoice_number.strip(),
            expense_date=payload.expense_date,
            description=payload.description.strip(),
            attachment=payload.attachment.strip() if payload.attachment else None,
            created_by=created_by,
            updated_by=created_by,
        )

        await self._log_activity(
            expense_id=expense.id,
            action="Expense Added",
            message=f"Expense {expense.expense_id} created",
            performed_by=created_by,
        )
        return self._to_read(expense)

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
        items, total = await self.expense_repository.list(
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

    async def get_by_id(self, expense_id: str) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise NotFoundException("Expense not found")
        return self._to_read(expense)

    async def update(self, expense_id: str, payload: ExpenseUpdateRequest, *, updated_by: str | None = None) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise NotFoundException("Expense not found")

        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("vendor") is not None:
            update_data["vendor"] = str(update_data["vendor"]).strip()
        if update_data.get("invoice_number") is not None:
            update_data["invoice_number"] = str(update_data["invoice_number"]).strip()
        if update_data.get("description") is not None:
            update_data["description"] = str(update_data["description"]).strip()
        if update_data.get("attachment") is not None:
            update_data["attachment"] = str(update_data["attachment"]).strip()

        update_data["updated_by"] = updated_by
        expense = await self.expense_repository.update(expense_id, **update_data)
        await self._log_activity(
            expense_id=expense.id,
            action="Expense Updated",
            message=f"Expense {expense.expense_id} updated",
            performed_by=updated_by,
        )
        return self._to_read(expense)

    async def delete(self, expense_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        expense = await self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise NotFoundException("Expense not found")

        await self.expense_repository.delete(expense_id)
        await self._log_activity(
            expense_id=expense.id,
            action="Expense Deleted",
            message=f"Expense {expense.expense_id} deleted",
            performed_by=deleted_by,
        )
        return {"detail": "Expense deleted successfully"}

    async def list_history(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.expense_repository.list_history()
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
        items = await self.expense_repository.list_by_vehicle(vehicle_id)
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(item) for item in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _generate_expense_id(self) -> str:
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        items, total = await self.expense_repository.list(limit=1000)
        expense_count = total + 1

        while True:
            candidate = f"EXP-{date_stamp}-{expense_count:04d}"
            existing = await self.expense_repository.get_by_expense_id(candidate)
            if existing is None:
                return candidate
            expense_count += 1

    async def _log_activity(self, *, expense_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            expense_id=expense_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _to_read(expense: Expense) -> ExpenseRead:
        return ExpenseRead(
            id=str(expense.id),
            expense_id=expense.expense_id,
            vehicle_id=str(expense.vehicle_id),
            trip_id=str(expense.trip_id) if expense.trip_id is not None else None,
            expense_type=expense.expense_type,
            amount=expense.amount,
            vendor=expense.vendor,
            invoice_number=expense.invoice_number,
            expense_date=expense.expense_date,
            description=expense.description,
            attachment=expense.attachment,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
            created_by=expense.created_by,
            updated_by=expense.updated_by,
        )


def get_expense_service() -> ExpenseService:
    """Build an expense service with concrete repositories."""

    return ExpenseService(
        expense_repository=ExpenseRepository(),
        vehicle_repository=VehicleRepository(),
        trip_repository=TripRepository(),
        activity_log_repository=ExpenseActivityLogRepository(),
    )
