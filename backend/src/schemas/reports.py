"""Read-only report response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.schemas.common import APIResponse


class ReportListResult(BaseModel):
    """Shared paginated reporting shape used by read-only report endpoints."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    size: int = Field(default=20)
    summary: dict[str, Any] = Field(default_factory=dict)


FleetReportResponse = APIResponse[ReportListResult]
DriverReportResponse = APIResponse[ReportListResult]
TripReportResponse = APIResponse[ReportListResult]
MaintenanceReportResponse = APIResponse[ReportListResult]
FuelReportResponse = APIResponse[ReportListResult]
ExpenseReportResponse = APIResponse[ReportListResult]
FinancialReportResponse = APIResponse[ReportListResult]
UtilizationReportResponse = APIResponse[ReportListResult]
SummaryReportResponse = APIResponse[ReportListResult]
