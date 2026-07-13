"""
Staff Auth Fortress (1B + 2A) — TDD security matrix.

1B: provisioned staff only; password and/or Google; never auto-provision.
2A: unlisted portal entry; hard API gates (UI hide is never the sole control).

No happy-path product coverage. Failures here are security regressions.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from bookings.models import StaffSecurityAudit
from bookings.tests.test_b6_helpers import future_monday
from bookings.tests.test_staff_auth_helpers import login_payload, make_staff
from bookings.tests.test_staff_portal_helpers import staff_login

REPO_ROOT = Path(__file__).resolve().parents[2]
GOOGLE_OAUTH_SETTINGS = {
    "STAFF_GOOGLE_OAUTH_CLIENT_ID": "google-client-id",
    "STAFF_GOOGLE_OAUTH_CLIENT_SECRET": "google-secret",
    "STAFF_GOOGLE_OAUTH_REDIRECT_URI": "https://api.example.test/api/staff/auth/google/callback/",
    "STAFF_GOOGLE_OAUTH_TOKEN_URL": "https://oauth2.googleapis.com/token",
    "STAFF_PORTAL_PUBLIC_ORIGIN": "http://127.0.0.1:3000",
}


def _fake_id_token(*, email: str, aud: str = "google-client-id") -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
    payload = (
        base64.urlsafe_b64encode(
            json.dumps(
                {
                    "email": email,
                    "email_verified": True,
                    "aud": aud,
                    "iss": "https://accounts.google.com",
                }
            ).encode()
        )
        .decode()
        .rstrip("=")
    )
    return f"{header}.{payload}.sig"


@pytest.mark.django_db
def test_1b_password_login_rejects_deactivated_staff():
    user = make_staff(email="fortress-deactivated@example.com")
    user.is_active = False
    user.save(update_fields=["is_active"])

    response = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="fortress-deactivated@example.com"),
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials."}


@pytest.mark.django_db
def test_1b_password_login_rejects_non_staff_with_same_body_as_bad_password():
    make_staff(email="fortress-staff@example.com")
    User = get_user_model()
    User.objects.create_user(
        email="fortress-guest@example.com",
        password="Correct horse battery staple 2026",
        phone_number="+254700000901",
        is_staff=False,
    )

    bad = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="fortress-staff@example.com", password="wrong"),
        content_type="application/json",
        secure=True,
    )
    guest = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="fortress-guest@example.com"),
        content_type="application/json",
        secure=True,
    )
    assert bad.status_code == guest.status_code == 400
    assert bad.json() == guest.json() == {"detail": "Invalid credentials."}


@pytest.mark.django_db
@override_settings(**GOOGLE_OAUTH_SETTINGS)
def test_1b_google_callback_rejects_unprovisioned_and_audits(monkeypatch, client):
    client.get("/api/staff/auth/google/start/", secure=True)
    state = client.session["staff_google_oauth_state"]
    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {"id_token": _fake_id_token(email="random-gmail@example.com")},
    )

    before = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_FAILURE).count()
    response = client.get(
        f"/api/staff/auth/google/callback/?code=auth-code&state={state}",
        secure=True,
    )
    assert response.status_code == 302
    assert "signin=unavailable" in response["Location"]
    assert "_auth_user_id" not in client.session

    failures = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_FAILURE)
    assert failures.count() == before + 1
    meta = failures.order_by("-id").first().metadata_redacted or {}
    assert meta.get("reason") == "staff_not_provisioned"
    assert meta.get("provider") == "google"
    serialized = str(meta).lower()
    assert "password" not in serialized
    assert "authorization_code" not in serialized
    assert "auth-code" not in serialized


@pytest.mark.django_db
@override_settings(**GOOGLE_OAUTH_SETTINGS)
def test_1b_google_callback_rejects_deactivated_provisioned_staff(monkeypatch, client):
    user = make_staff(email="fortress-oauth-off@example.com")
    user.is_active = False
    user.save(update_fields=["is_active"])

    client.get("/api/staff/auth/google/start/", secure=True)
    state = client.session["staff_google_oauth_state"]
    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {
            "id_token": _fake_id_token(email="fortress-oauth-off@example.com"),
        },
    )
    response = client.get(
        f"/api/staff/auth/google/callback/?code=auth-code&state={state}",
        secure=True,
    )
    assert response.status_code == 302
    assert "signin=unavailable" in response["Location"]
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
@override_settings(**GOOGLE_OAUTH_SETTINGS)
def test_1b_google_callback_logs_in_provisioned_staff_only(monkeypatch, client):
    make_staff(email="fortress-oauth-ok@example.com")
    client.get("/api/staff/auth/google/start/?next=/staff/dashboard", secure=True)
    state = client.session["staff_google_oauth_state"]
    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {
            "id_token": _fake_id_token(email="fortress-oauth-ok@example.com"),
        },
    )
    response = client.get(
        f"/api/staff/auth/google/callback/?code=auth-code&state={state}",
        secure=True,
    )
    assert response.status_code == 302
    assert response["Location"] == "http://127.0.0.1:3000/staff/dashboard"
    assert "_auth_user_id" in client.session

    me = client.get("/api/staff/auth/me/", secure=True)
    assert me.status_code == 200
    body = me.json()
    assert body.get("display_name")
    assert "session" not in str(body).lower()


@pytest.mark.django_db
def test_2a_unauthenticated_staff_apis_never_leak_booking_payload():
    """Guessing /staff URLs or APIs must not return PII without a staff session."""
    paths = [
        f"/api/staff/bookings/schedule/?date={future_monday().date().isoformat()}",
        "/api/staff/bookings/search/?q=abc",
        "/api/staff/auth/me/",
        "/api/staff/bookings/assignable/",
    ]
    anonymous = Client()
    for path in paths:
        response = anonymous.get(path, secure=True)
        assert response.status_code in {401, 403}, path
        text = response.content.decode("utf-8", errors="ignore").lower()
        assert "phone" not in text or "invalid" in text or "credential" in text or "session" in text
        assert "traceback" not in text
        assert "+254" not in text


@pytest.mark.django_db
def test_2a_customer_session_cannot_use_staff_schedule():
    from bookings.tests.test_staff_portal_helpers import make_customer_user

    path = f"/api/staff/bookings/schedule/?date={future_monday().date().isoformat()}"
    client = Client()
    client.force_login(make_customer_user())
    response = client.get(path, secure=True)
    assert response.status_code in {401, 403}
    assert "+254" not in response.content.decode("utf-8", errors="ignore")


@pytest.mark.django_db
def test_2a_beautician_cannot_hit_payments_desk_without_permission():
    """UI may hide Pay; API must still deny without view_staff_payments_desk."""
    client = Client()
    staff_login(client, permissions=["view_staff_portal", "view_staff_booking"])
    # Payments desk is a page; related APIs that require payments desk / receipt must stay gated.
    # Schedule is allowed with view_staff_booking — assert receipt PDF stays locked.
    from bookings.tests.test_booking_checkout_contract import _held_booking
    from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
    from bookings.tests.test_staff_portal_helpers import mark_confirmed

    booking = mark_confirmed(_held_booking(key="fortress-receipt-deny"))
    _confirm_paid_booking(booking)
    response = client.get(
        f"/api/staff/bookings/{booking.public_id}/receipt.pdf",
        secure=True,
    )
    assert response.status_code in {401, 403}


def test_2a_public_chrome_has_no_staff_nav_link_and_robots_disallow():
    footer = (REPO_ROOT / "frontend" / "components" / "SiteFooter.vue").read_text(encoding="utf-8")
    assert "/staff/login" not in footer
    assert "Staff login" not in footer

    robots = (REPO_ROOT / "frontend" / "public" / "robots.txt").read_text(encoding="utf-8")
    assert "Disallow: /staff" in robots or "Disallow: /staff/" in robots
