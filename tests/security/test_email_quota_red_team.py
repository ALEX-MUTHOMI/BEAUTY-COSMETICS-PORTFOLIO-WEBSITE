import pytest
from django.core.cache import cache

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_email_quota_alerts_do_not_leak_pii_or_provider_payload(settings, caplog):
    cache.clear()
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_DAILY_HARD_LIMIT = 0
    _confirm_paid_booking("quota-red-team")

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    BookingNotificationDeliveryService.send_pending(limit=10)
    surface = caplog.text
    assert "grace@example.com" not in surface
    assert "+254712345678" not in surface
    assert "api_key" not in surface.lower()
