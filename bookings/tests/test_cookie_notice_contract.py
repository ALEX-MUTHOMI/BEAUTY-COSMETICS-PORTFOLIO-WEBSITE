import pytest
from django.test import override_settings

from bookings.services.legal import load_legal_markdown_source


def test_cookie_notice_documents_essential_cookies_only():
    content = load_legal_markdown_source("COOKIE_NOTICE.md")

    assert "essential" in content.lower()
    assert "csrf" in content.lower()
    assert "session" in content.lower()
    assert "marketing cookies" in content.lower()
    assert "not currently use analytics or marketing cookies" in content.lower()


@override_settings(DEBUG=False)
def test_production_cookie_settings_are_secure(settings):
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SESSION_COOKIE_SAMESITE in {"Lax", "Strict"}
    assert settings.CSRF_COOKIE_SAMESITE in {"Lax", "Strict"}


@pytest.mark.django_db
def test_customer_action_cookie_contract_contains_no_pii(client):
    response = client.get("/api/bookings/status/not-a-uuid/")
    cookie_dump = " ".join(f"{key}={value.value}" for key, value in response.cookies.items())
    assert "@example.com" not in cookie_dump
    assert "+254" not in cookie_dump
