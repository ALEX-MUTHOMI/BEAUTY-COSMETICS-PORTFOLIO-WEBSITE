import pytest
from django.test import Client

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import (
    staff_booking_url,
    staff_contact_url,
    staff_login,
    staff_payment_url,
)


@pytest.mark.django_db
def test_staff_permissions_gate_detail_payment_and_contact_views():
    booking = create_booking()
    client = Client()
    staff_login(client)

    assert client.get(staff_booking_url(booking), secure=True).status_code == 403
    assert client.get(staff_payment_url(booking), secure=True).status_code == 403
    assert client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True).status_code == 403

    permitted = Client()
    staff_login(
        permitted,
        permissions=[
            "view_staff_booking",
            "view_staff_payment_summary",
            "view_staff_contact_details",
        ],
    )
    assert permitted.get(staff_booking_url(booking), secure=True).status_code == 200
    assert permitted.get(staff_payment_url(booking), secure=True).status_code == 200
    assert permitted.post(staff_contact_url(booking), {"reason": "call client"}, secure=True).status_code == 200
