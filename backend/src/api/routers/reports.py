"""Read-only reports and exports API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.schemas.common import build_response
from src.schemas.reports import (
    DriverReportResponse,
    ExpenseReportResponse,
    FinancialReportResponse,
    FleetReportResponse,
    FuelReportResponse,
    MaintenanceReportResponse,
    SummaryReportResponse,
    TripReportResponse,
    UtilizationReportResponse,
)
from src.services.reports import ExportService, ReportsService, get_export_service, get_reports_service

router = APIRouter(prefix="/reports", tags=["Reports & Export"])


@router.get(
    "/fleet",
    response_model=FleetReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Fleet utilization report",
    description="Return a paginated fleet utilization report with reusable aggregation logic and optional filters.",
)
async def get_fleet_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> FleetReportResponse:
    filters = {
        "status": status,
        "department": department,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_fleet(filters=filters, page=page, size=size)
    return build_response(success=True, message="Fleet report fetched successfully", data=result)


@router.get(
    "/drivers",
    response_model=DriverReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Driver performance report",
    description="Return paginated driver performance metrics with optional filters for department, status, and date windows.",
)
async def get_driver_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> DriverReportResponse:
    filters = {
        "status": status,
        "department": department,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_drivers(filters=filters, page=page, size=size)
    return build_response(success=True, message="Driver report fetched successfully", data=result)


@router.get(
    "/trips",
    response_model=TripReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Trip performance report",
    description="Return paginated trip performance metrics using reusable aggregation pipelines and filters.",
)
async def get_trip_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> TripReportResponse:
    filters = {
        "status": status,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_trips(filters=filters, page=page, size=size)
    return build_response(success=True, message="Trip report fetched successfully", data=result)


@router.get(
    "/maintenance",
    response_model=MaintenanceReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Maintenance report",
    description="Return paginated maintenance records and cost summaries filtered by type, status, and date window.",
)
async def get_maintenance_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> MaintenanceReportResponse:
    filters = {
        "status": status,
        "maintenance_type": maintenance_type,
        "vehicle_id": vehicle_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_maintenance(filters=filters, page=page, size=size)
    return build_response(success=True, message="Maintenance report fetched successfully", data=result)


@router.get(
    "/fuel",
    response_model=FuelReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Fuel consumption report",
    description="Return paginated fuel consumption records with filtering by vehicle, driver, trip, fuel type, and date window.",
)
async def get_fuel_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    fuel_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> FuelReportResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "fuel_type": fuel_type,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_fuel(filters=filters, page=page, size=size)
    return build_response(success=True, message="Fuel report fetched successfully", data=result)


@router.get(
    "/expenses",
    response_model=ExpenseReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Expense report",
    description="Return paginated expense records and category totals filtered by expense type, vehicle, trip, and date range.",
)
async def get_expense_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> ExpenseReportResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "expense_type": expense_type,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_expenses(filters=filters, page=page, size=size)
    return build_response(success=True, message="Expense report fetched successfully", data=result)


@router.get(
    "/financial",
    response_model=FinancialReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Financial summary report",
    description="Return a read-only financial summary that aggregates fuel, maintenance, and expense costs for the provided filters.",
)
async def get_financial_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    fuel_type: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> FinancialReportResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "expense_type": expense_type,
        "fuel_type": fuel_type,
        "maintenance_type": maintenance_type,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_financial(filters=filters, page=page, size=size)
    return build_response(success=True, message="Financial report fetched successfully", data=result)


@router.get(
    "/utilization",
    response_model=UtilizationReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Fleet utilization report",
    description="Return fleet utilization summary and ancillary fleet state metrics on a reusable read-only basis.",
)
async def get_utilization_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> UtilizationReportResponse:
    filters = {
        "status": status,
        "department": department,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_utilization(filters=filters, page=page, size=size)
    return build_response(success=True, message="Utilization report fetched successfully", data=result)


@router.get(
    "/summary",
    response_model=SummaryReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Operational summary report",
    description="Return an enterprise summary view with operational KPIs for the filtered reporting window.",
)
async def get_summary_report(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    department: str | None = Query(default=None),
    status: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    fuel_type: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    reports_service: ReportsService = Depends(get_reports_service),
) -> SummaryReportResponse:
    filters = {
        "department": department,
        "status": status,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "expense_type": expense_type,
        "fuel_type": fuel_type,
        "maintenance_type": maintenance_type,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await reports_service.get_summary(filters=filters, page=page, size=size)
    return build_response(success=True, message="Operational summary fetched successfully", data=result)


@router.get(
    "/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Export a report as CSV",
    description="Stream a CSV version of a supported report while preserving read-only semantics and large-dataset efficiency.",
)
async def export_csv_report(
    report_name: str = Query(..., description="Report name to export such as fleet, drivers, trips, maintenance, fuel, expenses, financial, utilization, or summary"),
    page: int = Query(1, ge=1),
    size: int = Query(1000, ge=1, le=5000),
    status: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    fuel_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    export_service: ExportService = Depends(get_export_service),
) -> Response:
    filters = {
        "status": status,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "department": department,
        "expense_type": expense_type,
        "maintenance_type": maintenance_type,
        "fuel_type": fuel_type,
        "date_from": date_from,
        "date_to": date_to,
    }
    return await export_service.export_csv(report_name=report_name, filters=filters, page=page, size=size)


@router.get(
    "/export/excel",
    status_code=status.HTTP_200_OK,
    summary="Export a report as Excel",
    description="Stream an Excel workbook export for a supported report while preserving read-only semantics and large-dataset efficiency.",
)
async def export_excel_report(
    report_name: str = Query(..., description="Report name to export such as fleet, drivers, trips, maintenance, fuel, expenses, financial, utilization, or summary"),
    page: int = Query(1, ge=1),
    size: int = Query(1000, ge=1, le=5000),
    status: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    maintenance_type: str | None = Query(default=None),
    fuel_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER, DISPATCHER)),
    export_service: ExportService = Depends(get_export_service),
) -> Response:
    filters = {
        "status": status,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "department": department,
        "expense_type": expense_type,
        "maintenance_type": maintenance_type,
        "fuel_type": fuel_type,
        "date_from": date_from,
        "date_to": date_to,
    }
    return await export_service.export_excel(report_name=report_name, filters=filters, page=page, size=size)
