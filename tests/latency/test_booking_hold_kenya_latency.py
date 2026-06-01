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
def test_mobile_reconnect_retries_are_idempotent_and_response_is_small():
    service, resource, _customer = create_service_resource_customer()
    starts_at = datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI)
    payload = {"full_name": "Grace", "email": "grace@example.com", "phone": "+254712345678"}

    responses = [
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=starts_at,
            customer_payload=payload,
            idempotency_key="kenya-mobile-retry",
        )
        for _ in range(5)
    ]

    assert len({response["booking_public_id"] for response in responses}) == 1
    assert Booking.objects.filter(idempotency_key="kenya-mobile-retry").count() == 1
    assert len(str(responses[-1])) < 900
