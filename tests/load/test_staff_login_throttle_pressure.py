import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_staff_login_throttle_bounds_1000_failed_attempts_without_success_or_500():
    make_staff()
    client = Client()
    statuses = []

    for _ in range(1000):
        response = client.post(
            "/api/staff/auth/login/",
            login_payload(password="wrong password"),
            content_type="application/json",
            secure=True,
        )
        statuses.append(response.status_code)

    assert 429 in statuses
    assert set(statuses).issubset({400, 429})
    assert all(status != 500 for status in statuses)
