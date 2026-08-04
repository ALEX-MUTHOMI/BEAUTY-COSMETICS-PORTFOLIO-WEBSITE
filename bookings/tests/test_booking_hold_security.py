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
def test_xss_payload_and_raw_pii_are_not_reflected_in_hold_response_or_error(caplog):
    service, resource, _customer = create_service_resource_customer()
    payload = {
        "full_name": "<script>alert(1)</script>",
        "email": "grace@example.com",
        "phone": "+254712345678",
        "notes": "<img src=x onerror=alert(1)>",
    }

    result = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI),
        customer_payload=payload,
        idempotency_key="xss-safe",
        request_context={"request_id": "req-redacted"},
    )

    output = str(result) + caplog.text
    assert "<script" not in output
    assert "onerror" not in output
    assert "+254712345678" not in output
    assert "grace@example.com" not in output


@pytest.mark.django_db
def test_unknown_and_inactive_service_or_resource_errors_are_generic():
    service, resource, _customer = create_service_resource_customer()
    service.is_active = False
    resource.is_active = False
    service.save(update_fields=["is_active", "updated_at"])
    resource.save(update_fields=["is_active", "updated_at"])

    with pytest.raises(ValidationError) as exc:
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI),
            customer_payload={"full_name": "Grace", "email": "bad", "phone": "bad"},
            idempotency_key="generic-errors",
        )

    assert "unavailable" in str(exc.value).lower()
    assert str(service.id) not in str(exc.value)
    assert str(resource.id) not in str(exc.value)
