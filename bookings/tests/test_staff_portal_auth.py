import pytest
from django.test import Client

from bookings.tests.test_b6_helpers import future_monday
from bookings.tests.test_staff_portal_helpers import make_customer_user, staff_login


@pytest.mark.django_db
def test_staff_schedule_blocks_anonymous_customer_and_allows_superuser():
    path = f"/api/staff/bookings/schedule/?date={future_monday().date().isoformat()}"

    assert Client().get(path, secure=True).status_code in {401, 403, 404}

    customer_client = Client()
    customer_client.force_login(make_customer_user())
    assert customer_client.get(path, secure=True).status_code in {401, 403}

    staff_client = Client()
    staff_login(staff_client, superuser=True)
    response = staff_client.get(path, secure=True)
    assert response.status_code == 200
    assert response.json()["timezone"] == "Africa/Nairobi"
