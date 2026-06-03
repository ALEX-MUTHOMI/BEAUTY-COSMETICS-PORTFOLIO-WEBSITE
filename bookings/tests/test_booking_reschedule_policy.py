import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import BookingPolicy, CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import make_utc_from_eat, valid_business_start_utc


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
            requested_starts_at=make_utc_from_eat(2030, 6, 5, 10, 0),
        )

    later = create_booking(status="confirmed", starts_at=valid_business_start_utc())
    token = _authorized_token(later)
    out_of_hours = make_utc_from_eat(2030, 6, 5, 3, 0)
    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=later.public_id,
            action_token=token,
            requested_starts_at=out_of_hours,
        )
