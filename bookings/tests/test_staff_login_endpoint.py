import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_customer, make_staff


@pytest.mark.django_db
def test_staff_login_endpoint_cookie_session_generic_errors_and_non_staff_rejection():
    make_staff()
    make_customer()

    client = Client()
    response = client.post("/api/staff/auth/login/", login_payload(), content_type="application/json", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["display_name"]
    assert "session" not in str(payload).lower()
    assert "id" not in payload
    assert client.session.session_key

    invalid = Client().post(
        "/api/staff/auth/login/",
        login_payload(password="wrong password"),
        content_type="application/json",
        secure=True,
    )
    non_staff = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="staff-auth-customer@example.com"),
        content_type="application/json",
        secure=True,
    )

    assert invalid.status_code == non_staff.status_code == 400
    assert invalid.json() == non_staff.json() == {"detail": "Invalid credentials."}


@pytest.mark.django_db
def test_staff_google_start_is_safe_when_not_configured():
    response = Client().get("/api/staff/auth/google/start/?next=/staff/portal", secure=True)
    assert response.status_code == 503
    assert response.json() == {"detail": "Staff Google sign-in is not configured."}
