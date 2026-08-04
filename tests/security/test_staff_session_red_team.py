import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_old_staff_session_fails_after_password_reset():
    staff = make_staff()
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            {"email": staff.email, "password": "Correct horse battery staple 2026"},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    from bookings.services.staff_auth import STAFF_PASSWORD_RESET_OUTBOX

    STAFF_PASSWORD_RESET_OUTBOX.clear()
    Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": staff.email},
        content_type="application/json",
        secure=True,
    )
    Client().post(
        "/api/staff/auth/password-reset/confirm/",
        {"token": STAFF_PASSWORD_RESET_OUTBOX[0]["token"], "new_password": "Reset invalidates session phrase 2026"},
        content_type="application/json",
        secure=True,
    )

    assert client.get("/api/staff/auth/me/", secure=True).status_code == 403
