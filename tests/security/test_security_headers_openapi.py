import json

import pytest
from django.conf import settings
from django.test import override_settings

SECURITY_HEADER_PATHS = (
    "/health/",
    "/api/health-check/",
    "/api/csrf/",
    "/api/unknown-security-probe/",
)


@pytest.mark.parametrize("path", SECURITY_HEADER_PATHS)
def test_security_headers_are_present_on_public_and_error_responses(client, path):
    response = client.get(path, secure=True)

    assert response["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]
    assert "object-src 'none'" in response["Content-Security-Policy"]
    assert response["Referrer-Policy"] in {"same-origin", "strict-origin-when-cross-origin"}
    expected_corp = "cross-origin" if path.startswith("/api/") else "same-origin"
    assert response["Cross-Origin-Resource-Policy"] == expected_corp
    assert "geolocation=()" in response["Permissions-Policy"]


@pytest.mark.parametrize("path", ("/health/", "/api/health-check/", "/api/csrf/"))
def test_sensitive_public_utility_responses_are_not_cacheable(client, path):
    response = client.get(path, secure=True)

    assert "no-store" in response["Cache-Control"]
    assert response["Pragma"] == "no-cache"
    assert response["Expires"] == "0"


def test_csrf_bootstrap_cookie_policy_is_explicit_for_spa_flow(client):
    response = client.get("/api/csrf/", secure=True)
    csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME)

    assert settings.CSRF_COOKIE_HTTPONLY is False
    assert settings.CSRF_COOKIE_SAMESITE == "Strict"
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert csrf_cookie is not None
    assert csrf_cookie["httponly"] == ""
    assert csrf_cookie["samesite"] == "Strict"


@override_settings(ENABLE_OPENAPI_SCHEMA=True)
def test_openapi_schema_endpoint_returns_sanitized_schema(client):
    response = client.get("/api/schema/", secure=True, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["openapi"].startswith("3.")
    assert "/admin/" not in json.dumps(payload).lower()
    assert "/api/bookings/" in json.dumps(payload)
    assert response["X-Content-Type-Options"] == "nosniff"
    assert "no-store" in response["Cache-Control"]

    serialized = json.dumps(payload).lower()
    banned_markers = (
        "consumer_secret",
        "consumer key",
        "consumer_key",
        "passkey",
        "password",
        "access_token",
        "access token",
        "refresh_token",
        "refresh token",
        "sessionid",
        "csrftoken",
        "receipt_token",
        "receipt token",
        "storage_key",
        "storage key",
        "private_bucket",
        "private bucket",
        "raw_provider_payload",
        "raw callback",
        "provider payload",
        "checkout_id",
        "ledger_id",
        "token hash",
        "phone=",
        "email=",
        "secret",
        "merchant request",
        "checkoutrequestid",
        "merchantrequestid",
        "mpesareceiptnumber",
    )
    for marker in banned_markers:
        assert marker not in serialized


@override_settings(ENABLE_OPENAPI_SCHEMA=False)
def test_openapi_schema_endpoint_is_disabled_when_setting_is_off(client):
    response = client.get("/api/schema/", secure=True)

    assert response.status_code == 404


@override_settings(SECURITY_SCAN_MODE=False)
def test_turnstile_non_json_response_fails_closed_without_pii_leak(client, monkeypatch, caplog):
    class NonJsonResponse:
        def json(self):
            raise ValueError("provider returned non-json body")

    monkeypatch.setattr("users.services.requests.post", lambda *args, **kwargs: NonJsonResponse())

    response = client.post(
        "/api/auth/request-otp/",
        {"email": "victim@example.com", "turnstile_token": "scanner-token"},
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 400
    assert "victim@example.com" not in caplog.text
    assert "scanner-token" not in caplog.text
    assert "provider returned non-json body" not in caplog.text


@override_settings(SECURITY_SCAN_MODE=True)
def test_security_scan_mode_fails_turnstile_closed_without_external_call(client, monkeypatch):
    def blocked_external_call(*_args, **_kwargs):
        raise AssertionError("security scan mode must not call external Turnstile")

    monkeypatch.setattr("users.services.requests.post", blocked_external_call)

    response = client.post(
        "/api/auth/request-otp/",
        {"email": "scanner@example.com", "turnstile_token": "scanner-token"},
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 400


@override_settings(SECURITY_SCAN_MODE=True)
def test_otp_throttle_handles_json_string_body_without_500(client):
    response = client.post(
        "/api/auth/request-otp/",
        '"scanner-generated-string"',
        content_type="application/json",
        secure=True,
    )

    assert response.status_code in {400, 415}
