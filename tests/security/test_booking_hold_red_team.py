from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


@pytest.mark.django_db
def test_frontend_supplied_duration_price_and_buffer_are_ignored():
    service, resource, _customer = create_service_resource_customer()

    result = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI),
        customer_payload={
            "full_name": "Grace",
            "email": "grace@example.com",
            "phone": "+254712345678",
            "duration_minutes": 1,
            "price": "0.00",
        },
        idempotency_key="ignore-client-money",
    )

    assert result["ends_at"].endswith("10:00:00+03:00")
    assert "price" not in result


@pytest.mark.django_db
def test_slot_conflict_error_is_generic_and_contains_no_customer_or_booking_details():
    service, resource, _customer = create_service_resource_customer()
    payload = {"full_name": "Grace", "email": "grace@example.com", "phone": "+254712345678"}
    _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI),
        customer_payload=payload,
        idempotency_key="first-conflict",
    )

    with pytest.raises(ValidationError) as exc:
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=datetime.combine(date(2026, 6, 1), time(9, 30), tzinfo=NAIROBI),
            customer_payload={"full_name": "Attacker", "email": "attacker@example.com", "phone": "+254798765432"},
            idempotency_key="second-conflict",
        )

    message = str(exc.value)
    assert "unavailable" in message.lower()
    assert "Grace" not in message
    assert "+254" not in message
    assert "first-conflict" not in message
