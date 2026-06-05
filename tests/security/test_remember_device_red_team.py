import pytest

from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_forged_revoked_and_hash_as_cookie_tokens_fail_safely(client):
    booking = confirmed_booking(key="remember-red-team")
    remember_device(client, booking)
    device = booking.customer_profile.returning_devices.get()

    client.cookies["bc_remember_device"] = device.token_hash_hmac
    assert client.get("/api/customers/remembered-device/", secure=True).json() == {"remembered": False}

    client.post("/api/customers/remembered-device/forget/", {}, content_type="application/json", secure=True)
    assert client.get("/api/customers/remembered-device/", secure=True).json() == {"remembered": False}

    client.cookies["bc_remember_device"] = "A" * 64
    assert client.get("/api/customers/remembered-device/", secure=True).json() == {"remembered": False}
