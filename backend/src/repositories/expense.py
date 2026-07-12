"""Repository layer for expense management models."""

from __future__ import annotations

from typing import Any

from beanie.odm.fields import PydanticObjectId

from src.core.exceptions import NotFoundException
from src.models.expense import Expense, ExpenseActivityLog, utcnow


def _to_object_id(identifier: str) -> PydanticObjectId | str:
    try:
        return PydanticObjectId(identifier)
    except Exception:
        return identifier


class ExpenseRepository:
    """Data access for expense documents."""

    async def get_by_id(self, expense_id: str) -> Expense | None:
        return await Expense.get(_to_object_id(expense_id))

    async def get_by_expense_id(self, expense_id: str) -> Expense | None:
        return await Expense.find_one(Expense.expense_id == expense_id)

    async def create(self, **expense_data: Any) -> Expense:
        expense = Expense(**expense_data)
        return await expense.insert()

    async def update(self, expense_id: str, **expense_data: Any) -> Expense:
        expense = await self.get_by_id(expense_id)
        if expense is None:
            raise NotFoundException("Expense not found")

        for field, value in expense_data.items():
            setattr(expense, field, value)

        expense.updated_at = utcnow()
        await expense.save()
        return expense

    async def delete(self, expense_id: str) -> Expense:
        expense = await self.get_by_id(expense_id)
        if expense is None:
            raise NotFoundException("Expense not found")

        expense.is_active = False
        expense.updated_at = utcnow()
        await expense.save()
        return expense

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> tuple[list[Expense], int]:
        query = Expense.find(Expense.is_active == True)

        if filters:
            vehicle_id = filters.get("vehicle_id")
            if vehicle_id:
                query = query.find(Expense.vehicle_id == _to_object_id(str(vehicle_id)))

            trip_id = filters.get("trip_id")
            if trip_id:
                query = query.find(Expense.trip_id == _to_object_id(str(trip_id)))

            expense_type = filters.get("expense_type")
            if expense_type:
                query = query.find(Expense.expense_type == expense_type)

            vendor = filters.get("vendor")
            if vendor:
                query = query.find(Expense.vendor == vendor)

        if search:
            query_text = search.lower().strip()
            query = query.find(
                {
                    "$or": [
                        {"expense_id": {"$regex": query_text, "$options": "i"}},
                        {"vendor": {"$regex": query_text, "$options": "i"}},
                        {"invoice_number": {"$regex": query_text, "$options": "i"}},
                        {"description": {"$regex": query_text, "$options": "i"}},
                    ]
                }
            )

        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = getattr(Expense, sort_by, Expense.created_at)
        total = await query.count()
        items = await query.sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        return items, total

    async def list_history(self) -> list[Expense]:
        return await Expense.find(Expense.is_active == True).to_list()

    async def list_by_vehicle(self, vehicle_id: str) -> list[Expense]:
        return await Expense.find((Expense.is_active == True) & (Expense.vehicle_id == _to_object_id(vehicle_id))).to_list()


class ExpenseActivityLogRepository:
    """Data access for expense audit trail documents."""

    async def create(self, **log_data: Any) -> ExpenseActivityLog:
        log_entry = ExpenseActivityLog(**log_data)
        return await log_entry.insert()
