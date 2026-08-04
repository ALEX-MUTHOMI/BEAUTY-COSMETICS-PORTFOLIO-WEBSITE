import pytest

from bookings.models import BookingNotification, BookingReceipt, ReceiptPDFArtifact
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_pipeline_red_team_pdf_email_failures_do_not_corrupt_payment(settings, tmp_path, monkeypatch):
    from bookings.services import notification_delivery
    from bookings.services.email_provider import EmailProviderError
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("receipt-pipeline-red-team")

    class FailingProvider:
        provider = "fake"

        def send_email(self, **_kwargs):
            raise EmailProviderError("429 provider quota for grace@example.com +254712345678")

    monkeypatch.setattr(notification_delivery, "get_email_provider", lambda: FailingProvider())
    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)

    booking.refresh_from_db()
    assert result.sent == 0
    assert result.failed == 1
    assert booking.status == "confirmed"
    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert (
        ReceiptPDFArtifact.objects.filter(receipt=booking.receipt, status=ReceiptPDFArtifact.Status.READY).count() == 1
    )
    assert notification.failure_code in {"email_provider_rate_limited", "email_provider_failure"}
    assert "grace@example.com" not in notification.last_error_redacted
    assert "+254" not in notification.last_error_redacted
