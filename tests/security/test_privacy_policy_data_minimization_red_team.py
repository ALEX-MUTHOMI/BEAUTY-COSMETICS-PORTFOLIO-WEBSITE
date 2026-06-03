import pytest

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_otp_pipeline_stores_hashes_not_raw_codes_or_recipient_pii():
    booking = create_booking()

    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "198.51.100.9", "user_agent": "<script>alert(1)</script>"},
    )

    surface = str(challenge.__dict__)
    assert CustomerOTPService._last_test_code not in surface
    assert "grace@example.com" not in surface
    assert "198.51.100.9" not in surface
    assert "<script>" not in surface
