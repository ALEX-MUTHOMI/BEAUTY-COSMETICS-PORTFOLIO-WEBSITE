import pytest
from django.urls import reverse

from bookings.models import LegalDocument
from bookings.services.legal import ensure_default_legal_documents


@pytest.mark.django_db
def test_public_legal_list_returns_active_required_documents(client):
    ensure_default_legal_documents()

    response = client.get(reverse("legal-document-list"), secure=True)

    assert response.status_code == 200
    payload = response.json()
    types = {item["document_type"] for item in payload["results"]}
    assert LegalDocument.DocumentType.TERMS in types
    assert LegalDocument.DocumentType.PRIVACY in types
    assert LegalDocument.DocumentType.BOOKING_POLICY in types
    assert all("id" not in item and "public_id" not in item for item in payload["results"])


@pytest.mark.django_db
def test_public_legal_invalid_type_is_generic_404(client):
    response = client.get(reverse("legal-document-detail", kwargs={"document_type": "not_real"}), secure=True)

    assert response.status_code == 404
    assert "Legal document is unavailable" in response.json()["detail"]


@pytest.mark.django_db
def test_public_legal_inactive_version_is_hidden(client):
    ensure_default_legal_documents()
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="old",
        title="Old Terms",
        slug="old-terms",
        status=LegalDocument.Status.ARCHIVED,
        content_markdown="Old terms.",
    )

    response = client.get(
        reverse("legal-document-version", kwargs={"document_type": "terms_of_service", "version": "old"}),
        secure=True,
    )

    assert response.status_code == 404
