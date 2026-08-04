from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db
def test_unknown_expired_and_xss_booking_payment_errors_are_generic_and_pii_safe(caplog):
    with pytest.raises(ValidationError) as unknown:
        _contract_service().create_checkout_for_held_booking(
            booking_public_id="00000000-0000-0000-0000-000000000000",
            idempotency_key="unknown-payment",
        )
    assert "available for checkout" in str(unknown.value).lower()

    booking = _held_booking(key="xss-payment-hold")
    booking.customer_profile.full_name_display = "<script>alert(1)</script>"
    booking.customer_profile.save(update_fields=["full_name_display", "updated_at"])
    result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="xss-payment-checkout",
    )

    output = str(result) + caplog.text
    assert "<script" not in output
    assert "grace@example.com" not in output
    assert "+254" not in output
    assert str(booking.id) not in output


@pytest.mark.django_db
def test_expired_booking_and_nonexistent_booking_do_not_leak_distinction():
    expired = _held_booking(key="expired-enumeration")
    expired.status = Booking.Status.EXPIRED
    expired.hold_expires_at = timezone.now() - timedelta(minutes=1)
    expired.save(update_fields=["status", "hold_expires_at", "updated_at"])

    errors = []
    for public_id in [expired.public_id, "00000000-0000-0000-0000-000000000000"]:
        with pytest.raises(ValidationError) as exc:
            _contract_service().create_checkout_for_held_booking(
                booking_public_id=public_id,
                idempotency_key=f"enum-{public_id}",
            )
        errors.append(str(exc.value))

    assert errors[0] == errors[1]
    assert CheckoutSession.objects.count() == 0
