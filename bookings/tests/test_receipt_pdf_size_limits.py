import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_oversized_pdf_is_rejected_and_not_attached(monkeypatch, settings):
    settings.RECEIPT_PDF_MAX_BYTES = 100
    booking, _session, _ledger = _confirm_paid_booking("pdf-size-limit")

    from bookings.models import BookingNotification, ReceiptPDFArtifact
    from bookings.services import receipt_pdf
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", lambda lines: b"%PDF-1.4\n" + (b"x" * 500))

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    assert result.sent == 0
    notification = BookingNotification.objects.get(booking=booking)
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)
    assert artifact.status == ReceiptPDFArtifact.Status.FAILED
    assert notification.status in {
        BookingNotification.Status.RETRY_SCHEDULED,
        BookingNotification.Status.ADMIN_REVIEW_REQUIRED,
        BookingNotification.Status.FAILED_FINAL,
    }
