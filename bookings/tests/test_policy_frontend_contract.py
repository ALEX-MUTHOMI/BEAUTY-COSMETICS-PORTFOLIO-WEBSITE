import pytest

from bookings.services.legal import LEGAL_FRONTEND_ROUTES


def test_frontend_legal_contract_lists_required_public_routes():
    assert LEGAL_FRONTEND_ROUTES["terms_of_service"] == "/terms-of-service"
    assert LEGAL_FRONTEND_ROUTES["privacy_policy"] == "/privacy-policy"
    assert LEGAL_FRONTEND_ROUTES["booking_policy"] == "/booking-policy"
    assert LEGAL_FRONTEND_ROUTES["cookie_notice"] == "/cookie-notice"
    assert LEGAL_FRONTEND_ROUTES["data_retention_policy"] == "/data-retention-policy"


@pytest.mark.django_db
def test_legal_api_contract_supports_frontend_rendering(client):
    from bookings.services.legal import ensure_default_legal_documents

    ensure_default_legal_documents()
    response = client.get("/api/legal/documents/privacy_policy/", secure=True)

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"]
    assert payload["version"]
    assert payload["effective_at"]
    assert payload["last_updated"]
    assert payload["content_markdown"]
    assert payload["content_html"]
    assert payload["frontend_path"] == "/privacy-policy"
