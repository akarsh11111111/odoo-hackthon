"""Expense management API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST
from src.dependencies.auth import require_role
from src.models.auth import User
from src.schemas.common import build_response
from src.schemas.expense import (
    ExpenseCreateRequest,
    ExpenseCreateResponse,
    ExpenseDeleteResponse,
    ExpenseDetailResponse,
    ExpenseHistoryResponse,
    ExpenseListResponse,
    ExpenseUpdateRequest,
    ExpenseUpdateResponse,
    ExpenseVehicleResponse,
)
from src.services.expense import ExpenseService, get_expense_service

router = APIRouter(prefix="/expenses", tags=["Fuel & Expense Management"])


@router.post(
    "",
    response_model=ExpenseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create expense",
    description="Create an expense record tied to a vehicle and optional trip for fleet cost tracking.",
)
async def create_expense(
    payload: ExpenseCreateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseCreateResponse:
    expense = await expense_service.create(payload, created_by=str(current_user.id))
    return build_response(success=True, message="Expense created successfully", data=expense)


@router.get(
    "",
    response_model=ExpenseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List expenses",
    description="List paginated expenses with filtering, sorting, and search support.",
)
async def list_expenses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    vehicle_id: str | None = Query(default=None),
    trip_id: str | None = Query(default=None),
    expense_type: str | None = Query(default=None),
    vendor: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseListResponse:
    filters = {
        "vehicle_id": vehicle_id,
        "trip_id": trip_id,
        "expense_type": expense_type,
        "vendor": vendor,
    }
    result = await expense_service.list(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return build_response(success=True, message="Expenses fetched successfully", data=result)


@router.get(
    "/{expense_id}",
    response_model=ExpenseDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get expense by id",
    description="Return a specific expense record and its stored operational context.",
)
async def get_expense(
    expense_id: str,
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseDetailResponse:
    expense = await expense_service.get_by_id(expense_id)
    return build_response(success=True, message="Expense fetched successfully", data=expense)


@router.put(
    "/{expense_id}",
    response_model=ExpenseUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update expense",
    description="Update an expense record while keeping the cost audit trail intact.",
)
async def update_expense(
    expense_id: str,
    payload: ExpenseUpdateRequest,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseUpdateResponse:
    expense = await expense_service.update(expense_id, payload, updated_by=str(current_user.id))
    return build_response(success=True, message="Expense updated successfully", data=expense)


@router.delete(
    "/{expense_id}",
    response_model=ExpenseDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete expense",
    description="Soft-delete an expense while preserving history.",
)
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(require_role(FLEET_MANAGER)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseDeleteResponse:
    result = await expense_service.delete(expense_id, deleted_by=str(current_user.id))
    return build_response(success=True, message="Expense deleted successfully", data=result)


@router.get(
    "/history",
    response_model=ExpenseHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="List expense history",
    description="Return the expense history available for compliance and fleet accounting review.",
)
async def list_expense_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseHistoryResponse:
    result = await expense_service.list_history(page=page, size=size)
    return build_response(success=True, message="Expense history fetched successfully", data=result)


@router.get(
    "/vehicle/{vehicle_id}",
    response_model=ExpenseVehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="List expenses for a vehicle",
    description="Return all expenses tied to a vehicle for operational cost reconciliation.",
)
async def list_expenses_by_vehicle(
    vehicle_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, FINANCIAL_ANALYST)),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseVehicleResponse:
    result = await expense_service.list_by_vehicle(vehicle_id, page=page, size=size)
    return build_response(success=True, message="Vehicle expenses fetched successfully", data=result)
