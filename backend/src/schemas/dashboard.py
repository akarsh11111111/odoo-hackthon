"""Dashboard analytics response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.schemas.common import APIResponse


class DashboardOverview(BaseModel):
    """High-level fleet and operations overview for the dashboard."""

    total_vehicles: int = Field(..., json_schema_extra={"example": 120})
    available_vehicles: int = Field(..., json_schema_extra={"example": 72})
    on_trip_vehicles: int = Field(..., json_schema_extra={"example": 24})
    vehicles_in_shop: int = Field(..., json_schema_extra={"example": 8})
    retired_vehicles: int = Field(..., json_schema_extra={"example": 16})
    total_drivers: int = Field(..., json_schema_extra={"example": 90})
    available_drivers: int = Field(..., json_schema_extra={"example": 48})
    drivers_on_trip: int = Field(..., json_schema_extra={"example": 22})
    drivers_suspended: int = Field(..., json_schema_extra={"example": 4})
    total_active_trips: int = Field(..., json_schema_extra={"example": 36})
    completed_trips: int = Field(..., json_schema_extra={"example": 560})
    cancelled_trips: int = Field(..., json_schema_extra={"example": 44})
    pending_trips: int = Field(..., json_schema_extra={"example": 12})
    fuel_cost: float = Field(..., json_schema_extra={"example": 42850.25})
    maintenance_cost: float = Field(..., json_schema_extra={"example": 30120.75})
    operational_cost: float = Field(..., json_schema_extra={"example": 72971.0})
    fleet_utilization_percent: float = Field(..., json_schema_extra={"example": 80.0})
    average_fuel_efficiency: float | None = Field(default=None, json_schema_extra={"example": 7.4})
    vehicle_roi: float | None = Field(default=None, json_schema_extra={"example": 18.25})


class DashboardFleetAnalytics(BaseModel):
    """Vehicle-centric analytics used by fleet operations teams."""

    vehicle_status_distribution: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "Available", "count": 72}]})
    fleet_utilization_percent: float = Field(..., json_schema_extra={"example": 80.0})
    vehicles_by_type: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "Truck", "count": 42}]})
    maintenance_frequency: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "vehicle-1", "maintenance_count": 3}]})
    top_costliest_vehicles: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"vehicle_id": "vehicle-1", "total_cost": 12000.0}]})
    vehicles_requiring_maintenance_soon: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "vehicle-2", "pending_requests": 2}]})


class DashboardDriverAnalytics(BaseModel):
    """Driver-centric analytics populated from the driver registry."""

    safety_score_distribution: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "90+", "count": 21}]})
    license_expiry_summary: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "0-30 days", "count": 3}]})
    driver_availability: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "Available", "count": 48}]})
    top_drivers: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"driver_id": "driver-1", "safety_score": 95}]})
    inactive_drivers: int = Field(..., json_schema_extra={"example": 5})


class DashboardTripAnalytics(BaseModel):
    """Trip execution analytics for operations review."""

    trips_per_month: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "2026-07", "trips": 18}]})
    completed_trips: int = Field(..., json_schema_extra={"example": 560})
    cancelled_trips: int = Field(..., json_schema_extra={"example": 44})
    distance_covered: float = Field(..., json_schema_extra={"example": 124500.0})
    cargo_statistics: dict[str, Any] = Field(..., json_schema_extra={"example": {"total_cargo_weight": 2000.0, "average_cargo_weight": 120.0}})
    average_trip_duration: float | None = Field(default=None, json_schema_extra={"example": 245.0})


class DashboardMaintenanceAnalytics(BaseModel):
    """Maintenance cost and lifecycle analytics."""

    maintenance_cost: float = Field(..., json_schema_extra={"example": 30120.75})
    pending_requests: int = Field(..., json_schema_extra={"example": 6})
    average_repair_time: float | None = Field(default=None, json_schema_extra={"example": 360.0})
    maintenance_by_vehicle: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "vehicle-1", "maintenance_count": 3, "total_cost": 5400.0}]})


class DashboardFuelAnalytics(BaseModel):
    """Fuel consumption and efficiency analytics."""

    fuel_consumption: float = Field(..., json_schema_extra={"example": 8200.0})
    fuel_cost: float = Field(..., json_schema_extra={"example": 42850.25})
    fuel_efficiency: float | None = Field(default=None, json_schema_extra={"example": 7.4})
    average_fuel_price: float | None = Field(default=None, json_schema_extra={"example": 1.35})


class DashboardExpenseAnalytics(BaseModel):
    """Expense allocation analytics for fleet operating cost review."""

    expense_breakdown: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "Fuel", "total_amount": 30000.0}]})
    expense_by_category: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "Fuel", "total_amount": 30000.0}]})
    monthly_operational_cost: list[dict[str, Any]] = Field(..., json_schema_extra={"example": [{"_id": "2026-07", "monthly_cost": 5000.0}]})


class DashboardKPI(BaseModel):
    """A compact KPI snapshot intended for dashboard cards."""

    total_vehicles: int = Field(..., json_schema_extra={"example": 120})
    available_vehicles: int = Field(..., json_schema_extra={"example": 72})
    total_active_trips: int = Field(..., json_schema_extra={"example": 36})
    total_drivers: int = Field(..., json_schema_extra={"example": 90})
    fuel_cost: float = Field(..., json_schema_extra={"example": 42850.25})
    maintenance_cost: float = Field(..., json_schema_extra={"example": 30120.75})
    operational_cost: float = Field(..., json_schema_extra={"example": 72971.0})
    fleet_utilization_percent: float = Field(..., json_schema_extra={"example": 80.0})
    average_fuel_efficiency: float | None = Field(default=None, json_schema_extra={"example": 7.4})
    vehicle_roi: float | None = Field(default=None, json_schema_extra={"example": 18.25})


DashboardOverviewResponse = APIResponse[DashboardOverview]
DashboardFleetResponse = APIResponse[DashboardFleetAnalytics]
DashboardDriversResponse = APIResponse[DashboardDriverAnalytics]
DashboardTripsResponse = APIResponse[DashboardTripAnalytics]
DashboardMaintenanceResponse = APIResponse[DashboardMaintenanceAnalytics]
DashboardFuelResponse = APIResponse[DashboardFuelAnalytics]
DashboardExpensesResponse = APIResponse[DashboardExpenseAnalytics]
DashboardKPIResponse = APIResponse[DashboardKPI]
