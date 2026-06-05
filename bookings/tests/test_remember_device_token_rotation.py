import pytest

from bookings.models import ReturningClientDevice
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_remember_device_token_hash_is_rotated_without_storing_raw_token(client):
    booking = confirmed_booking(key="remember-rotate")
    first = remember_device(client, booking)
    first_hash = ReturningClientDevice.objects.get().token_hash_hmac

    second = remember_device(client, booking)
    device = ReturningClientDevice.objects.order_by("-created_at").first()

    assert first != second
    assert device.token_hash_hmac != first
    assert device.token_hash_hmac != first_hash
    assert device.token_hash_hmac
    assert device.token_rotated_at is not None
