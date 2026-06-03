import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_slow_retry_reuses_reschedule_authorization_once_only():
    booking = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(days=5))
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
        requested_starts_at=booking.starts_at + timezone.timedelta(days=1),
    )
    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=booking.public_id,
            action_token=action.token,
            requested_starts_at=booking.starts_at + timezone.timedelta(days=2),
        )
