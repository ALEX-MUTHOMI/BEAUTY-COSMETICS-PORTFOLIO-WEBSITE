import pytest
from django.core.exceptions import ValidationError

from bookings.models import BookingPolicyAcceptance
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_checkout_to_booking_policy_acceptance_contract_is_atomic():
    ensure_default_legal_documents()
    booking = _held_booking(key="integration-policy-contract")

    result = BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="integration-policy-contract-checkout",
        request_context={
            "policy_acceptance": {"accepted": True, "checkbox_text": POLICY_ACCEPTANCE_TEXT},
            "ip": "203.0.113.88",
            "user_agent": "pytest",
        },
    )

    session = CheckoutSession.objects.get(id=result["checkout_public_id"])
    acceptance = BookingPolicyAcceptance.objects.get(booking=booking, checkout_session=session)
    assert acceptance.terms_version
    assert acceptance.privacy_version
    assert acceptance.booking_policy_version


@pytest.mark.django_db(transaction=True)
def test_checkout_policy_rejection_creates_no_checkout_session():
    ensure_default_legal_documents()
    booking = _held_booking(key="integration-policy-reject")

    with pytest.raises(ValidationError):
        BookingCheckoutContractService.create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="integration-policy-reject-checkout",
        )

    assert CheckoutSession.objects.count() == 0
