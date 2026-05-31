from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from bookings.models import Booking, BookingPolicy, BusinessHours
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


@pytest.mark.django_db
def test_max_daily_bookings_reached_returns_no_normal_slots():
    service, resource, customer = create_service_resource_customer()
    BookingPolicy.objects.create(max_daily_bookings=1)
    day = date(2026, 6, 1)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 7),
        ends_at=_utc_on(day, 8),
        status=Booking.Status.CONFIRMED,
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"] == []


@pytest.mark.django_db
def test_cancelled_and_expired_holds_do_not_count_against_daily_capacity():
    service, resource, customer = create_service_resource_customer()
    BookingPolicy.objects.create(max_daily_bookings=1)
    day = date(2026, 6, 2)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 7),
        ends_at=_utc_on(day, 8),
        status=Booking.Status.CANCELLED_BY_CLIENT,
    )
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 8),
        ends_at=_utc_on(day, 9),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"]


@pytest.mark.django_db
def test_capacity_is_calculated_by_nairobi_business_day_not_utc_day():
    service, resource, customer = create_service_resource_customer()
    BusinessHours.objects.filter(resource=resource, weekday=0).update(
        opens_at=time(0, 0), closes_at=time(3, 0), is_closed=False
    )
    BookingPolicy.objects.create(max_daily_bookings=1)
    day = date(2026, 6, 1)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 0, 30),
        ends_at=_utc_on(day, 1, 30),
        status=Booking.Status.CONFIRMED,
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    assert result[0]["slots"] == []
