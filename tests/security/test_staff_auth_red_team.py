import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_customer, make_staff


@pytest.mark.django_db
def test_staff_login_blocks_enumeration_and_non_staff_accounts():
    make_staff()
    make_customer()

    wrong_password = Client().post(
        "/api/staff/auth/login/",
        login_payload(password="wrong password"),
        content_type="application/json",
        secure=True,
    )
    missing = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="not-real@example.com"),
        content_type="application/json",
        secure=True,
    )
    customer = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="staff-auth-customer@example.com"),
        content_type="application/json",
        secure=True,
    )

    assert wrong_password.status_code == missing.status_code == customer.status_code == 400
    assert wrong_password.json() == missing.json() == customer.json() == {"detail": "Invalid credentials."}


@pytest.mark.django_db
def test_staff_login_never_returns_internal_ids_or_tokens():
    make_staff()
    response = Client().post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=True,
    )
    payload = response.json()
    serialized = str(payload).lower()

    assert response.status_code == 200
    assert "token" not in serialized
    assert "session" not in serialized
    assert "password" not in serialized
    assert "id" not in payload
