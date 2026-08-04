import pytest
from django.core.exceptions import ValidationError

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import make_utc_from_eat, valid_business_start_utc


@pytest.mark.django_db(transaction=True)
def test_slow_retry_reuses_reschedule_authorization_once_only():
    booking = create_booking(status="confirmed", starts_at=valid_business_start_utc())
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.80", "user_agent": "mobile"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)

    BookingRescheduleService.reschedule(
        booking_public_id=booking.public_id,
        action_token=action.token,
        requested_starts_at=make_utc_from_eat(2030, 6, 5, 10, 0),
    )
    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=booking.public_id,
            action_token=action.token,
            requested_starts_at=make_utc_from_eat(2030, 6, 6, 10, 0),
        )
