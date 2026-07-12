"""Enterprise audit logging service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.repositories.audit import AuditLogRepository


@dataclass(slots=True)
class AuditLogService:
    """Central audit log writer and reader for the enterprise control-plane."""

    repository: AuditLogRepository

    async def record(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        performed_by: str | None = None,
        performed_role: str | None = None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        created = await self.repository.create(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            performed_by=performed_by,
            performed_role=performed_role,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return self._to_read(created)

    async def list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        skip = (page - 1) * size
        items, total = await self.repository.list(skip=skip, limit=size, filters=filters)
        return [self._to_read(item) for item in items], total

    @staticmethod
    def _to_read(entry: Any) -> dict[str, Any]:
        if isinstance(entry, dict):
            return {
                "audit_id": entry.get("audit_id"),
                "entity_type": entry.get("entity_type"),
                "entity_id": entry.get("entity_id"),
                "action": entry.get("action"),
                "performed_by": entry.get("performed_by"),
                "performed_role": entry.get("performed_role"),
                "timestamp": entry.get("timestamp"),
                "old_value": entry.get("old_value"),
                "new_value": entry.get("new_value"),
                "ip_address": entry.get("ip_address"),
                "user_agent": entry.get("user_agent"),
            }

        return {
            "audit_id": getattr(entry, "audit_id", None),
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "action": entry.action,
            "performed_by": entry.performed_by,
            "performed_role": entry.performed_role,
            "timestamp": entry.timestamp,
            "old_value": entry.old_value,
            "new_value": entry.new_value,
            "ip_address": entry.ip_address,
            "user_agent": entry.user_agent,
        }


def get_audit_service() -> AuditLogService:
    """Build an audit logging service with the active repository dependency."""

    return AuditLogService(repository=AuditLogRepository())
