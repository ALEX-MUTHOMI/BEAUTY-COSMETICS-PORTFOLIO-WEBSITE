import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import BookingPolicy, CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking


def _authorized_token(booking):
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.31", "user_agent": "pytest"},
    )
    return CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code).token


@pytest.mark.django_db(transaction=True)
def test_reschedule_enforces_cutoff_max_count_business_hours_and_sunday_policy():
    BookingPolicy.objects.create(reschedule_cutoff_hours=24, max_reschedules_per_booking=1)
    booking = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(hours=23))
    token = _authorized_token(booking)

    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=booking.public_id,
            action_token=token,
            requested_starts_at=timezone.now() + timezone.timedelta(days=3),
        )

    later = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(days=5))
    token = _authorized_token(later)
    out_of_hours = later.starts_at.replace(hour=3)
    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=later.public_id,
            action_token=token,
            requested_starts_at=out_of_hours,
        )
