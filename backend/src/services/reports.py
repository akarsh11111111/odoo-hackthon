"""Read-only reports and export service for the TransitOps analytics domain."""

from __future__ import annotations

import csv
import io
import zipfile
from datetime import date, datetime, time, timezone
from typing import Any, Iterator

from bson import ObjectId
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_database
from src.services.dashboard import DashboardAnalyticsService


class ReportsService:
    """Enterprise report generation service built on MongoDB aggregation pipelines."""

    def __init__(
        self,
        database: AsyncIOMotorDatabase | Any | None = None,
        dashboard_service: DashboardAnalyticsService | None = None,
    ) -> None:
        self.database = database if database is not None else get_database()
        self.dashboard_service = dashboard_service or DashboardAnalyticsService(database=self.database)

    async def get_fleet(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_vehicle_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "vehicles",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("vehicles", match)
        summary = await self._aggregate(
            "vehicles",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_vehicles": {"$sum": 1},
                        "available_vehicles": {"$sum": {"$cond": [{"$eq": ["$status", "Available"]}, 1, 0]}},
                        "on_trip_vehicles": {"$sum": {"$cond": [{"$eq": ["$status", "On Trip"]}, 1, 0]}},
                        "vehicles_in_shop": {"$sum": {"$cond": [{"$eq": ["$status", "In Shop"]}, 1, 0]}},
                        "average_load_capacity": {"$avg": {"$ifNull": ["$maximum_load_capacity", 0]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_drivers(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_driver_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "drivers",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("drivers", match)
        summary = await self._aggregate(
            "drivers",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_drivers": {"$sum": 1},
                        "available_drivers": {"$sum": {"$cond": [{"$eq": ["$driver_status", "Available"]}, 1, 0]}},
                        "drivers_on_trip": {"$sum": {"$cond": [{"$eq": ["$driver_status", "On Trip"]}, 1, 0]}},
                        "drivers_suspended": {"$sum": {"$cond": [{"$eq": ["$driver_status", "Suspended"]}, 1, 0]}},
                        "average_safety_score": {"$avg": {"$ifNull": ["$safety_score", 0]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_trips(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "dispatch_time",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_trip_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "trips",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("trips", match)
        summary = await self._aggregate(
            "trips",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_trips": {"$sum": 1},
                        "completed": {"$sum": {"$cond": [{"$eq": ["$status", "Completed"]}, 1, 0]}},
                        "cancelled": {"$sum": {"$cond": [{"$eq": ["$status", "Cancelled"]}, 1, 0]}},
                        "dispatched": {"$sum": {"$cond": [{"$eq": ["$status", "Dispatched"]}, 1, 0]}},
                        "distance_covered": {"$sum": {"$ifNull": ["$actual_distance", "$estimated_distance"]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_maintenance(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "scheduled_date",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_maintenance_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "maintenance_requests",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("maintenance_requests", match)
        summary = await self._aggregate(
            "maintenance_requests",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "pending": {"$sum": {"$cond": [{"$eq": ["$status", "Pending"]}, 1, 0]}},
                        "completed": {"$sum": {"$cond": [{"$eq": ["$status", "Completed"]}, 1, 0]}},
                        "estimated_cost": {"$sum": {"$ifNull": ["$estimated_cost", 0]}},
                        "actual_cost": {"$sum": {"$ifNull": ["$actual_cost", 0]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_fuel(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "fuel_date",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_fuel_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "fuel_logs",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("fuel_logs", match)
        summary = await self._aggregate(
            "fuel_logs",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_logs": {"$sum": 1},
                        "fuel_cost": {"$sum": {"$ifNull": ["$total_cost", 0]}},
                        "liters": {"$sum": {"$ifNull": ["$liters", 0]}},
                        "average_price": {"$avg": {"$ifNull": ["$price_per_liter", 0]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_expenses(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        match = self._build_expense_match(filters)
        skip = (page - 1) * size
        items = await self._aggregate(
            "expenses",
            [
                {"$match": match},
                {"$sort": {sort_by: 1 if sort_order == "asc" else -1}},
                {"$skip": skip},
                {"$limit": size},
            ],
        )
        total = await self._count("expenses", match)
        summary = await self._aggregate(
            "expenses",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_expenses": {"$sum": 1},
                        "expense_amount": {"$sum": {"$ifNull": ["$amount", 0]}},
                    }
                },
            ],
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "summary": summary[0] if summary else {},
        }

    async def get_financial(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        filters = filters or {}
        expense_match = self._build_expense_match(filters)
        fuel_match = self._build_fuel_match(filters)
        maintenance_match = self._build_maintenance_match(filters)

        expense_total = await self._sum_numeric_value("expenses", "amount", match=expense_match)
        fuel_total = await self._sum_numeric_value("fuel_logs", "total_cost", match=fuel_match)
        maintenance_total = await self._sum_numeric_value(
            "maintenance_requests",
            "actual_cost",
            match=maintenance_match,
        )
        estimated_maintenance_total = await self._sum_numeric_value(
            "maintenance_requests",
            "estimated_cost",
            match=maintenance_match,
        )

        return {
            "items": [],
            "total": 0,
            "page": page,
            "size": size,
            "summary": {
                "fuel_cost": fuel_total,
                "expense_cost": expense_total,
                "maintenance_cost": maintenance_total or estimated_maintenance_total,
                "operational_cost": fuel_total + expense_total + (maintenance_total or estimated_maintenance_total),
            },
        }

    async def get_utilization(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        filters = filters or {}
        match = self._build_vehicle_match(filters)
        utilization = await self._aggregate(
            "vehicles",
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "total_vehicles": {"$sum": 1},
                        "active_vehicles": {
                            "$sum": {
                                "$cond": [{"$in": ["$status", ["Available", "On Trip"]]}, 1, 0]
                            }
                        },
                    }
                },
            ],
        )
        util_value = utilization[0] if utilization else {}
        return {
            "items": [],
            "total": util_value.get("total_vehicles", 0),
            "page": page,
            "size": size,
            "summary": {
                "fleet_utilization_percent": round(
                    ((util_value.get("active_vehicles", 0) / util_value.get("total_vehicles", 0)) * 100)
                    if util_value.get("total_vehicles", 0)
                    else 0.0,
                    2,
                )
            },
        }

    async def get_summary(
        self,
        *,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        filters = filters or {}
        vehicle_match = self._build_vehicle_match(filters)
        driver_match = self._build_driver_match(filters)
        trip_match = self._build_trip_match(filters)
        maintenance_match = self._build_maintenance_match(filters)
        fuel_match = self._build_fuel_match(filters)
        expense_match = self._build_expense_match(filters)

        total_vehicles = await self._count("vehicles", vehicle_match)
        total_drivers = await self._count("drivers", driver_match)
        total_active_trips = await self._count("trips", trip_match)
        fuel_cost = await self._sum_numeric_value("fuel_logs", "total_cost", match=fuel_match)
        maintenance_cost = await self._sum_numeric_value(
            "maintenance_requests",
            "actual_cost",
            match=maintenance_match,
        )
        expense_cost = await self._sum_numeric_value("expenses", "amount", match=expense_match)

        overview = await self.dashboard_service.get_overview()
        return {
            "total_vehicles": total_vehicles,
            "total_drivers": total_drivers,
            "total_active_trips": total_active_trips,
            "fuel_cost": fuel_cost,
            "maintenance_cost": maintenance_cost,
            "expense_cost": expense_cost,
            "operational_cost": fuel_cost + maintenance_cost + expense_cost,
            "fleet_utilization_percent": overview.get("fleet_utilization_percent"),
            "average_fuel_efficiency": overview.get("average_fuel_efficiency"),
            "vehicle_roi": overview.get("vehicle_roi"),
            "items": [],
            "page": page,
            "size": size,
            "total": total_vehicles,
        }

    async def _aggregate(self, collection_name: str, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        collection = self.database.get_collection(collection_name)
        return await collection.aggregate(pipeline).to_list(length=None)

    async def _count(self, collection_name: str, match: dict[str, Any]) -> int:
        result = await self._aggregate(
            collection_name,
            [
                {"$match": match},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
            ],
        )
        if not result:
            return 0
        first = result[0]
        if "count" in first:
            return int(first["count"])
        if "value" in first:
            return int(first["value"])

        field_map = {
            "vehicles": ("total_vehicles",),
            "drivers": ("total_drivers",),
            "trips": ("total_active_trips", "total_trips"),
            "maintenance_requests": ("total_requests",),
            "fuel_logs": ("total_logs",),
            "expenses": ("total_expenses",),
        }
        for candidate in field_map.get(collection_name, ()):
            if candidate in first:
                return int(first[candidate])
        return len(result)

    async def _sum_numeric_value(
        self,
        collection_name: str,
        field_name: str,
        *,
        match: dict[str, Any] | None = None,
    ) -> float:
        pipeline: list[dict[str, Any]] = [{"$match": match}] if match else []
        pipeline.append({"$group": {"_id": None, "value": {"$sum": {"$ifNull": [f"${field_name}", 0]}}}})
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

    def _normalize_filters(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        if not filters:
            return cleaned
        for key, value in filters.items():
            if value in (None, "", [], {}):
                continue
            cleaned[key] = value
        return cleaned

    def _build_vehicle_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("vehicle_id"):
            match["vehicle_id"] = self._coerce_object_id(cleaned["vehicle_id"])
        if cleaned.get("department"):
            match["region"] = cleaned["department"]
        if cleaned.get("status"):
            match["status"] = cleaned["status"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("vehicles", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _build_driver_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("driver_id"):
            match["_id"] = self._coerce_object_id(cleaned["driver_id"])
        if cleaned.get("department"):
            match["region"] = cleaned["department"]
        if cleaned.get("status"):
            match["driver_status"] = cleaned["status"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("drivers", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _build_trip_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("trip_id"):
            match["_id"] = self._coerce_object_id(cleaned["trip_id"])
        if cleaned.get("vehicle_id"):
            match["vehicle_id"] = self._coerce_object_id(cleaned["vehicle_id"])
        if cleaned.get("driver_id"):
            match["driver_id"] = self._coerce_object_id(cleaned["driver_id"])
        if cleaned.get("status"):
            match["status"] = cleaned["status"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("trips", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _build_maintenance_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("vehicle_id"):
            match["vehicle_id"] = self._coerce_object_id(cleaned["vehicle_id"])
        if cleaned.get("maintenance_type"):
            match["maintenance_type"] = cleaned["maintenance_type"]
        if cleaned.get("status"):
            match["status"] = cleaned["status"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("maintenance_requests", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _build_fuel_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("vehicle_id"):
            match["vehicle_id"] = self._coerce_object_id(cleaned["vehicle_id"])
        if cleaned.get("driver_id"):
            match["driver_id"] = self._coerce_object_id(cleaned["driver_id"])
        if cleaned.get("trip_id"):
            match["trip_id"] = self._coerce_object_id(cleaned["trip_id"])
        if cleaned.get("fuel_type"):
            match["fuel_type"] = cleaned["fuel_type"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("fuel_logs", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _build_expense_match(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        cleaned = self._normalize_filters(filters)
        match: dict[str, Any] = {}
        if cleaned.get("vehicle_id"):
            match["vehicle_id"] = self._coerce_object_id(cleaned["vehicle_id"])
        if cleaned.get("driver_id"):
            match["driver_id"] = self._coerce_object_id(cleaned["driver_id"])
        if cleaned.get("trip_id"):
            match["trip_id"] = self._coerce_object_id(cleaned["trip_id"])
        if cleaned.get("expense_type"):
            match["expense_type"] = cleaned["expense_type"]
        if cleaned.get("date_from") or cleaned.get("date_to"):
            match.update(self._date_match("expenses", cleaned.get("date_from"), cleaned.get("date_to")))
        return match

    def _date_match(self, collection_name: str, date_from: Any, date_to: Any) -> dict[str, Any]:
        field_map = {
            "vehicles": "created_at",
            "drivers": "created_at",
            "trips": "dispatch_time",
            "maintenance_requests": "scheduled_date",
            "fuel_logs": "fuel_date",
            "expenses": "expense_date",
        }
        field = field_map.get(collection_name, "created_at")
        match: dict[str, Any] = {}
        if date_from:
            date_from_value = self._coerce_date_value(date_from)
            match[field] = {"$gte": date_from_value}
        if date_to:
            date_to_value = self._coerce_date_value(date_to)
            if field in {"dispatch_time", "created_at"}:
                date_to_value = datetime.combine(date_to_value, time.max, tzinfo=timezone.utc)
            if field in {"scheduled_date", "fuel_date", "expense_date"}:
                date_to_value = date_to_value
            if field in match:
                match[field]["$lte"] = date_to_value
            else:
                match[field] = {"$lte": date_to_value}
        return match

    @staticmethod
    def _coerce_object_id(value: Any) -> ObjectId | Any:
        try:
            return ObjectId(str(value))
        except Exception:
            return value

    @staticmethod
    def _coerce_date_value(value: Any) -> date | datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        return value


class ExportService:
    """Streaming CSV and Excel exports for the read-only reports domain."""

    def __init__(self, database: AsyncIOMotorDatabase | Any | None = None) -> None:
        self.database = database if database is not None else get_database()
        self.reports_service = ReportsService(database=self.database)

    async def export_csv(
        self,
        *,
        report_name: str,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 1000,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> StreamingResponse:
        rows = await self._get_rows(report_name=report_name, filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
        headers = list(rows[0].keys()) if rows else self._headers_for_report(report_name)

        def stream_csv() -> Iterator[bytes]:
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            yield buffer.getvalue().encode("utf-8")
            for row in rows:
                buffer.seek(0)
                buffer.truncate(0)
                writer.writerow({header: row.get(header, "") for header in headers})
                yield buffer.getvalue().encode("utf-8")

        return StreamingResponse(
            stream_csv(),
            media_type="text/csv",
            headers={"content-disposition": f"attachment; filename={report_name}.csv"},
        )

    async def export_excel(
        self,
        *,
        report_name: str,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 1000,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> StreamingResponse:
        rows = await self._get_rows(report_name=report_name, filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
        headers = list(rows[0].keys()) if rows else self._headers_for_report(report_name)
        workbook_bytes = self._build_xlsx(headers=headers, rows=rows)

        async def stream_excel() -> Iterator[bytes]:
            yield workbook_bytes

        return StreamingResponse(
            stream_excel(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"content-disposition": f"attachment; filename={report_name}.xlsx"},
        )

    async def _get_rows(
        self,
        *,
        report_name: str,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        size: int = 1000,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[dict[str, Any]]:
        report_name = report_name.lower()
        if report_name == "fleet":
            result = await self.reports_service.get_fleet(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "drivers":
            result = await self.reports_service.get_drivers(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "trips":
            result = await self.reports_service.get_trips(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "maintenance":
            result = await self.reports_service.get_maintenance(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "fuel":
            result = await self.reports_service.get_fuel(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "expenses":
            result = await self.reports_service.get_expenses(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "financial":
            result = await self.reports_service.get_financial(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "utilization":
            result = await self.reports_service.get_utilization(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        if report_name == "summary":
            result = await self.reports_service.get_summary(filters=filters, page=page, size=size, sort_by=sort_by, sort_order=sort_order)
            return result["items"]
        raise ValueError("Unsupported report name")

    @staticmethod
    def _headers_for_report(report_name: str) -> list[str]:
        return ["id", "status"] if report_name == "fleet" else ["id", "created_at"]

    @staticmethod
    def _build_xlsx(*, headers: list[str], rows: list[dict[str, Any]]) -> bytes:
        workbook = io.BytesIO()
        with zipfile.ZipFile(workbook, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", ExportService._content_types_xml())
            archive.writestr("_rels/.rels", ExportService._root_relationships_xml())
            archive.writestr("xl/workbook.xml", ExportService._workbook_xml())
            archive.writestr("xl/_rels/workbook.xml.rels", ExportService._workbook_relationships_xml())
            archive.writestr("xl/worksheets/sheet1.xml", ExportService._worksheet_xml(headers=headers, rows=rows))
            archive.writestr("xl/styles.xml", ExportService._styles_xml())
        return workbook.getvalue()

    @staticmethod
    def _content_types_xml() -> str:
        return """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
  <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
  <Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>
</Types>"""

    @staticmethod
    def _root_relationships_xml() -> str:
        return """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>"""

    @staticmethod
    def _workbook_xml() -> str:
        return """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"Report\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
</workbook>"""

    @staticmethod
    def _workbook_relationships_xml() -> str:
        return """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
  <Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>
</Relationships>"""

    @staticmethod
    def _styles_xml() -> str:
        return """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <fonts count=\"1\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>
  <fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>
  <borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>
  <cellXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/></cellXfs>
</styleSheet>"""

    @staticmethod
    def _worksheet_xml(*, headers: list[str], rows: list[dict[str, Any]]) -> str:
        sheet_rows = [
            ["<row r=\"1\">"] + [f"<c r=\"{chr(65 + idx)}1\" t=\"inlineStr\"><is><t>{ExportService._escape_cell(header)}</t></is></c>" for idx, header in enumerate(headers)] + ["</row>"]
        ]
        for row_idx, row in enumerate(rows, start=2):
            cells = []
            for header_idx, header in enumerate(headers):
                value = row.get(header, "")
                cells.append(
                    f"<c r=\"{chr(65 + header_idx)}{row_idx}\" t=\"inlineStr\"><is><t>{ExportService._escape_cell(str(value))}</t></is></c>"
                )
            sheet_rows.append([f"<row r=\"{row_idx}\">"] + cells + ["</row>"])
        rows_xml = "".join("".join(row) for row in sheet_rows)
        return f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheetData>{rows_xml}</sheetData>
</worksheet>"""

    @staticmethod
    def _escape_cell(value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_reports_service() -> ReportsService:
    """Build a reports service with the active MongoDB database handle."""

    return ReportsService(database=get_database())


def get_export_service() -> ExportService:
    """Build an export service with the active MongoDB database handle."""

    return ExportService(database=get_database())
