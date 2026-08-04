import pytest
from django.utils import timezone

from bookings.models import ReturningClientDevice
from bookings.services.remember_device import cleanup_expired_returning_devices
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_expired_remember_device_is_ignored_and_cleanup_is_bounded(client):
    booking = confirmed_booking(key="remember-retention")
    remember_device(client, booking)
    device = ReturningClientDevice.objects.get()
    device.expires_at = timezone.now() - timezone.timedelta(days=1)
    device.save(update_fields=["expires_at", "updated_at"])

    response = client.get("/api/customers/remembered-device/", secure=True)
    assert response.json() == {"remembered": False}

    result = cleanup_expired_returning_devices(limit=10)
    device.refresh_from_db()
    assert result["expired"] == 1
    assert device.status == ReturningClientDevice.Status.EXPIRED
