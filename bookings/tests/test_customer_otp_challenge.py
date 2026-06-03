import pytest
from django.utils import timezone

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_reschedule_otp_is_hashed_expiring_single_use_and_session_scoped(monkeypatch):
    from bookings.models import CustomerActionSession, CustomerOTPChallenge
    from bookings.services.customer_otp import CustomerOTPService

    booking, _session, _ledger = _confirm_paid_booking("otp-b5")
    monkeypatch.setattr(CustomerOTPService, "_generate_code", staticmethod(lambda: "123456"))

    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.10", "user_agent": "pytest"},
    )

    assert challenge.status == CustomerOTPChallenge.Status.PENDING
    assert challenge.otp_hash_hmac
    assert "123456" not in challenge.otp_hash_hmac
    assert "grace@example.com" not in challenge.recipient_hash_hmac

    action = CustomerOTPService.verify_challenge(challenge.public_id, "123456")
    assert action.purpose == CustomerActionSession.Purpose.RESCHEDULE
    assert action.booking == booking
    assert CustomerOTPService.verify_challenge(challenge.public_id, "123456") is None

    challenge.expires_at = timezone.now() - timezone.timedelta(seconds=1)
    challenge.used_at = None
    challenge.status = CustomerOTPChallenge.Status.PENDING
    challenge.save(update_fields=["expires_at", "used_at", "status", "updated_at"])
    assert CustomerOTPService.verify_challenge(challenge.public_id, "123456") is None
