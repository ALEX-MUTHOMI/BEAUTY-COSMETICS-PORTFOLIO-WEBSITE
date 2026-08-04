import pytest

from bookings.models import ReturningClientDevice
from bookings.tests.test_remember_device_helpers import confirmed_booking


@pytest.mark.django_db
def test_remember_device_created_only_after_explicit_opt_in(client):
    booking = confirmed_booking(key="remember-create")

    no_opt_in = client.post(
        "/api/customers/remember-device/",
        {"booking_public_id": str(booking.public_id), "remember_device": False},
        content_type="application/json",
        secure=True,
    )
    assert no_opt_in.status_code == 400
    assert ReturningClientDevice.objects.count() == 0

    response = client.post(
        "/api/customers/remember-device/",
        {"booking_public_id": str(booking.public_id), "remember_device": True},
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 201
    assert ReturningClientDevice.objects.count() == 1
    payload = response.json()
    assert payload["remembered"] is True
    assert payload["profile_summary"]["email_redacted"]
    assert "token" not in payload
    assert "hash" not in str(payload).lower()
