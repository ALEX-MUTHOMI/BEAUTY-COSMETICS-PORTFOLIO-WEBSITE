import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt, ReceiptPDFArtifact
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_full_booking_billing_receipt_email_pipeline_is_ci_deterministic(settings, tmp_path):
    from bookings.services.email_provider import FAKE_EMAIL_OUTBOX, reset_fake_email_outbox
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    reset_fake_email_outbox()

    booking = _held_booking(key="b4d-full-pipeline")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="b4d-full-pipeline-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-ci-parity",
        provider_receipt="receipt-ci-parity",
    )

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)
    diagnostic = f"failure_code={notification.failure_code} reason={notification.last_error_redacted}"

    assert result.sent == 1, diagnostic
    assert result.failed == 0, diagnostic
    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert (
        ReceiptPDFArtifact.objects.filter(receipt=booking.receipt, status=ReceiptPDFArtifact.Status.READY).count() == 1
    )
    assert len(FAKE_EMAIL_OUTBOX) == 1
    assert len(FAKE_EMAIL_OUTBOX[0]["attachments"]) == 1
    assert FAKE_EMAIL_OUTBOX[0]["attachments"][0]["content_type"] == "application/pdf"
    assert FAKE_EMAIL_OUTBOX[0]["attachments"][0]["size_bytes"] <= settings.RECEIPT_PDF_MAX_BYTES
    assert result == BookingNotificationDeliveryService.send_pending(limit=10).__class__(sent=1)
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 0
