from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from bookings.models import Booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


@pytest.mark.django_db
def test_slow_network_retry_after_timeout_returns_existing_hold_without_duplicate():
    service, resource, _customer = create_service_resource_customer()
    starts_at = datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI)
    payload = {"full_name": "Grace Wanjiku", "email": "grace@example.com", "phone": "+254712345678"}

    first = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=starts_at,
        customer_payload=payload,
        idempotency_key="mobile-timeout",
    )
    retry = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=starts_at,
        customer_payload=payload,
        idempotency_key="mobile-timeout",
    )

    assert first["booking_public_id"] == retry["booking_public_id"]
    assert Booking.objects.filter(idempotency_key="mobile-timeout").count() == 1
    assert len(str(retry)) < 900
