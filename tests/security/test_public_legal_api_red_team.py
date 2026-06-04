import pytest

from bookings.models import LegalDocument


@pytest.mark.django_db
def test_invalid_legal_endpoint_returns_generic_error(client):
    response = client.get("/api/legal/documents/../../admin/", secure=True)

    assert response.status_code == 404
    assert "traceback" not in response.content.decode().lower()
    assert "admin" not in response.content.decode().lower()


@pytest.mark.django_db
def test_legal_api_does_not_reflect_script_in_document_type(client):
    response = client.get("/api/legal/documents/%3Cscript%3Ealert(1)%3C/script%3E/", secure=True)

    assert response.status_code == 404
    assert "<script" not in response.content.decode().lower()


@pytest.mark.django_db
def test_archived_policy_cannot_be_accepted_as_current_public_contract(client):
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.BOOKING_POLICY,
        version="archived",
        title="Booking Policy",
        slug="booking-archived",
        status=LegalDocument.Status.ARCHIVED,
        content_markdown="Archived policy.",
    )

    response = client.get("/api/legal/documents/booking_policy/archived/", secure=True)

    assert response.status_code == 404
