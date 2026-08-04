import pytest

from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_remember_device_cookie_response_contains_no_pii_or_internal_ids(client):
    booking = confirmed_booking(key="remember-cookie-red-team")
    token = remember_device(client, booking)
    response = client.get("/api/customers/remembered-device/", secure=True)
    dump = str(response.json()) + token

    assert "grace@example.com" not in dump.lower()
    assert "+254712345678" not in dump
    assert "booking_public_id" not in dump
    assert "customer_profile" not in dump
    assert "token_hash_hmac" not in dump
