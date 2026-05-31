from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from bookings.models import Booking
from bookings.tests.factories import create_booking, create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


def _next_weekday(target=0):
    today = timezone.localdate()
    delta = (target - today.weekday()) % 7
    if delta == 0:
        delta = 7
    return today + timedelta(days=delta)


def _utc_on(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), tzinfo=NAIROBI).astimezone(ZoneInfo("UTC"))


@pytest.mark.django_db
def test_generates_monday_to_saturday_slots_between_0700_and_1900_nairobi():
    service, resource, _customer = create_service_resource_customer()
    service.duration_minutes = 60
    service.save(update_fields=["duration_minutes", "updated_at"])
    monday = _next_weekday(0)

    result = _service().get_available_slots(service.id, monday, monday, resource_id=resource.id)

    slots = result[0]["slots"]
    assert slots[0]["starts_at"].endswith("07:00:00+03:00")
    assert slots[-1]["starts_at"].endswith("18:00:00+03:00")
    assert slots[-1]["ends_at"].endswith("19:00:00+03:00")
    assert all(slot["service_public_id"] == str(service.id) for slot in slots)
    assert all(slot["resource_public_id"] == str(resource.id) for slot in slots)


@pytest.mark.django_db
def test_service_duration_and_buffers_shrink_candidate_windows():
    service, resource, _customer = create_service_resource_customer()
    service.duration_minutes = 60
    service.buffer_before_minutes = 15
    service.buffer_after_minutes = 15
    service.save(update_fields=["duration_minutes", "buffer_before_minutes", "buffer_after_minutes", "updated_at"])
    monday = _next_weekday(0)

    result = _service().get_available_slots(service.id, monday, monday, resource_id=resource.id)

    starts = [slot["starts_at"] for slot in result[0]["slots"]]
    assert not any("07:00:00+03:00" in value for value in starts)
    assert any("07:30:00+03:00" in value for value in starts)
    assert any("17:30:00+03:00" in value for value in starts)
    assert not any("18:00:00+03:00" in value for value in starts)
    assert result[0]["slots"][0]["buffer_minutes"] == 30


@pytest.mark.django_db
def test_confirmed_booking_blocks_overlap_but_allows_adjacent_slot():
    service, resource, customer = create_service_resource_customer()
    day = _next_weekday(1)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 9),
        ends_at=_utc_on(day, 10),
        status=Booking.Status.CONFIRMED,
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    starts = [slot["starts_at"] for slot in result[0]["slots"]]
    assert not any("09:00:00+03:00" in value for value in starts)
    assert not any("09:30:00+03:00" in value for value in starts)
    assert any("10:00:00+03:00" in value for value in starts)


@pytest.mark.django_db
def test_active_holds_block_but_expired_holds_do_not_block():
    service, resource, customer = create_service_resource_customer()
    day = _next_weekday(2)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 8),
        ends_at=_utc_on(day, 9),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() + timedelta(minutes=5),
    )
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 11),
        ends_at=_utc_on(day, 12),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    starts = [slot["starts_at"] for slot in result[0]["slots"]]
    assert not any("08:00:00+03:00" in value for value in starts)
    assert any("11:00:00+03:00" in value for value in starts)
