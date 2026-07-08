"""Tests for CalendarPolicy — selection-aware day rules."""

from datetime import date, time
from uuid import UUID

import pytest

from bookings.domain.calendar import OFFERED_WEEKDAYS_BY_PROFILE
from bookings.domain.calendar_policy import CalendarDayPolicy, CalendarPolicy
from bookings.domain.selection import BookableSelection
from bookings.models import BookingDayPolicy
from bookings.services.day_policy import built_in_policy_for_weekday


def _selection(*, selection_type: str, policy_profile: str) -> BookableSelection:
    return BookableSelection(
        selection_type=selection_type,  # type: ignore[arg-type]
        public_id=UUID("00000000-0000-4000-8000-000000000001"),
        slug="test-slug",
        name="Test",
        duration_minutes=60,
        policy_profile=policy_profile,  # type: ignore[arg-type]
    )


@pytest.mark.django_db
def test_calendar_policy_marks_single_weekdays_offered():
    selection = _selection(selection_type="normal", policy_profile="single")
    monday = date(2026, 7, 6)
    policy = CalendarPolicy.for_date(selection=selection, local_date=monday)
    assert policy.offered is True
    assert policy.day_type == BookingDayPolicy.DayType.NORMAL
    assert policy.max_clients == 5
    assert policy.normal_bookings_allowed is True
    assert policy.full_package_allowed is False


@pytest.mark.django_db
def test_calendar_policy_marks_package_weekdays_offered():
    selection = _selection(selection_type="full_package", policy_profile="full_package")
    tuesday = date(2026, 7, 7)
    policy = CalendarPolicy.for_date(selection=selection, local_date=tuesday)
    assert policy.offered is True
    assert policy.day_type == BookingDayPolicy.DayType.FULL_PACKAGE
    assert policy.max_clients == 3
    assert policy.full_package_allowed is True


@pytest.mark.django_db
def test_calendar_policy_marks_wrong_profile_weekday_not_offered():
    selection = _selection(selection_type="full_package", policy_profile="full_package")
    monday = date(2026, 7, 6)
    policy = CalendarPolicy.for_date(selection=selection, local_date=monday)
    assert policy.offered is False
    assert monday.weekday() not in OFFERED_WEEKDAYS_BY_PROFILE["full_package"]


@pytest.mark.django_db
def test_calendar_policy_sunday_closed_studio_policy():
    selection = _selection(selection_type="normal", policy_profile="single")
    sunday = date(2026, 7, 5)
    policy = CalendarPolicy.for_date(selection=selection, local_date=sunday)
    assert policy.day_type == BookingDayPolicy.DayType.CLOSED
    assert policy.max_clients == 0


def test_calendar_day_policy_classification_payload_excludes_business_hours():
    base = built_in_policy_for_weekday(0)
    day_policy = CalendarDayPolicy.from_booking_day_policy(policy=base, offered=True)
    payload = day_policy.classification_payload()
    assert set(payload.keys()) == {
        "day_type",
        "normal_bookings_allowed",
        "full_package_allowed",
        "max_clients",
    }
    assert "business_start" not in payload
    assert "business_end" not in payload


@pytest.mark.django_db
def test_calendar_policy_business_hours_present_internally():
    selection = _selection(selection_type="normal", policy_profile="single")
    monday = date(2026, 7, 6)
    policy = CalendarPolicy.for_date(selection=selection, local_date=monday)
    assert policy.business_start == time(7, 0)
    assert policy.business_end == time(19, 0)


def test_is_weekday_offered_matches_profile():
    monday = date(2026, 7, 6)
    assert CalendarPolicy.is_weekday_offered(policy_profile="single", local_date=monday) is True
    assert CalendarPolicy.is_weekday_offered(policy_profile="full_package", local_date=monday) is False
