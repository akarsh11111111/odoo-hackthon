"""Driver management API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.models.driver import DriverStatus
from src.schemas.common import build_response
from src.schemas.driver import (
    DriverAvailableResponse,
    DriverCreateRequest,
    DriverCreateResponse,
    DriverDeleteResponse,
    DriverDetailResponse,
    DriverListResponse,
    DriverSearchResponse,
    DriverUpdateRequest,
    DriverUpdateResponse,
)
from src.services.driver import DriverService, get_driver_service

router = APIRouter(prefix="/drivers", tags=["Driver Management"])


@router.post(
    "",
    response_model=DriverCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create driver",
    description="Create a new driver record and capture the audit trail for the driver registry.",
)
async def create_driver(
    payload: DriverCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverCreateResponse:
    driver = await driver_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Driver created successfully", data=driver)


@router.get(
    "",
    response_model=DriverListResponse,
    status_code=status.HTTP_200_OK,
    summary="List drivers",
    description="List paginated, sortable, searchable, and filterable drivers for fleet operations.",
)
async def list_drivers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    region: str | None = Query(default=None),
    status: DriverStatus | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverListResponse:
    filters = {"region": region, "status": status}
    result = await driver_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Drivers fetched successfully", data=result)


@router.get(
    "/{driver_id}",
    response_model=DriverDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get driver by id",
    description="Return a specific driver record and its stored registry information.",
)
async def get_driver(
    driver_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverDetailResponse:
    driver = await driver_service.get_by_id(driver_id)
    return build_response(success=True, message="Driver fetched successfully", data=driver)


@router.put(
    "/{driver_id}",
    response_model=DriverUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update driver",
    description="Update an existing driver record with validation and audit behavior.",
)
async def update_driver(
    driver_id: str,
    payload: DriverUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverUpdateResponse:
    driver = await driver_service.update(driver_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Driver updated successfully", data=driver)


@router.delete(
    "/{driver_id}",
    response_model=DriverDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete driver",
    description="Soft-delete the driver record while retaining audit history.",
)
async def delete_driver(
    driver_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverDeleteResponse:
    result = await driver_service.delete(driver_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Driver deleted successfully", data=result)


@router.get(
    "/search",
    response_model=DriverSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search drivers",
    description="Search driver records by license number, name, or region.",
)
async def search_drivers(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverSearchResponse:
    result = await driver_service.search(query=query, page=page, size=size)
    return build_response(success=True, message="Driver search completed successfully", data=result)


@router.get(
    "/available",
    response_model=DriverAvailableResponse,
    status_code=status.HTTP_200_OK,
    summary="List available drivers",
    description="Return the current available driver set for dispatch and assignment workflows.",
)
async def list_available_drivers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    driver_service: DriverService = Depends(get_driver_service),
) -> DriverAvailableResponse:
    result = await driver_service.list_available(page=page, size=size)
    return build_response(success=True, message="Available drivers fetched successfully", data=result)
