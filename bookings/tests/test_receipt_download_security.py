import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from billing.services import record_successful_checkout_payment
from bookings.models import BookingAuditEvent
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
    return booking.receipt


@pytest.mark.django_db(transaction=True)
def test_valid_token_downloads_pdf_and_audits_without_internal_ids():
    receipt = _receipt("receipt-download")
    token = receipt.issue_download_token()

    from bookings.services.receipts import download_receipt_pdf_for_token

    pdf = download_receipt_pdf_for_token(token)
    assert pdf.startswith(b"%PDF-")
    assert BookingAuditEvent.objects.filter(booking=receipt.booking, reason="receipt_downloaded").count() == 1
    assert receipt.checkout_session_id.encode() not in pdf
    assert receipt.billing_ledger_id.encode() not in pdf


@pytest.mark.django_db(transaction=True)
def test_invalid_and_expired_download_tokens_are_generic():
    receipt = _receipt("receipt-download-expired")
    token = receipt.issue_download_token()
    receipt.download_token_expires_at = timezone.now() - timezone.timedelta(seconds=1)
    receipt.save(update_fields=["download_token_expires_at", "updated_at"])

    from bookings.services.receipts import download_receipt_pdf_for_token

    for value in [token, "guessed-token"]:
        with pytest.raises(ValidationError) as exc:
            download_receipt_pdf_for_token(value)
        assert "receipt unavailable" in str(exc.value).lower()
