import pytest
from django.test import override_settings

from bookings.tests.test_remember_device_helpers import confirmed_booking


@pytest.mark.django_db
@override_settings(DEBUG=False, REMEMBER_DEVICE_SECURE=True)
def test_remember_device_cookie_is_httponly_secure_samesite_and_opaque(client, settings):
    booking = confirmed_booking(key="remember-cookie")
    response = client.post(
        "/api/customers/remember-device/",
        {"booking_public_id": str(booking.public_id), "remember_device": True},
        content_type="application/json",
        secure=True,
    )

    cookie = response.cookies[settings.REMEMBER_DEVICE_COOKIE_NAME]
    assert cookie["httponly"] is True
    assert cookie["secure"] is True
    assert cookie["samesite"] in {"Lax", "Strict"}
    assert int(cookie["max-age"]) > 0
    assert "@" not in cookie.value
    assert "+254" not in cookie.value
    assert str(booking.public_id) not in cookie.value
    assert len(cookie.value) >= 43
