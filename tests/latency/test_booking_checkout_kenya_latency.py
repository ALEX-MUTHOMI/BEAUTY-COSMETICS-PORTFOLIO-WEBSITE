import pytest

from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db
def test_mobile_reconnect_checkout_retries_are_idempotent_and_poll_friendly():
    booking = _held_booking(key="kenya-checkout-retry")

    responses = [
        _contract_service().create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="kenya-checkout-retry-key",
        )
        for _ in range(5)
    ]

    booking.refresh_from_db()
    assert len({response["checkout_public_id"] for response in responses}) == 1
    assert CheckoutSession.objects.count() == 1
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert responses[-1]["next_action"] in {"initiate_payment", "payment_pending"}
    assert len(str(responses[-1])) < 900
