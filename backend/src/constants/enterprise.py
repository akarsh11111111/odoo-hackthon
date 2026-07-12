"""Shared constants for enterprise control-plane modules."""

from __future__ import annotations

from typing import Final

SEARCH_COLLECTIONS: Final[dict[str, dict[str, list[str] | str]]] = {
    "vehicles": {
        "search_fields": ["registration_number", "vehicle_name", "vehicle_model", "region"],
        "display_field": "registration_number",
        "description_field": "vehicle_name",
    },
    "drivers": {
        "search_fields": ["license_number", "first_name", "last_name", "email"],
        "display_field": "license_number",
        "description_field": "first_name",
    },
    "trips": {
        "search_fields": ["trip_number", "source", "destination", "cargo_description"],
        "display_field": "trip_number",
        "description_field": "source",
    },
    "maintenance_requests": {
        "search_fields": ["maintenance_id", "title", "description", "vendor_name"],
        "display_field": "maintenance_id",
        "description_field": "title",
    },
    "fuel_logs": {
        "search_fields": ["fuel_log_id", "fuel_station", "notes"],
        "display_field": "fuel_log_id",
        "description_field": "fuel_station",
    },
    "expenses": {
        "search_fields": ["expense_id", "invoice_number", "vendor", "description"],
        "display_field": "expense_id",
        "description_field": "vendor",
    },
}

DEFAULT_REALTIME_AUDIT_ACTIONS: Final[tuple[str, ...]] = (
    "Vehicle Created",
    "Vehicle Updated",
    "Vehicle Deleted",
    "Driver Created",
    "Driver Updated",
    "Trip Created",
    "Trip Dispatched",
    "Trip Completed",
    "Trip Cancelled",
    "Maintenance Created",
    "Maintenance Approved",
    "Maintenance Started",
    "Maintenance Completed",
    "Fuel Added",
    "Expense Added",
    "Login",
    "Logout",
    "Role Change",
)
