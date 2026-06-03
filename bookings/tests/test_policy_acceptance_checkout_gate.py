import pytest
from django.core.exceptions import ValidationError

from bookings.models import BookingPolicyAcceptance
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.test_booking_checkout_contract import _held_booking


@pytest.mark.django_db
def test_checkout_creation_blocks_without_policy_acceptance():
    ensure_default_legal_documents()
    booking = _held_booking(key="policy-gate-missing")

    with pytest.raises(ValidationError):
        BookingCheckoutContractService.create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="policy-gate-missing-checkout",
        )


@pytest.mark.django_db
def test_checkout_creation_records_policy_acceptance_without_raw_ip_or_user_agent():
    ensure_default_legal_documents()
    booking = _held_booking(key="policy-gate-accepted")

    BookingCheckoutContractService.create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="policy-gate-accepted-checkout",
        request_context={
            "ip": "203.0.113.55",
            "user_agent": "Mozilla/5.0 raw-agent",
            "policy_acceptance": {
                "accepted": True,
                "checkbox_text": POLICY_ACCEPTANCE_TEXT,
                "locale": "en-KE",
                "timezone_name": "Africa/Nairobi",
                "country_hint": "KE",
            },
        },
    )

    acceptance = BookingPolicyAcceptance.objects.get(booking=booking)
    assert acceptance.terms_version
    assert acceptance.privacy_version
    assert acceptance.booking_policy_version
    assert acceptance.acceptance_text_hash
    assert acceptance.ip_hash_hmac
    assert acceptance.user_agent_hash_hmac
    assert "203.0.113.55" not in str(acceptance.__dict__)
    assert "raw-agent" not in str(acceptance.__dict__)
