import pytest
from django.apps import apps
from django.test import Client, override_settings

from bookings.services.staff_auth import LOGIN_FAILURE_REASON_INVALID_CREDENTIALS
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
    failure = events[0]
    assert failure.metadata_redacted.get("reason") == LOGIN_FAILURE_REASON_INVALID_CREDENTIALS
    assert failure.metadata_redacted.get("login_failed") is True
    serialized = " ".join(str(event.metadata_redacted) for event in events)
    assert "wrong password" not in serialized
    assert "Correct horse" not in serialized
    assert "203.0.113.44" not in serialized
    assert all(event.ip_hash_hmac for event in events)


@pytest.mark.django_db
@override_settings(SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
def test_staff_login_csrf_failure_audits_transport_or_csrf_reason():
    """Missing CSRF on staff login must audit login_failed — never look like bad credentials alone."""
    make_staff()
    client = Client(enforce_csrf_checks=True, REMOTE_ADDR="203.0.113.50")
    response = client.post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=False,
    )
    assert response.status_code == 403

    audit_model = apps.get_model("bookings", "StaffSecurityAudit")
    events = list(audit_model.objects.filter(event_type="login_failure"))
    assert len(events) == 1
    reason = events[0].metadata_redacted.get("reason")
    assert reason in {"csrf", "session", "transport"}
    assert events[0].metadata_redacted.get("login_failed") is True
    blob = str(events[0].metadata_redacted).lower()
    assert "wrong password" not in blob
    assert "correct horse" not in blob
