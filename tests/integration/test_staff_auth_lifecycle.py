import pytest
from django.contrib.auth.models import Permission
from django.test import Client

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_auth_helpers import make_staff
from bookings.tests.test_staff_portal_helpers import staff_contact_url


@pytest.mark.django_db
def test_staff_auth_lifecycle_login_me_reauth_contact_logout():
    booking = create_booking()
    staff = make_staff()
    staff.user_permissions.add(Permission.objects.get(codename="view_staff_contact_details"))
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
    assert client.get("/api/staff/auth/me/", secure=True).status_code == 200
    assert (
        client.post(
            "/api/staff/auth/reauth/",
            {"password": "Correct horse battery staple 2026"},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )
    assert client.post(staff_contact_url(booking), {"reason": "call client"}, secure=True).status_code == 200
    assert client.post("/api/staff/auth/logout/", secure=True).status_code == 200
    assert client.get("/api/staff/auth/me/", secure=True).status_code == 403
