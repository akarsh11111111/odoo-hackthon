"""API router assembly for TransitOps."""

from fastapi import APIRouter

from src.api.routers.auth import router as auth_router
from src.api.routers.control_plane import router as control_plane_router
from src.api.routers.dashboard import router as dashboard_router
from src.api.routers.driver import router as driver_router
from src.api.routers.expense import router as expense_router
from src.api.routers.fuel import router as fuel_router
from src.api.routers.health import router as health_router
from src.api.routers.maintenance import router as maintenance_router
from src.api.routers.reports import router as reports_router
from src.api.routers.trip import router as trip_router
from src.api.routers.vehicle import router as vehicle_router
from src.core.config import get_settings


settings = get_settings()

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(auth_router)
api_router.include_router(vehicle_router)
api_router.include_router(driver_router)
api_router.include_router(trip_router)
api_router.include_router(maintenance_router)
api_router.include_router(fuel_router)
api_router.include_router(expense_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(control_plane_router)
api_router.include_router(health_router)
