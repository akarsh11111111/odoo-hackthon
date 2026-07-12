from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.driver import DriverStatus
from src.schemas.driver import DriverCreateRequest, DriverUpdateRequest


def test_driver_create_request_validates_enum_and_score_range() -> None:
    payload = DriverCreateRequest(
        license_number="DL-1001",
        first_name="Asha",
        last_name="Patel",
        phone="+15550000001",
        email="asha@example.com",
        address="12 Main Road",
        date_of_birth=date(1990, 5, 20),
        license_expiry=date(2027, 1, 1),
        safety_score=92,
        driver_status=DriverStatus.AVAILABLE,
        region="North",
        documents=["license.pdf"],
        years_of_experience=6,
    )

    assert payload.driver_status == DriverStatus.AVAILABLE
    assert payload.safety_score == 92


def test_driver_update_request_rejects_invalid_score_and_expired_license() -> None:
    with pytest.raises(ValidationError):
        DriverUpdateRequest(safety_score=101)

    with pytest.raises(ValidationError):
        DriverUpdateRequest(license_expiry=date(2020, 1, 1))
