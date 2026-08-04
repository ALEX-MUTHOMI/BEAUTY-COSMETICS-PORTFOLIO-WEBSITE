import pytest
from django.test import Client

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import staff_booking_url, staff_login


@pytest.mark.django_db
def test_staff_default_views_do_not_leak_pii_tokens_or_provider_identifiers():
    booking = create_booking()
    booking.checkout_session_id = "checkout-raw-secret"
    booking.save(update_fields=["checkout_session_id", "updated_at"])

    client = Client()
    staff_login(client, permissions=["view_staff_portal", "view_staff_booking"])
    daily = client.get(f"/api/staff/bookings/schedule/?date={booking.local_booking_date}", secure=True).content.decode()
    detail = client.get(staff_booking_url(booking), secure=True).content.decode()

    surface = daily + detail
    assert "grace@example.com" not in surface.lower()
    assert "+254" not in surface
    assert "checkout-raw-secret" not in surface
    assert "download_token" not in surface
