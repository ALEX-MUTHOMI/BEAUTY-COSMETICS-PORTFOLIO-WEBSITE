import pytest

from bookings.models import CustomerActionSession
from bookings.services.customer_otp import CustomerOTPService
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_remembered_device_does_not_create_otp_action_session_or_bypass_sensitive_actions(client):
    booking = confirmed_booking(key="remember-sensitive")
    remember_device(client, booking)

    assert CustomerActionSession.objects.count() == 0
    assert (
        CustomerOTPService.consume_action_session(
            token=client.cookies["bc_remember_device"].value,
            booking=booking,
            purpose=CustomerActionSession.Purpose.RESCHEDULE,
        )
        is None
    )
