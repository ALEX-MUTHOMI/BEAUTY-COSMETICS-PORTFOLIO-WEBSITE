import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_otp_requests_are_rate_limited_and_unknown_booking_is_generic(settings):
    from bookings.models import CustomerOTPChallenge
    from bookings.services.customer_otp import CustomerOTPService

    settings.CUSTOMER_OTP_REQUEST_LIMIT = 2
    booking, _session, _ledger = _confirm_paid_booking("otp-rate-b5")

    first = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.11", "user_agent": "pytest"},
    )
    second = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.11", "user_agent": "pytest"},
    )
    third = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.11", "user_agent": "pytest"},
    )
    unknown = CustomerOTPService.request_challenge(
        booking_public_id="00000000-0000-4000-8000-000000000000",
        email="nobody@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.12", "user_agent": "pytest"},
    )

    assert first is not None
    assert second is not None
    assert third is None
    assert unknown is None
