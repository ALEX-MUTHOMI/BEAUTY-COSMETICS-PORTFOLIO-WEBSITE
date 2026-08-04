import pytest

from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db
def test_mobile_timeout_retry_returns_stable_small_checkout_response_without_duplicates():
    booking = _held_booking(key="mobile-checkout-timeout")

    first = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="mobile-checkout-timeout-key",
    )
    retry = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="mobile-checkout-timeout-key",
    )

    booking.refresh_from_db()
    assert first == retry
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert CheckoutSession.objects.count() == 1
    assert retry["next_action"] == "initiate_payment"
    assert len(str(retry)) < 900
