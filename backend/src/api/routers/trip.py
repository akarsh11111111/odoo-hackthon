"""Trip management API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import require_role
from src.models.auth import User
from src.models.trip import TripPriority, TripStatus
from src.schemas.common import build_response
from src.schemas.trip import (
    TripActiveResponse,
    TripCancelResponse,
    TripCompleteRequest,
    TripCompleteResponse,
    TripCreateRequest,
    TripCreateResponse,
    TripDeleteResponse,
    TripDetailResponse,
    TripDispatchRequest,
    TripDispatchResponse,
    TripHistoryResponse,
    TripListResponse,
    TripUpdateRequest,
    TripUpdateResponse,
)
from src.services.trip import TripService, get_trip_service

router = APIRouter(prefix="/trips", tags=["Trip Management"])


@router.post(
    "",
    response_model=TripCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create trip",
    description="Create a new trip record in the logistics engine.",
)
async def create_trip(
    payload: TripCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripCreateResponse:
    trip = await trip_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Trip created successfully", data=trip)


@router.get(
    "",
    response_model=TripListResponse,
    status_code=status.HTTP_200_OK,
    summary="List trips",
    description="List paginated, searchable, and filterable trips for authorized fleet operations.",
)
async def list_trips(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: TripStatus | None = Query(default=None),
    priority: TripPriority | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripListResponse:
    filters = {
        "status": status,
        "priority": priority,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
    }
    result = await trip_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Trips fetched successfully", data=result)


@router.get(
    "/{trip_id}",
    response_model=TripDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get trip by id",
    description="Return a specific trip record for operations or analytics workflows.",
)
async def get_trip(
    trip_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    trip = await trip_service.get_by_id(trip_id)
    return build_response(success=True, message="Trip fetched successfully", data=trip)


@router.put(
    "/{trip_id}",
    response_model=TripUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update trip",
    description="Update a draft or in-flight trip record with lifecycle protections.",
)
async def update_trip(
    trip_id: str,
    payload: TripUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripUpdateResponse:
    trip = await trip_service.update(trip_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Trip updated successfully", data=trip)


@router.delete(
    "/{trip_id}",
    response_model=TripDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete trip",
    description="Soft cancel a trip record to preserve lifecycle history.",
)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDeleteResponse:
    result = await trip_service.delete(trip_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Trip deleted successfully", data=result)


@router.post(
    "/{trip_id}/dispatch",
    response_model=TripDispatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Dispatch trip",
    description="Dispatch an assigned trip and transition its vehicle and driver to the on-trip state.",
)
async def dispatch_trip(
    trip_id: str,
    payload: TripDispatchRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDispatchResponse:
    trip = await trip_service.dispatch(trip_id, payload, dispatched_by=str(current_user.id))
    return build_response(success=True, message="Trip dispatched successfully", data=trip)


@router.post(
    "/{trip_id}/complete",
    response_model=TripCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete trip",
    description="Complete a dispatched trip and restore the vehicle and driver to available status.",
)
async def complete_trip(
    trip_id: str,
    payload: TripCompleteRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripCompleteResponse:
    trip = await trip_service.complete(trip_id, payload, completed_by=str(current_user.id))
    return build_response(success=True, message="Trip completed successfully", data=trip)


@router.post(
    "/{trip_id}/cancel",
    response_model=TripCancelResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel trip",
    description="Cancel an active trip, restore fleet availability, and retain the cancellation reason.",
)
async def cancel_trip(
    trip_id: str,
    cancellation_reason: str | None = Query(default=None),
    current_user: User = Depends(require_role(FLEET_MANAGER, DISPATCHER)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripCancelResponse:
    trip = await trip_service.cancel(trip_id, cancellation_reason=cancellation_reason, cancelled_by=str(current_user.id))
    return build_response(success=True, message="Trip cancelled successfully", data=trip)


@router.get(
    "/active",
    response_model=TripActiveResponse,
    status_code=status.HTTP_200_OK,
    summary="List active trips",
    description="Return currently dispatched trips in the active logistics queue.",
)
async def list_active_trips(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripActiveResponse:
    result = await trip_service.list_active(page=page, size=size)
    return build_response(success=True, message="Active trips fetched successfully", data=result)


@router.get(
    "/history",
    response_model=TripHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="List trip history",
    description="Return completed and cancelled trip history for analytics and audit review.",
)
async def list_trip_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    trip_service: TripService = Depends(get_trip_service),
) -> TripHistoryResponse:
    result = await trip_service.list_history(page=page, size=size)
    return build_response(success=True, message="Trip history fetched successfully", data=result)
