"""Repository access for the enterprise audit log collection."""

from __future__ import annotations

from typing import Any

from src.core.database import get_database
from src.models.audit import AuditLog, utcnow


class AuditLogRepository:
    """Repository for central audit log records."""

    def __init__(self, database: Any | None = None) -> None:
        self.database = database if database is not None else get_database()

    async def create(self, **log_data: Any) -> AuditLog:
        log_entry = AuditLog(**log_data)
        log_entry.timestamp = log_entry.timestamp or utcnow()
        return await log_entry.insert()

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[AuditLog], int]:
        query = AuditLog.find()
        normalized = filters or {}

        if normalized.get("entity_type"):
            query = query.find(AuditLog.entity_type == str(normalized["entity_type"]))
        if normalized.get("entity_id"):
            query = query.find(AuditLog.entity_id == str(normalized["entity_id"]))
        if normalized.get("action"):
            query = query.find(AuditLog.action == str(normalized["action"]))
        if normalized.get("performed_by"):
            query = query.find(AuditLog.performed_by == str(normalized["performed_by"]))
        if normalized.get("date_from"):
            query = query.find(AuditLog.timestamp >= normalized["date_from"])
        if normalized.get("date_to"):
            query = query.find(AuditLog.timestamp <= normalized["date_to"])

        items = await query.sort(-AuditLog.timestamp).skip(skip).limit(limit).to_list()
        total = await query.count()
        return items, total
