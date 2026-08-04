import pytest
from django.core.exceptions import ValidationError

from billing.services import record_successful_checkout_payment
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _receipt(key):
    booking = _held_booking(key=key)
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"{key}-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference=f"provider-{key}",
        provider_receipt=f"receipt-{key}",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    from bookings.models import BookingReceipt

    return BookingReceipt.objects.get(booking=booking)


@pytest.mark.django_db(transaction=True)
def test_receipt_download_token_is_hashed_and_generic_errors_are_used():
    receipt = _receipt("download-security")
    raw_token = receipt.issue_download_token()
    receipt.refresh_from_db()

    assert raw_token
    assert raw_token not in receipt.download_token_hash
    assert receipt.download_token_hash

    from bookings.services.receipts import get_receipt_for_download_token

    assert get_receipt_for_download_token(raw_token).id == receipt.id
    with pytest.raises(ValidationError) as exc:
        get_receipt_for_download_token("attacker-token")
    assert "receipt unavailable" in str(exc.value).lower()


@pytest.mark.django_db(transaction=True)
def test_receipt_rendering_does_not_reflect_xss_or_internal_identifiers():
    receipt = _receipt("download-xss")
    receipt.booking.customer_profile.full_name_display = "<script>alert(1)</script>"
    receipt.booking.customer_profile.save(update_fields=["full_name_display", "updated_at"])

    from bookings.services.receipts import render_receipt_payload

    payload = render_receipt_payload(receipt)
    rendered = str(payload)
    assert "<script" not in rendered
    assert "grace@example.com" not in rendered
    assert "+254712345678" not in rendered
    assert "***" in rendered
    assert str(receipt.booking.id) not in rendered
    assert str(receipt.id) not in rendered
