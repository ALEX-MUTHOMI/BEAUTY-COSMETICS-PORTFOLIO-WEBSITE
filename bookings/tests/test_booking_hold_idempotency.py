from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


def _payload(phone="+254712345678", email="grace@example.com"):
    return {"full_name": "Grace Wanjiku", "email": email, "phone": phone}


def _starts(hour=9):
    return datetime.combine(date(2026, 6, 1), time(hour, 0), tzinfo=NAIROBI)


@pytest.mark.django_db
def test_same_key_same_payload_returns_same_hold_for_double_click_retry():
    service, resource, _customer = create_service_resource_customer()

    first = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload=_payload(),
        idempotency_key="same-key",
    )
    second = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload=_payload(),
        idempotency_key="same-key",
    )

    assert first["booking_public_id"] == second["booking_public_id"]
    assert Booking.objects.filter(idempotency_key="same-key").count() == 1


@pytest.mark.django_db
def test_same_key_different_payload_is_rejected_without_leaking_pii():
    service, resource, _customer = create_service_resource_customer()
    _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload=_payload(),
        idempotency_key="conflict-key",
    )

    with pytest.raises(ValidationError) as exc:
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=_starts(hour=10),
            customer_payload=_payload(phone="+254798765432"),
            idempotency_key="conflict-key",
        )

    assert "idempotency" in str(exc.value).lower()
    assert "+254" not in str(exc.value)
