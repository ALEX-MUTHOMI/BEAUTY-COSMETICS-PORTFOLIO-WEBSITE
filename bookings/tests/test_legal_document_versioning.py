import pytest

from bookings.models import LegalDocument
from bookings.services.legal import activate_legal_document


@pytest.mark.django_db
def test_content_hash_is_stable_and_changes_with_content():
    first = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="v-hash",
        title="Terms",
        slug="terms",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="Same content.",
    )
    second = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="v-hash",
        title="Terms",
        slug="privacy",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="Same content.",
    )

    assert first.content_hash != second.content_hash
    original_hash = first.content_hash
    first.content_markdown = "Changed content."
    first.save()
    assert first.content_hash != original_hash


@pytest.mark.django_db
def test_activate_service_preserves_old_version_for_audit():
    old = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="v1",
        title="Privacy",
        slug="privacy-v1",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="Old privacy.",
    )
    new = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="v2",
        title="Privacy",
        slug="privacy-v2",
        status=LegalDocument.Status.BUSINESS_APPROVED,
        replaces_version="v1",
        content_markdown="New privacy.",
    )

    activate_legal_document(new)

    old.refresh_from_db()
    new.refresh_from_db()
    assert old.status == LegalDocument.Status.ARCHIVED
    assert old.archived_at is not None
    assert new.status == LegalDocument.Status.ACTIVE
    assert new.published_at is not None
