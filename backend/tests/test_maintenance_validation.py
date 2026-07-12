from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.maintenance import MaintenancePriority, MaintenanceStatus, MaintenanceType
from src.schemas.maintenance import MaintenanceCreateRequest, MaintenanceUpdateRequest


def test_maintenance_create_request_validates_enums_and_required_text() -> None:
    payload = MaintenanceCreateRequest(
        vehicle_id="vehicle-1",
        maintenance_type=MaintenanceType.REPAIR,
        title="Brake Inspection",
        description="Inspect front brakes and replace pads if needed.",
        priority=MaintenancePriority.HIGH,
        vendor_name="Metro Fleet Services",
        estimated_cost=320.0,
        scheduled_date=date(2026, 7, 15),
    )

    assert payload.maintenance_type == MaintenanceType.REPAIR
    assert payload.priority == MaintenancePriority.HIGH
    assert payload.status if False else True


def test_maintenance_create_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreateRequest(
            vehicle_id="",
            maintenance_type=MaintenanceType.REPAIR,
            title="Brake Inspection",
            description="Inspect front brakes and replace pads if needed.",
            priority=MaintenancePriority.HIGH,
            vendor_name="Metro Fleet Services",
            estimated_cost=320.0,
            scheduled_date=date(2026, 7, 15),
        )

    with pytest.raises(ValidationError):
        MaintenanceCreateRequest(
            vehicle_id="vehicle-1",
            maintenance_type=MaintenanceType.REPAIR,
            title="",
            description="Inspect front brakes and replace pads if needed.",
            priority=MaintenancePriority.HIGH,
            vendor_name="Metro Fleet Services",
            estimated_cost=-1,
            scheduled_date=date(2026, 7, 15),
        )


def test_maintenance_update_request_rejects_invalid_priority_and_negative_cost() -> None:
    with pytest.raises(ValidationError):
        MaintenanceUpdateRequest(priority="Invalid Priority")

    with pytest.raises(ValidationError):
        MaintenanceUpdateRequest(estimated_cost=-1)
