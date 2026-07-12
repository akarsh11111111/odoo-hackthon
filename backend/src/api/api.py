"""API router assembly for TransitOps."""

from fastapi import APIRouter

from src.api.routers.auth import router as auth_router
from src.api.routers.driver import router as driver_router
from src.api.routers.health import router as health_router
from src.api.routers.maintenance import router as maintenance_router
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
api_router.include_router(health_router)
