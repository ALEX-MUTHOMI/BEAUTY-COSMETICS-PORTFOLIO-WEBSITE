import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_staff_login_rotates_existing_session_and_logout_invalidates_it():
    make_staff()
    client = Client()
    session = client.session
    session["pre_login_marker"] = "anonymous"
    session.save()
    old_key = client.session.session_key

    login = client.post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=True,
    )
    new_key = client.session.session_key

    assert login.status_code == 200
    assert new_key
    assert new_key != old_key

    assert client.get("/api/staff/auth/me/", secure=True).status_code == 200
    logout = client.post("/api/staff/auth/logout/", secure=True)
    assert logout.status_code == 200
    assert client.get("/api/staff/auth/me/", secure=True).status_code == 403
