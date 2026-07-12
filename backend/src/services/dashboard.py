"""Enterprise dashboard analytics service built on MongoDB aggregation pipelines."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_database


class DashboardAnalyticsService:
    """Aggregate fleet, driver, trip, maintenance, fuel, and expense KPIs from MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase | Any | None = None) -> None:
        self.database = database if database is not None else get_database()

    async def get_overview(self) -> dict[str, Any]:
        """Return the top-level fleet operations dashboard overview."""

        vehicle_snapshot = await self._aggregate(
            "vehicles",
            [
                {
                    "$group": {
                        "_id": None,
                        "total_vehicles": {"$sum": 1},
                        "available_vehicles": {"$sum": {"$cond": [{"$eq": ["$status", "Available"]}, 1, 0]}},
                        "on_trip_vehicles": {"$sum": {"$cond": [{"$eq": ["$status", "On Trip"]}, 1, 0]}},
                        "vehicles_in_shop": {"$sum": {"$cond": [{"$eq": ["$status", "In Shop"]}, 1, 0]}},
                        "retired_vehicles": {"$sum": {"$cond": [{"$eq": ["$status", "Retired"]}, 1, 0]}},
                    }
                }
            ],
        )
        vehicles = vehicle_snapshot[0] if vehicle_snapshot else {}

        drivers_snapshot = await self._aggregate(
            "drivers",
            [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": None,
                        "total_drivers": {"$sum": 1},
                        "available_drivers": {"$sum": {"$cond": [{"$eq": ["$driver_status", "Available"]}, 1, 0]}},
                        "drivers_on_trip": {"$sum": {"$cond": [{"$eq": ["$driver_status", "On Trip"]}, 1, 0]}},
                        "drivers_suspended": {"$sum": {"$cond": [{"$eq": ["$driver_status", "Suspended"]}, 1, 0]}},
                    }
                },
            ],
        )
        drivers = drivers_snapshot[0] if drivers_snapshot else {}

        trips_snapshot = await self._aggregate(
            "trips",
            [
                {
                    "$group": {
                        "_id": None,
                        "total_active_trips": {"$sum": {"$cond": [{"$eq": ["$status", "Dispatched"]}, 1, 0]}},
                        "completed_trips": {"$sum": {"$cond": [{"$eq": ["$status", "Completed"]}, 1, 0]}},
                        "cancelled_trips": {"$sum": {"$cond": [{"$eq": ["$status", "Cancelled"]}, 1, 0]}},
                        "pending_trips": {"$sum": {"$cond": [{"$eq": ["$status", "Draft"]}, 1, 0]}},
                    }
                }
            ],
        )
        trips = trips_snapshot[0] if trips_snapshot else {}

        fuel_cost = await self._sum_numeric_value("fuel_logs", "total_cost")
        maintenance_cost = await self._sum_maintenance_cost()
        expense_cost = await self._sum_numeric_value("expenses", "amount")
        operational_cost = fuel_cost + maintenance_cost + expense_cost

        fleet_utilization = self._percentage(
            vehicles.get("available_vehicles", 0) + vehicles.get("on_trip_vehicles", 0),
            vehicles.get("total_vehicles", 0),
        )

        avg_fuel_efficiency = await self._average_numeric_value("trips", "fuel_efficiency")
        vehicle_roi = await self._calculate_vehicle_roi()

        return {
            "total_vehicles": vehicles.get("total_vehicles", 0),
            "available_vehicles": vehicles.get("available_vehicles", 0),
            "on_trip_vehicles": vehicles.get("on_trip_vehicles", 0),
            "vehicles_in_shop": vehicles.get("vehicles_in_shop", 0),
            "retired_vehicles": vehicles.get("retired_vehicles", 0),
            "total_drivers": drivers.get("total_drivers", 0),
            "available_drivers": drivers.get("available_drivers", 0),
            "drivers_on_trip": drivers.get("drivers_on_trip", 0),
            "drivers_suspended": drivers.get("drivers_suspended", 0),
            "total_active_trips": trips.get("total_active_trips", 0),
            "completed_trips": trips.get("completed_trips", 0),
            "cancelled_trips": trips.get("cancelled_trips", 0),
            "pending_trips": trips.get("pending_trips", 0),
            "fuel_cost": round(fuel_cost, 2),
            "maintenance_cost": round(maintenance_cost, 2),
            "operational_cost": round(operational_cost, 2),
            "fleet_utilization_percent": round(fleet_utilization, 2),
            "average_fuel_efficiency": round(avg_fuel_efficiency, 2) if avg_fuel_efficiency is not None else None,
            "vehicle_roi": round(vehicle_roi, 2) if vehicle_roi is not None else None,
        }

    async def get_fleet(self) -> dict[str, Any]:
        """Return fleet-level analytics using aggregation pipelines."""

        status_distribution = await self._aggregate(
            "vehicles",
            [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
        )
        fleet_utilization = await self._aggregate(
            "vehicles",
            [
                {
                    "$group": {
                        "_id": None,
                        "total_vehicles": {"$sum": 1},
                        "active_vehicles": {
                            "$sum": {
                                "$cond": [
                                    {"$in": ["$status", ["Available", "On Trip"]]},
                                    1,
                                    0,
                                ]
                            }
                        },
                    }
                }
            ],
        )
        vehicles_by_type = await self._aggregate(
            "vehicles",
            [
                {"$group": {"_id": "$vehicle_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
        )
        maintenance_frequency = await self._aggregate(
            "maintenance_requests",
            [
                {"$group": {"_id": "$vehicle_id", "maintenance_count": {"$sum": 1}}},
                {"$sort": {"maintenance_count": -1, "_id": 1}},
                {"$limit": 10},
            ],
        )
        top_costliest_vehicles = await self._aggregate(
            "fuel_logs",
            [
                {"$project": {"vehicle_id": 1, "cost": {"$ifNull": ["$total_cost", 0]}}},
                {
                    "$unionWith": {
                        "coll": "expenses",
                        "pipeline": [
                            {"$project": {"vehicle_id": 1, "cost": {"$ifNull": ["$amount", 0]}}}
                        ],
                    }
                },
                {
                    "$unionWith": {
                        "coll": "maintenance_requests",
                        "pipeline": [
                            {
                                "$project": {
                                    "vehicle_id": 1,
                                    "cost": {"$ifNull": ["$actual_cost", {"$ifNull": ["$estimated_cost", 0]}]},
                                }
                            }
                        ],
                    }
                },
                {"$group": {"_id": "$vehicle_id", "total_cost": {"$sum": "$cost"}}},
                {"$sort": {"total_cost": -1}},
                {"$limit": 5},
                {"$lookup": {"from": "vehicles", "localField": "_id", "foreignField": "_id", "as": "vehicle"}},
                {"$unwind": "$vehicle"},
                {
                    "$project": {
                        "_id": 0,
                        "vehicle_id": {"$toString": "$_id"},
                        "registration_number": "$vehicle.registration_number",
                        "vehicle_name": "$vehicle.vehicle_name",
                        "total_cost": 1,
                    }
                },
            ],
        )
        maintenance_due = await self._aggregate(
            "maintenance_requests",
            [
                {
                    "$match": {
                        "status": {"$in": ["Pending", "Approved", "In Progress"]},
                        "scheduled_date": {"$gte": datetime.now(timezone.utc).date().isoformat()},
                    }
                },
                {"$group": {"_id": "$vehicle_id", "pending_requests": {"$sum": 1}}},
                {"$sort": {"pending_requests": -1}},
            ],
        )
        utilization_value = fleet_utilization[0] if fleet_utilization else {}

        return {
            "vehicle_status_distribution": status_distribution,
            "fleet_utilization_percent": round(
                self._percentage(
                    utilization_value.get("active_vehicles", 0),
                    utilization_value.get("total_vehicles", 0),
                ),
                2,
            ),
            "vehicles_by_type": vehicles_by_type,
            "maintenance_frequency": maintenance_frequency,
            "top_costliest_vehicles": top_costliest_vehicles,
            "vehicles_requiring_maintenance_soon": maintenance_due,
        }

    async def get_drivers(self) -> dict[str, Any]:
        """Return driver analytics metrics."""

        safety_distribution = await self._aggregate(
            "drivers",
            [
                {
                    "$project": {
                        "safety_bucket": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$gte": ["$safety_score", 90]}, "then": "90+"},
                                    {"case": {"$gte": ["$safety_score", 80]}, "then": "80-89"},
                                    {"case": {"$gte": ["$safety_score", 70]}, "then": "70-79"},
                                ],
                                "default": "Below 70",
                            }
                        }
                    }
                },
                {"$group": {"_id": "$safety_bucket", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
        )
        license_expiry_summary = await self._aggregate(
            "drivers",
            [
                {
                    "$project": {
                        "license_bucket": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$lte": [{"$dateDiff": {"startDate": "$$NOW", "endDate": "$license_expiry", "unit": "day"}}, 0]}, "then": "Expired"},
                                    {"case": {"$lte": [{"$dateDiff": {"startDate": "$$NOW", "endDate": "$license_expiry", "unit": "day"}}, 30]}, "then": "0-30 days"},
                                    {"case": {"$lte": [{"$dateDiff": {"startDate": "$$NOW", "endDate": "$license_expiry", "unit": "day"}}, 60]}, "then": "31-60 days"},
                                    {"case": {"$lte": [{"$dateDiff": {"startDate": "$$NOW", "endDate": "$license_expiry", "unit": "day"}}, 90]}, "then": "61-90 days"},
                                ],
                                "default": "91+ days",
                            }
                        }
                    }
                },
                {"$group": {"_id": "$license_bucket", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
        )
        driver_availability = await self._aggregate(
            "drivers",
            [
                {"$group": {"_id": "$driver_status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
        )
        top_drivers = await self._aggregate(
            "drivers",
            [
                {"$match": {"is_active": True}},
                {"$sort": {"safety_score": -1, "created_at": -1}},
                {"$limit": 5},
                {
                    "$project": {
                        "_id": 0,
                        "driver_id": {"$toString": "$_id"},
                        "first_name": 1,
                        "last_name": 1,
                        "safety_score": 1,
                        "driver_status": 1,
                    }
                },
            ],
        )
        inactive_drivers = await self._aggregate(
            "drivers",
            [
                {"$match": {"is_active": False}},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
            ],
        )

        return {
            "safety_score_distribution": safety_distribution,
            "license_expiry_summary": license_expiry_summary,
            "driver_availability": driver_availability,
            "top_drivers": top_drivers,
            "inactive_drivers": inactive_drivers[0]["count"] if inactive_drivers else 0,
        }

    async def get_trips(self) -> dict[str, Any]:
        """Return trip analytics derived from the trip collection."""

        trips_per_month = await self._aggregate(
            "trips",
            [
                {
                    "$match": {"dispatch_time": {"$ne": None}},
                },
                {
                    "$project": {
                        "month": {"$dateToString": {"format": "%Y-%m", "date": "$dispatch_time"}},
                        "status": 1,
                        "actual_distance": 1,
                        "cargo_weight": 1,
                        "actual_duration": 1,
                    }
                },
                {
                    "$group": {
                        "_id": "$month",
                        "trips": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
            ],
        )
        completed_trips = await self._aggregate(
            "trips",
            [
                {"$match": {"status": "Completed"}},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
            ],
        )
        cancelled_trips = await self._aggregate(
            "trips",
            [
                {"$match": {"status": "Cancelled"}},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
            ],
        )
        distance_covered = await self._aggregate(
            "trips",
            [
                {
                    "$group": {
                        "_id": None,
                        "distance_covered": {"$sum": {"$ifNull": ["$actual_distance", "$estimated_distance"]}},
                    }
                }
            ],
        )
        cargo_statistics = await self._aggregate(
            "trips",
            [
                {
                    "$group": {
                        "_id": None,
                        "total_cargo_weight": {"$sum": {"$ifNull": ["$cargo_weight", 0]}},
                        "average_cargo_weight": {"$avg": {"$ifNull": ["$cargo_weight", 0]}},
                    }
                }
            ],
        )
        avg_duration = await self._aggregate(
            "trips",
            [
                {
                    "$group": {
                        "_id": None,
                        "average_trip_duration": {"$avg": {"$ifNull": ["$actual_duration", "$estimated_duration"]}},
                    }
                }
            ],
        )

        return {
            "trips_per_month": trips_per_month,
            "completed_trips": completed_trips[0]["count"] if completed_trips else 0,
            "cancelled_trips": cancelled_trips[0]["count"] if cancelled_trips else 0,
            "distance_covered": round(distance_covered[0]["distance_covered"], 2) if distance_covered else 0.0,
            "cargo_statistics": cargo_statistics[0] if cargo_statistics else {"total_cargo_weight": 0, "average_cargo_weight": 0},
            "average_trip_duration": round(avg_duration[0]["average_trip_duration"], 2) if avg_duration else None,
        }

    async def get_maintenance(self) -> dict[str, Any]:
        """Return maintenance analytics derived from the maintenance request collection."""

        maintenance_cost = await self._sum_maintenance_cost()
        pending_requests = await self._aggregate(
            "maintenance_requests",
            [
                {"$match": {"status": "Pending"}},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
            ],
        )
        avg_repair_time = await self._aggregate(
            "maintenance_requests",
            [
                {
                    "$match": {
                        "started_at": {"$ne": None},
                        "completed_at": {"$ne": None},
                    }
                },
                {
                    "$project": {
                        "repair_time_minutes": {
                            "$dateDiff": {
                                "startDate": "$started_at",
                                "endDate": "$completed_at",
                                "unit": "minute",
                            }
                        }
                    }
                },
                {"$group": {"_id": None, "average_repair_time": {"$avg": "$repair_time_minutes"}}},
            ],
        )
        maintenance_by_vehicle = await self._aggregate(
            "maintenance_requests",
            [
                {
                    "$project": {
                        "vehicle_id": 1,
                        "cost": {"$ifNull": ["$actual_cost", {"$ifNull": ["$estimated_cost", 0]}]},
                    }
                },
                {
                    "$group": {
                        "_id": "$vehicle_id",
                        "maintenance_count": {"$sum": 1},
                        "total_cost": {"$sum": "$cost"},
                    }
                },
                {"$sort": {"maintenance_count": -1, "total_cost": -1}},
                {"$limit": 10},
            ],
        )

        return {
            "maintenance_cost": round(maintenance_cost, 2),
            "pending_requests": pending_requests[0]["count"] if pending_requests else 0,
            "average_repair_time": round(avg_repair_time[0]["average_repair_time"], 2) if avg_repair_time else None,
            "maintenance_by_vehicle": maintenance_by_vehicle,
        }

    async def get_fuel(self) -> dict[str, Any]:
        """Return fuel analytics derived from the existing fuel and trip collections."""

        fuel_consumption = await self._sum_numeric_value("fuel_logs", "liters")
        fuel_cost = await self._sum_numeric_value("fuel_logs", "total_cost")
        fuel_efficiency = await self._average_numeric_value("trips", "fuel_efficiency")
        avg_fuel_price = await self._average_numeric_value("fuel_logs", "price_per_liter")

        return {
            "fuel_consumption": round(fuel_consumption, 2),
            "fuel_cost": round(fuel_cost, 2),
            "fuel_efficiency": round(fuel_efficiency, 2) if fuel_efficiency is not None else None,
            "average_fuel_price": round(avg_fuel_price, 2) if avg_fuel_price is not None else None,
        }

    async def get_expenses(self) -> dict[str, Any]:
        """Return expense analytics derived from the expense collection."""

        expense_breakdown = await self._aggregate(
            "expenses",
            [
                {"$group": {"_id": "$expense_type", "total_amount": {"$sum": "$amount"}}},
                {"$sort": {"total_amount": -1, "_id": 1}},
            ],
        )
        monthly_operational_cost = await self._aggregate(
            "expenses",
            [
                {
                    "$project": {
                        "month": {"$dateToString": {"format": "%Y-%m", "date": "$expense_date"}},
                        "amount": 1,
                    }
                },
                {"$group": {"_id": "$month", "monthly_cost": {"$sum": "$amount"}}},
                {"$sort": {"_id": 1}},
            ],
        )

        return {
            "expense_breakdown": expense_breakdown,
            "expense_by_category": expense_breakdown,
            "monthly_operational_cost": monthly_operational_cost,
        }

    async def get_kpis(self) -> dict[str, Any]:
        """Return a compact KPI view for dashboard consumption."""

        overview = await self.get_overview()
        return {
            "total_vehicles": overview["total_vehicles"],
            "available_vehicles": overview["available_vehicles"],
            "total_active_trips": overview["total_active_trips"],
            "total_drivers": overview["total_drivers"],
            "fuel_cost": overview["fuel_cost"],
            "maintenance_cost": overview["maintenance_cost"],
            "operational_cost": overview["operational_cost"],
            "fleet_utilization_percent": overview["fleet_utilization_percent"],
            "average_fuel_efficiency": overview["average_fuel_efficiency"],
            "vehicle_roi": overview["vehicle_roi"],
        }

    async def _aggregate(self, collection_name: str, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        collection = self.database.get_collection(collection_name)
        return await collection.aggregate(pipeline).to_list(length=None)

    async def _sum_numeric_value(self, collection_name: str, field_name: str) -> float:
        pipeline = [{"$group": {"_id": None, "value": {"$sum": {"$ifNull": [f"${field_name}", 0]}}}}]
        result = await self._aggregate(collection_name, pipeline)
        if not result:
            return 0.0
        if "value" in result[0]:
            return float(result[0]["value"])

        numeric_total = 0.0
        for row in result:
            numeric_value = row.get(field_name)
            if numeric_value is None:
                numeric_value = row.get("value")
            if numeric_value is None:
                continue
            try:
                numeric_total += float(numeric_value)
            except (TypeError, ValueError):
                continue
        return numeric_total

    async def _average_numeric_value(self, collection_name: str, field_name: str) -> float | None:
        pipeline = [{"$group": {"_id": None, "value": {"$avg": {"$ifNull": [f"${field_name}", None]}}}}]
        result = await self._aggregate(collection_name, pipeline)
        if not result:
            return None
        if "value" in result[0]:
            value = result[0]["value"]
            return None if value is None else float(value)

        numeric_values = [
            float(row[field_name])
            for row in result
            if row.get(field_name) is not None and self._is_numeric(row.get(field_name))
        ]
        if not numeric_values:
            return None
        return sum(numeric_values) / len(numeric_values)

    async def _sum_maintenance_cost(self) -> float:
        pipeline = [
            {
                "$project": {
                    "cost": {
                        "$ifNull": ["$actual_cost", {"$ifNull": ["$estimated_cost", 0]}]
                    }
                }
            },
            {"$group": {"_id": None, "value": {"$sum": "$cost"}}},
        ]
        result = await self._aggregate("maintenance_requests", pipeline)
        if not result:
            return 0.0
        if "value" in result[0]:
            return float(result[0]["value"])

        numeric_total = 0.0
        for row in result:
            cost = row.get("actual_cost")
            if cost is None:
                cost = row.get("estimated_cost", 0)
            if cost is None:
                cost = row.get("value")
            if cost is None:
                continue
            try:
                numeric_total += float(cost)
            except (TypeError, ValueError):
                continue
        return numeric_total

    async def _calculate_vehicle_roi(self) -> float | None:
        distance_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "distance_covered": {"$sum": {"$ifNull": ["$actual_distance", "$estimated_distance"]}},
                }
            }
        ]
        distance_result = await self._aggregate("trips", distance_pipeline)
        if distance_result and "distance_covered" in distance_result[0]:
            distance_covered = float(distance_result[0]["distance_covered"])
        elif distance_result:
            distance_covered = 0.0
            for row in distance_result:
                covered = row.get("actual_distance", row.get("estimated_distance", 0))
                if covered is None:
                    continue
                try:
                    distance_covered += float(covered)
                except (TypeError, ValueError):
                    continue
        else:
            distance_covered = 0.0

        acquisition_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_acquisition_cost": {"$sum": {"$ifNull": ["$acquisition_cost", 0]}},
                }
            }
        ]
        acquisition_result = await self._aggregate("vehicles", acquisition_pipeline)
        if acquisition_result and "total_acquisition_cost" in acquisition_result[0]:
            total_acquisition_cost = float(acquisition_result[0]["total_acquisition_cost"])
        else:
            total_acquisition_cost = 0.0

        if total_acquisition_cost <= 0:
            return None

        return distance_covered / total_acquisition_cost

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _percentage(numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return (numerator / denominator) * 100


def get_dashboard_service() -> DashboardAnalyticsService:
    """Build a dashboard analytics service with the active MongoDB database handle."""

    return DashboardAnalyticsService(database=get_database())
