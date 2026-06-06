from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.utils import timezone

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_auth_helpers import make_staff
from bookings.tests.test_staff_portal_helpers import staff_contact_url

STAFF_PASSWORD = "Correct horse battery staple 2026"


@pytest.mark.django_db
def test_contact_reveal_requires_recent_password_reauth(settings):
    settings.STAFF_RECENT_AUTH_TIMEOUT_SECONDS = 60
    booking = create_booking()
    staff = make_staff(password=STAFF_PASSWORD)
    staff.user_permissions.add(Permission.objects.get(codename="view_staff_contact_details"))
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            {"email": staff.email, "password": STAFF_PASSWORD},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    blocked = client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True)
    assert blocked.status_code == 403
    assert blocked.json() == {"detail": "Recent staff password confirmation required."}

    reauth = client.post(
        "/api/staff/auth/reauth/",
        {"password": STAFF_PASSWORD},
        content_type="application/json",
        secure=True,
    )
    allowed = client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True)

    assert reauth.status_code == 200
    assert allowed.status_code == 200

    session = client.session
    session["staff_recent_auth_at"] = (timezone.now() - timedelta(seconds=120)).timestamp()
    session.save()
    expired = client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True)
    assert expired.status_code == 403


@pytest.mark.django_db
def test_recent_reauth_does_not_bypass_contact_permission():
    booking = create_booking()
    staff = make_staff(password=STAFF_PASSWORD)
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            {"email": staff.email, "password": STAFF_PASSWORD},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/staff/auth/reauth/",
            {"password": STAFF_PASSWORD},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    response = client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True)

    assert response.status_code == 403
