import base64
import json

import pytest
from django.test import Client, override_settings

from bookings.tests.test_staff_auth_helpers import make_staff


def _fake_id_token(*, email: str, aud: str, iss: str = "https://accounts.google.com") -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
    payload = (
        base64.urlsafe_b64encode(json.dumps({"email": email, "email_verified": True, "aud": aud, "iss": iss}).encode())
        .decode()
        .rstrip("=")
    )
    return f"{header}.{payload}.sig"


APPLE_OAUTH_SETTINGS = {
    "STAFF_APPLE_OAUTH_CLIENT_ID": "apple-client-id",
    "STAFF_APPLE_OAUTH_CLIENT_SECRET": "apple-secret",
    "STAFF_APPLE_OAUTH_REDIRECT_URI": "https://api.example.test/api/staff/auth/apple/callback/",
    "STAFF_APPLE_OAUTH_TOKEN_URL": "https://appleid.apple.com/auth/token",
    "STAFF_PORTAL_PUBLIC_ORIGIN": "http://127.0.0.1:3000",
}


@pytest.mark.django_db
def test_staff_oauth_providers_booleans_only():
    response = Client().get("/api/staff/auth/providers/", secure=True)
    assert response.status_code == 200
    assert response.json() == {"google": False, "apple": False}


@pytest.mark.django_db
@override_settings(
    STAFF_GOOGLE_OAUTH_CLIENT_ID="google-client-id",
    STAFF_GOOGLE_OAUTH_CLIENT_SECRET="google-secret",
    STAFF_GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/google/callback/",
    STAFF_GOOGLE_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token",
    STAFF_PORTAL_PUBLIC_ORIGIN="http://localhost:3000",
)
def test_staff_google_start_redirects_when_fully_configured(client):
    response = client.get("/api/staff/auth/google/start/?next=https://evil.example", secure=True)
    assert response.status_code == 302
    assert "accounts.google.com" in response["Location"]
    assert client.session["staff_google_oauth_next"] == "/staff/dashboard"


@pytest.mark.django_db
@override_settings(
    STAFF_GOOGLE_OAUTH_CLIENT_ID="google-client-id",
    STAFF_GOOGLE_OAUTH_CLIENT_SECRET="google-secret",
    STAFF_GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/google/callback/",
    STAFF_GOOGLE_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token",
    STAFF_PORTAL_PUBLIC_ORIGIN="http://localhost:3000",
)
def test_staff_google_callback_rejects_bad_state(client):
    client.get("/api/staff/auth/google/start/?next=/staff/dashboard", secure=True)
    response = client.get(
        "/api/staff/auth/google/callback/?code=abc&state=wrong",
        secure=True,
    )
    assert response.status_code == 302
    assert response["Location"] == "http://localhost:3000/staff/login?signin=unavailable"


@pytest.mark.django_db
@override_settings(
    STAFF_GOOGLE_OAUTH_CLIENT_ID="google-client-id",
    STAFF_GOOGLE_OAUTH_CLIENT_SECRET="google-secret",
    STAFF_GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/google/callback/",
    STAFF_GOOGLE_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token",
    STAFF_PORTAL_PUBLIC_ORIGIN="http://localhost:3000",
)
def test_staff_google_callback_logs_in_existing_staff(monkeypatch, client):
    make_staff(email="oauth-staff@example.com")
    start_response = client.get("/api/staff/auth/google/start/?next=/staff/bookings", secure=True)
    assert start_response.status_code == 302
    state = client.session["staff_google_oauth_state"]

    def fake_exchange(_provider, _code):
        return {
            "id_token": _fake_id_token(email="oauth-staff@example.com", aud="google-client-id"),
        }

    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        fake_exchange,
    )

    response = client.get(
        f"/api/staff/auth/google/callback/?code=auth-code&state={state}",
        secure=True,
    )
    assert response.status_code == 302
    assert response["Location"] == "http://localhost:3000/staff/bookings"
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
@override_settings(
    STAFF_GOOGLE_OAUTH_CLIENT_ID="google-client-id",
    STAFF_GOOGLE_OAUTH_CLIENT_SECRET="google-secret",
    STAFF_GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/google/callback/",
    STAFF_GOOGLE_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token",
    STAFF_PORTAL_PUBLIC_ORIGIN="http://localhost:3000",
)
def test_staff_google_callback_rejects_unknown_email(monkeypatch, client):
    from bookings.models import StaffSecurityAudit

    client.get("/api/staff/auth/google/start/", secure=True)
    state = client.session["staff_google_oauth_state"]

    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {
            "id_token": _fake_id_token(email="stranger@example.com", aud="google-client-id"),
        },
    )
    response = client.get(
        f"/api/staff/auth/google/callback/?code=auth-code&state={state}",
        secure=True,
    )
    assert response.status_code == 302
    assert "signin=unavailable" in response["Location"]
    assert "_auth_user_id" not in client.session
    failure = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_FAILURE).latest("id")
    assert failure.metadata_redacted.get("reason") == "staff_not_provisioned"
    assert failure.metadata_redacted.get("provider") == "google"


@pytest.mark.django_db
@override_settings(**APPLE_OAUTH_SETTINGS)
def test_staff_apple_callback_logs_in_existing_staff(monkeypatch, client):
    make_staff(email="apple-staff@example.com")
    start = client.get("/api/staff/auth/apple/start/?next=/staff/dashboard", secure=True)
    assert start.status_code == 302
    state = client.session["staff_apple_oauth_state"]

    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {
            "id_token": _fake_id_token(
                email="apple-staff@example.com",
                aud="apple-client-id",
                iss="https://appleid.apple.com",
            ),
        },
    )
    response = client.post(
        "/api/staff/auth/apple/callback/",
        data={"code": "auth-code", "state": state},
        secure=True,
    )
    assert response.status_code == 302
    assert response["Location"] == "http://127.0.0.1:3000/staff/dashboard"
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
@override_settings(**APPLE_OAUTH_SETTINGS)
def test_staff_apple_callback_rejects_unprovisioned(monkeypatch, client):
    from bookings.models import StaffSecurityAudit

    client.get("/api/staff/auth/apple/start/", secure=True)
    state = client.session["staff_apple_oauth_state"]
    monkeypatch.setattr(
        "bookings.staff_auth_views.exchange_authorization_code",
        lambda _provider, _code: {
            "id_token": _fake_id_token(
                email="stranger-apple@example.com",
                aud="apple-client-id",
                iss="https://appleid.apple.com",
            ),
        },
    )
    response = client.post(
        "/api/staff/auth/apple/callback/",
        data={"code": "auth-code", "state": state},
        secure=True,
    )
    assert response.status_code == 302
    assert "signin=unavailable" in response["Location"]
    assert "_auth_user_id" not in client.session
    failure = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_FAILURE).latest("id")
    assert failure.metadata_redacted.get("reason") == "staff_not_provisioned"
    assert failure.metadata_redacted.get("provider") == "apple"
