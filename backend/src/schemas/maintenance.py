"""Maintenance management request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.maintenance import MaintenancePriority, MaintenanceStatus, MaintenanceType
from src.schemas.common import APIResponse


class MaintenanceCreateRequest(BaseModel):
    """Payload for creating a maintenance request."""

    vehicle_id: str = Field(min_length=1, examples=["vehicle-1"])
    maintenance_type: MaintenanceType = Field(default=MaintenanceType.REPAIR, examples=[MaintenanceType.REPAIR])
    title: str = Field(min_length=1, examples=["Brake Inspection"])
    description: str = Field(min_length=1, examples=["Inspect and replace front brake pads"])
    priority: MaintenancePriority = Field(default=MaintenancePriority.NORMAL, examples=[MaintenancePriority.HIGH])
    vendor_name: str = Field(min_length=1, examples=["Metro Fleet Services"])
    estimated_cost: float = Field(ge=0, examples=[320.0])
    scheduled_date: date | None = Field(default=None, examples=["2026-07-15"])
    notes: str | None = Field(default=None, examples=["Vehicle inspection required before dispatch"])
    attachments: list[str] = Field(default_factory=list, examples=[["inspection.pdf"]])

    @field_validator("title", "description", "vendor_name", "notes")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class MaintenanceUpdateRequest(BaseModel):
    """Payload for updating an existing maintenance request."""

    maintenance_type: MaintenanceType | None = Field(default=None, examples=[MaintenanceType.REPAIR])
    title: str | None = Field(default=None, min_length=1, examples=["Brake Replacement"])
    description: str | None = Field(default=None, min_length=1, examples=["Replace front axle brake pads"])
    priority: MaintenancePriority | None = Field(default=None, examples=[MaintenancePriority.HIGH])
    vendor_name: str | None = Field(default=None, min_length=1, examples=["Metro Fleet Services"])
    estimated_cost: float | None = Field(default=None, ge=0, examples=[420.0])
    scheduled_date: date | None = Field(default=None, examples=["2026-07-20"])
    notes: str | None = Field(default=None, examples=["Updated service plan"])
    attachments: list[str] | None = Field(default=None, examples=[["inspection.pdf"]])

    @field_validator("title", "description", "vendor_name", "notes")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class MaintenanceApproveRequest(BaseModel):
    """Payload for approving a pending maintenance request."""

    approval_notes: str | None = Field(default=None, examples=["Approved for vendor scheduling"])


class MaintenanceRejectRequest(BaseModel):
    """Payload for rejecting a maintenance request."""

    rejection_reason: str = Field(min_length=1, examples=["Budget approval unavailable"])


class MaintenanceStartRequest(BaseModel):
    """Payload for marking a maintenance request as in progress."""

    current_odometer: int | None = Field(default=None, ge=0, examples=[5100])
    technician_notes: str | None = Field(default=None, examples=["Repair team is on site"])


class MaintenanceCompleteRequest(BaseModel):
    """Payload for completing maintenance work."""

    actual_cost: float = Field(ge=0, examples=[310.0])
    completion_notes: str = Field(min_length=1, examples=["Brake pads replaced and alignment verified"])
    technician_notes: str | None = Field(default=None, examples=["Final inspection passed"])
    final_odometer: int | None = Field(default=None, ge=0, examples=[5150])

    @field_validator("completion_notes", "technician_notes")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class MaintenanceRead(BaseModel):
    """Public maintenance representation returned by the API."""

    id: str
    maintenance_id: str
    vehicle_id: str
    maintenance_type: MaintenanceType
    title: str
    description: str
    priority: MaintenancePriority
    vendor_name: str
    estimated_cost: float
    actual_cost: float | None = None
    scheduled_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: MaintenanceStatus
    notes: str | None = None
    attachments: list[str]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class MaintenanceListResult(BaseModel):
    """Paginated maintenance listing payload."""

    items: list[MaintenanceRead]
    total: int
    page: int
    size: int


MaintenanceCreateResponse = APIResponse[MaintenanceRead]
MaintenanceUpdateResponse = APIResponse[MaintenanceRead]
MaintenanceListResponse = APIResponse[MaintenanceListResult]
MaintenanceDetailResponse = APIResponse[MaintenanceRead]
MaintenanceDeleteResponse = APIResponse[dict[str, str]]
MaintenanceApproveResponse = APIResponse[MaintenanceRead]
MaintenanceRejectResponse = APIResponse[MaintenanceRead]
MaintenanceStartResponse = APIResponse[MaintenanceRead]
MaintenanceCompleteResponse = APIResponse[MaintenanceRead]
MaintenanceActiveResponse = APIResponse[MaintenanceListResult]
MaintenanceHistoryResponse = APIResponse[MaintenanceListResult]
