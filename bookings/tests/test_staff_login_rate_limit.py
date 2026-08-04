import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_repeated_staff_login_failures_trigger_generic_cooldown():
    make_staff()
    client = Client()

    responses = [
        client.post(
            "/api/staff/auth/login/",
            login_payload(password="wrong password"),
            content_type="application/json",
            secure=True,
        )
        for _ in range(6)
    ]

    assert responses[-1].status_code == 429
    assert responses[-1].json() == {"detail": "Please try again later."}
    assert "staff-auth@example.com" not in str(responses[-1].content).lower()


@pytest.mark.django_db
def test_successful_staff_login_clears_failed_login_bucket():
    make_staff()
    client = Client()

    for _ in range(4):
        response = client.post(
            "/api/staff/auth/login/",
            login_payload(password="wrong password"),
            content_type="application/json",
            secure=True,
        )
        assert response.status_code == 400

    success = client.post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=True,
    )

    assert success.status_code == 200
