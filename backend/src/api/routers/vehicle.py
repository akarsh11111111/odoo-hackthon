"""Vehicle registry API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.common import build_response
from src.schemas.vehicle import (
    VehicleAvailableResponse,
    VehicleCreateRequest,
    VehicleCreateResponse,
    VehicleDeleteResponse,
    VehicleDetailResponse,
    VehicleListResponse,
    VehicleSearchResponse,
    VehicleUpdateRequest,
    VehicleUpdateResponse,
)
from src.services.vehicle import VehicleService, get_vehicle_service

router = APIRouter(prefix="/vehicles", tags=["Vehicle Registry"])


@router.post(
    "",
    response_model=VehicleCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create vehicle",
    description="Create a new vehicle record in the registry and publish the creation audit entry.",
)
async def create_vehicle(
    payload: VehicleCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleCreateResponse:
    vehicle = await vehicle_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Vehicle created successfully", data=vehicle)


@router.get(
    "",
    response_model=VehicleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List vehicles",
    description="List paginated, sortable, searchable, and filterable vehicles for authorized fleet roles.",
)
async def list_vehicles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    region: str | None = Query(default=None),
    status: VehicleStatus | None = Query(default=None),
    vehicle_type: VehicleType | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleListResponse:
    filters = {
        "region": region,
        "status": status,
        "vehicle_type": vehicle_type,
    }
    result = await vehicle_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Vehicles fetched successfully", data=result)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get vehicle by id",
    description="Return the full vehicle identifier and registry details for the requested record.",
)
async def get_vehicle(
    vehicle_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleDetailResponse:
    vehicle = await vehicle_service.get_by_id(vehicle_id)
    return build_response(success=True, message="Vehicle fetched successfully", data=vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update vehicle",
    description="Update a vehicle record with validation and audit tracking.",
)
async def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleUpdateResponse:
    vehicle = await vehicle_service.update(vehicle_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Vehicle updated successfully", data=vehicle)


@router.delete(
    "/{vehicle_id}",
    response_model=VehicleDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete vehicle",
    description="Soft-delete a vehicle record while preserving the audit trail.",
)
async def delete_vehicle(
    vehicle_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleDeleteResponse:
    result = await vehicle_service.delete(vehicle_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Vehicle deleted successfully", data=result)


@router.get(
    "/search",
    response_model=VehicleSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search vehicles",
    description="Search vehicle records by registration number, name, model, or region.",
)
async def search_vehicles(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleSearchResponse:
    result = await vehicle_service.search(query=query, page=page, size=size)
    return build_response(success=True, message="Vehicle search completed successfully", data=result)


@router.get(
    "/available",
    response_model=VehicleAvailableResponse,
    status_code=status.HTTP_200_OK,
    summary="List available vehicles",
    description="Return the currently available vehicles for dispatch or operations workflows.",
)
async def list_available_vehicles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleAvailableResponse:
    result = await vehicle_service.list_available(page=page, size=size)
    return build_response(success=True, message="Available vehicles fetched successfully", data=result)
