"""Expense management Beanie documents."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class ExpenseType(str, Enum):
    """Expense classification for fleet operations."""

    FUEL = "Fuel"
    REPAIR = "Repair"
    INSURANCE = "Insurance"
    PARKING = "Parking"
    TOLL = "Toll"
    CLEANING = "Cleaning"
    TYRES = "Tyres"
    SERVICE = "Service"
    MISCELLANEOUS = "Miscellaneous"


class Expense(Document):
    """Fleet expense register persisted in MongoDB."""

    expense_id: Indexed(str, unique=True)
    vehicle_id: PydanticObjectId
    trip_id: PydanticObjectId | None = None
    expense_type: ExpenseType
    amount: float = Field(ge=0)
    vendor: str
    invoice_number: str
    expense_date: date
    description: str
    attachment: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_by: str | None = None

    class Settings:
        name = "expenses"
        indexes = [
            IndexModel([("vehicle_id", ASCENDING), ("expense_date", ASCENDING)], name="expense_vehicle_date_idx"),
            IndexModel([("trip_id", ASCENDING), ("expense_type", ASCENDING)], name="expense_trip_type_idx"),
        ]


class ExpenseActivityLog(Document):
    """Audit trail entry for expense lifecycle events."""

    expense_id: PydanticObjectId
    action: str
    message: str
    performed_by: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "expense_activity_logs"
