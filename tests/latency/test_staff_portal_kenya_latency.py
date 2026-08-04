import pytest
from django.test import Client

from bookings.tests.test_staff_portal_helpers import staff_login


@pytest.mark.django_db
def test_staff_weekly_payload_is_kenya_latency_friendly_and_bounded():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.get("/api/staff/bookings/week/?start_date=2030-06-03", secure=True)

    assert response.status_code == 200
    assert len(response.content) < 30000
    assert len(response.json()["days"]) == 7
