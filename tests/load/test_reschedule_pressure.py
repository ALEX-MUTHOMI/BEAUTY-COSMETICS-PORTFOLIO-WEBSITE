from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import close_old_connections
from django.utils import timezone

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_reschedule_pressure_does_not_double_apply_one_authorization():
    booking = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(days=5))
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.70", "user_agent": "pytest"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)

    def attempt():
        try:
            BookingRescheduleService.reschedule(
                booking_public_id=booking.public_id,
                action_token=action.token,
                requested_starts_at=booking.starts_at + timezone.timedelta(days=1),
            )
            return "ok"
        except Exception:
            return "rejected"
        finally:
            close_old_connections()

    results = list(ThreadPoolExecutor(max_workers=10).map(lambda _i: attempt(), range(10)))
    booking.refresh_from_db()
    assert results.count("ok") == 1
    assert booking.reschedule_count == 1
