"""Reusable analytics helpers for fuel and expense management."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FuelExpenseAnalyticsService:
    """Reusable calculations for fleet financial analytics."""

    @staticmethod
    def calculate_fuel_efficiency(distance_km: float, fuel_liters: float) -> float | None:
        if distance_km <= 0 or fuel_liters <= 0:
            return None
        return distance_km / fuel_liters

    @staticmethod
    def calculate_cost_per_kilometer(total_cost: float, distance_km: float) -> float | None:
        if total_cost < 0 or distance_km <= 0:
            return None
        return total_cost / distance_km

    @staticmethod
    def calculate_operational_cost(*, fuel_cost: float, maintenance_cost: float = 0, other_expenses: float = 0) -> float:
        return fuel_cost + maintenance_cost + other_expenses

    @staticmethod
    def summarize_vehicle_expenses(*, fuel_cost: float, maintenance_cost: float = 0, other_expenses: float = 0) -> dict[str, float]:
        return {
            "fuel_cost": fuel_cost,
            "maintenance_cost": maintenance_cost,
            "other_expenses": other_expenses,
            "operational_cost": FuelExpenseAnalyticsService.calculate_operational_cost(
                fuel_cost=fuel_cost,
                maintenance_cost=maintenance_cost,
                other_expenses=other_expenses,
            ),
        }
