"""Document staff session cookie posture for local HTTP vs TLS desks."""

from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client, override_settings

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_compose_defaults_secure_ssl_redirect_false_for_local_http():
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "SECURE_SSL_REDIRECT=${SECURE_SSL_REDIRECT:-False}" in compose


def test_staging_example_keeps_secure_ssl_redirect_true():
    staging = (REPO_ROOT / ".env.staging.example").read_text(encoding="utf-8")
    assert "SECURE_SSL_REDIRECT=True" in staging


def test_ops_runbook_documents_local_http_requires_ssl_redirect_false():
    runbook = (REPO_ROOT / "docs" / "ops" / "STAFF_PORTAL_PROVISIONING.md").read_text(encoding="utf-8")
    assert "SECURE_SSL_REDIRECT=False" in runbook
    assert "local HTTP" in runbook


@override_settings(
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
def test_local_http_desk_cookie_posture_allows_insecure_cookies():
    """Local HTTP desks: Secure cookies must be off or the browser drops session/CSRF."""
    assert settings.SECURE_SSL_REDIRECT is False
    assert settings.SESSION_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_SECURE is False


@override_settings(
    SECURE_SSL_REDIRECT=True,
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
)
def test_tls_desk_cookie_posture_requires_secure_cookies():
    """Staging/prod TLS: Secure cookies stay on with SSL redirect."""
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True


@pytest.mark.django_db
@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
def test_staff_login_sets_session_cookie_on_http_when_secure_flags_off():
    make_staff()
    client = Client()
    response = client.post(
        "/api/staff/auth/login/",
        login_payload(),
        content_type="application/json",
        secure=False,
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
    assert session_cookie is not None
    assert session_cookie["secure"] is False or session_cookie["secure"] == ""
