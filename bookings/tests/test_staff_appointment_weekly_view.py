import pytest
from django.test import Client

from bookings.tests.test_staff_portal_helpers import staff_login


@pytest.mark.django_db
def test_weekly_overview_is_seven_days_policy_aware_and_pii_free():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])

    response = client.get("/api/staff/bookings/week/?start_date=2030-06-03", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["week_start"] == "2030-06-03"
    assert len(payload["days"]) == 7
    day_types = {day["local_date"]: day["day_type"] for day in payload["days"]}
    assert day_types["2030-06-04"] == "full_package"
    assert day_types["2030-06-05"] == "full_package"
    assert day_types["2030-06-09"] == "closed"
    assert "grace@example.com" not in str(payload).lower()
