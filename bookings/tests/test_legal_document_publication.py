import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import LegalDocument


@pytest.mark.django_db
def test_active_legal_document_is_public_without_internal_id(client):
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="v-test-active",
        title="Terms of Service",
        slug="terms-of-service",
        status=LegalDocument.Status.ACTIVE,
        legal_review_status=LegalDocument.LegalReviewStatus.PENDING,
        effective_at=timezone.now(),
        published_at=timezone.now(),
        content_markdown="Business-approved terms. Paid bookings are non-refundable.",
    )

    response = client.get(reverse("legal-document-detail", kwargs={"document_type": "terms_of_service"}), secure=True)

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_type"] == "terms_of_service"
    assert payload["version"] == "v-test-active"
    assert payload["content_hash"]
    assert "id" not in payload
    assert "public_id" not in payload


@pytest.mark.django_db
def test_draft_legal_document_is_not_public(client):
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="v-draft",
        title="Privacy Policy",
        slug="privacy-policy",
        status=LegalDocument.Status.DRAFT,
        content_markdown="Draft privacy content.",
    )

    response = client.get(reverse("legal-document-detail", kwargs={"document_type": "privacy_policy"}), secure=True)

    assert response.status_code == 404
    assert "Draft privacy content" not in response.content.decode()


@pytest.mark.django_db
def test_activating_new_policy_archives_prior_active_version():
    old = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.BOOKING_POLICY,
        version="v1",
        title="Booking Policy",
        slug="booking-policy",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="Old booking policy.",
    )

    new = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.BOOKING_POLICY,
        version="v2",
        title="Booking Policy",
        slug="booking-policy-v2",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="New booking policy.",
    )

    old.refresh_from_db()
    new.refresh_from_db()
    assert old.status == LegalDocument.Status.ARCHIVED
    assert old.is_active is False
    assert new.status == LegalDocument.Status.ACTIVE
    assert new.is_active is True
