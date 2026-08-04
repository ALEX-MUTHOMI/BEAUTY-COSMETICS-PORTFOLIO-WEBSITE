import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_three_hundred_notification_viral_day_backlog_is_bounded(settings):
    settings.EMAIL_PROVIDER = "fake"
    for index in range(30):
        _confirm_paid_booking(f"viral-day-{index}")

    from bookings.models import BookingNotification, ReceiptPDFArtifact
    from bookings.services.notification_delivery import BookingNotificationDeliveryService, notification_backlog_summary

    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 30
    assert notification_backlog_summary()["pending"] == 30
    sent = 0
    for _ in range(3):
        sent += BookingNotificationDeliveryService.send_pending(limit=10).sent
    assert sent == 30
    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 0
    assert ReceiptPDFArtifact.objects.count() == 30
