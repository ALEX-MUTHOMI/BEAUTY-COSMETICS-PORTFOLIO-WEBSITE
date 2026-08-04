from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from bookings.models import Booking, BusinessHours
from bookings.tests.factories import create_booking, create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


def _utc_on(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), tzinfo=NAIROBI).astimezone(ZoneInfo("UTC"))


def _fill_dynamic_quota(service, resource, customer, day, count):
    """Create *count* non-overlapping confirmed bookings to exhaust dynamic quota."""
    for index in range(count):
        start_hour = 7 + index
        create_booking(
            service=service,
            resource=resource,
            customer_profile=customer,
            starts_at=_utc_on(day, start_hour),
            ends_at=_utc_on(day, start_hour + 1),
            status=Booking.Status.CONFIRMED,
            idempotency_key=f"capacity-fill-{day.isoformat()}-{index}",
        )


@pytest.mark.django_db
def test_dynamic_quota_reached_returns_no_normal_slots():
    """60m service → floor(720/60)=12; filling 12 clients empties the day."""
    service, resource, customer = create_service_resource_customer()
    day = date(2026, 6, 1)  # Monday
    _fill_dynamic_quota(service, resource, customer, day, 12)

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"] == []


@pytest.mark.django_db
def test_cancelled_and_expired_holds_do_not_count_against_daily_capacity():
    service, resource, customer = create_service_resource_customer()
    day = date(2026, 6, 2)  # Tuesday — singles not offered by day policy, but
    # availability get_available_slots still generates for non-Sunday unless closed.
    # Use Monday for singles.
    day = date(2026, 6, 1)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 7),
        ends_at=_utc_on(day, 8),
        status=Booking.Status.CANCELLED_BY_CLIENT,
        idempotency_key="cancelled-capacity",
    )
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 8),
        ends_at=_utc_on(day, 9),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
        idempotency_key="expired-hold-capacity",
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"]


@pytest.mark.django_db
def test_capacity_uses_day_policy_hours_not_resource_business_hours_override():
    """Slot engine prefers BookingDayPolicy 07:00–19:00 over resource BusinessHours."""
    service, resource, customer = create_service_resource_customer()
    BusinessHours.objects.filter(resource=resource, weekday=0).update(
        opens_at=time(0, 0), closes_at=time(3, 0), is_closed=False
    )
    day = date(2026, 6, 1)
    # One morning booking should not exhaust dynamic quota of 12.
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 7),
        ends_at=_utc_on(day, 8),
        status=Booking.Status.CONFIRMED,
        idempotency_key="policy-hours-one",
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"]
    starts = [slot["starts_at"] for slot in result[0]["slots"]]
    # Dense packing continues after 08:00 within 07–19 policy window.
    assert any("08:00" in start or "08:30" in start or "09:00" in start for start in starts)
