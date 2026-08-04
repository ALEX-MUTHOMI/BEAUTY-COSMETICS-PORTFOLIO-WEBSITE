import pytest
from django.core.exceptions import ValidationError

from bookings.models import LegalDocument
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking


@pytest.mark.django_db
def test_inactive_policy_version_cannot_be_used_to_force_checkout():
    ensure_default_legal_documents()
    LegalDocument.objects.filter(document_type=LegalDocument.DocumentType.TERMS).update(is_active=False)
    booking = _held_booking(key="inactive-policy-red-team")

    with pytest.raises(ValidationError):
        BookingCheckoutContractService.create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="inactive-policy-red-team-checkout",
            request_context={
                "policy_acceptance": {
                    "accepted": True,
                    "checkbox_text": POLICY_ACCEPTANCE_TEXT,
                    "terms_version": "v0",
                }
            },
        )
