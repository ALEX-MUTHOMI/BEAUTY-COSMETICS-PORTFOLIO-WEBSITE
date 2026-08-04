import pytest
from django.core.exceptions import ValidationError

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import valid_business_start_utc, valid_reschedule_start_utc


@pytest.mark.django_db(transaction=True)
def test_reschedule_requires_scoped_otp_and_keeps_original_when_unauthorized():
    booking = create_booking(status="confirmed", starts_at=valid_business_start_utc())
    original_start = booking.starts_at

    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=booking.public_id,
            action_token="invalid",
            requested_starts_at=valid_reschedule_start_utc(),
        )
    booking.refresh_from_db()
    assert booking.starts_at == original_start

    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.30", "user_agent": "pytest"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)
    requested_start = valid_reschedule_start_utc()
    updated = BookingRescheduleService.reschedule(
        booking_public_id=booking.public_id,
        action_token=action.token,
        requested_starts_at=requested_start,
    )

    assert updated.starts_at == requested_start
    assert updated.status == "confirmed"
    assert updated.reschedule_count == 1
