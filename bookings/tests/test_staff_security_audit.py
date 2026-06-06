import pytest
from django.apps import apps
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_staff_auth_security_events_are_audited_without_passwords_or_raw_ip():
    make_staff()
    client = Client(REMOTE_ADDR="203.0.113.44", HTTP_USER_AGENT="staff-browser/1.0")

    client.post(
        "/api/staff/auth/login/",
        login_payload(password="wrong password"),
        content_type="application/json",
        secure=True,
    )
    client.post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=True,
    )
    client.post("/api/staff/auth/logout/", secure=True)

    audit_model = apps.get_model("bookings", "StaffSecurityAudit")
    events = list(audit_model.objects.order_by("created_at"))

    assert [event.event_type for event in events] == ["login_failure", "login_success", "logout"]
    serialized = " ".join(str(event.metadata_redacted) for event in events)
    assert "wrong password" not in serialized
    assert "Correct horse" not in serialized
    assert "203.0.113.44" not in serialized
    assert all(event.ip_hash_hmac for event in events)
