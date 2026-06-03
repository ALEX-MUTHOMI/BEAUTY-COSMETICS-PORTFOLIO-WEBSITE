import pytest

from bookings.models import BookingPolicyAcceptance, LegalDocument
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking


@pytest.mark.django_db
def test_policy_acceptance_preserves_old_versions_after_policy_rotation():
    ensure_default_legal_documents()
    booking = _held_booking(key="policy-audit-old-version")

    BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="policy-audit-old-version-checkout",
        request_context={
            "policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT},
        },
    )
    acceptance = BookingPolicyAcceptance.objects.get(booking=booking)
    old_terms_version = acceptance.terms_version

    LegalDocument.objects.filter(document_type=LegalDocument.DocumentType.TERMS).update(is_active=False)
    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="v2026.07-draft",
        title="Terms of Service",
        content_markdown="Draft for legal review before production. Updated terms.",
        is_active=True,
    )

    acceptance.refresh_from_db()
    assert acceptance.terms_version == old_terms_version
