import pytest
from django.core.exceptions import ValidationError

from bookings.models import BookingPolicyAcceptance, LegalDocument
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, activate_legal_document, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking


@pytest.mark.django_db(transaction=True)
def test_policy_update_requires_new_active_version_for_future_checkout_without_mutating_old_acceptance():
    ensure_default_legal_documents()
    first_booking = _held_booking(key="legal-lifecycle-first")
    BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=first_booking.public_id,
        idempotency_key="legal-lifecycle-first-checkout",
        request_context={"policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT}},
    )
    old_acceptance = BookingPolicyAcceptance.objects.get(booking=first_booking)

    next_privacy = LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.PRIVACY,
        version="v-lifecycle-next",
        title="Privacy",
        slug="privacy-next",
        status=LegalDocument.Status.BUSINESS_APPROVED,
        content_markdown="Updated privacy policy.",
    )
    activate_legal_document(next_privacy)

    second_booking = _held_booking(key="legal-lifecycle-second")
    BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=second_booking.public_id,
        idempotency_key="legal-lifecycle-second-checkout",
        request_context={"policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT}},
    )
    new_acceptance = BookingPolicyAcceptance.objects.get(booking=second_booking)

    old_acceptance.refresh_from_db()
    assert old_acceptance.privacy_version != new_acceptance.privacy_version
    assert old_acceptance.privacy_content_hash != new_acceptance.privacy_content_hash


@pytest.mark.django_db(transaction=True)
def test_missing_active_required_policy_fails_closed():
    ensure_default_legal_documents()
    LegalDocument.objects.filter(document_type=LegalDocument.DocumentType.TERMS).update(
        status=LegalDocument.Status.ARCHIVED,
        is_active=False,
    )
    booking = _held_booking(key="legal-lifecycle-missing-active")

    with pytest.raises(ValidationError):
        BookingCheckoutContractService.create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="legal-lifecycle-missing-active-checkout",
            request_context={"policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT}},
        )
