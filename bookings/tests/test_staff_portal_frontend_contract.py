import pytest
from django.test import Client

from bookings.tests.test_staff_portal_helpers import staff_login


@pytest.mark.django_db
def test_staff_portal_payload_supports_spreadsheet_and_mobile_card_contract():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.get("/api/staff/bookings/schedule/?date=2030-06-03", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert {"local_date", "timezone", "day_type", "capacity", "appointments"} <= set(payload)
    assert len(response.content) < 25000
