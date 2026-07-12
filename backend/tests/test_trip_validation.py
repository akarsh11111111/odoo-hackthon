from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.trip import TripPriority, TripStatus
from src.schemas.trip import TripCreateRequest, TripUpdateRequest


def test_trip_create_request_validates_status_and_priority() -> None:
    payload = TripCreateRequest(
        vehicle_id="vehicle-1",
        driver_id="driver-1",
        source="Hub A",
        destination="Hub B",
        cargo_description="Medical supplies",
        cargo_weight=5000.0,
        estimated_distance=140.0,
        estimated_duration=180,
        dispatch_time=datetime(2026, 7, 12, 8, 0, tzinfo=timezone.utc),
        expected_arrival=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc),
        priority=TripPriority.HIGH,
        status=TripStatus.DRAFT,
    )

    assert payload.priority == TripPriority.HIGH
    assert payload.status == TripStatus.DRAFT


def test_trip_update_request_rejects_invalid_priority_and_time_window() -> None:
    with pytest.raises(ValidationError):
        TripUpdateRequest(priority="Invalid Priority")

    with pytest.raises(ValidationError):
        TripUpdateRequest(dispatch_time=datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc), expected_arrival=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc))
