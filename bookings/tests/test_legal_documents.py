import pytest

from bookings.models import LegalDocument
from bookings.services.legal import ensure_default_legal_documents, get_active_required_documents


@pytest.mark.django_db
def test_active_legal_documents_are_versioned_and_hashed():
    docs = ensure_default_legal_documents()

    assert {doc.document_type for doc in docs} >= {
        LegalDocument.DocumentType.TERMS,
        LegalDocument.DocumentType.PRIVACY,
        LegalDocument.DocumentType.BOOKING_POLICY,
    }
    assert all(doc.version for doc in docs)
    assert all(doc.content_hash for doc in docs)


@pytest.mark.django_db
def test_prior_policy_hash_changes_when_content_changes():
    [doc] = [
        item for item in ensure_default_legal_documents() if item.document_type == LegalDocument.DocumentType.TERMS
    ]
    original_hash = doc.content_hash

    doc.content_markdown += "\nMaterial update."
    doc.save()

    assert doc.content_hash != original_hash
    assert get_active_required_documents()[LegalDocument.DocumentType.TERMS].version == doc.version
