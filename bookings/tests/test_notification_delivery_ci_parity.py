import pytest
from django.core.exceptions import ValidationError

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_pdf_failure_records_safe_ci_diagnostic_without_pii(monkeypatch, settings, tmp_path):
    from bookings.models import Booking, BookingNotification
    from bookings.services import notification_delivery
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("ci-diagnostic-failure")

    def fail_pdf(_receipt):
        raise ValidationError("PDF artifact missing for grace@example.com +254712345678")

    monkeypatch.setattr(notification_delivery.ReceiptPDFService, "ensure_artifact", fail_pdf)
    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)

    assert result.sent == 0
    assert result.failed == 1
    assert notification.failure_code == "pdf_artifact_unavailable"
    assert "redacted-email" in notification.last_error_redacted
    assert "+254" not in notification.last_error_redacted
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED


@pytest.mark.django_db(transaction=True)
def test_fake_provider_delivery_success_clears_failure_diagnostics(settings, tmp_path):
    from bookings.models import BookingNotification, ReceiptPDFArtifact
    from bookings.services.email_provider import FAKE_EMAIL_OUTBOX, reset_fake_email_outbox
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    reset_fake_email_outbox()
    booking, _session, _ledger = _confirm_paid_booking("ci-diagnostic-success")

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)

    assert result.sent == 1
    assert result.failed == 0
    assert notification.failure_code == ""
    assert notification.last_error_redacted == ""
    assert artifact.status == ReceiptPDFArtifact.Status.READY
    assert artifact.storage_key
    assert artifact.size_bytes > 0
    assert artifact.sha256_hash
    assert len(FAKE_EMAIL_OUTBOX) == 1
