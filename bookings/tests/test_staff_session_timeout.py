from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_staff_me_rejects_idle_session_after_timeout(settings):
    settings.STAFF_SESSION_IDLE_TIMEOUT_SECONDS = 60
    make_staff()
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            login_payload(),
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    session = client.session
    session["staff_last_activity_at"] = (timezone.now() - timedelta(seconds=120)).timestamp()
    session.save()

    response = client.get("/api/staff/auth/me/", secure=True)

    assert response.status_code == 403
    assert response.json() == {"detail": "Staff session expired. Please sign in again."}


@pytest.mark.django_db
def test_staff_me_rejects_session_after_absolute_lifetime(settings):
    settings.STAFF_SESSION_ABSOLUTE_TIMEOUT_SECONDS = 60
    make_staff()
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            login_payload(),
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    session = client.session
    session["staff_auth_at"] = (timezone.now() - timedelta(seconds=120)).timestamp()
    session.save()

    response = client.get("/api/staff/auth/me/", secure=True)

    assert response.status_code == 403
    assert response.json() == {"detail": "Staff session expired. Please sign in again."}
