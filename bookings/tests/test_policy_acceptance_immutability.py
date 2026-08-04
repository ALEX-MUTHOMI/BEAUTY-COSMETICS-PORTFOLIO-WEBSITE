import pytest

from bookings.models import BookingPolicyAcceptance, LegalDocument
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, activate_legal_document, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking


@pytest.mark.django_db
def test_acceptance_stores_exact_policy_hashes_and_survives_policy_update():
    ensure_default_legal_documents()
    booking = _held_booking(key="policy-immutability")

    BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="policy-immutability-checkout",
        request_context={"policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT}},
    )
    acceptance = BookingPolicyAcceptance.objects.get(booking=booking)
    original_terms_version = acceptance.terms_version
    original_terms_hash = acceptance.terms_content_hash

    next_terms = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="v-next",
        title="Terms",
        slug="terms-next",
        status=LegalDocument.Status.BUSINESS_APPROVED,
        content_markdown="Updated terms. Paid bookings are non-refundable.",
    )
    activate_legal_document(next_terms)

    acceptance.refresh_from_db()
    assert acceptance.terms_version == original_terms_version
    assert acceptance.terms_content_hash == original_terms_hash
    assert acceptance.terms_content_hash != next_terms.content_hash
