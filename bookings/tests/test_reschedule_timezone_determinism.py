import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import make_utc_from_eat, valid_business_start_utc


def _confirmed_booking():
    booking = create_booking(
        status=Booking.Status.CONFIRMED,
        starts_at=valid_business_start_utc(),
    )
    booking.ends_at = booking.starts_at + timezone.timedelta(minutes=booking.service.duration_minutes)
    booking.save(update_fields=["ends_at", "updated_at"])
    return booking


def _action_token(booking):
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.10", "user_agent": "pytest"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)
    return action.token


@pytest.mark.django_db
def test_reschedule_accepts_deterministic_1000_eat_start():
    booking = _confirmed_booking()

    updated = BookingRescheduleService.reschedule(
        booking_public_id=booking.public_id,
        action_token=_action_token(booking),
        requested_starts_at=make_utc_from_eat(2026, 6, 10, 10, 0),
    )

    assert updated.starts_at == make_utc_from_eat(2026, 6, 10, 10, 0)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "requested",
    [
        make_utc_from_eat(2030, 6, 5, 6, 59),
        make_utc_from_eat(2030, 6, 5, 19, 0),
        make_utc_from_eat(2030, 6, 5, 19, 2),
        make_utc_from_eat(2030, 6, 9, 10, 0),
    ],
)
def test_reschedule_rejects_after_hours_boundaries_and_sunday(requested):
    booking = _confirmed_booking()

    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=booking.public_id,
            action_token=_action_token(booking),
            requested_starts_at=requested,
        )
