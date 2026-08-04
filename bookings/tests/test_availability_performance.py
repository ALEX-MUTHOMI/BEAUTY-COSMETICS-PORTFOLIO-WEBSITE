from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.models import Booking
from bookings.tests.factories import create_booking, create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


def _utc_on(day, hour):
    return datetime.combine(day, time(hour, 0), tzinfo=NAIROBI).astimezone(ZoneInfo("UTC"))


@pytest.mark.django_db
def test_seven_day_range_uses_bounded_queries_not_per_slot_queries():
    service, resource, customer = create_service_resource_customer()
    start = date(2026, 6, 1)
    for offset in range(6):
        day = start + timedelta(days=offset)
        create_booking(
            service=service,
            resource=resource,
            customer_profile=customer,
            starts_at=_utc_on(day, 7),
            ends_at=_utc_on(day, 8),
            status=Booking.Status.CONFIRMED,
            idempotency_key=f"perf-{offset}",
        )

    with CaptureQueriesContext(connection) as captured:
        result = _service().get_available_slots(service.id, start, start + timedelta(days=6), resource_id=resource.id)

    assert len(result) == 7
    assert len(captured) <= 10
