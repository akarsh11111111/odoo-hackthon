"""Fuel management API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST
from src.dependencies.auth import require_role
from src.models.auth import User
from src.schemas.common import build_response
from src.schemas.fuel import (
    FuelLogCreateRequest,
    FuelLogCreateResponse,
    FuelLogDeleteResponse,
    FuelLogDetailResponse,
    FuelLogHistoryResponse,
    FuelLogListResponse,
    FuelLogUpdateRequest,
    FuelLogUpdateResponse,
    FuelLogVehicleResponse,
)
from src.services.fuel import FuelService, get_fuel_service

router = APIRouter(prefix="/fuel-logs", tags=["Fuel & Expense Management"])


@router.post(
    "",
    response_model=FuelLogCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create fuel log",
    description="Create a fuel consumption record tied to a vehicle, optional trip, and assigned driver.",
)
async def create_fuel_log(
    payload: FuelLogCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogCreateResponse:
    fuel_log = await fuel_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Fuel log created successfully", data=fuel_log)


@router.get(
    "",
    response_model=FuelLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List fuel logs",
    description="List paginated fuel logs with filtering, sorting, and search support.",
)
async def list_fuel_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogListResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "trip_id": trip_id,
        "driver_id": driver_id,
    }
    result = await fuel_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Fuel logs fetched successfully", data=result)


@router.get(
    "/{fuel_log_id}",
    response_model=FuelLogDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get fuel log by id",
    description="Return a specific fuel log record and its available lifecycle context.",
)
async def get_fuel_log(
    fuel_log_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogDetailResponse:
    fuel_log = await fuel_service.get_by_id(fuel_log_id)
    return build_response(success=True, message="Fuel log fetched successfully", data=fuel_log)


@router.put(
    "/{fuel_log_id}",
    response_model=FuelLogUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update fuel log",
    description="Update a fuel log entry while preserving business-rule enforcement and audit history.",
)
async def update_fuel_log(
    fuel_log_id: str,
    payload: FuelLogUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogUpdateResponse:
    fuel_log = await fuel_service.update(fuel_log_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Fuel log updated successfully", data=fuel_log)


@router.delete(
    "/{fuel_log_id}",
    response_model=FuelLogDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete fuel log",
    description="Soft-delete a fuel log while retaining the historical record.",
)
async def delete_fuel_log(
    fuel_log_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogDeleteResponse:
    result = await fuel_service.delete(fuel_log_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Fuel log deleted successfully", data=result)


@router.get(
    "/history",
    response_model=FuelLogHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="List fuel log history",
    description="Return the full fuel history for fleet audit and operational review.",
)
async def list_fuel_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogHistoryResponse:
    result = await fuel_service.list_history(page=page, size=size)
    return build_response(success=True, message="Fuel history fetched successfully", data=result)


@router.get(
    "/vehicle/{vehicle_id}",
    response_model=FuelLogVehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="List fuel logs for a vehicle",
    description="Return all active fuel logs tied to a specific vehicle for review and reconciliation.",
)
async def list_fuel_logs_by_vehicle(
    vehicle_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    fuel_service: FuelService = Depends(get_fuel_service),
) -> FuelLogVehicleResponse:
    result = await fuel_service.list_by_vehicle(vehicle_id, page=page, size=size)
    return build_response(success=True, message="Vehicle fuel logs fetched successfully", data=result)
