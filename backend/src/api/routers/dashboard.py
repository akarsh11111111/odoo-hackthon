"""Enterprise dashboard analytics routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.schemas.common import build_response
from src.schemas.dashboard import (
    DashboardDriversResponse,
    DashboardExpenseAnalytics,
    DashboardExpensesResponse,
    DashboardFleetAnalytics,
    DashboardFleetResponse,
    DashboardFuelAnalytics,
    DashboardFuelResponse,
    DashboardKPI,
    DashboardKPIResponse,
    DashboardMaintenanceAnalytics,
    DashboardMaintenanceResponse,
    DashboardOverview,
    DashboardOverviewResponse,
    DashboardTripAnalytics,
    DashboardTripsResponse,
)
from src.services.dashboard import DashboardAnalyticsService, get_dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard overview",
    description="Return fleet, driver, trip, fuel, maintenance, and expense KPIs using MongoDB aggregation pipelines.",
)
async def get_dashboard_overview(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardOverviewResponse:
    overview = await dashboard_service.get_overview()
    return build_response(success=True, message="Dashboard overview fetched successfully", data=DashboardOverview(**overview))


@router.get(
    "/fleet",
    response_model=DashboardFleetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get fleet analytics",
    description="Return fleet utilization, status distribution, vehicle-type segmentation, maintenance frequency, and costliest vehicles.",
)
async def get_dashboard_fleet(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardFleetResponse:
    fleet = await dashboard_service.get_fleet()
    return build_response(success=True, message="Fleet analytics fetched successfully", data=DashboardFleetAnalytics(**fleet))


@router.get(
    "/drivers",
    response_model=DashboardDriversResponse,
    status_code=status.HTTP_200_OK,
    summary="Get driver analytics",
    description="Return driver safety distribution, licensure readiness, availability, and top-driver performance summaries.",
)
async def get_dashboard_drivers(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardDriversResponse:
    drivers = await dashboard_service.get_drivers()
    return build_response(success=True, message="Driver analytics fetched successfully", data=drivers)


@router.get(
    "/trips",
    response_model=DashboardTripsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get trip analytics",
    description="Return trip throughput, distance traveled, cargo statistics, and trip-duration aggregates.",
)
async def get_dashboard_trips(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardTripsResponse:
    trips = await dashboard_service.get_trips()
    return build_response(success=True, message="Trip analytics fetched successfully", data=DashboardTripAnalytics(**trips))


@router.get(
    "/maintenance",
    response_model=DashboardMaintenanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get maintenance analytics",
    description="Return maintenance cost, repair-time averages, pending request counts, and vehicle maintenance concentration.",
)
async def get_dashboard_maintenance(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardMaintenanceResponse:
    maintenance = await dashboard_service.get_maintenance()
    return build_response(success=True, message="Maintenance analytics fetched successfully", data=DashboardMaintenanceAnalytics(**maintenance))


@router.get(
    "/fuel",
    response_model=DashboardFuelResponse,
    status_code=status.HTTP_200_OK,
    summary="Get fuel analytics",
    description="Return fuel consumption, cost, price, and efficiency metrics derived from the fuel and trip collections.",
)
async def get_dashboard_fuel(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardFuelResponse:
    fuel = await dashboard_service.get_fuel()
    return build_response(success=True, message="Fuel analytics fetched successfully", data=DashboardFuelAnalytics(**fuel))


@router.get(
    "/expenses",
    response_model=DashboardExpensesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get expense analytics",
    description="Return category breakdowns and monthly expense exposure for fleet cost management.",
)
async def get_dashboard_expenses(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardExpensesResponse:
    expenses = await dashboard_service.get_expenses()
    return build_response(success=True, message="Expense analytics fetched successfully", data=DashboardExpenseAnalytics(**expenses))


@router.get(
    "/kpis",
    response_model=DashboardKPIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get KPI snapshot",
    description="Return a compact KPI set optimized for dashboard cards and embedded views.",
)
async def get_dashboard_kpis(
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    dashboard_service: DashboardAnalyticsService = Depends(get_dashboard_service),
) -> DashboardKPIResponse:
    kpis = await dashboard_service.get_kpis()
    return build_response(success=True, message="KPI snapshot fetched successfully", data=DashboardKPI(**kpis))
