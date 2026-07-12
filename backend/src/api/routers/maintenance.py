"""Maintenance management API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.models.maintenance import MaintenancePriority, MaintenanceStatus
from src.schemas.common import build_response
from src.schemas.maintenance import (
    MaintenanceActiveResponse,
    MaintenanceApproveRequest,
    MaintenanceApproveResponse,
    MaintenanceCompleteRequest,
    MaintenanceCompleteResponse,
    MaintenanceCreateRequest,
    MaintenanceCreateResponse,
    MaintenanceDeleteResponse,
    MaintenanceDetailResponse,
    MaintenanceHistoryResponse,
    MaintenanceListResponse,
    MaintenanceRejectRequest,
    MaintenanceRejectResponse,
    MaintenanceStartRequest,
    MaintenanceStartResponse,
    MaintenanceUpdateRequest,
    MaintenanceUpdateResponse,
)
from src.services.maintenance import MaintenanceService, get_maintenance_service

router = APIRouter(prefix="/maintenance", tags=["Maintenance Management"])


@router.post(
    "",
    response_model=MaintenanceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create maintenance request",
    description="Create a maintenance request for a vehicle and immediately place the vehicle in shop status.",
)
async def create_maintenance(
    payload: MaintenanceCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceCreateResponse:
    maintenance = await maintenance_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request created successfully", data=maintenance)


@router.get(
    "",
    response_model=MaintenanceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List maintenance requests",
    description="List paginated maintenance requests with filtering, sorting, and search support.",
)
async def list_maintenance(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    status: MaintenanceStatus | None = Query(default=None),
    priority: MaintenancePriority | None = Query(default=None),
    vendor_name: str | None = Query(default=None),
    date: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceListResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "status": status,
        "priority": priority,
        "vendor_name": vendor_name,
    }
    if date:
        filters["scheduled_date"] = date

    result = await maintenance_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Maintenance requests fetched successfully", data=result)


@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get maintenance request by id",
    description="Return the requested maintenance record and all lifecycle details.",
)
async def get_maintenance(
    maintenance_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceDetailResponse:
    maintenance = await maintenance_service.get_by_id(maintenance_id)
    return build_response(success=True, message="Maintenance request fetched successfully", data=maintenance)


@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update maintenance request",
    description="Update a maintenance request while preserving lifecycle rules and audit tracking.",
)
async def update_maintenance(
    maintenance_id: str,
    payload: MaintenanceUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceUpdateResponse:
    maintenance = await maintenance_service.update(maintenance_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request updated successfully", data=maintenance)


@router.delete(
    "/{maintenance_id}",
    response_model=MaintenanceDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete maintenance request",
    description="Soft-delete a maintenance request while preserving the history and audit record.",
)
async def delete_maintenance(
    maintenance_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceDeleteResponse:
    result = await maintenance_service.delete(maintenance_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request deleted successfully", data=result)


@router.post(
    "/{maintenance_id}/approve",
    response_model=MaintenanceApproveResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve maintenance request",
    description="Approve a pending maintenance request and move the corresponding vehicle into the shop queue.",
)
async def approve_maintenance(
    maintenance_id: str,
    payload: MaintenanceApproveRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceApproveResponse:
    maintenance = await maintenance_service.approve(maintenance_id, payload, approved_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request approved successfully", data=maintenance)


@router.post(
    "/{maintenance_id}/reject",
    response_model=MaintenanceRejectResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject maintenance request",
    description="Reject a pending or approved maintenance request and restore the vehicle to availability when appropriate.",
)
async def reject_maintenance(
    maintenance_id: str,
    payload: MaintenanceRejectRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRejectResponse:
    maintenance = await maintenance_service.reject(maintenance_id, payload, rejected_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request rejected successfully", data=maintenance)


@router.post(
    "/{maintenance_id}/start",
    response_model=MaintenanceStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start maintenance work",
    description="Mark an approved maintenance request as in progress and log the work commencement.",
)
async def start_maintenance(
    maintenance_id: str,
    payload: MaintenanceStartRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceStartResponse:
    maintenance = await maintenance_service.start(maintenance_id, payload, started_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request started successfully", data=maintenance)


@router.post(
    "/{maintenance_id}/complete",
    response_model=MaintenanceCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete maintenance work",
    description="Complete a maintenance request, restore vehicle availability, and store repair history.",
)
async def complete_maintenance(
    maintenance_id: str,
    payload: MaintenanceCompleteRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceCompleteResponse:
    maintenance = await maintenance_service.complete(maintenance_id, payload, completed_by=str(current_user.id))
    return build_response(success=True, message="Maintenance request completed successfully", data=maintenance)


@router.get(
    "/active",
    response_model=MaintenanceActiveResponse,
    status_code=status.HTTP_200_OK,
    summary="List active maintenance requests",
    description="Return all active maintenance requests that are still pending, approved, or in progress.",
)
async def list_active_maintenance(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceActiveResponse:
    result = await maintenance_service.list_active(page=page, size=size)
    return build_response(success=True, message="Active maintenance requests fetched successfully", data=result)


@router.get(
    "/history",
    response_model=MaintenanceHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="List maintenance history",
    description="Return completed and rejected maintenance history across the fleet.",
)
async def list_history_maintenance(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    maintenance_service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceHistoryResponse:
    result = await maintenance_service.list_history(page=page, size=size)
    return build_response(success=True, message="Maintenance history fetched successfully", data=result)
