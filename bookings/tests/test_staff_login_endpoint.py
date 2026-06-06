import pytest
from django.test import Client, override_settings

from bookings.tests.test_staff_auth_helpers import login_payload, make_customer, make_staff


@pytest.mark.django_db
def test_staff_login_endpoint_cookie_session_generic_errors_and_non_staff_rejection():
    make_staff()
    make_customer()

    client = Client()
    response = client.post("/api/staff/auth/login/", login_payload(), content_type="application/json", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["display_name"]
    assert "session" not in str(payload).lower()
    assert "id" not in payload
    assert client.session.session_key

    invalid = Client().post(
        "/api/staff/auth/login/",
        login_payload(password="wrong password"),
        content_type="application/json",
        secure=True,
    )
    non_staff = Client().post(
        "/api/staff/auth/login/",
        login_payload(email="staff-auth-customer@example.com"),
        content_type="application/json",
        secure=True,
    )

    assert invalid.status_code == non_staff.status_code == 400
    assert invalid.json() == non_staff.json() == {"detail": "Invalid credentials."}


@pytest.mark.django_db
def test_staff_google_start_is_safe_when_not_configured():
    response = Client().get("/api/staff/auth/google/start/?next=/staff/portal", secure=True)
    assert response.status_code == 503
    assert response.json() == {"detail": "Staff Google sign-in is not configured."}


@pytest.mark.django_db
def test_staff_apple_start_is_safe_when_not_configured():
    response = Client().get("/api/staff/auth/apple/start/?next=/staff/dashboard", secure=True)
    assert response.status_code == 503
    assert response.json() == {"detail": "Staff Apple sign-in is not configured."}


@pytest.mark.django_db
@override_settings(
    STAFF_GOOGLE_OAUTH_CLIENT_ID="google-client-id",
    STAFF_GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/google/callback/",
)
def test_staff_google_start_redirects_when_configured_and_sanitizes_next():
    client = Client()
    response = client.get("/api/staff/auth/google/start/?next=https://evil.example", secure=True)

    assert response.status_code == 302
    location = response["Location"]
    assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=google-client-id" in location
    assert "redirect_uri=https%3A%2F%2Fapi.example.test%2Fapi%2Fstaff%2Fauth%2Fgoogle%2Fcallback%2F" in location
    assert "response_type=code" in location
    assert "scope=openid+email+profile" in location
    assert "state=" in location
    assert client.session["staff_google_oauth_next"] == "/staff/dashboard"


@pytest.mark.django_db
@override_settings(
    STAFF_APPLE_OAUTH_CLIENT_ID="apple-client-id",
    STAFF_APPLE_OAUTH_REDIRECT_URI="https://api.example.test/api/staff/auth/apple/callback/",
)
def test_staff_apple_start_redirects_when_configured():
    response = Client().get("/api/staff/auth/apple/start/?next=/staff/settings/security", secure=True)

    assert response.status_code == 302
    location = response["Location"]
    assert location.startswith("https://appleid.apple.com/auth/authorize?")
    assert "client_id=apple-client-id" in location
    assert "response_mode=form_post" in location
    assert "state=" in location
