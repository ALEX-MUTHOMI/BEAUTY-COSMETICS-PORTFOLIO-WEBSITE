import pytest
from django.core.management import call_command

from bookings.models import LegalDocument


@pytest.mark.django_db
def test_seed_legal_documents_creates_required_docs_without_auto_activation():
    call_command("seed_legal_documents")

    document_types = set(LegalDocument.objects.values_list("document_type", flat=True))
    assert LegalDocument.DocumentType.TERMS in document_types
    assert LegalDocument.DocumentType.PRIVACY in document_types
    assert LegalDocument.DocumentType.BOOKING_POLICY in document_types
    assert LegalDocument.DocumentType.COOKIE_NOTICE in document_types
    assert LegalDocument.DocumentType.DATA_RETENTION in document_types
    assert "legal_review_notes" not in document_types
    assert not LegalDocument.objects.filter(status=LegalDocument.Status.ACTIVE).exists()


@pytest.mark.django_db
def test_seed_legal_documents_is_idempotent_and_can_activate_explicitly():
    call_command("seed_legal_documents", "--activate")
    first_count = LegalDocument.objects.count()
    call_command("seed_legal_documents", "--activate")

    assert LegalDocument.objects.count() == first_count
    assert LegalDocument.objects.filter(status=LegalDocument.Status.ACTIVE).count() == 5
