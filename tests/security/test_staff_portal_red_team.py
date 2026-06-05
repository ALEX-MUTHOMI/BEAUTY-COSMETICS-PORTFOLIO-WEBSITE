import pytest
from django.test import Client

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import make_customer_user, staff_booking_url, staff_login


@pytest.mark.django_db
def test_staff_portal_red_team_blocks_customer_tokens_xss_and_sqlish_filters():
    booking = create_booking()
    customer = Client()
    customer.force_login(make_customer_user())
    customer.cookies["bc_remember_device"] = "forged-customer-cookie"
    assert customer.get(staff_booking_url(booking), secure=True).status_code in {401, 403}

    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.get(
        "/api/staff/bookings/schedule/?date=2030-06-03&status=' OR 1=1 --&booking_type=<script>",
        secure=True,
    )
    assert response.status_code in {200, 400}
    assert "<script" not in response.content.decode().lower()
