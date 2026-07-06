"""Tests for deterministic calendar day classification (pure domain)."""

import pytest

from bookings.domain.calendar import (
    REASON_DAY_CAPACITY_REACHED,
    REASON_NO_OPEN_TIMES,
    REASON_STUDIO_CLOSED,
    REASON_WRONG_DAY_TYPE,
    STATUS_AVAILABLE,
    STATUS_CAPACITY_FULL,
    STATUS_CLOSED,
    STATUS_NOT_OFFERED,
    STATUS_NO_SLOTS,
    classify_calendar_day,
)


@pytest.mark.parametrize(
    ("selection_type", "normal_allowed", "package_allowed", "expected_status", "reason"),
    [
        ("normal", False, True, STATUS_NOT_OFFERED, REASON_WRONG_DAY_TYPE),
        ("full_package", True, False, STATUS_NOT_OFFERED, REASON_WRONG_DAY_TYPE),
    ],
)
def test_classify_marks_wrong_day_type_as_not_offered(
    selection_type, normal_allowed, package_allowed, expected_status, reason
):
    result = classify_calendar_day(
        selection_type=selection_type,
        day_type="full_package",
        normal_bookings_allowed=normal_allowed,
        full_package_allowed=package_allowed,
        max_clients=3,
        booked_clients=0,
        slot_count=5,
    )
    assert result["status"] == expected_status
    assert result["reason_code"] == reason
    assert result["capacity"]["max"] == 0


def test_classify_sunday_as_closed():
    result = classify_calendar_day(
        selection_type="normal",
        day_type="closed",
        normal_bookings_allowed=False,
        full_package_allowed=False,
        max_clients=0,
        booked_clients=0,
        slot_count=0,
    )
    assert result["status"] == STATUS_CLOSED
    assert result["reason_code"] == REASON_STUDIO_CLOSED


def test_classify_capacity_full_before_slot_check():
    result = classify_calendar_day(
        selection_type="normal",
        day_type="normal",
        normal_bookings_allowed=True,
        full_package_allowed=False,
        max_clients=5,
        booked_clients=5,
        slot_count=10,
    )
    assert result["status"] == STATUS_CAPACITY_FULL
    assert result["reason_code"] == REASON_DAY_CAPACITY_REACHED
    assert result["slot_count"] == 0
    assert result["capacity"]["remaining"] == 0


def test_classify_no_slots_when_capacity_remains():
    result = classify_calendar_day(
        selection_type="full_package",
        day_type="full_package",
        normal_bookings_allowed=False,
        full_package_allowed=True,
        max_clients=3,
        booked_clients=1,
        slot_count=0,
    )
    assert result["status"] == STATUS_NO_SLOTS
    assert result["reason_code"] == REASON_NO_OPEN_TIMES
    assert result["capacity"]["remaining"] == 2


def test_classify_available_with_capacity_and_slots():
    result = classify_calendar_day(
        selection_type="normal",
        day_type="normal",
        normal_bookings_allowed=True,
        full_package_allowed=False,
        max_clients=5,
        booked_clients=2,
        slot_count=8,
    )
    assert result == {
        "status": STATUS_AVAILABLE,
        "reason_code": None,
        "slot_count": 8,
        "capacity": {"max": 5, "booked": 2, "remaining": 3},
    }


def test_classify_is_deterministic_for_identical_inputs():
    kwargs = dict(
        selection_type="normal",
        day_type="normal",
        normal_bookings_allowed=True,
        full_package_allowed=False,
        max_clients=5,
        booked_clients=1,
        slot_count=4,
    )
    assert classify_calendar_day(**kwargs) == classify_calendar_day(**kwargs)
