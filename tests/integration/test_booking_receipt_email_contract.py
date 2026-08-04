import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt, ReceiptPDFArtifact
from bookings.services.email_provider import FAKE_EMAIL_OUTBOX, reset_fake_email_outbox
from bookings.services.receipt_pdf import ReceiptPDFService
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_booking_checkout_billing_receipt_email_contract(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    reset_fake_email_outbox()
    booking = _held_booking(key="receipt-email-contract")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="receipt-email-contract-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-contract",
        provider_receipt="receipt-contract",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.services.notification_delivery import BookingNotificationDeliveryService
    from bookings.services.receipts import download_receipt_pdf_for_token

    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert BookingNotification.objects.filter(booking=booking).count() == 1

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)
    assert result.sent == 1, (
        "delivery failed: "
        f"sent={result.sent}, failed={result.failed}, skipped={result.skipped}, "
        f"status={notification.status}, "
        f"failure_code={notification.failure_code}, "
        f"failure_reason={notification.last_error_redacted}, "
        f"attempts={notification.attempts}"
    )
    assert result.failed == 0
    assert notification.status == BookingNotification.Status.SENT
    assert notification.failure_code == ""
    assert notification.last_error_redacted == ""

    receipt = BookingReceipt.objects.get(booking=booking)
    artifact = ReceiptPDFArtifact.objects.get(receipt=receipt)
    pdf = ReceiptPDFService.read_artifact(artifact)
    assert artifact.status == ReceiptPDFArtifact.Status.READY
    assert artifact.size_bytes == len(pdf)
    assert 0 < artifact.size_bytes <= int(settings.RECEIPT_PDF_MAX_BYTES)
    assert artifact.sha256_hash
    assert pdf.startswith(b"%PDF-")

    assert len(FAKE_EMAIL_OUTBOX) == 1
    message = FAKE_EMAIL_OUTBOX[0]
    assert message["provider"] == "fake"
    assert len(message["attachments"]) == 1
    attachment = message["attachments"][0]
    assert attachment["filename"].endswith(".pdf")
    assert attachment["content_type"] == "application/pdf"
    assert attachment["size_bytes"] == artifact.size_bytes
    assert attachment["sha256"] == artifact.sha256_hash

    # Duplicate successful callback/confirmation replay must not duplicate trust artifacts or sends.
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert ReceiptPDFArtifact.objects.filter(receipt=receipt).count() == 1
    assert BookingNotification.objects.filter(booking=booking).count() == 1
    duplicate_result = BookingNotificationDeliveryService.send_pending(limit=10)
    assert duplicate_result.sent == 0
    assert duplicate_result.failed == 0
    assert len(FAKE_EMAIL_OUTBOX) == 1

    token = booking.receipt.issue_download_token()
    assert download_receipt_pdf_for_token(token).startswith(b"%PDF-")
