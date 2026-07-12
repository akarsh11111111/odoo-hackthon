from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.vehicle import VehicleStatus, VehicleType
from src.schemas.vehicle import VehicleCreateRequest, VehicleUpdateRequest


def test_vehicle_create_request_validates_enum_and_positive_numbers() -> None:
    payload = VehicleCreateRequest(
        registration_number="ABC-123",
        vehicle_name="Mini Bus",
        vehicle_model="Volvo 9700",
        vehicle_type=VehicleType.BUS,
        maximum_load_capacity=5000,
        current_odometer=1000,
        acquisition_cost=90000.0,
        purchase_date=date(2023, 1, 1),
        status=VehicleStatus.AVAILABLE,
        region="Central",
        documents=["insurance.pdf"],
    )

    assert payload.status == VehicleStatus.AVAILABLE
    assert payload.vehicle_type == VehicleType.BUS


def test_vehicle_update_request_rejects_negative_cost_and_decreasing_odometer() -> None:
    with pytest.raises(ValidationError):
        VehicleUpdateRequest(acquisition_cost=-1)

    with pytest.raises(ValidationError):
        VehicleUpdateRequest(previous_odometer=5000, current_odometer=4999)
