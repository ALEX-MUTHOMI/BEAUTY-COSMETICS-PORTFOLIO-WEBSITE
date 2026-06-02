import pytest

from bookings.models import BookingNotification, ReceiptPDFArtifact
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
@pytest.mark.payment_load
def test_one_thousand_notification_backlog_is_batch_bounded_and_artifact_reuse_safe(settings, tmp_path):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    settings.EMAIL_DAILY_HARD_LIMIT = 0

    for index in range(1000):
        _confirm_paid_booking(f"b4d-backlog-{index}")

    first = BookingNotificationDeliveryService.send_pending(limit=100)
    assert first.sent == 0
    assert first.failed == 100
    assert BookingNotification.objects.filter(status=BookingNotification.Status.QUOTA_BLOCKED).count() == 100
    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 900
    assert ReceiptPDFArtifact.objects.filter(status=ReceiptPDFArtifact.Status.READY).count() == 100
    assert BookingNotification.objects.count() == 1000
