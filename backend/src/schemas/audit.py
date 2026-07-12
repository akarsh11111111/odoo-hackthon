"""Audit logging API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogRecord(BaseModel):
    """Canonical audit log entry returned by the control-plane API."""

    audit_id: str | None = None
    entity_type: str
    entity_id: str
    action: str
    performed_by: str | None = None
    performed_role: str | None = None
    timestamp: datetime
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class AuditLogListResponse(BaseModel):
    """Paginated list response for audit logs."""

    items: list[AuditLogRecord]
    total: int
    page: int
    size: int


class AuditLogCreateRequest(BaseModel):
    """Audit payload shape emitted by the service layer when a state transition occurs."""

    entity_type: str = Field(..., examples=["vehicles"])
    entity_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    action: str = Field(..., examples=["Vehicle Created"])
    performed_by: str | None = Field(default=None, examples=["user-1"])
    performed_role: str | None = Field(default=None, examples=["Fleet Manager"])
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    ip_address: str | None = Field(default=None, examples=["127.0.0.1"])
    user_agent: str | None = Field(default=None, examples=["Mozilla/5.0"])
