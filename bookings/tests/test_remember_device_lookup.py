import pytest

from bookings.models import ReturningClientDevice
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_remembered_device_lookup_returns_redacted_summary_only(client):
    booking = confirmed_booking(key="remember-lookup")
    remember_device(client, booking)

    response = client.get("/api/customers/remembered-device/", secure=True)

    assert response.status_code == 200
    payload = response.json()
    assert payload["remembered"] is True
    assert payload["can_use_saved_details"] is True
    assert "g***@example.com" in str(payload)
    assert "grace@example.com" not in str(payload).lower()
    assert "+254712345678" not in str(payload)
    assert "token_hash_hmac" not in str(payload)
    assert "id" not in payload["profile_summary"]
    assert ReturningClientDevice.objects.count() == 1


@pytest.mark.django_db
def test_missing_or_malformed_remembered_device_cookie_fails_safely(client):
    client.cookies["bc_remember_device"] = "not-a-valid-real-token"
    response = client.get("/api/customers/remembered-device/", secure=True)
    assert response.status_code == 200
    assert response.json() == {"remembered": False}
