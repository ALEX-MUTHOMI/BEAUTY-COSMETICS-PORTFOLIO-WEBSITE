from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from billing.services import record_successful_checkout_payment
from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirmed_receipt(key="pdf-generation"):
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
def test_receipt_pdf_bytes_are_generated_from_safe_snapshot():
    receipt = _confirmed_receipt("pdf-safe")

    from bookings.services.receipt_pdf import ReceiptPDFService

    pdf = ReceiptPDFService.generate_pdf(receipt)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) < 120_000
    assert receipt.receipt_number.encode() in pdf
    assert b"Booking Payment Receipt" in pdf
    assert b"2500.00" in pdf
    assert b"KES" in pdf
    assert b"grace@example.com" not in pdf
    assert b"+254712345678" not in pdf
    assert str(receipt.booking.id).encode() not in pdf
    assert receipt.checkout_session_id.encode() not in pdf
    assert receipt.billing_ledger_id.encode() not in pdf
    assert b"receipt-pdf-safe" not in pdf


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_rejects_unconfirmed_or_manual_review_receipts():
    receipt = _confirmed_receipt("pdf-reject")
    receipt.booking.status = Booking.Status.PAYMENT_FAILED
    receipt.booking.save(update_fields=["status", "updated_at"])

    from bookings.services.receipt_pdf import ReceiptPDFService

    with pytest.raises(ValidationError):
        ReceiptPDFService.generate_pdf(receipt)

    receipt.booking.status = Booking.Status.CONFIRMED
    receipt.booking.confirmed_at = timezone.now() - timedelta(minutes=1)
    receipt.booking.save(update_fields=["status", "confirmed_at", "updated_at"])
    assert ReceiptPDFService.generate_pdf(receipt).startswith(b"%PDF-")


@pytest.mark.django_db(transaction=True)
def test_pdf_generation_failure_records_failed_status_without_deconfirming(monkeypatch):
    receipt = _confirmed_receipt("pdf-failure")

    from bookings.services import receipt_pdf

    monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", lambda _lines: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(RuntimeError):
        receipt_pdf.ReceiptPDFService.generate_pdf(receipt)

    receipt.refresh_from_db()
    receipt.booking.refresh_from_db()
    assert receipt.pdf_status == "failed"
    assert receipt.booking.status == Booking.Status.CONFIRMED
