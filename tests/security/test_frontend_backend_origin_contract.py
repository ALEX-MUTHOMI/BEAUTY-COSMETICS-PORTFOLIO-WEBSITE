"""
Frontend↔backend origin trust contract (Nuxt :3000 ↔ Django :8000).

Attacker goals covered:
- Spoof Origin to steal credentialed responses
- Host-header injection / domain reroute
- CSRF-less cross-site POST against money-path endpoints
"""

from __future__ import annotations

from django.conf import settings
from django.test import Client, override_settings


def test_compose_default_cors_and_csrf_origins_include_localhost_3000():
    """Local Nuxt must be an explicit trusted peer — never wildcard."""
    assert "*" not in settings.CORS_ALLOWED_ORIGINS
    assert "*" not in settings.CSRF_TRUSTED_ORIGINS
    assert "http://localhost:3000" in settings.CORS_ALLOWED_ORIGINS
    assert "http://localhost:3000" in settings.CSRF_TRUSTED_ORIGINS
    assert settings.CORS_ALLOW_CREDENTIALS is True
    assert settings.CSRF_COOKIE_SAMESITE == "Strict"


def test_disallowed_origin_does_not_receive_cors_allow_origin(client):
    response = client.get(
        "/api/csrf/",
        secure=True,
        HTTP_ORIGIN="https://evil.example",
    )
    # Request may succeed for same-site bootstrap, but must not grant evil Origin.
    assert response.get("Access-Control-Allow-Origin") != "https://evil.example"


def test_allowed_localhost_origin_is_reflected_for_credentialed_cors(client):
    response = client.get(
        "/api/csrf/",
        secure=True,
        HTTP_ORIGIN="http://localhost:3000",
    )
    assert response.status_code == 200
    assert response.get("Access-Control-Allow-Origin") == "http://localhost:3000"
    assert response.get("Access-Control-Allow-Credentials") == "true"


def test_host_header_injection_is_rejected():
    """Forged Host must not be accepted when not in ALLOWED_HOSTS."""
    client = Client()
    response = client.get(
        "/api/csrf/",
        secure=True,
        HTTP_HOST="attacker.trycloudflare.com",
    )
    assert response.status_code == 400


@override_settings(ALLOWED_HOSTS=["localhost", "127.0.0.1", "testserver", "web"])
def test_legitimate_host_is_accepted(client):
    response = client.get("/api/csrf/", secure=True, HTTP_HOST="localhost")
    assert response.status_code == 200


def test_credentialed_booking_hold_without_csrf_is_forbidden():
    """Cross-site style POST without CSRF token must fail closed."""
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        "/api/bookings/holds/",
        data="{}",
        content_type="application/json",
        secure=True,
        HTTP_ORIGIN="http://localhost:3000",
    )
    assert response.status_code in {403, 400, 401}
    assert response.status_code != 201
