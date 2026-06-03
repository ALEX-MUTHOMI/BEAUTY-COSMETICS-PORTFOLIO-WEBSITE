import pytest

from bookings.models import BookingNotification, CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.email_provider import FakeEmailProvider, get_email_provider
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_customer_otp_request_pumping_is_bounded_and_generic(settings):
    settings.EMAIL_PROVIDER = "fake"
    settings.CUSTOMER_OTP_REQUEST_LIMIT = 2
    booking = create_booking()
    meta = {"ip": "198.51.100.44", "user_agent": "attacker-bot"}

    first = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta=meta,
    )
    second = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta=meta,
    )
    blocked = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta=meta,
    )

    assert first is not None
    assert second is not None
    assert blocked is None
    assert BookingNotification.objects.filter(notification_type="customer_otp_reschedule").count() == 1


def test_default_email_provider_is_fake_to_prevent_provider_hijack(settings):
    settings.EMAIL_PROVIDER = "fake"

    assert isinstance(get_email_provider(), FakeEmailProvider)
