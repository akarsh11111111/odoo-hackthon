"""Enterprise control-plane routes for audit, timeline, notifications, and search."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.dependencies.auth import get_current_active_user, require_role
from src.models.auth import User
from src.schemas.common import build_response
from src.schemas.notification import NotificationListResponse, NotificationMarkReadResponse, NotificationReadAllResponse
from src.schemas.search import GlobalSearchResponse
from src.schemas.timeline import TimelineListResponse
from src.services.audit import AuditLogService, get_audit_service
from src.services.notification import NotificationService, get_notification_service
from src.services.search import GlobalSearchService, get_search_service
from src.services.timeline import TimelineService, get_timeline_service

router = APIRouter(tags=["Enterprise Control Plane"])


@router.get(
    "/timeline",
    response_model=TimelineListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified activity timeline",
    description="Return a unified read-only activity timeline combining audit records and notifications for authorized fleet personnel.",
)
async def get_timeline(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: str | None = Query(default=None),
    entity: str | None = Query(default=None),
    action: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    timeline_service: TimelineService = Depends(get_timeline_service),
) -> TimelineListResponse:
    filters = {
        "user": user,
        "entity_type": entity,
        "action": action,
        "date_from": date_from,
        "date_to": date_to,
    }
    result = await timeline_service.list(page=page, size=size, filters=filters)
    return build_response(success=True, message="Timeline fetched successfully", data=result)


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notifications",
    description="Return notifications for the authenticated user with filtering by unread state, type, and priority.",
)
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_read: bool | None = Query(default=None),
    notification_type: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    filters = {
        "recipient_user_id": str(current_user.id),
        "is_read": is_read,
        "type": notification_type,
        "priority": priority,
    }
    items, total = await notification_service.list(page=page, size=size, filters=filters)
    return build_response(
        success=True,
        message="Notifications fetched successfully",
        data={"items": items, "total": total, "page": page, "size": size},
    )


@router.post(
    "/notifications/read/{notification_id}",
    response_model=NotificationMarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    description="Mark a notification as read for the authenticated user.",
)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationMarkReadResponse:
    notification = await notification_service.mark_read(notification_id)
    if notification is None:
        raise ValueError("Notification not found")
    return build_response(
        success=True,
        message="Notification marked as read",
        data={
            "notification_id": notification["notification_id"],
            "is_read": notification["is_read"],
            "read_at": notification["read_at"],
        },
    )


@router.post(
    "/notifications/read-all",
    response_model=NotificationReadAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Mark every unread notification for the authenticated user as read.",
)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationReadAllResponse:
    updated_count = await notification_service.mark_all_read(recipient_user_id=str(current_user.id))
    return build_response(
        success=True,
        message="Notifications marked as read",
        data={"updated_count": updated_count},
    )


@router.get(
    "/search",
    response_model=GlobalSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search all enterprise entities",
    description="Search vehicles, drivers, trips, maintenance requests, fuel logs, and expenses by name, ID, registration number, license number, trip ID, or maintenance ID.",
)
async def global_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role(FLEET_MANAGER, DISPATCHER, SAFETY_OFFICER, FINANCIAL_ANALYST)),
    search_service: GlobalSearchService = Depends(get_search_service),
) -> GlobalSearchResponse:
    result = await search_service.search(query=query, page=page, size=size)
    return build_response(success=True, message="Search completed successfully", data=result)


@router.get(
    "/audit-logs",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List audit logs",
    description="Return audit records for enterprise governance and operational traceability.",
)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditLogService = Depends(get_audit_service),
) -> dict:
    filters = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "performed_by": str(current_user.id),
    }
    items, total = await audit_service.list(page=page, size=size, filters=filters)
    return build_response(
        success=True,
        message="Audit logs fetched successfully",
        data={"items": items, "total": total, "page": page, "size": size},
    )
