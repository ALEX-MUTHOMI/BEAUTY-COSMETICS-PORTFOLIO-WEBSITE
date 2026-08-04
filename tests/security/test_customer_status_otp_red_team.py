import pytest
from django.test import Client

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_customer_status_and_otp_red_team_blocks_enumeration_replay_and_pii(settings, caplog):
    settings.CUSTOMER_OTP_MAX_ATTEMPTS = 2
    booking, _session, _ledger = _confirm_paid_booking("status-otp-red-b5")

    missing = Client().get("/api/bookings/status/00000000-0000-4000-8000-000000000000/", secure=True)
    malformed = Client().get("/api/bookings/status/not-a-uuid/", secure=True)
    assert missing.json() == malformed.json()

    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.50", "user_agent": "pytest"},
    )
    assert CustomerOTPService.verify_challenge(challenge.public_id, "000000") is None
    assert CustomerOTPService.verify_challenge(challenge.public_id, "111111") is None
    challenge.refresh_from_db()
    assert challenge.status == CustomerOTPChallenge.Status.LOCKED
    assert CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code) is None
    assert "grace@example.com" not in caplog.text
    assert "+254" not in caplog.text
