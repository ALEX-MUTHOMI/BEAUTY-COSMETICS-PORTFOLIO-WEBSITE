import pytest
from django.core.cache import cache

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_quota_blocked_viral_day_backlog_is_retained_without_duplicate_pdf(settings):
    cache.clear()
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_DAILY_HARD_LIMIT = 0
    for index in range(20):
        _confirm_paid_booking(f"quota-viral-{index}")

    from bookings.models import BookingNotification, ReceiptPDFArtifact
    from bookings.services.notification_delivery import BookingNotificationDeliveryService, notification_backlog_summary

    result = BookingNotificationDeliveryService.send_pending(limit=50)
    assert result.sent == 0
    assert notification_backlog_summary()["quota_blocked"] == 20
    assert BookingNotification.objects.filter(status=BookingNotification.Status.QUOTA_BLOCKED).count() == 20
    assert ReceiptPDFArtifact.objects.count() == 0
