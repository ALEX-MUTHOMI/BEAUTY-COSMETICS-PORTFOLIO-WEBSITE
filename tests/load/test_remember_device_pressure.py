import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.models import ReturningClientDevice
from bookings.services.remember_device import lookup_returning_device
from bookings.tests.test_remember_device_helpers import confirmed_booking, create_many_devices


@pytest.mark.django_db
@pytest.mark.load
def test_one_thousand_remembered_devices_have_bounded_hmac_lookup():
    booking = confirmed_booking(key="remember-load")
    tokens = create_many_devices(booking.customer_profile, 1000)

    with CaptureQueriesContext(connection) as captured:
        device = lookup_returning_device(tokens[-1])

    assert ReturningClientDevice.objects.count() == 1000
    assert device is not None
    assert len(captured) <= 2
