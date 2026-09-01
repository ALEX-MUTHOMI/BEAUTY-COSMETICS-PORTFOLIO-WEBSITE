"""TDD contracts for DSA calendar quality remediations."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.domain.selection import BookableSelection
from bookings.services.availability import MAX_AVAILABILITY_RANGE_DAYS
from bookings.services.booking_calendar import _slots_by_date, _slots_for_dates
from bookings.services.hold_expiry import BookingHoldExpiryService


def _selection(suffix: str) -> BookableSelection:
    return BookableSelection.from_parts(
        selection_type="normal",
        public_id=UUID(f"00000000-0000-0000-0000-{suffix.zfill(12)}"),
        name="Facial",
        slug="facial",
        duration_minutes=60,
    )


def test_slots_for_dates_uses_one_availability_call_per_batch_not_per_day():
    start = date(2030, 6, 2)
    dates = [start + timedelta(days=i) for i in range(8)]
    selection = _selection("1")
    calls = []

    def fake_slots(**kwargs):
        calls.append((kwargs["slot_start"], kwargs["slot_end"]))
        return {d.isoformat(): [] for d in dates}

    with patch("bookings.services.booking_calendar._slots_by_date", side_effect=fake_slots):
        _slots_for_dates(selection=selection, dates=dates, resource_id=None, request_context={})

    assert len(calls) == 1
    assert calls[0][0] == dates[0]
    assert calls[0][1] == dates[-1]
    assert (calls[0][1] - calls[0][0]).days + 1 <= MAX_AVAILABILITY_RANGE_DAYS


def test_slots_by_date_logs_unexpected_errors_and_degrades_to_empty():
    selection = _selection("2")
    with patch(
        "bookings.services.booking_calendar.AvailabilityService.get_available_slots",
        side_effect=RuntimeError("redis down"),
    ):
        with patch("bookings.services.booking_calendar.logger.exception") as logged:
            assert (
                _slots_by_date(
                    selection=selection,
                    slot_start=date(2030, 6, 2),
                    slot_end=date(2030, 6, 2),
                    resource_id=None,
                    request_context={},
                )
                == {}
            )
        logged.assert_called_once()
        assert logged.call_args.args[0] == "booking.calendar.slots_fetch_failed"


def test_slots_by_date_still_maps_validation_error_to_empty():
    selection = _selection("3")
    with patch(
        "bookings.services.booking_calendar.AvailabilityService.get_available_slots",
        side_effect=ValidationError("closed day"),
    ):
        assert (
            _slots_by_date(
                selection=selection,
                slot_start=date(2030, 6, 2),
                slot_end=date(2030, 6, 2),
                resource_id=None,
                request_context={},
            )
            == {}
        )


@pytest.mark.django_db(transaction=True)
def test_hold_expiry_dedupes_capacity_bumps_per_local_date(monkeypatch):
    from bookings.models import Booking
    from bookings.tests.test_booking_checkout_contract import _held_booking

    b1 = _held_booking(key="hold-dedupe-a")
    b2 = _held_booking(key="hold-dedupe-b")
    shared_day = b1.local_booking_date
    Booking.objects.filter(pk__in=[b1.pk, b2.pk]).update(
        local_booking_date=shared_day,
        hold_expires_at=timezone.now() - timedelta(minutes=5),
    )

    bumps = []

    def capture(**kwargs):
        bumps.append(kwargs["local_date"])

    monkeypatch.setattr(
        "bookings.services.hold_expiry.invalidate_calendar_capacity_for_transition",
        capture,
    )
    expired = BookingHoldExpiryService.expire_stale_holds(limit=10, redis_client=MagicMock())
    assert expired == 2
    assert bumps == [shared_day]
