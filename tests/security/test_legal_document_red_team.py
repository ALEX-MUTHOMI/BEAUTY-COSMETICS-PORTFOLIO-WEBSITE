import pytest

from bookings.models import LegalDocument


@pytest.mark.django_db
def test_draft_policy_with_xss_payload_is_not_public(client):
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="draft-xss",
        title="Draft Terms",
        slug="draft-xss",
        status=LegalDocument.Status.DRAFT,
        content_markdown="<script>steal()</script>",
    )

    response = client.get("/api/legal/documents/terms_of_service/", secure=True)

    assert response.status_code == 404
    assert "steal" not in response.content.decode()


@pytest.mark.django_db
def test_public_legal_api_leaks_no_internal_identifiers(client):
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="active",
        title="Privacy",
        slug="privacy-active",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="Privacy content.",
    )

    payload = client.get("/api/legal/documents/privacy_policy/", secure=True).json()

    assert "id" not in payload
    assert "public_id" not in payload
    assert "pk" not in payload
