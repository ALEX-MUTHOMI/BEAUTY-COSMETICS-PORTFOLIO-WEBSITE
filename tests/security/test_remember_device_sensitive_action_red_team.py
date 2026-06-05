import pytest

from bookings.models import CustomerActionSession
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_stolen_remembered_device_cannot_create_sensitive_action_authorization(client):
    booking = confirmed_booking(key="remember-sensitive-red-team")
    remember_device(client, booking)

    assert CustomerActionSession.objects.filter(booking=booking).count() == 0
    assert client.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code == 200
    assert CustomerActionSession.objects.filter(booking=booking).count() == 0
