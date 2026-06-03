from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import close_old_connections, connections

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import valid_business_start_utc, valid_reschedule_start_utc


@pytest.mark.django_db(transaction=True)
def test_reschedule_pressure_does_not_double_apply_one_authorization():
    booking = create_booking(status="confirmed", starts_at=valid_business_start_utc())
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
                requested_starts_at=valid_reschedule_start_utc(),
            )
            return "ok"
        except Exception:
            return "rejected"
        finally:
            close_old_connections()
            connections.close_all()

    results = list(ThreadPoolExecutor(max_workers=10).map(lambda _i: attempt(), range(10)))
    booking.refresh_from_db()
    assert results.count("ok") == 1
    assert booking.reschedule_count == 1
