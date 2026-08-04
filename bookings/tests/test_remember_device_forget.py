import pytest

from bookings.models import ReturningClientDevice
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_forget_device_revokes_token_and_clears_cookie(client, settings):
    booking = confirmed_booking(key="remember-forget")
    remember_device(client, booking)

    response = client.post("/api/customers/remembered-device/forget/", {}, content_type="application/json", secure=True)

    assert response.status_code == 200
    device = ReturningClientDevice.objects.get()
    assert device.status == ReturningClientDevice.Status.REVOKED
    assert device.revoked_at is not None
    assert response.cookies[settings.REMEMBER_DEVICE_COOKIE_NAME].value == ""

    lookup = client.get("/api/customers/remembered-device/", secure=True)
    assert lookup.json() == {"remembered": False}
