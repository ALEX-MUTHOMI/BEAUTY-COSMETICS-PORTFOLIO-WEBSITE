import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import make_customer


@pytest.mark.django_db
def test_customer_session_and_otp_flags_cannot_access_staff_auth_or_portal():
    customer = make_customer()
    client = Client()
    client.force_login(customer)
    session = client.session
    session["customer_otp_verified"] = True
    session["remember_device_verified"] = True
    session.save()

    me = client.get("/api/staff/auth/me/", secure=True)
    schedule = client.get("/api/staff/bookings/schedule/?date=2026-06-06", secure=True)
    reauth = client.post(
        "/api/staff/auth/reauth/",
        {"password": "Correct horse battery staple 2026"},
        content_type="application/json",
        secure=True,
    )

    assert me.status_code == 403
    assert schedule.status_code == 403
    assert reauth.status_code == 403
